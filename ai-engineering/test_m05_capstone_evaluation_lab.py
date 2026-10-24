import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from m05_capstone_evaluation_lab import FIXTURES,decide

class LaunchCapstoneTests(unittest.TestCase):
    def test_all_fixtures(self):self.assertEqual(len(FIXTURES),10)
    def test_healthy_release_sequence(self):
        self.assertEqual(decide(phase="offline")["decision"],"SHADOW")
        self.assertEqual(decide(phase="shadow")["decision"],"CANARY")
        self.assertEqual(decide(phase="online")["decision"],"GUARDED_ROLLOUT")
    def test_rare_regression_hard_gate(self):
        self.assertEqual(decide("rare_regression")["decision"],"BLOCK")
    def test_unauthorized_tool_is_hard_gate(self):
        self.assertIn("unauthorized tool calls",decide("unsafe")["reasons"])
    def test_unknown_write_requires_reconciliation(self):
        self.assertEqual(decide("unknown_write")["decision"],"BLOCK")
    def test_incomplete_trace_blocks(self):
        self.assertEqual(decide("missing")["decision"],"BLOCK")
    def test_shadow_budgets(self):
        for case in ("slow","expensive"):
            self.assertEqual(decide(case,phase="offline")["decision"],"SHADOW")
            self.assertEqual(decide(case,phase="shadow")["decision"],"BLOCK")
    def test_online_harm_rollback(self):
        self.assertEqual(decide("online_harm")["decision"],"ROLLBACK")
    def test_incident_overrides_improvement(self):
        self.assertEqual(decide("incident")["decision"],"ROLLBACK")
    def test_small_experiment_holds(self):
        self.assertEqual(decide("inconclusive")["decision"],"HOLD")
    def test_practical_margin_holds(self):
        self.assertEqual(decide(margin=.03)["decision"],"HOLD")
    def test_rare_floor_changes_outcome(self):
        self.assertEqual(decide(rare_floor=.9)["decision"],"BLOCK")
        self.assertEqual(decide("rare_regression",rare_floor=.5)["decision"],"GUARDED_ROLLOUT")
    def test_interval_valid_order(self):
        x=decide()
        self.assertLess(x["lower"],x["delta"]);self.assertLess(x["delta"],x["upper"])
    def test_invalid_inputs(self):
        for kw in ({"scenario":"bad"},{"phase":"bad"},{"rare_floor":2},{"margin":-1}):
            with self.subTest(kw=kw):
                with self.assertRaises(ValueError):decide(**kw)
if __name__=="__main__":unittest.main()
