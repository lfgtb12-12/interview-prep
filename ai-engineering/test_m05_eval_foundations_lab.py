import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from m05_eval_foundations_lab import Case, FIXTURES, evaluate, by_slice

class EvaluationTests(unittest.TestCase):
    def test_lower_threshold(self):
        m=evaluate(FIXTURES,.5)
        self.assertEqual((m["answered"],m["correct"],m["errors"]),(7,4,3))
    def test_mid_threshold(self):
        m=evaluate(FIXTURES,.75)
        self.assertEqual((m["answered"],m["correct"],m["errors"]),(4,3,1))
        self.assertAlmostEqual(m["answered_accuracy"],.75)
    def test_high_threshold(self):
        m=evaluate(FIXTURES,.9)
        self.assertEqual((m["answered"],m["correct"],m["errors"]),(1,1,0))
    def test_security_gate_overrides_score(self):
        self.assertEqual(evaluate((Case("x","s",True,True,1,False),),0)["answered"],0)
    def test_all_abstain_denominator(self):
        m=evaluate(FIXTURES,1)
        self.assertIsNone(m["answered_accuracy"])
        self.assertEqual(m["coverage"],0)
    def test_empty_rejected(self):
        with self.assertRaises(ValueError):evaluate([],0)
    def test_invalid_threshold(self):
        for x in (-.1,1.1):
            with self.assertRaises(ValueError):evaluate(FIXTURES,x)
    def test_invalid_score(self):
        with self.assertRaises(ValueError):evaluate((Case("x","s",True,True,1.5),),.5)
    def test_duplicate_ids(self):
        with self.assertRaises(ValueError):evaluate((FIXTURES[0],FIXTURES[0]),.5)
    def test_slices_reconcile(self):
        slices=by_slice(FIXTURES,.75)
        self.assertEqual(sum(x["requests"] for x in slices.values()),10)
        self.assertEqual(sum(x["answered"] for x in slices.values()),4)
    def test_rare_code_regression_visible(self):
        rare=by_slice(FIXTURES,.75)["rare-code"]
        self.assertEqual((rare["answered"],rare["errors"]),(1,1))
    def test_not_answerable_selected_is_error(self):
        x=Case("x","s",False,False,.95)
        self.assertEqual(evaluate((x,),.8)["errors"],1)
    def test_answerable_coverage_denominator(self):
        m=evaluate(FIXTURES,.75)
        self.assertAlmostEqual(m["answerable_coverage"],3/7)

if __name__=="__main__":unittest.main()
