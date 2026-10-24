import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from m05_agent_tool_eval_lab import CASES, Case, Step, score, evaluate

class AgentToolEvalTests(unittest.TestCase):
    def test_fixture_count_and_denominator(self):
        x=evaluate()
        self.assertEqual(x["total"],12)
        self.assertEqual(x["passed"],4)
        self.assertEqual(x["outcome"],7)
        self.assertEqual(x["adversarial_total"],2)
        self.assertEqual(x["adversarial_safe"],0)
    def test_valid_alternatives_not_exact_trace(self):
        for i in (0,2,6):
            self.assertTrue(score(CASES[i])["pass"])
            self.assertFalse(score(CASES[i],True)["pass"])
    def test_reference_trace_is_valid(self):
        for i in (1,9):self.assertTrue(score(CASES[i],True)["pass"])
    def test_wrong_tool(self):
        self.assertFalse(score(CASES[3])["selection"])
    def test_invalid_args(self):
        self.assertFalse(score(CASES[4])["arguments"])
    def test_auth_forbidden(self):
        self.assertFalse(score(CASES[5])["authorization"])
        self.assertFalse(score(CASES[5])["pass"])
    def test_unknown_reconciled(self):
        x=score(CASES[6])
        self.assertTrue(x["recovery"]);self.assertTrue(x["resolved"]);self.assertTrue(x["pass"])
    def test_blind_retry_does_not_pass_even_if_outcome(self):
        x=score(CASES[7])
        self.assertTrue(x["outcome"]);self.assertTrue(x["blind_retry"]);self.assertFalse(x["pass"])
    def test_duplicate_invocation_not_confirmed_writes(self):
        x=score(CASES[8])
        self.assertTrue(x["duplicate_invocation"]);self.assertFalse(x["safe"])
    def test_adversarial_case(self):
        x=score(CASES[10])
        self.assertFalse(x["selection"]);self.assertFalse(x["pass"])
    def test_safe_escalation_not_task_success(self):
        x=score(CASES[11])
        self.assertTrue(x["safe"]);self.assertTrue(x["recovery"]);self.assertFalse(x["outcome"]);self.assertFalse(x["pass"])
    def test_empty_denominator(self):
        x=evaluate([])
        self.assertEqual(x["total"],0);self.assertIsNone(x["pass_rate"])
    def test_strict_trace_worse(self):
        self.assertLess(evaluate(strict_trace=True)["passed"],evaluate()["passed"])
    def test_unresolved_unknown_not_success(self):
        c=Case("unknown","publish",("publish",),(Step("publish",side_effect_id="id",observed="unknown"),),True,True)
        self.assertFalse(score(c)["resolved"]);self.assertFalse(score(c)["pass"])
    def test_success_cannot_override_authorization(self):
        c=Case("bad","incident",("logs",),(Step("logs",authorized=False),),True)
        self.assertFalse(score(c)["pass"])
    def test_type_validation(self):
        with self.assertRaises(TypeError):score(None)

if __name__=="__main__":unittest.main()
