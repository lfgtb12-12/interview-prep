"""Offline regression tests for the batch preview CLI."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from batch import build, propose_pr

EXAMPLE = Path(__file__).parent / "examples" / "M03-L05.json"


class BatchCLITests(unittest.TestCase):
    def test_one_lesson_generates_report_and_preview(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "previews"
            report = build([EXAMPLE], out)
            self.assertEqual(report["lesson_ids"], ["M03-L05"])
            self.assertFalse(report["fact_checked"])
            self.assertFalse(report["browser_tested"])
            self.assertIn("Generated preview", (out / "m03-l05.html").read_text())
            self.assertEqual(json.loads((out / "quality-report.json").read_text())["structural_errors"], [])

    def test_two_lesson_batch_end_to_end(self):
        with tempfile.TemporaryDirectory() as temp:
            second = Path(temp) / "second.json"
            data = json.loads(EXAMPLE.read_text())
            data["id"] = "M03-L06"
            data["title"] = "Recovery and Audit Trail Boundaries"
            second.write_text(json.dumps(data))
            out = Path(temp) / "preview"
            report = build([EXAMPLE, second], out)
            self.assertEqual(report["lesson_ids"], ["M03-L05", "M03-L06"])
            self.assertTrue((out / "m03-l05.html").is_file())
            self.assertTrue((out / "m03-l06.html").is_file())
            self.assertIn("M03-L06", (out / "index.html").read_text())
            self.assertEqual(len(report["editorial_warnings"]) > 0, True)

    def test_duplicate_ids_prevent_all_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            duplicate = Path(temp) / "copy.json"
            duplicate.write_text(EXAMPLE.read_text())
            out = Path(temp) / "preview"
            with self.assertRaises(ValueError):
                build([EXAMPLE, duplicate], out)
            self.assertFalse(out.exists())

    def test_strict_editorial_blocks_sparse_lesson(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "preview"
            with self.assertRaises(ValueError):
                build([EXAMPLE], out, strict=True)
            self.assertFalse(out.exists())

    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "preview"
            build([EXAMPLE], out)
            with self.assertRaises(FileExistsError):
                build([EXAMPLE], out)

    def test_batch_size_limit(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                build([EXAMPLE] * 4, Path(temp) / "preview")

    def test_published_directory_protected(self):
        with self.assertRaises(ValueError):
            build([EXAMPLE], Path(__file__).resolve().parent.parent / "previews")

    def test_pr_requires_factory_branch_before_side_effect(self):
        with self.assertRaises(ValueError):
            propose_pr("feature/not-allowed", "Draft", "Test")

    @patch("batch.subprocess.run")
    def test_pr_requires_clean_tree(self, run):
        run.side_effect = [
            type("Done", (), {"stdout": "factory/test\n"})(),
            type("Done", (), {"stdout": " M some-file\n"})(),
        ]
        with self.assertRaises(ValueError):
            propose_pr("factory/test", "Draft", "Test")
        self.assertEqual(run.call_count, 2)


if __name__ == "__main__":
    unittest.main()
