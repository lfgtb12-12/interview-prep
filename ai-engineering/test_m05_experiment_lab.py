import sys
import unittest
from math import sqrt
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from m05_experiment_lab import difference_interval, approximate_per_arm, zero_event_upper, allocation_pvalue, simulate, decision

class ExperimentTests(unittest.TestCase):
    def test_independent_difference_and_interval(self):
        m=difference_interval(1600,2000,1660,2000)
        self.assertAlmostEqual(m['delta'],.03)
        self.assertAlmostEqual(m['se'],sqrt((.8*.2+.83*.17)/2000))
        self.assertLess(m['lower'],.01);self.assertGreater(m['lower'],0)
    def test_zero_effect_interval(self):
        m=difference_interval(80,100,80,100)
        self.assertEqual(m['delta'],0);self.assertAlmostEqual(m['lower'],-m['upper'])
    def test_more_users_shrink_width(self):
        a,b=simulate(200),simulate(20000)
        self.assertAlmostEqual(a['interval']['se']/b['interval']['se'],10)
    def test_wider_confidence_widens_interval(self):
        self.assertLess(simulate(confidence=.99)['interval']['lower'],simulate(confidence=.90)['interval']['lower'])
    def test_sparse_counts_return_no_normal_interval(self):
        for a,n,b,nb in ((0,100,1,100),(100,100,99,100),(1,5,2,5)):
            self.assertIsNone(difference_interval(a,n,b,nb)['lower'])
    def test_invalid_counts_and_confidence(self):
        for args in ((-1,10,5,10),(1,0,5,10),(True,10,5,10),(1,10,11,10)):
            with self.assertRaises(ValueError):difference_interval(*args)
        with self.assertRaises(ValueError):difference_interval(80,100,83,100,.8)
    def test_default_is_inconclusive_for_one_point_margin(self):
        self.assertEqual(simulate()['decision'],'inconclusive')
    def test_large_benefit_is_eligible_not_automatic_launch(self):
        self.assertEqual(simulate(20000)['decision'],'eligible')
    def test_practical_and_statistical_decisions_differ(self):
        self.assertEqual(simulate(20000,'tiny')['decision'],'below_margin')
        self.assertEqual(simulate(20000,'harm')['decision'],'harm')
    def test_guardrail_blocks_benefit(self):
        for scenario in ('slow','unsafe'):
            self.assertEqual(simulate(20000,scenario)['decision'],'block')
    def test_sample_ratio_integrity(self):
        self.assertEqual(allocation_pvalue(1000,1000),1)
        self.assertLess(allocation_pvalue(2000,1400),.001)
        self.assertEqual(simulate(mismatch=True)['decision'],'investigate')
    def test_peeking_invalidates_fixed_horizon_decision(self):
        self.assertEqual(simulate(20000,peek=True)['decision'],'investigate')
    def test_duplicates_do_not_change_valid_interval_or_decision(self):
        a,b=simulate(copies=1),simulate(copies=10)
        self.assertEqual(a['interval'],b['interval']);self.assertEqual(a['decision'],b['decision'])
        self.assertAlmostEqual(a['interval']['se']/b['naive']['se'],sqrt(10))
    def test_planning_mde_halving_quadruples_size(self):
        a,b=approximate_per_arm(mde=.04),approximate_per_arm(mde=.02)
        self.assertLessEqual(abs(b-4*a),3)
        self.assertEqual(approximate_per_arm(),2791)
    def test_power_and_confidence_cost_samples(self):
        n=approximate_per_arm()
        self.assertGreater(approximate_per_arm(power=.9),n)
        self.assertGreater(approximate_per_arm(alpha=.01),n)
    def test_invalid_planning_inputs(self):
        for kw in ({'mde':0},{'baseline':1},{'power':.2},{'alpha':0},{'mde':float('nan')},{'baseline':True}):
            with self.assertRaises(ValueError):approximate_per_arm(**kw)
    def test_zero_event_exact_bound(self):
        bound=zero_event_upper(200)
        self.assertAlmostEqual((1-bound)**200,.05)
        self.assertGreater(bound,0);self.assertLess(zero_event_upper(2000),bound)
    def test_invalid_risk_sample(self):
        for n in (0,-1,True):
            with self.assertRaises(ValueError):zero_event_upper(n)
    def test_inference_gate_precedence_and_no_interval(self):
        sparse=difference_interval(0,100,1,100)
        self.assertEqual(decision(sparse),'insufficient')
        self.assertEqual(decision(sparse,integrity=False,guardrails=False),'investigate')
        self.assertEqual(decision(sparse,guardrails=False),'block')
    def test_simulator_validation(self):
        for kw in ({'n':1},{'copies':0},{'scenario':'unknown'}):
            with self.assertRaises(ValueError):simulate(**kw)

if __name__=='__main__':unittest.main()
