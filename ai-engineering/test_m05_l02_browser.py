"""Behavior, Python/JS parity and live publication checks.

M05_SITE_URL=https://.../ai-engineering/ runs against the deployed site.
Default: serve the checkout over HTTP, including real curriculum navigation.
"""
import copy
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
from m05_rag_evaluation_lab import retrieval_metrics, answer_metrics, CLAIMS, GRADES, REQUIRED

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

class RagBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=None
        cls.base=os.getenv('M05_SITE_URL')
        if not cls.base:
            handler=functools.partial(QuietHandler,directory=str(Path(__file__).resolve().parent))
            cls.server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
            cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
            cls.base=f'http://127.0.0.1:{cls.server.server_port}/'
        cls.p=sync_playwright().start()
        proxy={'server':os.environ['HTTPS_PROXY']} if os.getenv('M05_SITE_URL') and os.getenv('HTTPS_PROXY') else None
        cls.browser=cls.p.chromium.launch(proxy=proxy)
    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.p.stop()
        if cls.server:cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def setUp(self):
        self.context=self.browser.new_context(ignore_https_errors=True,viewport={'width':1280,'height':900})
        self.page=self.context.new_page();self.errors=[]
        self.page.on('pageerror',lambda e:self.errors.append(str(e)))
        self.page.goto(self.base+'chapter-m05-l02.html')
        self.page.locator('a[aria-current="page"]').wait_for()
    def tearDown(self):
        self.context.close();self.assertEqual(self.errors,[])
    def metrics(self):
        return self.page.evaluate("evaluateRag(document.querySelector('#ranking').value,Number(document.querySelector('#cutoff').value),document.querySelector('#drop').checked,document.querySelector('#answer-mode').value).metrics")
    def test_cutoff_ranking_and_visual_gain(self):
        self.assertEqual(self.metrics()['recall'],.5)
        self.assertIn('0.497',self.page.locator('#retrieval-metrics').inner_text())
        self.page.locator('#ranking').select_option('improved')
        self.assertEqual(self.metrics()['ndcg'],1)
        self.assertEqual(self.page.locator('.gain').first.evaluate('e=>e.style.width'),'100%')
        self.page.locator('#cutoff').evaluate("e=>{e.value='4';e.dispatchEvent(new Event('input'))}")
        self.assertEqual(self.metrics()['context_relevance'],.5)
        self.assertEqual(self.page.locator('.rank-row').count(),4)
    def test_context_packing_attribution_and_incompleteness(self):
        self.page.locator('#ranking').select_option('improved')
        self.page.locator('#drop').check()
        m=self.metrics();self.assertEqual((m['recall'],m['context_recall'],m['faithfulness']),(1,.5,.5))
        self.assertIn('Context packing loses',self.page.locator('#diagnosis').inner_text())
        self.page.locator('#drop').uncheck()
        self.page.locator('#answer-mode').select_option('wrong-citation')
        m=self.metrics();self.assertEqual((m['faithfulness'],m['citation_precision']),(1,0))
        self.page.locator('#answer-mode').select_option('partial')
        m=self.metrics();self.assertEqual((m['faithfulness'],m['completeness']),(1,.5))
    def test_abstention_and_undefined_values(self):
        self.page.locator('#answer-mode').select_option('abstain')
        self.assertIn('False abstention',self.page.locator('#abstention').inner_text())
        self.assertIsNone(self.metrics()['faithfulness'])
        self.page.locator('#ranking').select_option('unanswerable')
        self.assertIn('Correct abstention',self.page.locator('#abstention').inner_text())
        self.assertIsNone(self.metrics()['recall'])
        self.assertIsNone(self.metrics()['completeness'])
        self.page.locator('#answer-mode').select_option('uncited')
        self.assertIsNone(self.metrics()['citation_precision'])
        self.assertEqual(self.metrics()['citation_coverage'],0)
    def test_python_js_parity_192_configurations(self):
        for ranking in ('baseline','improved','miss','unanswerable'):
            for k in range(1,5):
                for drop in (False,True):
                    for mode in ('complete','partial','unsafe','wrong-citation','uncited','abstain'):
                        with self.subTest(ranking=ranking,k=k,drop=drop,mode=mode):
                            ranked={'baseline':['C','A','B','D'],'improved':['A','B','C','D'],'miss':['C','D'],'unanswerable':['C','D']}[ranking]
                            grades=GRADES if ranking!='unanswerable' else {'C':0,'D':0}
                            top=ranked[:k];context=[d for d in top if not drop or d!='B']
                            expected=retrieval_metrics(ranked,grades,k)
                            expected['context_relevance']=retrieval_metrics(context,grades,k)['context_relevance']
                            expected['context_recall']=retrieval_metrics(context,grades,k)['recall']
                            claims=copy.deepcopy(CLAIMS)
                            if mode=='partial':claims=claims[:1]
                            if mode=='unsafe':claims.append({'fact':'retry','correct':False,'supports':[],'cites':['C']})
                            if mode=='wrong-citation':
                                for i,c in enumerate(claims):c['cites']=['A' if i else 'B']
                            if mode=='uncited':
                                for c in claims:c['cites']=[]
                            if mode=='abstain':claims=[]
                            expected.update(answer_metrics(claims,context,REQUIRED if ranking!='unanswerable' else []))
                            actual=self.page.evaluate('args=>evaluateRag(...args).metrics',[ranking,k,drop,mode])
                            for key,value in expected.items():
                                if value is None:self.assertIsNone(actual[key])
                                else:self.assertAlmostEqual(actual[key],value)
    def test_quizzes_explained_saved_and_old_progress_preserved(self):
        self.assertEqual(self.page.locator('#questions fieldset').count(),8)
        data=self.page.locator('#lesson-data').text_content();quiz=json.loads(data)['quiz']
        first=self.page.locator('#questions fieldset').first
        first.locator('button').click();self.assertIn('Choose',first.locator('.feedback').inner_text())
        first.locator('input[value="0"]').check();first.locator('button').click()
        self.assertIn('Not quite',first.locator('.feedback').inner_text())
        for i,item in enumerate(quiz):
            q=self.page.locator('#questions fieldset').nth(i)
            q.locator(f'input[value="{item[2]}"]').check();q.locator('button').click()
            self.assertIn('Correct.',q.locator('.feedback').inner_text())
            self.assertIn(item[3],q.locator('.feedback').inner_text())
        self.page.evaluate("localStorage.setItem('ai-handbook-m05-l01-v1',JSON.stringify({done:true,answers:{0:1}}))")
        self.page.locator('#done').check();self.page.reload()
        self.assertTrue(self.page.locator('#done').is_checked())
        self.assertTrue(self.page.locator('#questions fieldset').first.locator('input[value="1"]').is_checked())
        self.assertEqual(self.page.evaluate("JSON.parse(localStorage.getItem('ai-handbook-m05-l01-v1')).answers[0]"),1)
    def test_navigation_and_curriculum(self):
        current=self.page.locator('a[aria-current="page"]')
        self.assertIn('Retrieval and Grounded',current.inner_text())
        with self.page.expect_response('**/curriculum.json') as response:
            self.page.reload()
        curriculum=response.value.json()
        lesson=next(l for m in curriculum['modules'] for l in m['lessons'] if l['id']=='M05-L02')
        self.assertEqual(lesson['path'],'chapter-m05-l02.html')
        self.page.locator('a[href="./chapter-m05-l01.html"]').click()
        self.page.wait_for_url('**/chapter-m05-l01.html')
        self.page.locator('a[aria-current="page"]').wait_for()
        self.assertEqual(self.page.locator('#questions fieldset').count(),8)
    def test_mobile_drawer_and_no_overflow(self):
        self.page.set_viewport_size({'width':390,'height':844})
        self.assertTrue(self.page.locator('#ranking').is_visible())
        self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),390)
        self.page.locator('.handbook-drawer-button').click()
        self.assertEqual(self.page.locator('.handbook-drawer-button').get_attribute('aria-expanded'),'true')
        self.page.keyboard.press('Escape')
        self.assertEqual(self.page.locator('.handbook-drawer-button').get_attribute('aria-expanded'),'false')

if __name__=='__main__':unittest.main()
