"""Dependency-free RAG evaluation over reviewed labels, not automatic truth detection.

Units: unique passage IDs, atomic claims, claim-citation links and required facts.
Undefined denominators return None. Retrieval metrics require complete qrels;
real-world missing judgments must be adjudicated, not silently marked irrelevant.
"""
from math import log2
from statistics import mean


def retrieval_metrics(ranked, grades, k):
    """Grades 0..3; positive means relevant. Short result lists keep their ranks."""
    if type(k) is not int or k < 1:
        raise ValueError("k must be a positive integer")
    if len(ranked) != len(set(ranked)):
        raise ValueError("deduplicate passage IDs before ranking")
    if any(type(g) is not int or not 0 <= g <= 3 for g in grades.values()):
        raise ValueError("grades must be integers from 0 to 3")
    if set(ranked) - grades.keys():
        raise ValueError("every returned passage needs a relevance judgment")
    top = ranked[:k]
    relevant = {doc for doc, grade in grades.items() if grade > 0}
    hits = len(set(top) & relevant)
    def dcg(values):
        return sum((2**g - 1) / log2(i + 2) for i, g in enumerate(values))
    ideal = dcg(sorted(grades.values(), reverse=True)[:k])
    return {
        "recall": hits / len(relevant) if relevant else None,
        "rr": next((1 / (i+1) for i, doc in enumerate(top) if doc in relevant), 0.0) if relevant else None,
        "ndcg": dcg([grades[doc] for doc in top]) / ideal if ideal else None,
        "context_relevance": hits / len(top) if top else None,
    }


def answer_metrics(claims, context, required):
    """Claims have reviewed supporting IDs, citations, correct flag and fact ID.

    Support is single-passage entailment in this simplified lab. Joint-evidence
    claims require a richer annotation model. Correctness is independently judged.
    """
    if len(context) != len(set(context)):
        raise ValueError("duplicate context IDs")
    if len(required) != len(set(required)):
        raise ValueError("duplicate required facts")
    context = set(context)
    links = [(c, doc) for c in claims for doc in c['cites']]
    for c in claims:
        if type(c['correct']) is not bool or len(c['cites']) != len(set(c['cites'])):
            raise ValueError("invalid correctness label or duplicate citation")
    supported = sum(bool(set(c['supports']) & context) for c in claims)
    valid_links = sum(doc in context and doc in c['supports'] for c, doc in links)
    cited_claims = sum(any(doc in context and doc in c['supports'] for doc in c['cites']) for c in claims)
    facts = {c['fact'] for c in claims if c['correct']}
    return {
        "faithfulness": supported / len(claims) if claims else None,
        "citation_precision": valid_links / len(links) if links else None,
        "citation_coverage": cited_claims / len(claims) if claims else None,
        "completeness": len(set(required) & facts) / len(required) if required else None,
    }


def abstention_metrics(cases):
    """Each case: (authorized-corpus-answerable, abstained). Outages excluded."""
    if any(type(a) is not bool or type(b) is not bool for a, b in cases):
        raise ValueError("boolean labels required")
    no = [abstained for answerable, abstained in cases if not answerable]
    yes = [abstained for answerable, abstained in cases if answerable]
    return {
        "correct_abstention": sum(no) / len(no) if no else None,
        "false_abstention": sum(yes) / len(yes) if yes else None,
    }


GRADES = {'A': 3, 'B': 2, 'C': 0, 'D': 0}
CLAIMS = [
    {'text': 'Check payment status by request ID.', 'fact': 'status', 'correct': True, 'supports': ['A'], 'cites': ['A']},
    {'text': 'Do not blindly retry; reconcile unknown outcomes.', 'fact': 'no_retry', 'correct': True, 'supports': ['B'], 'cites': ['B']},
]
REQUIRED = ['status', 'no_retry']

if __name__ == '__main__':
    rankings = [['C', 'A', 'B', 'D'], ['A', 'B', 'C', 'D'], ['C', 'D']]
    for ranked in rankings:
        print(ranked, retrieval_metrics(ranked, GRADES, 2))
        print('answer:', answer_metrics(CLAIMS, ranked[:2], REQUIRED))
    # RR is a single-query metric. MRR is its mean over eligible queries.
    print('MRR@2:', mean(retrieval_metrics(r, GRADES, 2)['rr'] for r in rankings))
    print('abstention:', abstention_metrics([(True, False), (True, True), (False, True), (False, False)]))
