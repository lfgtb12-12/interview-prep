"""M05-L01 browser smoke tests for real behavior and persistence."""
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright

URL=Path(__file__).with_name("chapter-m05-l01.html").as_uri()

class M05BrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright=sync_playwright().start()
        cls.browser=cls.playwright.chromium.launch(headless=True)
    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
    def setUp(self):
        self.context=self.browser.new_context(viewport={"width":900,"height":750})
        self.page=self.context.new_page()
        self.page.goto(URL)
    def tearDown(self):
        self.context.close()
    def test_real_threshold_metrics(self):
        metrics=self.page.locator("#metrics")
        self.assertIn("75%",metrics.inner_text())
        self.page.locator("#threshold").evaluate("(el) => { el.value = '0.9'; el.dispatchEvent(new Event('input', {bubbles:true})); }")
        self.assertIn("10%",metrics.inner_text())
        self.assertIn("Correct 1",self.page.locator("#bar").inner_text())
    def test_risky_slice_and_acl(self):
        self.assertIn("rare-code: 0 correct, 1 wrong",self.page.locator("#slices").inner_text())
        self.assertIn("Abstentions",self.page.locator("#metrics").inner_text())
        # High-scoring unauthorized a9 is not included at threshold 0.90.
        self.page.locator("#threshold").evaluate("(el) => { el.value = '0.9'; el.dispatchEvent(new Event('input', {bubbles:true})); }")
        self.assertIn("1/10",self.page.locator("#metrics").inner_text())
    def test_quiz_explanations(self):
        first=self.page.locator("#questions fieldset").first
        self.assertEqual(self.page.locator("#questions fieldset").count(),8)
        first.locator("input[value='1']").check()
        first.locator("button").click()
        self.assertIn("Correct",first.locator(".feedback").inner_text())
    def test_mobile_layout(self):
        self.page.set_viewport_size({"width":390,"height":844})
        self.assertTrue(self.page.locator("#threshold").is_visible())
        self.assertTrue(self.page.locator("#metrics").is_visible())

if __name__=="__main__":unittest.main()
