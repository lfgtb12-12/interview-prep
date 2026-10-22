"""Browser interaction smoke tests; run after rendering a preview.

Requires playwright and installed Chromium; CI installs both.
"""
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path("/tmp/textbook-staging/m03-l05.html").as_uri()

class BrowserComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)
    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
    def setUp(self):
        self.page = self.browser.new_page(viewport={"width":900,"height":800})
        self.page.goto(PAGE)
    def tearDown(self):
        self.page.close()
    def test_graph_progress(self):
        graph=self.page.locator("[data-diagram]").first
        self.assertEqual(graph.get_attribute("data-step"),"0")
        graph.locator("[data-next]").click()
        self.assertEqual(graph.get_attribute("data-step"),"1")
        graph.locator("[data-prev]").click()
        self.assertEqual(graph.get_attribute("data-step"),"0")
    def test_timeline_sequential_is_slower(self):
        timeline=self.page.locator("[data-widget]").first
        self.assertIn("6.0s",timeline.locator("output").inner_text())
        timeline.locator("[data-strategy]").select_option("sequential")
        self.assertIn("9.0s",timeline.locator("output").inner_text())
    def test_ambiguous_retry_stops(self):
        retry=self.page.locator("[data-widget]").nth(1)
        retry.locator("[data-next]").click()
        self.assertIn("UNKNOWN",retry.locator("[data-state]").inner_text())
        self.assertTrue(retry.locator("[data-next]").is_disabled())
        retry.locator("[data-reset]").click()
        self.assertFalse(retry.locator("[data-next]").is_disabled())
    def test_parameter_and_quiz(self):
        exercise=self.page.locator("[data-widget]").nth(2)
        exercise.locator("[data-value]").evaluate("(el) => { el.value = '2'; el.dispatchEvent(new Event('input', {bubbles:true})); }")
        exercise.locator("[data-check]").click()
        self.assertIn("Correct",exercise.locator("[data-answer]").inner_text())
        quiz=self.page.locator("[data-quiz]").first
        quiz.locator("input[value='1']").check()
        quiz.locator("button").click()
        self.assertIn("Correct",quiz.locator(".feedback").inner_text())
    def test_mobile_controls(self):
        self.page.set_viewport_size({"width":390,"height":844})
        self.assertTrue(self.page.locator("[data-diagram] [data-next]").is_visible())
        self.assertTrue(self.page.locator("[data-widget]").first.locator("[data-strategy]").is_visible())

if __name__=="__main__":
    unittest.main()
