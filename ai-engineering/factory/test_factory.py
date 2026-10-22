"""Unit tests for lesson contract, escaping, rendering and safe staging."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from validate import validate
from render import render


EXAMPLE = Path(__file__).parent / "examples" / "M03-L05.json"


class FactoryTests(unittest.TestCase):
    def setUp(self):
        self.lesson = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_example_valid(self):
        self.assertEqual(validate(self.lesson)["id"], "M03-L05")

    def test_module_mismatch(self):
        lesson = copy.deepcopy(self.lesson)
        lesson["module"] = "M02"
        with self.assertRaises(ValueError):
            validate(lesson)

    def test_duplicate_section_id(self):
        lesson = copy.deepcopy(self.lesson)
        lesson["sections"][1]["id"] = lesson["sections"][0]["id"]
        with self.assertRaises(ValueError):
            validate(lesson)

    def test_bad_diagram_reference(self):
        lesson = copy.deepcopy(self.lesson)
        lesson["sections"][0]["diagram"]["edges"][0][1] = "NOT_A_NODE"
        with self.assertRaises(ValueError):
            validate(lesson)

    def test_invalid_answer(self):
        lesson = copy.deepcopy(self.lesson)
        lesson["quiz"][0]["answer"] = True
        with self.assertRaises(ValueError):
            validate(lesson)

    def test_escaped_html(self):
        lesson = copy.deepcopy(self.lesson)
        lesson["title"] = "<script>alert(1)</script> Safe"
        output = render(validate(lesson))
        self.assertIn("&lt;script&gt;", output)
        self.assertNotIn("<script>alert(1)</script>", output)
        self.assertIn("data-diagram", output)
        self.assertIn("Knowledge check", output)


if __name__ == "__main__":
    unittest.main()
