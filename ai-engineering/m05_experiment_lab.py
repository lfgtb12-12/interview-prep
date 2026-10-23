"""Independent-user binary A/B experiment arithmetic; no external dependencies.

Normal intervals are educational approximations, not a universal statistics engine.
Repeated copies of a user's outcome are NOT independent observations.
"""
from math import ceil, erfc, isfinite, sqrt
from statistics import NormalDist


def counts(successes, total):
    if type(total) is not int or total<=0 or type(successes) is not int or not 0<=successes<=total:
        raise ValueError('integer successes and positive total required')


def difference_interval(a, na, b, nb, confidence=.95):
    """Unpooled Wald interval for treatment minus control; eligible large counts only."""
    counts(a,na);counts(b,nb)
    if confidence not in (.90,.95,.99):raise ValueError('supported confidence: .90/.95/.99')
    pa,pb=a/na,b/nb
    delta=pb-pa
    if min(a,na-a,b,nb-b)<10:
        return {'delta':delta,'se':None,'lower':None,'upper':None}
    se=sqrt(pa*(1-pa)/na+pb*(1-pb)/nb)
    z=NormalDist().inv_cdf((1+confidence)/2)
    return {'delta':delta,'se':se,'lower':delta-z*se,'upper':delta+z*se}


def allocation_pvalue(na, nb):
    """Pearson chi-square approximation for a predeclared 1:1 assignment ratio."""
    if type(na) is not int or type(nb) is not int or min(na,nb)<5:
        raise ValueError('at least five assigned units per arm required')
    chi2=(na-nb)**2/(na+nb)
    return erfc(sqrt(chi2/2))


def approximate_per_arm(baseline=.8, mde=.03, alpha=.05, power=.8):
    """Planning heuristic: equal arms, independent Bernoulli units, test vs zero.

    This detects an effect of MDE against a zero-effect null. It does NOT power
    the stricter decision rule requiring an interval wholly above a margin=MDE.
    """
    values=(baseline,mde,alpha,power)
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not isfinite(v) for v in values):
        raise ValueError('finite numeric inputs required')
    if not 0<baseline<1 or not 0<mde<1-baseline or not 0<alpha<1 or not .5<power<1:
        raise ValueError('invalid planning inputs')
    za=NormalDist().inv_cdf(1-alpha/2)
    zb=NormalDist().inv_cdf(power)
    return ceil(2*(za+zb)**2*baseline*(1-baseline)/mde**2)


def zero_event_upper(n, confidence=.95):
    """Exact one-sided binomial upper bound when zero independent units fail."""
    if type(n) is not int or n<=0 or not 0<confidence<1:
        raise ValueError('positive independent-unit count and valid confidence required')
    return 1-(1-confidence)**(1/n)


SCENARIOS={
 'benefit': {'rate_b':.83,'latency_ms':1100,'cost':.018,'violations':0},
 'tiny': {'rate_b':.802,'latency_ms':1100,'cost':.018,'violations':0},
 'harm': {'rate_b':.78,'latency_ms':1100,'cost':.018,'violations':0},
 'slow': {'rate_b':.83,'latency_ms':1400,'cost':.018,'violations':0},
 'unsafe': {'rate_b':.83,'latency_ms':1100,'cost':.018,'violations':1},
}


def decision(interval, margin=.01, integrity=True, guardrails=True):
    if not isfinite(margin) or margin<0:raise ValueError('nonnegative finite margin required')
    if not integrity:return 'investigate'
    if not guardrails:return 'block'
    if interval['lower'] is None:return 'insufficient'
    if interval['upper']<0:return 'harm'
    if interval['upper']<margin:return 'below_margin'
    if interval['lower']>margin:return 'eligible'
    return 'inconclusive'


def simulate(n=2000, scenario='benefit', confidence=.95, margin=.01, copies=1, mismatch=False, peek=False):
    if type(n) is not int or n<20:raise ValueError('at least 20 users per planned arm required')
    if scenario not in SCENARIOS:raise ValueError('unknown scenario')
    if type(copies) is not int or not 1<=copies<=20:raise ValueError('copies must be 1..20')
    config=SCENARIOS[scenario]
    na,nb=n,7*n//10 if mismatch else n
    # Deterministic rounding, explicitly matched by the JavaScript fixture.
    a,b=int(.8*na+.5),int(config['rate_b']*nb+.5)
    interval=difference_interval(a,na,b,nb,confidence)
    naive=difference_interval(a*copies,na*copies,b*copies,nb*copies,confidence)
    srm_p=allocation_pvalue(na,nb)
    integrity=srm_p>=.001 and not peek
    guardrails=config['latency_ms']<=1200 and config['cost']<=.02 and config['violations']==0
    return {'a':a,'na':na,'b':b,'nb':nb,'interval':interval,'naive':naive,
            'srm_p':srm_p,'integrity':integrity,'guardrails':guardrails,
            'decision':decision(interval,margin,integrity,guardrails),
            'zero_event_bound':zero_event_upper(nb) if not config['violations'] else None}


if __name__=='__main__':
    for n in (200,2000,20000):
        print('users/arm:',n,simulate(n)['interval'],simulate(n)['decision'])
    print('planned n/arm for 3pp vs zero:',approximate_per_arm())
    print('zero violations / 200 users: one-sided 95% upper risk:',zero_event_upper(200))
