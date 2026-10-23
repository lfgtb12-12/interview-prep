"""Tiny deterministic RAG pipeline: no models, network or dependencies needed.

The retrieval scores are lexical teaching aids, not embeddings.
"""
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    source: str
    audience: frozenset[str]

DOCUMENTS = (
    Chunk("a", "Payments service retries transient 503 reads with jitter.", "payments-runbook#retry", frozenset({"engineering"})),
    Chunk("b", "Payments service outbound writes require an idempotency key.", "payments-runbook#writes", frozenset({"engineering"})),
    Chunk("c", "Survey service limits concurrent imports to ten.", "survey-runbook#import", frozenset({"engineering", "support"})),
    Chunk("secret", "Payments customer credentials are kept in vault.", "restricted-vault#credentials", frozenset({"security"})),
)

def tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.lower()))

def retrieve(question: str, role: str, k: int = 2) -> list[Chunk]:
    """ACL-filter BEFORE ranking; no match returns an empty list."""
    if not isinstance(k, int) or k < 1:
        raise ValueError("k must be a positive integer")
    query = tokens(question)
    ranked = []
    for chunk in DOCUMENTS:
        if role not in chunk.audience:
            continue
        score = len(query & tokens(chunk.text))
        if score:
            ranked.append((-score, chunk.id, chunk))
    ranked.sort(key=lambda item: (item[0], item[1]))
    return [entry[2] for entry in ranked[:k]]

def answer(question: str, role: str) -> dict:
    """Only return extractive evidence. Do not invent an answer for empty retrieval."""
    chunks = retrieve(question, role)
    if not chunks:
        return {"status": "insufficient_evidence", "answer": None, "citations": []}
    return {
        "status": "evidence_found",
        "answer": " ".join(chunk.text for chunk in chunks),
        "citations": [{"chunk_id": c.id, "source": c.source} for c in chunks],
    }
