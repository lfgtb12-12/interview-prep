"""Save alongside orchestration_lab.py; python -m unittest -v test_orchestration.py"""
import unittest
from orchestration_lab import Task, Store, UnknownOutcome, run

class TestOrchestration(unittest.TestCase):
    def test_dependencies_and_resume(self):
        calls = []
        tasks = {
            "a": Task((), lambda _: calls.append("a") or 3),
            "b": Task(("a",), lambda x: calls.append("b") or x["a"] * 2),
        }
        store = Store()
        self.assertEqual(run(tasks, store)["b"], 6)
        run(tasks, store)
        self.assertEqual(calls, ["a", "b"])

    def test_cycle_rejected(self):
        with self.assertRaises(ValueError):
            run({"a": Task(("b",), lambda _: 1),
                 "b": Task(("a",), lambda _: 2)}, Store())

    def test_unknown_write_never_replayed(self):
        calls = []
        def send(_):
            calls.append("sent")
            raise UnknownOutcome("acknowledgement lost")
        tasks = {"send": Task((), send, side_effect=True)}
        store = Store()
        with self.assertRaises(RuntimeError):
            run(tasks, store)
        self.assertEqual(store.status["send"], "UNKNOWN")
        with self.assertRaises(UnknownOutcome):
            run(tasks, store)
        self.assertEqual(calls, ["sent"])

    def test_failure_blocks_downstream(self):
        calls = []
        def fail(_): raise ValueError("provider error")
        tasks = {"read": Task((), fail), "publish": Task(("read",), lambda _: calls.append(1))}
        with self.assertRaises(RuntimeError):
            run(tasks, Store())
        self.assertFalse(calls)

if __name__ == "__main__":
    unittest.main()
