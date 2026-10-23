"""Judge calibration arithmetic over authored, human-labeled fixtures.

No LLM is called. Ratings are ordinal fixture values, NOT probabilities.
Routing order: trusted hard failure, invalid judge output, then score bands.
"""
import json
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Case:
    id: str
    human_pass: bool
    baseline: float
    anchored: float
    slice: str
    valid: bool = True
    hard_gate: bool = True


CASES = (
    Case('j1',True,.95,.95,'routine'),
    Case('j2',True,.88,.90,'routine'),
    Case('j3',True,.72,.85,'paraphrase'),
    Case('j4',True,.62,.80,'terse'),
    Case('j5',True,.48,.78,'terse'),
    Case('j6',False,.92,.45,'polished-unsupported'),
    Case('j7',False,.78,.40,'missing-safety-fact'),
    Case('j8',False,.59,.25,'wrong-citation'),
    Case('j9',False,.35,.20,'contradiction'),
    Case('j10',False,.20,.10,'irrelevant'),
    Case('j11',True,.99,.99,'invalid-json',valid=False),
    Case('j12',False,.98,.98,'missing-citation',hard_gate=False),
)


def route(case, threshold=.75, band=.1, profile='baseline'):
    if profile not in ('baseline','anchored'):
        raise ValueError('unknown judge profile')
    if not all(isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) for x in (threshold,band)) or not 0<=threshold<=1 or not 0<=band<=.5:
        raise ValueError('invalid threshold or review band')
    score=getattr(case,profile)
    if not math.isfinite(score) or not 0<=score<=1:
        raise ValueError('invalid fixture score')
    if not case.hard_gate:return 'fail'
    if not case.valid:return 'review'
    if score>=threshold+band:return 'pass'
    if score<threshold-band:return 'fail'
    return 'review'


def evaluate(cases, threshold=.75, band=.1, profile='baseline'):
    if len(cases)!=len({c.id for c in cases}):
        raise ValueError('duplicate case ID')
    counts=dict(tp=0,fp=0,tn=0,fn=0,review=0)
    for c in cases:
        if type(c.human_pass) is not bool:raise ValueError('boolean human label required')
        decision=route(c,threshold,band,profile)
        key='review' if decision=='review' else ('tp' if c.human_pass else 'fp') if decision=='pass' else ('fn' if c.human_pass else 'tn')
        counts[key]+=1
    automated=len(cases)-counts['review']
    passed=counts['tp']+counts['fp']
    return {**counts,'total':len(cases),'coverage':automated/len(cases) if cases else None,
            'agreement':(counts['tp']+counts['tn'])/automated if automated else None,
            'pass_precision':counts['tp']/passed if passed else None}


def parse_rubric_output(raw, allowed_ids):
    """Validate protocol and provenance IDs; cannot establish semantic truth."""
    def unique(pairs):
        result={}
        for k,v in pairs:
            if k in result:raise ValueError('duplicate JSON key')
            result[k]=v
        return result
    data=json.loads(raw,object_pairs_hook=unique)
    keys={'support','completeness','correctness','evidence_ids','reason'}
    if type(data) is not dict or data.keys()!=keys:raise ValueError('unexpected schema')
    for key in ('support','completeness','correctness'):
        if data[key] not in ('pass','fail','unknown'):raise ValueError('invalid criterion')
    ids=data['evidence_ids']
    if type(ids) is not list or any(type(x) is not str for x in ids) or len(ids)!=len(set(ids)) or not set(ids)<=set(allowed_ids):
        raise ValueError('invalid evidence IDs')
    if type(data['reason']) is not str or not data['reason'].strip() or len(data['reason'])>500:
        raise ValueError('bounded explanation required')
    values=[data[key] for key in ('support','completeness','correctness')]
    # Any known failed mandatory criterion fails the semantic rubric.
    verdict='fail' if 'fail' in values else 'review' if 'unknown' in values else 'pass'
    if verdict=='pass' and not ids:raise ValueError('supporting evidence required')
    return verdict


def swap_consistency(pairs):
    """Votes are original candidate IDs after mapping display positions back."""
    if any(a not in ('A','B','tie') or b not in ('A','B','tie') for a,b in pairs):
        raise ValueError('invalid pairwise vote')
    return sum(a==b for a,b in pairs)/len(pairs) if pairs else None


if __name__=='__main__':
    for profile in ('baseline','anchored'):
        print(profile,evaluate(CASES,profile=profile))
    print('swap consistency:',swap_consistency([('A','A'),('A','B'),('tie','tie'),('B','A')]))
