"""M05-L07 UI, parity, knowledge check and mobile navigation."""
import functools,http.server,json,os,sys,threading,unittest
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parent))
from m05_capstone_evaluation_lab import decide,FIXTURES
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
class CapstoneBrowserTests(unittest.TestCase):
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
        self.page.goto(self.base+"chapter-m05-l07.html")
        self.page.locator('a[aria-current="page"]').wait_for()
    def tearDown(self):
        self.context.close();self.assertEqual(self.errors,[])
    def test_all_phase_scenario_parity(self):
        for scenario in FIXTURES:
            for phase in ("offline","shadow","online"):
                for floor in (.5,.75,.9):
                    for margin in (0,.01,.03):
                        args=[scenario,phase,floor,margin]
                        with self.subTest(args=args):
                            expected=decide(*args)
                            actual=self.page.evaluate("args=>launchDecision(...args)",args)
                            self.assertEqual(actual["decision"],expected["decision"])
                            self.assertEqual(actual["reasons"],expected["reasons"])
                            for k in ("rare_rate","delta","lower","upper"):
                                if expected[k] is None:self.assertIsNone(actual[k])
                                else:self.assertAlmostEqual(expected[k],actual[k],places=10)
    def test_phase_and_hard_gates(self):
        self.page.locator("#phase").select_option("offline")
        self.assertIn("SHADOW",self.page.locator("#metrics").inner_text())
        self.page.locator("#phase").select_option("shadow")
        self.assertIn("CANARY",self.page.locator("#metrics").inner_text())
        self.page.locator("#scenario").select_option("unsafe")
        self.assertIn("BLOCK",self.page.locator("#metrics").inner_text())
        self.page.locator("#scenario").select_option("healthy")
        self.page.locator("#phase").select_option("online")
        self.assertIn("GUARDED_ROLLOUT",self.page.locator("#metrics").inner_text())
    def test_harm_and_safety_rollback(self):
        for scenario in ("online_harm","incident"):
            self.page.locator("#scenario").select_option(scenario)
            self.assertIn("ROLLBACK",self.page.locator("#metrics").inner_text())
        self.page.locator("#scenario").select_option("inconclusive")
        self.assertIn("HOLD",self.page.locator("#metrics").inner_text())
    def test_quizzes_persistence_and_old_keys(self):
        quiz=json.loads(self.page.locator("#lesson-data").text_content())["quiz"]
        self.assertEqual(len(quiz),8)
        for i,item in enumerate(quiz):
            f=self.page.locator("#questions fieldset").nth(i)
            f.locator(f'input[value="{item[2]}"]').check();f.locator("button").click()
            self.assertIn("Correct.",f.locator(".feedback").inner_text())
        self.page.evaluate("localStorage.setItem('ai-handbook-m05-l06-v1',JSON.stringify({done:true}))")
        self.page.locator("#done").check();self.page.reload()
        self.assertTrue(self.page.locator("#done").is_checked())
        self.assertTrue(self.page.evaluate("JSON.parse(localStorage.getItem('ai-handbook-m05-l06-v1')).done"))
    def test_mobile_navigation(self):
        self.page.set_viewport_size({"width":390,"height":844})
        self.assertLessEqual(self.page.evaluate("document.documentElement.scrollWidth"),390)
        self.page.locator(".handbook-drawer-button").click()
        self.page.locator('a[href="./chapter-m05-l06.html"]').click()
        self.page.wait_for_url("**/chapter-m05-l06.html")
        self.page.locator("#profile").wait_for()
if __name__=="__main__":unittest.main()
