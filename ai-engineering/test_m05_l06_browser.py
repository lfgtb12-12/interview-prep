"""Browser parity and usability for M05-L06."""
import functools,http.server,json,os,sys,threading,unittest
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parent))
from m05_ci_gates_lab import evaluate,PROFILES
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
class CIGateBrowserTests(unittest.TestCase):
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
        self.page.goto(self.base+"chapter-m05-l06.html")
        self.page.locator('a[aria-current="page"]').wait_for()
    def tearDown(self):
        self.context.close();self.assertEqual(self.errors,[])
    def test_fixture_policy_python_js_parity(self):
        for profile in PROFILES:
            for rate in (0,.5,.75):
                for loss in (0,.25,.5):
                    for strict in (False,True):
                        args=[profile,2,rate,loss,1500,500,strict]
                        with self.subTest(args=args):
                            py=evaluate(profile,2,rate,loss,1500,500,strict)
                            js=self.page.evaluate("args=>evaluateCIGates(...args)",args)
                            self.assertEqual(js,py)
    def test_scenarios_change_real_gates(self):
        self.assertIn("Passes",self.page.locator("#decision").inner_text())
        for scenario,keyword in (("rare_regression","paired regressions"),("safety","unsafe"),("latency","latency"),("cost","cost"),("broken_trace","broken trace"),("missing","missing observations")):
            self.page.locator("#profile").select_option(scenario)
            self.assertIn("Blocked",self.page.locator("#decision").inner_text())
            self.assertIn(keyword,self.page.locator("#failures").inner_text())
        self.page.locator("#strictmissing").uncheck()
        self.assertIn("Passes",self.page.locator("#decision").inner_text())
    def test_budget_controls_change_outcome(self):
        self.page.locator("#profile").select_option("latency")
        self.page.locator("#latency").select_option("2500")
        self.assertIn("Passes",self.page.locator("#decision").inner_text())
        self.page.locator("#profile").select_option("cost")
        self.page.locator("#cost").select_option("1000")
        self.assertIn("Passes",self.page.locator("#decision").inner_text())
    def test_quizzes_and_history_preserved(self):
        quiz=json.loads(self.page.locator("#lesson-data").text_content())["quiz"]
        self.assertEqual(len(quiz),8)
        for i,item in enumerate(quiz):
            q=self.page.locator("#questions fieldset").nth(i)
            q.locator(f'input[value="{item[2]}"]').check();q.locator("button").click()
            self.assertIn("Correct.",q.locator(".feedback").inner_text())
            self.assertIn(item[3],q.locator(".feedback").inner_text())
        self.page.evaluate("localStorage.setItem('ai-handbook-m05-l05-v1',JSON.stringify({done:true}))")
        self.page.locator("#done").check();self.page.reload()
        self.assertTrue(self.page.locator("#done").is_checked())
        self.assertTrue(self.page.evaluate("JSON.parse(localStorage.getItem('ai-handbook-m05-l05-v1')).done"))
    def test_mobile_navigation(self):
        self.page.set_viewport_size({"width":390,"height":844})
        self.assertLessEqual(self.page.evaluate("document.documentElement.scrollWidth"),390)
        self.page.locator(".handbook-drawer-button").click()
        self.page.locator('a[href="./chapter-m05-l05.html"]').click()
        self.page.wait_for_url("**/chapter-m05-l05.html")
        self.page.locator("#scenario").wait_for()
if __name__=="__main__":unittest.main()
