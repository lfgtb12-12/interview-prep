"""Promotion gate regression: no live writes or progress key regressions."""
import json
import tempfile
import unittest
from pathlib import Path

from prepare_publication import prepare, SITE, HERE

SPECS = [HERE / "examples" / "M03-L06.json", HERE / "examples" / "M03-L07.json"]


class PublicationCandidateTests(unittest.TestCase):
    def test_candidate_batch_and_navigation(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "candidate"
            result = prepare(SPECS, output, SITE / "curriculum.json")
            self.assertEqual(len(result["files"]), 2)
            self.assertTrue(result["publication_requires_separate_approval"])
            self.assertTrue(result["curriculum_unchanged"])
            for name in result["files"]:
                page = (output / name).read_text()
                self.assertIn('href="navigation.css"', page)
                self.assertIn('src="navigation.js"', page)
                self.assertIn('"ai-handbook-" + data.id.toLowerCase() + "-v1"', page)
                self.assertIn('href="./"', page)
                self.assertIn("data-widget", page)
                self.assertIn("data-diagram", page)
                self.assertNotIn("Generated preview · Not published", page)
            self.assertFalse((SITE / "chapter-m03-l06.html").exists())

    def test_existing_lesson_ids_blocked(self):
        with tempfile.TemporaryDirectory() as folder:
            manifest = Path(folder) / "curriculum.json"
            manifest.write_text(json.dumps({"modules": [{"lessons": [{"id": "M03-L06"}]}]}))
            out = Path(folder) / "out"
            with self.assertRaisesRegex(ValueError, "already published"):
                prepare(SPECS, out, manifest)
            self.assertFalse(out.exists())

    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "candidate"
            prepare(SPECS, output, SITE / "curriculum.json")
            with self.assertRaises(FileExistsError):
                prepare(SPECS, output, SITE / "curriculum.json")

    def test_no_write_into_live_site(self):
        with self.assertRaisesRegex(ValueError, "deployed directory"):
            prepare(SPECS, SITE / "new-directory", SITE / "curriculum.json")


if __name__ == "__main__":
    unittest.main()
