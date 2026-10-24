"""M05-L06: deterministic CI evaluation gates and monitoring fixtures (stdlib only).

One case = one independently labeled task; unobserved outcomes remain missing,
not silently counted as a success. This is a teaching harness, not a statistical
significance test or permission enforcement.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Task:
    id: str
    slice: str
    baseline: bool
    candidate: bool
    safety_ok: bool = True
    latency_ms: int = 800
    cost_millicents: int = 100
    trace_ok: bool = True

TASKS = (
    Task("a1","common",True,True),Task("a2","common",True,True),
    Task("a3","common",True,True),Task("a4","common",False,True),
    Task("a5","common",True,True),Task("a6","common",True,True),
    Task("b1","rare",True,False),Task("b2","rare",True,False),
    Task("b3","rare",False,True),Task("b4","rare",True,True),
)
PROFILES = {
    "healthy":{},
    "rare_regression":{"b3":False,"b4":False},
    "safety":{"a1_safety":False},
    "latency":{"a1_latency":2200},
    "cost":{"a1_cost":700},
    "broken_trace":{"a1_trace":False},
    "missing":{"b1_missing":True},
}
def evaluate(profile="healthy", min_tasks=2, min_rate=.5, max_regression=.25,
             latency_budget=1500, cost_budget=500, strict_missing=True):
    if profile not in PROFILES:raise ValueError("unknown fixture")
    if type(min_tasks) is not int or min_tasks<1:raise ValueError("positive min_tasks required")
    if not 0<=min_rate<=1 or not 0<=max_regression<=1:raise ValueError("invalid rate threshold")
    if latency_budget<=0 or cost_budget<=0:raise ValueError("positive budgets required")
    overrides=PROFILES[profile]
    per_slice={}
    failures=[]
    observed=0
    for t in TASKS:
        d=per_slice.setdefault(t.slice,{"total":0,"observed":0,"baseline":0,"candidate":0})
        d["total"]+=1;d["baseline"]+=int(t.baseline)
        if overrides.get(t.id+"_missing",False):continue
        observed+=1;d["observed"]+=1
        candidate=overrides.get(t.id,t.candidate)
        d["candidate"]+=int(candidate)
        if not overrides.get(t.id+"_safety",t.safety_ok):failures.append(t.id+": unsafe")
        if not overrides.get(t.id+"_trace",t.trace_ok):failures.append(t.id+": broken trace")
        if overrides.get(t.id+"_latency",t.latency_ms)>latency_budget:failures.append(t.id+": latency")
        if overrides.get(t.id+"_cost",t.cost_millicents)>cost_budget:failures.append(t.id+": cost")
    slices={}
    for name,d in per_slice.items():
        complete=d["observed"]==d["total"]
        base=d["baseline"]/d["total"]
        cand=d["candidate"]/d["observed"] if d["observed"] else None
        # Fixed-case paired regression = baseline successes lost / total labeled tasks;
        # separately report coverage because incomplete observations invalidate comparison.
        lost=sum(1 for t in TASKS if t.slice==name and t.baseline and
            not overrides.get(t.id+"_missing",False) and not overrides.get(t.id,t.candidate))
        lost_rate=lost/d["total"]
        slices[name]={**d,"baseline_rate":base,"candidate_rate":cand,
                      "lost_rate":lost_rate,"complete":complete}
        if d["total"]<min_tasks:failures.append(name+": insufficient fixture coverage")
        if strict_missing and not complete:failures.append(name+": missing observations")
        if cand is not None and cand<min_rate:failures.append(name+": quality below minimum")
        if lost_rate>max_regression:failures.append(name+": paired regressions")
    return {"profile":profile,"total":len(TASKS),"observed":observed,
            "slices":slices,"failures":failures,"decision":"BLOCK" if failures else "PASS"}
if __name__=="__main__":
    for p in PROFILES: print(p,evaluate(p)["decision"],evaluate(p)["failures"])
