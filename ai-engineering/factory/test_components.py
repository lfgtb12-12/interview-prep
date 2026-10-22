"""Regression tests for reusable animated SVG graph rendering."""
import json
import unittest
from pathlib import Path
from validate import validate
from render import render

EXAMPLE = Path(__file__).parent / "examples" / "M03-L05.json"

class InteractiveComponentTests(unittest.TestCase):
    def setUp(self):
        self.lesson = validate(json.loads(EXAMPLE.read_text(encoding="utf-8")))

    def test_svg_control_contract(self):
        page = render(self.lesson)
        for marker in ('class="sim-graph"', 'data-prev', 'data-next', 'data-reset',
                       'data-progress', 'data-steps', 'data-current', 'mountSimulation(area, diagram)'):
            self.assertIn(marker, page)

    def test_node_labels_use_text_content(self):
        page = render(self.lesson)
        self.assertIn('label.textContent=name.length', page)
        self.assertNotIn('innerHTML', page)

    def test_existing_progress_key_unchanged(self):
        page = render(self.lesson)
        self.assertIn('"ai-textbook-factory-" + data.id + "-v1"', page)

    def test_accessibility_and_reduced_motion(self):
        page = render(self.lesson)
        for marker in ('role="group"', 'role="img"', 'aria-live="polite"',
                       'prefers-reduced-motion:reduce'):
            self.assertIn(marker,page)

if __name__ == "__main__":
    unittest.main()
