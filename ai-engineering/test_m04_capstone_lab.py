import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from m04_capstone_lab import Index, Source, answer

POLICY = "A timeout does not prove a charge failed; check status before replay."
def source(revision=1,roles=frozenset({"engineer"}),deleted=False,facts=frozenset({POLICY})):
    return Source("pay503",revision,"PAY-503 charge retry timeout",roles,facts,deleted)
def index():
    i=Index();i.apply(source());return i

class CapstoneTests(unittest.TestCase):
    def test_grounded_answer_and_revision(self):
        result=answer(index(),"engineer","PAY-503")
        self.assertEqual(result.status,"grounded")
        self.assertEqual(result.claims[0][1],"pay503@r1")
    def test_role_isolation(self):self.assertEqual(answer(index(),"guest","PAY-503").claims,())
    def test_revocation(self):
        i=index();i.apply(source(2,roles=frozenset({"security"})))
        self.assertEqual(answer(i,"engineer","PAY-503").status,"no_authorized_evidence")
    def test_versioned_deletion(self):
        i=index();i.apply(source(2,deleted=True))
        self.assertFalse(i.visible("engineer"))
    def test_stale_update_after_delete_rejected(self):
        i=index();i.apply(source(3,deleted=True))
        with self.assertRaises(ValueError):i.apply(source(2))
        self.assertFalse(i.visible("engineer"))
    def test_equal_revision_rejected(self):
        i=index()
        with self.assertRaises(ValueError):i.apply(source())
    def test_vector_outage_fallback(self):
        self.assertEqual(answer(index(),"engineer","PAY-503",vector_ok=False).status,"grounded")
    def test_lexical_outage_fallback(self):
        self.assertEqual(answer(index(),"engineer","PAY-503",lexical_ok=False).status,"grounded")
    def test_both_outage(self):
        self.assertEqual(answer(index(),"engineer","PAY-503",lexical_ok=False,vector_ok=False).status,"retrieval_unavailable")
    def test_fallback_disabled(self):
        self.assertEqual(answer(index(),"engineer","PAY-503",vector_ok=False,allow_fallback=False).status,"retrieval_degraded")
    def test_unknown_claim_not_output(self):
        i=Index();i.apply(source(facts=frozenset({"retry immediately"})))
        self.assertEqual(answer(i,"engineer","PAY-503").status,"insufficient_evidence")
    def test_deadline(self):
        self.assertEqual(answer(index(),"engineer","PAY-503",latency_budget_ms=0).status,"deadline_exceeded")
    def test_empty_index(self):
        self.assertEqual(answer(Index(),"engineer","PAY-503").status,"no_authorized_evidence")
    def test_lexical_no_hit(self):
        self.assertEqual(answer(index(),"engineer","unrelated",vector_ok=False).status,"no_evidence")
if __name__=="__main__":unittest.main()
