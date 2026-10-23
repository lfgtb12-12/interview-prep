"""Pure Python evaluation lab. Explicit judged labels, not an LLM judge."""
from dataclasses import dataclass
from math import log2
from statistics import mean

def recall_at_k(results: list[str], relevant: set[str], k: int) -> float:
    if k <= 0 or not relevant:
        raise ValueError("positive k and nonempty relevance required")
    return len(set(results[:k]) & relevant) / len(relevant)

def precision_at_k(results: list[str], relevant: set[str], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")
    return len(set(results[:k]) & relevant) / k

def reciprocal_rank(results: list[str], relevant: set[str]) -> float:
    return next((1 / (i+1) for i, doc in enumerate(results) if doc in relevant), 0.0)

def ndcg_at_k(results: list[str], grades: dict[str, int], k: int) -> float:
    if k <= 0 or any(not isinstance(g, int) or g < 0 for g in grades.values()):
        raise ValueError("invalid k or relevance grades")
    if len(results) != len(set(results)):
        raise ValueError("duplicate document IDs")
    def dcg(values):
        return sum((2**g - 1) / log2(rank+2) for rank, g in enumerate(values))
    actual = dcg([grades.get(doc, 0) for doc in results[:k]])
    ideal = dcg(sorted(grades.values(), reverse=True)[:k])
    return actual / ideal if ideal else 0.0

@dataclass(frozen=True)
class Case:
    query: str
    candidates: tuple[str, ...]
    context: tuple[str, ...]
    relevant: frozenset[str]
    claim_supported: tuple[bool, ...]
    latency_ms: int

def evaluate(cases: list[Case], k: int = 2) -> dict[str, float]:
    if not cases:
        raise ValueError("at least one case required")
    if k <= 0:
        raise ValueError("positive k required")
    for c in cases:
        if not c.relevant or c.latency_ms < 0:
            raise ValueError("invalid judged case")
        if len(c.candidates) != len(set(c.candidates)) or len(c.context) != len(set(c.context)):
            raise ValueError("duplicate IDs")
        if not set(c.context).issubset(c.candidates):
            raise ValueError("context must come from authorized candidates")
    all_claims = [v for c in cases for v in c.claim_supported]
    return {
        "candidate_recall": mean(recall_at_k(list(c.candidates), set(c.relevant), len(c.candidates)) for c in cases),
        "context_recall_at_k": mean(recall_at_k(list(c.context), set(c.relevant), k) for c in cases),
        "support_rate": sum(all_claims) / len(all_claims) if all_claims else 0.0,
        "mean_latency_ms": mean(c.latency_ms for c in cases)
    }

def diagnose(case: Case, k: int = 2) -> str:
    if not set(case.relevant).issubset(case.candidates):
        return "candidate_retrieval"
    if not set(case.relevant).issubset(case.context[:k]):
        return "rerank_or_context"
    if not all(case.claim_supported):
        return "generation_or_verification"
    return "ok"

if __name__ == "__main__":
    cases = [
        Case("PAY-503 replay", ("pay503","retry","general"), ("pay503","retry"), frozenset({"pay503","retry"}), (True,True), 510),
        Case("timeout fallback", ("retry","general"), ("retry","general"), frozenset({"pay503","retry"}), (False,True), 580)
    ]
    print(evaluate(cases))
    for c in cases:
        print(c.query, diagnose(c))
