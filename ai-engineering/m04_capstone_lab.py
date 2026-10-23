"""Small deterministic RAG capstone: trusted provenance, revisions and fallback."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Source:
    id: str
    revision: int
    text: str
    roles: frozenset[str]
    facts: frozenset[str]
    deleted: bool = False

class Index:
    def __init__(self):
        self._docs = {}
    def apply(self, document: Source):
        prior = self._docs.get(document.id)
        if document.revision <= 0 or (prior and document.revision <= prior.revision):
            raise ValueError("stale or invalid revision")
        self._docs[document.id] = document
    def visible(self, role: str):
        return {id: d for id,d in self._docs.items() if not d.deleted and role in d.roles}

@dataclass(frozen=True)
class Result:
    status: str
    claims: tuple[tuple[str,str], ...]

def answer(index: Index, role: str, query: str, *, lexical_ok: bool = True,
           vector_ok: bool = True, allow_fallback: bool = True,
           latency_budget_ms: int = 900) -> Result:
    if latency_budget_ms <= 0:
        return Result("deadline_exceeded", ())
    if not lexical_ok and not vector_ok:
        return Result("retrieval_unavailable", ())
    if not lexical_ok or not vector_ok:
        if not allow_fallback:
            return Result("retrieval_degraded", ())
    visible = index.visible(role)
    if not visible:
        return Result("no_authorized_evidence", ())
    # Authenticated eligible content only; real search would use indexes.
    lexical = sorted([d for d in visible.values() if any(t in d.text.lower() for t in query.lower().split())],key=lambda d:d.id) if lexical_ok else []
    semantic = sorted(visible.values(), key=lambda d:d.id) if vector_ok else []  # authored candidate stand-in
    candidates = {d.id:d for d in lexical + semantic}
    if not candidates:
        return Result("no_evidence", ())
    # A policy answer is permitted only if an approved fact appears in eligible sources.
    policy = "A timeout does not prove a charge failed; check status before replay."
    eligible = sorted((d for d in candidates.values() if policy in d.facts),key=lambda d:d.id)
    if not eligible:
        return Result("insufficient_evidence", ())
    source = eligible[0]
    # Re-check source revision and permission at output boundary.
    current = index.visible(role).get(source.id)
    if current is None or current.revision != source.revision or policy not in current.facts:
        return Result("source_changed", ())
    return Result("grounded", ((policy, source.id + "@r" + str(source.revision)),))

if __name__ == "__main__":
    index = Index()
    policy = "A timeout does not prove a charge failed; check status before replay."
    index.apply(Source("pay503",1,"PAY-503 charge retry timeout",frozenset({"engineer"}),frozenset({policy})))
    print(answer(index,"engineer","PAY-503 charge timeout"))
