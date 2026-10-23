import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from m04_ingestion_lab import Document, Index, chunk_document

def doc(revision=1, roles=frozenset({"engineer"}), text="alpha beta gamma delta epsilon zeta eta theta"):
    return Document("payments", revision, text, roles, "runbook/payments")

class IngestionTests(unittest.TestCase):
    def test_overlap_boundaries(self):
        parts = chunk_document(doc(), 4, 2)
        self.assertEqual([(p.start_word, p.end_word) for p in parts], [(0, 4), (2, 6), (4, 8)])

    def test_exact_fit_has_no_empty_tail(self):
        self.assertEqual(len(chunk_document(doc(text="a b c d"), 4, 2)), 1)

    def test_invalid_overlap(self):
        for size, overlap in ((4, 4), (4, -1), (0, 0)):
            with self.subTest(size=size, overlap=overlap):
                with self.assertRaises(ValueError):
                    chunk_document(doc(), size, overlap)

    def test_revision_replaces_old_chunks(self):
        index = Index()
        index.upsert(doc(), 4, 1)
        index.upsert(doc(revision=2, text="new words only"), 4, 1)
        self.assertTrue(all(c.revision == 2 for c in index.all_chunks()))
        self.assertTrue(all("alpha" not in c.text for c in index.all_chunks()))

    def test_stale_update_refused(self):
        index = Index()
        index.upsert(doc())
        with self.assertRaises(ValueError):
            index.upsert(doc())

    def test_acl_revocation_on_revision(self):
        index = Index()
        index.upsert(doc())
        self.assertTrue(index.visible("engineer"))
        index.upsert(doc(revision=2, roles=frozenset({"security"})))
        self.assertEqual(index.visible("engineer"), [])
        self.assertTrue(index.visible("security"))

    def test_delete_removes_indexed_chunks(self):
        index = Index()
        index.upsert(doc())
        index.delete("payments", 2)
        self.assertEqual(index.all_chunks(), [])

    def test_stale_delete_rejected(self):
        index = Index()
        index.upsert(doc(revision=3))
        with self.assertRaises(ValueError):
            index.delete("payments", 2)
        self.assertTrue(index.all_chunks())

    def test_rejected_update_preserves_old_index(self):
        index = Index()
        index.upsert(doc())
        old = index.all_chunks()
        with self.assertRaises(ValueError):
            index.upsert(doc(revision=2), 5, 5)
        self.assertEqual(index.all_chunks(), old)

if __name__ == "__main__":
    unittest.main()
