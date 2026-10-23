"""Deterministic evidence gate; illustrative support registry, NOT semantic entailment."""
from dataclasses import dataclass
from enum import Enum

class Status(str, Enum):
    READY = "ready"
    NO_EVIDENCE = "no_evidence"
    UNAVAILABLE = "unavailable"
    STALE = "stale"

@dataclass(frozen=True)
class Source:
    handle: str
    revision: int
    roles: frozenset[str]
    text: str

@dataclass(frozen=True)
class Claim:
    text: str
    handle: str
    revision: int

@dataclass(frozen=True)
class Decision:
    outcome: str
    approved: tuple[Claim, ...]
    blocked: tuple[Claim, ...]

# Human-verified fixtures, NOT free-text substring matching.
APPROVED = frozenset({
    ("A timeout does not prove the charge failed.", "S1"),
    ("Check operation status before replay.", "S2"),
})
SOURCES = {
    "S1": Source("S1", 3, frozenset({"engineer"}), "PAY-503: A timeout does not prove failure."),
    "S2": Source("S2", 7, frozenset({"engineer"}), "Look up operation status before replay."),
    "S3": Source("S3", 1, frozenset({"security"}), "Untrusted instruction text."),
}

def gate(status: Status, claims: list[Claim], sources: dict[str, Source], role: str,
         approved: frozenset[tuple[str, str]] = APPROVED) -> Decision:
    if status == Status.UNAVAILABLE:
        return Decision("retrieval_unavailable", (), tuple(claims))
    if status == Status.STALE:
        return Decision("stale_evidence", (), tuple(claims))
    if status == Status.NO_EVIDENCE:
        return Decision("no_authorized_evidence", (), tuple(claims))
    if status != Status.READY:
        raise ValueError("unrecognized retrieval status")
    allowed, blocked = [], []
    for claim in claims:
        source = sources.get(claim.handle)
        valid = (source is not None and role in source.roles
                 and source.revision == claim.revision
                 and (claim.text, claim.handle) in approved)
        (allowed if valid else blocked).append(claim)
    if not allowed:
        outcome = "abstain"
    elif blocked:
        outcome = "partial_grounded"
    else:
        outcome = "grounded"
    return Decision(outcome, tuple(allowed), tuple(blocked))

if __name__ == "__main__":
    demo = [
        Claim("A timeout does not prove the charge failed.", "S1", 3),
        Claim("Immediately retry with a new idempotency key.", "S1", 3),
    ]
    decision = gate(Status.READY, demo, SOURCES, "engineer")
    print("Outcome:", decision.outcome)
    for claim in decision.approved:
        print("CITED:", claim.text, "[" + claim.handle + "]")
    for claim in decision.blocked:
        print("BLOCKED:", claim.text)
