import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from m04_rag_lab import answer, retrieve, tokens

class RAGLabTests(unittest.TestCase):
    def test_tokenization(self):
        self.assertEqual(tokens("503; 503!"), {"503"})

    def test_retrieval_is_stable(self):
        ids = [c.id for c in retrieve("payments service", "engineering")]
        self.assertEqual(ids, ["a", "b"])

    def test_acl_filters_before_ranking(self):
        self.assertNotIn("secret", [c.id for c in retrieve("payments customer credentials vault", "engineering", 10)])
        self.assertEqual([c.id for c in retrieve("payments customer credentials vault", "security")], ["secret"])

    def test_no_match_abstains(self):
        response = answer("unknown planetary quantum policy", "engineering")
        self.assertEqual(response["status"], "insufficient_evidence")
        self.assertIsNone(response["answer"])
        self.assertEqual(response["citations"], [])

    def test_citations_provenance(self):
        response = answer("idempotency outbound writes", "engineering")
        self.assertEqual(response["citations"], [{"chunk_id": "b", "source": "payments-runbook#writes"}])

    def test_invalid_k(self):
        with self.assertRaises(ValueError):
            retrieve("payments", "engineering", 0)

if __name__ == "__main__":
    unittest.main()
