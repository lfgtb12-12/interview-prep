"""Smoke-test the first substantive two-spec factory batch without publishing."""
import tempfile
import unittest
from pathlib import Path
from batch import build
from batch_quality import inspect

HERE = Path(__file__).resolve().parent
SPECS = [HERE / "examples" / f"M03-L{i:02d}.json" for i in (6, 7)]


class FirstBatchTests(unittest.TestCase):
    def test_structural_and_editorial_quality(self):
        errors, warnings = inspect(SPECS)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_two_lessons_render_without_publication(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "preview"
            report = build(SPECS, target, strict=True)
            self.assertEqual(report["lesson_ids"], ["M03-L06", "M03-L07"])
            self.assertFalse(report["fact_checked"])
            for ident in ("m03-l06", "m03-l07"):
                content = (target / f"{ident}.html").read_text()
                self.assertIn("data-diagram", content)
                self.assertIn("data-widget", content)
                self.assertIn("Knowledge check", content)
            index = (target / "index.html").read_text()
            self.assertIn("m03-l06.html", index)
            self.assertIn("m03-l07.html", index)


if __name__ == "__main__":
    unittest.main()
