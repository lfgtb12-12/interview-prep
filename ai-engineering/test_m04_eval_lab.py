import unittest, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from m04_eval_lab import Case, recall_at_k, precision_at_k, reciprocal_rank, ndcg_at_k, evaluate, diagnose

def case(pool=("pay503","retry"),context=("pay503","retry"),supported=(True,True)):
    return Case("PAY-503",pool,context,frozenset({"pay503","retry"}),supported,500)

class EvaluationTests(unittest.TestCase):
    def test_recall(self): self.assertEqual(recall_at_k(["x","pay503"],{"pay503","retry"},2), .5)
    def test_precision(self): self.assertEqual(precision_at_k(["x","pay503"],{"pay503"},2), .5)
    def test_precision_k_denominator(self): self.assertEqual(precision_at_k(["pay503"],{"pay503"},2), .5)
    def test_mrr(self): self.assertEqual(reciprocal_rank(["x","pay503"],{"pay503"}), .5)
    def test_mrr_missing(self): self.assertEqual(reciprocal_rank(["x"],{"pay503"}), 0)
    def test_ndcg_ideal(self): self.assertAlmostEqual(ndcg_at_k(["a","b"],{"a":3,"b":1},2),1)
    def test_ndcg_reversed(self): self.assertLess(ndcg_at_k(["b","a"],{"a":3,"b":1},2),1)
    def test_ndcg_no_labels(self): self.assertEqual(ndcg_at_k(["a"],{},1),0)
    def test_duplicate_ndcg_rejected(self):
        with self.assertRaises(ValueError): ndcg_at_k(["a","a"],{"a":2},2)
    def test_full_evaluation(self):
        r=evaluate([case()])
        self.assertEqual(r["candidate_recall"],1)
        self.assertEqual(r["context_recall_at_k"],1)
        self.assertEqual(r["support_rate"],1)
    def test_diagnosis_candidate_miss(self): self.assertEqual(diagnose(case(pool=("retry",),context=("retry",))),"candidate_retrieval")
    def test_diagnosis_context_loss(self): self.assertEqual(diagnose(case(context=("retry",))),"rerank_or_context")
    def test_diagnosis_unsupported_claim(self): self.assertEqual(diagnose(case(supported=(False,True))),"generation_or_verification")
    def test_diagnosis_clean(self): self.assertEqual(diagnose(case()),"ok")
    def test_empty_dataset_rejected(self):
        with self.assertRaises(ValueError): evaluate([])
    def test_invalid_context_rejected(self):
        with self.assertRaises(ValueError): evaluate([case(context=("foreign",))])
    def test_bad_k_rejected(self):
        with self.assertRaises(ValueError): recall_at_k(["a"],{"a"},0)
    def test_negative_latency_rejected(self):
        with self.assertRaises(ValueError): evaluate([Case("q",("a",),("a",),frozenset({"a"}),(True,),-1)])
if __name__=="__main__": unittest.main()
