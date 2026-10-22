"""Tests for batch quality gate: do not treat heuristics as factual review."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("batch_quality.py")
SPEC = importlib.util.spec_from_file_location("batch_quality", MODULE_PATH)
batch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(batch)


def sample(ident="M03-L05"):
    return {
        "id": ident, "module": "M03", "title": "Testing title",
        "sections": [{"id": "intro", "title": "Introduction",
                      "paragraphs": ["A sufficiently long paragraph for examples."]}],
        "quiz": [], "interview": [], "lab": {"expected": "An observable output"},
    }


class BatchQualityTests(unittest.TestCase):
    def test_sparse_lesson_reports_warnings(self):
        errors, warnings = batch.check_spec(sample(), Path("a.json"))
        self.assertEqual(errors, [])
        self.assertTrue(any("fewer than 500" in w for w in warnings))

    def test_placeholder_warns_not_errors(self):
        data = sample()
        data["sections"][0]["paragraphs"] = ["TODO: add example"]
        errors, warnings = batch.check_spec(data, Path("a.json"))
        self.assertEqual(errors, [])
        self.assertTrue(any("placeholder" in w for w in warnings))

    def test_missing_lab_expected_blocks(self):
        data = sample()
        data["lab"]["expected"] = ""
        errors, _ = batch.check_spec(data, Path("a.json"))
        self.assertTrue(any("lacks expected" in e for e in errors))

    def test_invalid_json_is_error(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.json"
            path.write_text("{not json")
            errors, _ = batch.inspect([path])
        self.assertTrue(any("cannot read JSON" in e for e in errors))

    def test_duplicate_ids_are_errors(self):
        import json
        with tempfile.TemporaryDirectory() as folder:
            paths = []
            for name in ("a", "b"):
                path = Path(folder) / f"{name}.json"
                path.write_text(json.dumps(sample()))
                paths.append(path)
            errors, _ = batch.inspect(paths)
        self.assertTrue(any("duplicate lesson id" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
