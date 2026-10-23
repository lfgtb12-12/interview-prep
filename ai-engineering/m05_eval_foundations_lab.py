"""Dependency-free, deterministic selective-answer evaluation.

Fixture scores are uncalibrated model confidences, NOT probabilities of truth.
Rows are adjudicated: answerable indicates sufficient authorized evidence;
correct means the proposed answer is supported and factually correct.
"""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Case:
    id: str
    slice: str
    answerable: bool
    correct: bool
    score: float
    authorized: bool = True

FIXTURES = (
    Case("a1","common",True,True,.95),
    Case("a2","common",True,True,.82),
    Case("a3","common",True,False,.64),
    Case("a4","rare-code",True,False,.89),
    Case("a5","rare-code",True,True,.58),
    Case("a6","common",False,False,.32),
    Case("a7","rare-code",False,False,.73),
    Case("a8","common",True,True,.77),
    Case("a9","permission",True,True,.99,False),
    Case("a10","permission",False,False,.85,False),
)

def evaluate(cases: Iterable[Case], threshold: float) -> dict:
    """Respond only above threshold AND when trusted ACL gate allows it.

    "precision" here is answered-item correctness, not retrieval precision.
    "coverage" is responses / all requests; "answerable_coverage" measures
    correctly answered answerable requests / all answerable requests.
    """
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be in [0,1]")
    rows = tuple(cases)
    if not rows:
        raise ValueError("evaluation dataset cannot be empty")
    if len({r.id for r in rows}) != len(rows):
        raise ValueError("duplicate case IDs")
    if any(not 0 <= r.score <= 1 for r in rows):
        raise ValueError("scores must lie in [0,1]")
    selected = tuple(r for r in rows if r.authorized and r.score >= threshold)
    correct = sum(r.correct and r.answerable for r in selected)
    errors = len(selected) - correct
    answerable = sum(r.answerable and r.authorized for r in rows)
    return {
        "requests": len(rows),
        "answered": len(selected),
        "correct": correct,
        "errors": errors,
        "abstained": len(rows)-len(selected),
        "coverage": len(selected)/len(rows),
        "answered_accuracy": correct/len(selected) if selected else None,
        "answerable_coverage": correct/answerable if answerable else None,
        "error_rate_per_request": errors/len(rows),
        "unauthorized_exposures": sum(not r.authorized for r in selected),
    }

def by_slice(cases: Iterable[Case], threshold: float) -> dict:
    rows = tuple(cases)
    return {name: evaluate((r for r in rows if r.slice == name), threshold)
            for name in sorted({r.slice for r in rows})}

if __name__ == "__main__":
    for threshold in (.5,.75,.9):
        print(threshold, evaluate(FIXTURES, threshold))
