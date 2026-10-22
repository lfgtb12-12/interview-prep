"""Typed interactive widget regression tests."""
import copy
import json
import unittest
from pathlib import Path
from render import render
from validate import validate

DATA=json.loads((Path(__file__).parent/"examples"/"M03-L05.json").read_text())

class WidgetTests(unittest.TestCase):
    def test_valid_widgets(self):
        page=render(validate(copy.deepcopy(DATA)))
        for label in ('data-strategy','data-speed','data-lanes','data-attempts','data-state','data-value','data-check','mountWidget(area,'):
            self.assertIn(label,page)
    def test_invalid_task_duration(self):
        value=copy.deepcopy(DATA)
        value["sections"][0]["interactive"]["tasks"][0]["duration"]=-1
        with self.assertRaises(ValueError):validate(value)
    def test_unknown_widget_rejected(self):
        value=copy.deepcopy(DATA)
        value["sections"][1]["interactive"]["type"]="execute-code"
        with self.assertRaises(ValueError):validate(value)
    def test_unescaped_payload_not_inserted(self):
        value=copy.deepcopy(DATA)
        value["sections"][0]["interactive"]["tasks"][0]["name"]="<img src=x onerror=alert(1)>"
        page=render(validate(value))
        self.assertNotIn("<img src=x onerror=alert(1)>",page)
        self.assertIn("textContent=t.name",page)
if __name__=="__main__":unittest.main()
