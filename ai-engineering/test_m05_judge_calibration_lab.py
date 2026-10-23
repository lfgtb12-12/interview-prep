import json
import sys
import unittest
from dataclasses import replace
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from m05_judge_calibration_lab import CASES, evaluate, route, parse_rubric_output, swap_consistency

class JudgeTests(unittest.TestCase):
    def test_baseline_confusion_and_denominators(self):
        m=evaluate(CASES)
        self.assertEqual([m[k] for k in ('tp','fp','tn','fn','review')],[2,1,4,2,3])
        self.assertEqual(m['coverage'],.75);self.assertAlmostEqual(m['agreement'],6/9)
        self.assertAlmostEqual(m['pass_precision'],2/3)
    def test_anchored_profile_is_authored_comparison(self):
        m=evaluate(CASES,profile='anchored')
        self.assertEqual([m[k] for k in ('tp','fp','tn','fn','review')],[3,0,6,0,3])
        self.assertEqual(m['agreement'],1);self.assertEqual(m['coverage'],.75)
    def test_hard_failure_cannot_be_overridden(self):
        self.assertEqual(route(CASES[-1],0,0),'fail')
        self.assertEqual(route(replace(CASES[-1],valid=False),0,0),'fail')
    def test_invalid_output_is_review_even_at_high_rating(self):
        self.assertEqual(route(CASES[-2],0,0),'review')
    def test_exact_band_edges(self):
        self.assertEqual(route(replace(CASES[0],baseline=.75),.75,0),'pass')
        self.assertEqual(route(replace(CASES[0],baseline=.5),.5,.25),'review')
        self.assertEqual(route(replace(CASES[0],baseline=.25),.5,.25),'review')
        self.assertEqual(route(replace(CASES[0],baseline=.75),.5,.25),'pass')
    def test_all_review_undefined_agreement(self):
        m=evaluate(CASES[:1],.5,.5)
        self.assertEqual(m['coverage'],0);self.assertIsNone(m['agreement']);self.assertIsNone(m['pass_precision'])
    def test_empty_dataset(self):
        self.assertIsNone(evaluate([])['coverage'])
    def test_invalid_thresholds_profile_and_ids(self):
        for t in (-1,2,float('nan'),True):
            with self.assertRaises(ValueError):route(CASES[0],t)
        with self.assertRaises(ValueError):evaluate(CASES,profile='magic')
        with self.assertRaises(ValueError):evaluate([CASES[0],CASES[0]])
    def payload(self,**updates):
        d={'support':'pass','completeness':'pass','correctness':'pass','evidence_ids':['A','B'],'reason':'Both required facts are supported.'};d.update(updates);return json.dumps(d)
    def test_valid_rubric_output(self):
        self.assertEqual(parse_rubric_output(self.payload(),{'A','B'}),'pass')
        self.assertEqual(parse_rubric_output(self.payload(support='unknown'),{'A','B'}),'review')
        self.assertEqual(parse_rubric_output(self.payload(support='unknown',correctness='fail'),{'A','B'}),'fail')
    def test_forged_ids_and_missing_evidence(self):
        for ids in (['invented'],[],['A','A']):
            with self.assertRaises(ValueError):parse_rubric_output(self.payload(evidence_ids=ids),{'A','B'})
    def test_malformed_json_is_not_pass(self):
        for raw in ('not json','[]','{"support":"pass","support":"fail"}',self.payload(extra='pass'),self.payload(support='excellent'),self.payload(reason='')):
            with self.assertRaises(ValueError):parse_rubric_output(raw,{'A','B'})
    def test_stable_votes_are_not_correctness(self):
        # Both orders choose B; humans could still prefer A.
        self.assertEqual(swap_consistency([('B','B')]),1)
    def test_swap_mapping_and_empty(self):
        self.assertEqual(swap_consistency([('A','A'),('A','B'),('tie','tie'),('B','A')]),.5)
        self.assertIsNone(swap_consistency([]))
        with self.assertRaises(ValueError):swap_consistency([('first','A')])

if __name__=='__main__':unittest.main()
