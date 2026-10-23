"""Small dependency-free vector search lab, Python 3.11+.

Vectors are hand-authored illustrations, NOT output from an embedding model.
"""
from dataclasses import dataclass
from math import sqrt, isfinite

@dataclass(frozen=True)
class Passage:
    id: str
    vector: tuple[float, ...]
    role: str

DATA = (
    Passage("retry-runbook", (1.0, 0.0, 0.0), "engineer"),
    Passage("write-safety", (0.8, 0.6, 0.0), "engineer"),
    Passage("survey-guide", (0.0, 1.0, 0.0), "engineer"),
    Passage("restricted", (1.0, 0.0, 0.0), "security"),
)

def validate(vector):
    if not vector or any(not isinstance(x, (int, float)) or not isfinite(x) for x in vector):
        raise ValueError("Vector must contain finite numbers")

def dot(a, b):
    validate(a)
    validate(b)
    if len(a) != len(b):
        raise ValueError("Dimensions differ")
    return sum(x * y for x, y in zip(a, b))

def magnitude(a):
    validate(a)
    return sqrt(dot(a, a))

def cosine(a, b):
    den = magnitude(a) * magnitude(b)
    if den == 0:
        raise ValueError("Cosine undefined for zero vector")
    return dot(a, b) / den

def squared_l2(a, b):
    validate(a)
    validate(b)
    if len(a) != len(b):
        raise ValueError("Dimensions differ")
    return sum((x-y)**2 for x, y in zip(a, b))

def search(query, role="engineer", metric="cosine", k=2):
    if metric not in ("cosine", "dot", "l2"):
        raise ValueError("Unknown metric")
    if type(k) is not int or k < 1:
        raise ValueError("k must be positive")
    validate(query)
    visible = [p for p in DATA if p.role == role]
    score = {"cosine": cosine, "dot": dot, "l2": squared_l2}[metric]
    scored = [(score(query, p.vector), p.id) for p in visible]
    scored.sort(key=lambda pair: (pair[0] if metric == "l2" else -pair[0], pair[1]))
    return scored[:k]

if __name__ == "__main__":
    for metric in ("cosine", "dot", "l2"):
        print(metric, search((1., 0., 0.), metric=metric))
