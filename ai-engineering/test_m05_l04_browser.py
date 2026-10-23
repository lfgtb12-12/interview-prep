"""A/B experiment interactions, calculation parity, persistence and publication."""
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
from m05_experiment_lab import simulate, approximate_per_arm

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

class ExperimentBrowserTests(unittest.TestCase):
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
        self.page.goto(self.base+'chapter-m05-l04.html');self.page.locator('a[aria-current="page"]').wait_for()
    def tearDown(self):
        self.context.close();self.assertEqual(self.errors,[])
    def slider(self,id,value):
        self.page.locator('#'+id).evaluate('(e,value)=>{e.value=value;e.dispatchEvent(new Event("input"))}',str(value))
    def current(self):
        return self.page.evaluate("simulateExperiment(Number(document.querySelector('#sample').value),document.querySelector('#scenario').value,Number(document.querySelector('#confidence').value),Number(document.querySelector('#margin').value)/100,Number(document.querySelector('#copies').value),document.querySelector('#mismatch').checked,document.querySelector('#peek').checked)")
    def test_effect_interval_and_real_launch_decision(self):
        self.assertEqual(self.current()['decision'],'inconclusive')
        self.assertIn('0.60 pp to 5.40 pp',self.page.locator('#interval-summary').inner_text())
        self.page.locator('#sample').select_option('20000')
        self.assertEqual(self.page.locator('#decision').get_attribute('data-result'),'eligible')
        self.page.locator('#scenario').select_option('tiny')
        self.assertEqual(self.current()['decision'],'below_margin')
        self.page.locator('#scenario').select_option('harm')
        self.assertEqual(self.current()['decision'],'harm')
    def test_copied_rows_shrink_only_invalid_interval(self):
        before=self.current()
        valid_x=self.page.locator('#interval-plot line[y1="80"]').first.get_attribute('x1')
        naive_x=self.page.locator('#interval-plot line[y1="150"]').first.get_attribute('x1')
        self.slider('copies',10);after=self.current()
        self.assertEqual(before['interval'],after['interval'])
        self.assertEqual(before['decision'],after['decision'])
        self.assertLess(after['naive']['se'],before['naive']['se'])
        self.assertEqual(valid_x,self.page.locator('#interval-plot line[y1="80"]').first.get_attribute('x1'))
        self.assertNotEqual(naive_x,self.page.locator('#interval-plot line[y1="150"]').first.get_attribute('x1'))
        self.assertIn('40000',self.page.locator('#experiment-metrics').inner_text())
    def test_guardrails_and_integrity_override_positive_effect(self):
        self.page.locator('#sample').select_option('20000')
        for scenario in ('slow','unsafe'):
            self.page.locator('#scenario').select_option(scenario)
            self.assertEqual(self.current()['decision'],'block')
        self.page.locator('#scenario').select_option('benefit')
        self.page.locator('#mismatch').check()
        self.assertEqual(self.current()['decision'],'investigate')
        self.assertIn('SRM detected',self.page.locator('#integrity').inner_text())
        self.page.locator('#mismatch').uncheck();self.page.locator('#peek').check()
        self.assertEqual(self.current()['decision'],'investigate')
        self.assertIn('early stopping',self.page.locator('#integrity').inner_text())
    def test_planning_and_rare_risk(self):
        self.assertIn('2,791',self.page.locator('#planning').inner_text())
        self.slider('mde',1.5)
        self.assertIn(f"{approximate_per_arm(mde=.015):,}",self.page.locator('#planning').inner_text())
        self.page.locator('#sample').select_option('200')
        self.assertIn('1.487%',self.page.locator('#risk-bound').inner_text())
    def test_python_js_parity_240_configurations(self):
        for n in (200,2000,20000):
            for scenario in ('benefit','tiny','harm','slow','unsafe'):
                for confidence in (.9,.99):
                    for copies in (1,10):
                        for mismatch in (False,True):
                            for peek in (False,True):
                                args=[n,scenario,confidence,.01,copies,mismatch,peek]
                                with self.subTest(args=args):
                                    expected=simulate(*args)
                                    actual=self.page.evaluate('args=>simulateExperiment(...args)',args)
                                    for k,v in expected.items():
                                        if isinstance(v,dict):
                                            for sub,value in v.items():
                                                if value is None:self.assertIsNone(actual[k][sub])
                                                else:self.assertAlmostEqual(actual[k][sub],value)
                                        elif v is None:self.assertIsNone(actual[k])
                                        elif type(v) is float:self.assertAlmostEqual(actual[k],v,places=7)
                                        else:self.assertEqual(actual[k],v)
    def test_quizzes_saved_and_historical_keys_preserved(self):
        quiz=json.loads(self.page.locator('#lesson-data').text_content())['quiz']
        self.assertEqual(self.page.locator('#questions fieldset').count(),8)
        for i,item in enumerate(quiz):
            q=self.page.locator('#questions fieldset').nth(i);q.locator(f'input[value="{item[2]}"]').check();q.locator('button').click()
            self.assertIn('Correct.',q.locator('.feedback').inner_text());self.assertIn(item[3],q.locator('.feedback').inner_text())
        self.page.evaluate("localStorage.setItem('ai-handbook-m05-l03-v1',JSON.stringify({done:true,answers:{0:0}}))")
        self.page.locator('#done').check();self.page.reload()
        self.assertTrue(self.page.locator('#done').is_checked())
        self.assertTrue(self.page.locator('#questions fieldset').first.locator('input[value="0"]').is_checked())
        self.assertEqual(self.page.evaluate("JSON.parse(localStorage.getItem('ai-handbook-m05-l03-v1')).answers[0]"),0)
    def test_mobile_plot_navigation_and_manifest_link(self):
        self.assertIn('Experiment Design',self.page.locator('a[aria-current="page"]').inner_text())
        self.page.set_viewport_size({'width':390,'height':844})
        self.assertTrue(self.page.locator('#interval-plot').is_visible())
        self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),390)
        self.page.locator('.handbook-drawer-button').click()
        self.assertEqual(self.page.locator('.handbook-drawer-button').get_attribute('aria-expanded'),'true')
        self.page.locator('a[href="./chapter-m05-l03.html"]').click();self.page.wait_for_url('**/chapter-m05-l03.html')
        self.page.locator('#profile').wait_for();self.assertEqual(self.page.locator('#questions fieldset').count(),8)

if __name__=='__main__':unittest.main()
