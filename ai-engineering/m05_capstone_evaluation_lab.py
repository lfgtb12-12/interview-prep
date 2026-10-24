"""M05-L07 launch decision capstone: deterministic, authored fixtures.

Each phase has its own evidence. Offline tests cannot prove user behavior;
shadow cannot measure exposure effects; online cannot override hard security gates.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Evidence:
    name: str
    offline_success: int = 88
    offline_total: int = 100
    rare_success: int = 8
    rare_total: int = 10
    unsafe_calls: int = 0
    unverified_writes: int = 0
    missing_traces: int = 0
    shadow_latency_ms: int = 1050
    shadow_cost_mills: int = 18
    online_users: int = 2000
    control_success: int = 1600
    treatment_success: int = 1660
    guardrail_incidents: int = 0

FIXTURES = {
    "healthy": Evidence("healthy"),
    "rare_regression": Evidence("rare_regression",rare_success=5),
    "unsafe": Evidence("unsafe",unsafe_calls=1),
    "unknown_write": Evidence("unknown_write",unverified_writes=1),
    "missing": Evidence("missing",missing_traces=3),
    "slow": Evidence("slow",shadow_latency_ms=1700),
    "expensive": Evidence("expensive",shadow_cost_mills=30),
    "inconclusive": Evidence("inconclusive",online_users=200,control_success=160,treatment_success=166),
    "online_harm": Evidence("online_harm",control_success=1600,treatment_success=1500),
    "incident": Evidence("incident",guardrail_incidents=1),
}
def decide(scenario="healthy", phase="online", rare_floor=.75, margin=.01):
    if scenario not in FIXTURES: raise ValueError("unknown scenario")
    if phase not in ("offline","shadow","online"): raise ValueError("invalid phase")
    if not 0<=rare_floor<=1 or not 0<=margin<1: raise ValueError("invalid thresholds")
    x=FIXTURES[scenario]
    failures=[]
    if x.unsafe_calls: failures.append("unauthorized tool calls")
    if x.unverified_writes: failures.append("unreconciled side effects")
    if x.missing_traces: failures.append("incomplete trace coverage")
    if x.offline_success/x.offline_total<.80:failures.append("overall offline task floor")
    if x.rare_success/x.rare_total<rare_floor:failures.append("rare-task slice floor")
    if failures:return {"decision":"BLOCK","phase":phase,"reasons":failures,"delta":None,"lower":None,"upper":None,"rare_rate":x.rare_success/x.rare_total}
    if phase=="offline":return {"decision":"SHADOW","phase":phase,"reasons":["offline gates passed; measure shadow latency and cost"],"delta":None,"lower":None,"upper":None,"rare_rate":x.rare_success/x.rare_total}
    if x.shadow_latency_ms>1200:failures.append("shadow latency budget")
    if x.shadow_cost_mills>20:failures.append("shadow cost budget")
    if failures:return {"decision":"BLOCK","phase":phase,"reasons":failures,"delta":None,"lower":None,"upper":None,"rare_rate":x.rare_success/x.rare_total}
    if phase=="shadow":return {"decision":"CANARY","phase":phase,"reasons":["shadow gates passed; online outcomes still unknown"],"delta":None,"lower":None,"upper":None,"rare_rate":x.rare_success/x.rare_total}
    if x.guardrail_incidents:return {"decision":"ROLLBACK","phase":phase,"reasons":["online safety incident"],"delta":None,"lower":None,"upper":None,"rare_rate":x.rare_success/x.rare_total}
    import math
    n=x.online_users
    a=x.control_success/n;b=x.treatment_success/n
    effect=b-a
    se=math.sqrt(a*(1-a)/n+b*(1-b)/n)
    low=effect-1.959963984540054*se
    high=effect+1.959963984540054*se
    if low>margin:status="GUARDED_ROLLOUT"
    elif high<0:status="ROLLBACK"
    else:status="HOLD"
    return {"decision":status,"phase":phase,"reasons":[{"GUARDED_ROLLOUT":"practical benefit supported under illustrative assumptions","ROLLBACK":"observed interval below zero","HOLD":"practical benefit not established"}[status]],"delta":effect,"lower":low,"upper":high,"rare_rate":x.rare_success/x.rare_total}

if __name__=="__main__":
    for name in FIXTURES:
        print(name, decide(name)["decision"])
