"""Judge calibration interactions, calculation parity, persistence and publication."""
import functools
import http.server
import json
import os
from pathlib import Path
import sys
import threading
import unittest
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parent))
from m05_judge_calibration_lab import evaluate, CASES

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

class JudgeBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=None;cls.base=os.getenv('M05_SITE_URL')
        if not cls.base:
            cls.server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(Path(__file__).resolve().parent)))
            cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start();cls.base=f'http://127.0.0.1:{cls.server.server_port}/'
        cls.p=sync_playwright().start()
        proxy={'server':os.environ['HTTPS_PROXY']} if os.getenv('M05_SITE_URL') and os.getenv('HTTPS_PROXY') else None
        cls.browser=cls.p.chromium.launch(proxy=proxy)
    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.p.stop()
        if cls.server:cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def setUp(self):
        self.context=self.browser.new_context(ignore_https_errors=True,viewport={'width':1280,'height':900})
        self.page=self.context.new_page();self.errors=[];self.page.on('pageerror',lambda e:self.errors.append(str(e)))
        self.page.goto(self.base+'chapter-m05-l03.html');self.page.locator('a[aria-current="page"]').wait_for()
    def tearDown(self):
        self.context.close();self.assertEqual(self.errors,[])
    def slider(self,id,value):
        self.page.locator('#'+id).evaluate('(e,value)=>{e.value=value;e.dispatchEvent(new Event("input"))}',str(value))
    def test_actual_confusion_and_review_routing(self):
        self.assertIn('66.7%',self.page.locator('#judge-metrics').inner_text())
        self.assertIn('75.0%',self.page.locator('#judge-metrics').inner_text())
        self.assertEqual(self.page.locator('#case-rows tr').count(),12)
        self.assertIn('False pass\n1',self.page.locator('#confusion').inner_text())
        self.slider('threshold',0);self.slider('band',0)
        self.assertIn('fail (hard gate)',self.page.locator('#case-rows tr').last.inner_text())
        self.assertIn('review (invalid output)',self.page.locator('#case-rows tr').nth(10).inner_text())
    def test_profile_changes_actual_errors(self):
        self.page.locator('#profile').select_option('anchored')
        self.assertIn('100.0%',self.page.locator('#judge-metrics').inner_text())
        self.assertIn('False pass\n0',self.page.locator('#confusion').inner_text())
        self.assertIn('75.0%',self.page.locator('#judge-metrics').inner_text())
        self.slider('threshold',.5);self.slider('band',.5)
        self.assertIn('N/A',self.page.locator('#judge-metrics').inner_text())
        self.assertIn('11 / 12',self.page.locator('#judge-metrics').inner_text())
    def test_python_js_parity_40_configurations(self):
        for profile in ('baseline','anchored'):
            for t in (0,.25,.5,.75,1):
                for band in (0,.1,.25,.5):
                    with self.subTest(profile=profile,t=t,band=band):
                        expected=evaluate(CASES,t,band,profile)
                        actual=self.page.evaluate('args=>evaluateJudge(JSON.parse(document.querySelector("#lesson-data").textContent).rows,...args)',[t,band,profile])
                        for k,v in expected.items():
                            if v is None:self.assertIsNone(actual[k])
                            else:self.assertAlmostEqual(actual[k],v)
    def test_pairwise_swap_maps_candidate_identity(self):
        self.page.locator('#pair').select_option('1')
        self.assertIn('Mapped vote: A',self.page.locator('#pair-result').inner_text())
        self.page.locator('#reversed').check()
        self.assertIn('Mapped vote: B',self.page.locator('#pair-result').inner_text())
        self.assertIn('Original B',self.page.locator('.winner').inner_text())
        self.assertIn('Order-inconsistent',self.page.locator('#pair-result').inner_text())
        self.page.locator('#pair').select_option('3')
        self.assertIn('Order-consistent',self.page.locator('#pair-result').inner_text())
        self.assertIn('disagrees',self.page.locator('#pair-result').inner_text())
        self.assertIn('75.0%',self.page.locator('#pair-summary').inner_text())
        self.assertIn('62.5%',self.page.locator('#pair-summary').inner_text())
    def test_eight_explained_quizzes_and_persistence(self):
        quiz=json.loads(self.page.locator('#lesson-data').text_content())['quiz']
        self.assertEqual(self.page.locator('#questions fieldset').count(),8)
        for i,item in enumerate(quiz):
            q=self.page.locator('#questions fieldset').nth(i);q.locator(f'input[value="{item[2]}"]').check();q.locator('button').click()
            self.assertIn('Correct.',q.locator('.feedback').inner_text());self.assertIn(item[3],q.locator('.feedback').inner_text())
        self.page.evaluate("localStorage.setItem('ai-handbook-m05-l02-v1',JSON.stringify({done:true,answers:{0:1}}))")
        self.page.locator('#done').check();self.page.reload()
        self.assertTrue(self.page.locator('#done').is_checked())
        self.assertTrue(self.page.locator('#questions fieldset').first.locator('input[value="0"]').is_checked())
        self.assertEqual(self.page.evaluate("JSON.parse(localStorage.getItem('ai-handbook-m05-l02-v1')).answers[0]"),1)
    def test_mobile_navigation_and_curriculum(self):
        self.assertIn('LLM-as-Judge',self.page.locator('a[aria-current="page"]').inner_text())
        self.page.set_viewport_size({'width':390,'height':844})
        self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),390)
        self.page.locator('.handbook-drawer-button').click()
        self.assertEqual(self.page.locator('.handbook-drawer-button').get_attribute('aria-expanded'),'true')
        self.page.locator('a[href="./chapter-m05-l02.html"]').click();self.page.wait_for_url('**/chapter-m05-l02.html')
        self.page.locator('#ranking').wait_for()
        self.assertEqual(self.page.locator('#questions fieldset').count(),8)

if __name__=='__main__':unittest.main()
