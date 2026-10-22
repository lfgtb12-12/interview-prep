"""Deterministic tests for M03-L06 and M03-L07 lab reference implementations."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "labs"))
from observability_lab import evaluate, simulate
from checkpoint_lab import Operation, FakeProvider, claim, dispatch, reconcile


class ObservabilityLabTests(unittest.TestCase):
    def test_complete_report(self):
        trace, report = simulate([str(i) for i in range(10)])
        self.assertEqual(report["status"], "complete")
        self.assertEqual([s["count"] for s in trace.stages], [10, 10, 10])

    def test_retrieval_and_synthesis_failures_separated(self):
        _, report = simulate(["a", "b", "c"], drop_at_retrieval=["a"],
                             drop_at_synthesis=["b"])
        self.assertEqual(report["missing_at_retrieval"], ["a"])
        self.assertEqual(report["missing_at_synthesis"], ["b"])
        self.assertEqual(report["answer_completeness"], 1 / 3)

    def test_unsupported_reference(self):
        report = evaluate({"a"}, {"a"}, {"a", "invented"})
        self.assertEqual(report["unsupported_ids"], ["invented"])

    def test_deadline_is_not_success(self):
        trace, report = simulate(["a"], deadline_exceeded=True)
        self.assertEqual(report["status"], "deadline_exceeded")
        self.assertEqual(trace.stages[-1]["outcome"], "deadline_exceeded")


class CheckpointLabTests(unittest.TestCase):
    def test_claim_is_conditional(self):
        op = Operation("op1", "hash1")
        v = claim(op, "worker-a", 0)
        self.assertEqual(v, 1)
        with self.assertRaises(ValueError):
            claim(op, "worker-b", 0)

    def test_lost_ack_reconciles_without_duplicate(self):
        op, provider = Operation("op2", "hash2"), FakeProvider()
        v = claim(op, "worker-a", 0)
        dispatch(op, "worker-a", v, provider, lose_ack=True)
        self.assertEqual(op.state, "UNKNOWN")
        self.assertEqual(provider.effect_count, 1)
        self.assertTrue(reconcile(op, provider))
        self.assertEqual(op.state, "SUCCEEDED")
        self.assertEqual(provider.effect_count, 1)

    def test_stale_worker_blocked(self):
        op, provider = Operation("op3", "hash3"), FakeProvider()
        v = claim(op, "worker-a", 0)
        with self.assertRaises(ValueError):
            dispatch(op, "worker-b", v, provider)
        with self.assertRaises(ValueError):
            dispatch(op, "worker-a", v + 1, provider)
        self.assertEqual(provider.effect_count, 0)

    def test_provider_key_reuse_requires_same_digest(self):
        provider = FakeProvider()
        provider.send("same", "hash-a")
        provider.send("same", "hash-a")
        with self.assertRaises(ValueError):
            provider.send("same", "hash-b")
        self.assertEqual(provider.effect_count, 1)

    def test_unknown_lookup_absence_does_not_replay(self):
        op, provider = Operation("op4", "hash4", "UNKNOWN", 2, "worker", "key")
        self.assertFalse(reconcile(op, provider))
        self.assertEqual(op.state, "UNKNOWN")
        self.assertEqual(provider.effect_count, 0)


if __name__ == "__main__":
    unittest.main()
