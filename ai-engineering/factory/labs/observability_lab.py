"""M03-L06: deterministic report-agent observability exercise (stdlib only).

Educational simulator: no model API or customer data.
"""
from dataclasses import dataclass, field
from typing import Iterable


@dataclass
class RunTrace:
    run_id: str
    stages: list[dict] = field(default_factory=list)

    def record(self, stage: str, ids: Iterable[str], outcome: str = "ok") -> None:
        # This deliberately records IDs and counts, not ticket bodies or credentials.
        identifiers = list(ids)
        self.stages.append({"stage": stage, "count": len(identifiers),
                            "source_ids": identifiers, "outcome": outcome})


def evaluate(required: set[str], retrieved: set[str], included: set[str]) -> dict:
    """A support proxy based on IDs, NOT semantic claim entailment."""
    return {
        "retrieval_coverage": len(required & retrieved) / len(required) if required else 1.0,
        "answer_completeness": len(required & included) / len(required) if required else 1.0,
        "unsupported_ids": sorted(included - retrieved),
        "missing_at_retrieval": sorted(required - retrieved),
        "missing_at_synthesis": sorted((required & retrieved) - included),
    }


def simulate(required: Iterable[str], *, drop_at_retrieval=(), drop_at_synthesis=(),
             deadline_exceeded=False) -> tuple[RunTrace, dict]:
    required_set = set(required)
    trace = RunTrace("educational-run")
    trace.record("input", sorted(required_set))
    retrieved = required_set - set(drop_at_retrieval)
    trace.record("retrieval", sorted(retrieved))
    included = set() if deadline_exceeded else retrieved - set(drop_at_synthesis)
    trace.record("synthesis", sorted(included),
                 "deadline_exceeded" if deadline_exceeded else "ok")
    report = evaluate(required_set, retrieved, included)
    report["status"] = "deadline_exceeded" if deadline_exceeded else (
        "complete" if report["answer_completeness"] == 1.0 and not report["unsupported_ids"]
        else "incomplete")
    return trace, report
