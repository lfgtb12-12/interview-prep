"""Offline DAG runner. Python 3.11+; no external packages."""
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from typing import Callable

@dataclass(frozen=True)
class Task:
    deps: tuple[str, ...]
    fn: Callable[[dict], object]
    side_effect: bool = False

@dataclass
class Store:
    # Teaching store: substitute transactional DB for production.
    status: dict[str, str] = field(default_factory=dict)
    result: dict[str, object] = field(default_factory=dict)

class UnknownOutcome(RuntimeError):
    pass

def validate(tasks: dict[str, Task]) -> None:
    for name, task in tasks.items():
        if name in task.deps or any(d not in tasks for d in task.deps):
            raise ValueError("invalid dependency")
    seen, active = set(), set()
    def visit(n):
        if n in active:
            raise ValueError("cycle")
        if n in seen:
            return
        active.add(n)
        for d in tasks[n].deps:
            visit(d)
        active.remove(n)
        seen.add(n)
    for name in tasks:
        visit(name)

def run(tasks: dict[str, Task], store: Store, workers=2):
    validate(tasks)
    if workers < 1:
        raise ValueError("workers must be positive")
    pending = set(tasks) - {n for n in tasks if store.status.get(n) == "SUCCEEDED"}
    running = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        while pending or running:
            # Snapshot immutable dependency results before task submission.
            ready = sorted(n for n in pending if all(store.status.get(d) == "SUCCEEDED" for d in tasks[n].deps))
            for n in ready[:max(0, workers - len(running))]:
                if tasks[n].side_effect and store.status.get(n) in ("RUNNING", "UNKNOWN"):
                    raise UnknownOutcome(n + ": reconcile before replay")
                store.status[n] = "RUNNING"  # production: durable CAS before submission
                inputs = {d: store.result[d] for d in tasks[n].deps}
                running[pool.submit(tasks[n].fn, inputs)] = n
                pending.remove(n)
            if not running:
                raise RuntimeError("blocked by failed/unknown dependency")
            done, _ = wait(running, return_when=FIRST_COMPLETED)
            for future in done:
                n = running.pop(future)
                try:
                    value = future.result()
                except UnknownOutcome:
                    store.status[n] = "UNKNOWN"
                except Exception:
                    store.status[n] = "FAILED"
                else:
                    store.result[n] = value  # production: atomic result + status commit
                    store.status[n] = "SUCCEEDED"
            if any(store.status.get(n) in ("FAILED", "UNKNOWN") for n in tasks):
                # In-flight reads may finish; do not dispatch more downstream tasks.
                if running:
                    for future in running: future.cancel()
                raise RuntimeError("workflow stopped: inspect checkpoint")
    return store.result

def demo():
    tasks = {
        "orders": Task((), lambda _: ["o1", "o2"]),
        "inventory": Task((), lambda _: {"available": True}),
        "synthesize": Task(("orders", "inventory"), lambda v: {"evidence": v}),
        "report": Task(("synthesize",), lambda v: "report-ready"),
    }
    s = Store()
    assert run(tasks, s)["report"] == "report-ready"
    assert run(tasks, s)["report"] == "report-ready"  # completed steps skipped
    assert all(v == "SUCCEEDED" for v in s.status.values())

if __name__ == "__main__":
    demo()
    print("All assertions passed")
