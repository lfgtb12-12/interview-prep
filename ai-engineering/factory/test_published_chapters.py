"""Published lesson contract checks for M03-L06 and M03-L07."""
import json
import re
import unittest
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent


class PublishedChapterTests(unittest.TestCase):
    def test_chapters_registered_and_have_interactive_content(self):
        manifest = json.loads((SITE / "curriculum.json").read_text())
        lessons = {l["id"]: l for m in manifest["modules"] for l in m["lessons"]}
        for ident in ("M03-L05", "M03-L06", "M03-L07"):
            with self.subTest(ident=ident):
                self.assertIn(ident, lessons)
                path = SITE / lessons[ident]["path"]
                self.assertTrue(path.is_file())
                page = path.read_text()
                self.assertIn('src="navigation.js"', page)
                self.assertIn('href="navigation.css"', page)
                self.assertIn('href="./"', page)
                self.assertTrue('id="states"' in page or 'data-diagram=' in page)
                self.assertTrue('id="scenario"' in page or 'data-widget=' in page)
                self.assertTrue('id="quiz-items"' in page or 'data-question=' in page)
                self.assertIn('id="done"', page)
                self.assertIn('ai-handbook-', page)
                self.assertNotIn('Generated preview · Not published', page)
                match = re.search(r'<script id="lesson-data" type="application/json">(.*?)</script>', page, re.S)
                self.assertIsNotNone(match)
                data = json.loads(match.group(1))
                self.assertEqual(data["id"], ident)
                self.assertEqual(len(data["quiz"]), 5)


if __name__ == "__main__":
    unittest.main()
