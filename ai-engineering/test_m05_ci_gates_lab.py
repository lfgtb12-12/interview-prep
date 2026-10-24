import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from m05_ci_gates_lab import TASKS,PROFILES,evaluate

class CIGateTests(unittest.TestCase):
    def test_fixture_coverage(self):
        self.assertEqual(len(TASKS),10)
        self.assertEqual({t.slice for t in TASKS},{"common","rare"})
    def test_healthy_passes(self):
        r=evaluate();self.assertEqual(r["decision"],"PASS");self.assertEqual(r["observed"],10)
        self.assertEqual(r["slices"]["rare"]["candidate_rate"],1)
    def test_each_negative_profile_blocks(self):
        for name in PROFILES:
            if name!="healthy":
                with self.subTest(name=name):self.assertEqual(evaluate(name)["decision"],"BLOCK")
    def test_rare_slice_loss_not_hidden_by_aggregate(self):
        r=evaluate("rare_regression")
        self.assertEqual(r["slices"]["rare"]["lost_rate"],.5)
        self.assertTrue(any("paired regressions" in x for x in r["failures"]))
    def test_safety_independent_of_quality(self):
        r=evaluate("safety")
        self.assertEqual(r["slices"]["common"]["candidate_rate"],1)
        self.assertIn("a1: unsafe",r["failures"])
    def test_trace_is_hard_gate(self):self.assertIn("a1: broken trace",evaluate("broken_trace")["failures"])
    def test_latency_threshold_changes_decision(self):
        self.assertEqual(evaluate("latency")["decision"],"BLOCK")
        self.assertEqual(evaluate("latency",latency_budget=2500)["decision"],"PASS")
    def test_cost_threshold_changes_decision(self):
        self.assertEqual(evaluate("cost")["decision"],"BLOCK")
        self.assertEqual(evaluate("cost",cost_budget=1000)["decision"],"PASS")
    def test_missing_is_not_silent_success(self):
        x=evaluate("missing")
        self.assertEqual(x["observed"],9)
        self.assertIn("rare: missing observations",x["failures"])
        self.assertFalse(x["slices"]["rare"]["complete"])
    def test_missing_policy_explicit(self):
        self.assertEqual(evaluate("missing",strict_missing=False)["decision"],"PASS")
    def test_stricter_quality_floor(self):
        self.assertEqual(evaluate("rare_regression",min_rate=.75)["decision"],"BLOCK")
    def test_stricter_loss_gate(self):
        self.assertEqual(evaluate("rare_regression",max_regression=0)["decision"],"BLOCK")
    def test_empty_slice_undercoverage_blocks(self):
        self.assertIn("rare: insufficient fixture coverage",evaluate(min_tasks=5)["failures"])
    def test_reject_invalid_profile(self):
        with self.assertRaises(ValueError):evaluate("unknown")
    def test_reject_invalid_thresholds(self):
        for kwargs in ({"min_tasks":0},{"min_rate":2},{"max_regression":-1},{"latency_budget":0},{"cost_budget":0}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):evaluate(**kwargs)
if __name__=="__main__":unittest.main()
