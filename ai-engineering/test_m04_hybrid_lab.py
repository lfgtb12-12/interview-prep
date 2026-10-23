import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from m04_hybrid_lab import Doc, bm25, rrf, candidates, rerank, recall_at_k, reciprocal_rank, tokenize

class HybridLabTests(unittest.TestCase):
    def test_identifier_tokenization(self):
        self.assertEqual(tokenize("PAY-503 503?"), ["pay-503", "503"])
    def test_bm25_exact_identifier_beats_unrelated(self):
        docs = [Doc("exact", "PAY-503 charge", frozenset()), Doc("other", "survey export", frozenset())]
        self.assertEqual(bm25("PAY-503", docs)[0][0], "exact")
    def test_bm25_order_independent_and_empty(self):
        docs = [Doc("z", "", frozenset()), Doc("a", "", frozenset())]
        self.assertEqual(bm25("none", docs), [("a", 0.0), ("z", 0.0)])
        self.assertEqual(bm25("none", []), [])
    def test_rrf_union_and_weight_extremes(self):
        self.assertEqual(rrf(["a"], ["b"], 1)[0][0], "a")
        self.assertEqual(rrf(["a"], ["b"], 0)[0][0], "b")
        self.assertEqual({x for x,_ in rrf(["a"], ["b"])}, {"a", "b"})
    def test_rrf_deterministic_ties(self):
        self.assertEqual([x for x,_ in rrf(["b"], ["a"])], ["a", "b"])
    def test_rrf_absent_cannot_reappear(self):
        self.assertNotIn("missing", dict(rrf(["a"], ["b"])))
    def test_reject_duplicate_branch(self):
        with self.assertRaises(ValueError): rrf(["a", "a"], [])
    def test_reject_bad_parameters(self):
        with self.assertRaises(ValueError): rrf(["a"], [], -1)
        with self.assertRaises(ValueError): bm25("q", [Doc("x","a",frozenset())], b=2)
    def test_acl_pruned_before_candidate_union(self):
        self.assertNotIn("security-only", candidates("engineer", "PAY-503", ["security-only", "retry"]))
    def test_rerank_only_reorders_candidates(self):
        self.assertEqual(rerank(["a", "b"], {"a": .1, "b": .9, "missing": 9.0}, 1), ["b"])
    def test_missing_rerank_score_fails(self):
        with self.assertRaises(ValueError): rerank(["a"], {}, 1)
    def test_recall_and_mrr(self):
        self.assertEqual(recall_at_k(["x","a","b"], {"a","b"}, 2), .5)
        self.assertEqual(reciprocal_rank(["x","a"], {"a"}), .5)
        self.assertEqual(reciprocal_rank(["x"], {"a"}), 0.0)
    def test_zero_k_rejected(self):
        with self.assertRaises(ValueError): recall_at_k(["a"], {"a"}, 0)

if __name__ == "__main__": unittest.main()
