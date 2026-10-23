"""Deterministic hybrid retrieval teaching lab. Python 3.11+, standard library only."""
from collections import Counter
from dataclasses import dataclass
from math import log
import re

@dataclass(frozen=True)
class Doc:
    id: str
    text: str
    roles: frozenset[str]

DOCS = (
    Doc("pay-503", "PAY-503 charge timeout unknown outcome reconcile before replay", frozenset({"engineer"})),
    Doc("retry", "payment retry idempotency key transient failures", frozenset({"engineer"})),
    Doc("timeout", "HTTP timeout general guidance", frozenset({"engineer"})),
    Doc("survey", "survey imports retry transient failures", frozenset({"engineer"})),
    Doc("security-only", "PAY-503 confidential root cause", frozenset({"security"})),
)

def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower())

def bm25(query: str, docs: list[Doc], k1: float = 1.2, b: float = 0.75) -> list[tuple[str, float]]:
    if k1 <= 0 or not 0 <= b <= 1:
        raise ValueError("invalid BM25 parameters")
    if not docs:
        return []
    words = [Counter(tokenize(d.text)) for d in docs]
    avgdl = sum(sum(w.values()) for w in words) / len(words)
    if avgdl == 0:
        return [(d.id, 0.0) for d in sorted(docs, key=lambda d: d.id)]
    df = Counter(t for counts in words for t in counts)
    query_terms = set(tokenize(query))
    scored = []
    for doc, counts in zip(docs, words):
        length = sum(counts.values())
        score = 0.0
        for term in query_terms:
            tf = counts[term]
            if tf:
                idf = log(1 + (len(docs)-df[term]+0.5)/(df[term]+0.5))
                score += idf * tf * (k1+1)/(tf+k1*(1-b+b*length/avgdl))
        scored.append((doc.id, score))
    return sorted(scored, key=lambda pair: (-pair[1], pair[0]))

def rrf(lexical: list[str], semantic: list[str], weight: float = 0.5, k: int = 60) -> list[tuple[str, float]]:
    if not 0 <= weight <= 1 or k <= 0:
        raise ValueError("invalid fusion parameters")
    if len(lexical) != len(set(lexical)) or len(semantic) != len(set(semantic)):
        raise ValueError("duplicate IDs in a branch")
    scores = {}
    for ids, w in ((lexical, weight), (semantic, 1-weight)):
        for rank, ident in enumerate(ids, 1):
            scores[ident] = scores.get(ident, 0.0) + w/(k+rank)
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))

def candidates(role: str, query: str, semantic_ids: list[str], limit: int = 4) -> list[str]:
    if limit <= 0:
        raise ValueError("limit must be positive")
    eligible = [d for d in DOCS if role in d.roles]
    allowed = {d.id for d in eligible}
    lexical = [id for id, score in bm25(query, eligible) if score > 0][:limit]
    semantic = [ident for ident in semantic_ids if ident in allowed][:limit]
    return [ident for ident, _ in rrf(lexical, semantic)]

def rerank(ids: list[str], pair_scores: dict[str, float], top_k: int) -> list[str]:
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    if any(ident not in pair_scores for ident in ids):
        raise ValueError("reranker score missing for candidate")
    return sorted(ids, key=lambda ident: (-pair_scores[ident], ident))[:top_k]

def recall_at_k(ids: list[str], relevant: set[str], k: int) -> float:
    if not relevant or k <= 0:
        raise ValueError("nonempty relevance and positive k required")
    return len(set(ids[:k]) & relevant) / len(relevant)

def reciprocal_rank(ids: list[str], relevant: set[str]) -> float:
    return next((1/rank for rank, ident in enumerate(ids, 1) if ident in relevant), 0.0)

if __name__ == "__main__":
    query = "PAY-503 charge replay"
    pool = candidates("engineer", query, ["retry", "timeout", "pay-503", "survey"])
    ranked = rerank(pool, {"pay-503": .97, "retry": .83, "timeout": .3, "survey": .1}, 3)
    print("Query:", query)
    print("Candidate pool:", pool)
    print("Reranked top-3:", ranked)
    print("Recall@3:", recall_at_k(ranked, {"pay-503", "retry"}, 3))
    print("MRR:", reciprocal_rank(ranked, {"pay-503"}))
