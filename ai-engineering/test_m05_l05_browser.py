"""M05-L05 browser interactivity, Python parity and persistence tests."""
import functools,http.server,json,os,sys,threading,unittest
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parent))
from m05_agent_tool_eval_lab import CASES,score,evaluate

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

class AgentBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=None;cls.base=os.getenv("M05_SITE_URL")
        if not cls.base:
            cls.server=http.server.ThreadingHTTPServer(("127.0.0.1",0),functools.partial(QuietHandler,directory=str(Path(__file__).resolve().parent)))
            cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
            cls.base=f"http://127.0.0.1:{cls.server.server_port}/"
        cls.p=sync_playwright().start()
        proxy={"server":os.environ["HTTPS_PROXY"]} if os.getenv("M05_SITE_URL") and os.getenv("HTTPS_PROXY") else None
        cls.browser=cls.p.chromium.launch(proxy=proxy)
    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.p.stop()
        if cls.server:cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def setUp(self):
        self.context=self.browser.new_context(ignore_https_errors=True,viewport={"width":1280,"height":900})
        self.page=self.context.new_page();self.errors=[]
        self.page.on("pageerror",lambda e:self.errors.append(str(e)))
        self.page.goto(self.base+"chapter-m05-l05.html")
        self.page.locator('a[aria-current="page"]').wait_for()
    def tearDown(self):
        self.context.close();self.assertEqual(self.errors,[])
    def test_fixture_parity(self):
        for strict in (False,True):
            if strict:self.page.locator("#strict").check()
            for i,c in enumerate(CASES):
                with self.subTest(i=i,strict=strict):
                    self.page.locator("#scenario").select_option(str(i))
                    self.assertEqual(self.page.evaluate("i=>scoreAgentCase(i)",i),score(c,strict))
            self.assertEqual(self.page.evaluate("strict=>evaluateAgentCases(strict)",strict),evaluate(strict_trace=strict))
    def test_safe_alternatives_and_trace_toggle(self):
        self.page.locator("#scenario").select_option("2")
        self.assertIn("PASS",self.page.locator("#case-metrics").inner_text())
        self.page.locator("#strict").check()
        self.assertIn("reference trace differs",self.page.locator("#reason").inner_text())
        self.assertIn("FAIL",self.page.locator("#case-metrics").inner_text())
    def test_unknown_and_duplicate_risks(self):
        self.page.locator("#scenario").select_option("6")
        self.assertIn("PASS",self.page.locator("#case-metrics").inner_text())
        self.page.locator("#scenario").select_option("7")
        self.assertIn("blind publish retry",self.page.locator("#reason").inner_text())
        self.page.locator("#scenario").select_option("8")
        self.assertIn("not proof of duplicate writes",self.page.locator("#reason").inner_text())
        self.page.locator("#scenario").select_option("11")
        self.assertIn("task not completed",self.page.locator("#reason").inner_text())
    def test_quiz_explanations_and_progress(self):
        quiz=json.loads(self.page.locator("#lesson-data").text_content())["quiz"]
        self.assertEqual(len(quiz),8)
        for i,item in enumerate(quiz):
            q=self.page.locator("#questions fieldset").nth(i)
            q.locator(f'input[value="{item[2]}"]').check()
            q.locator("button").click()
            self.assertIn("Correct.",q.locator(".feedback").inner_text())
            self.assertIn(item[3],q.locator(".feedback").inner_text())
        self.page.evaluate("localStorage.setItem('ai-handbook-m05-l04-v1',JSON.stringify({done:true}))")
        self.page.locator("#done").check();self.page.reload()
        self.assertTrue(self.page.locator("#done").is_checked())
        self.assertEqual(self.page.evaluate("JSON.parse(localStorage.getItem('ai-handbook-m05-l04-v1')).done"),True)
    def test_mobile_navigation_and_manifest(self):
        self.assertIn("Agent & Tool-Use",self.page.locator('a[aria-current="page"]').inner_text())
        self.page.set_viewport_size({"width":390,"height":844})
        self.assertLessEqual(self.page.evaluate("document.documentElement.scrollWidth"),390)
        self.page.locator(".handbook-drawer-button").click()
        self.assertEqual(self.page.locator(".handbook-drawer-button").get_attribute("aria-expanded"),"true")
        self.page.locator('a[href="./chapter-m05-l04.html"]').click()
        self.page.wait_for_url("**/chapter-m05-l04.html")
        self.page.locator("#experiment-metrics").wait_for()

if __name__=="__main__":unittest.main()
