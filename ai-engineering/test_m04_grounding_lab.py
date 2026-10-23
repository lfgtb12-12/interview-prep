import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from m04_grounding_lab import Source, Claim, Decision, Status, SOURCES, gate

GOOD = Claim("A timeout does not prove the charge failed.", "S1", 3)
SECOND = Claim("Check operation status before replay.", "S2", 7)
BAD = Claim("Immediately retry with a new idempotency key.", "S1", 3)

class GroundingTests(unittest.TestCase):
    def test_two_supported_claims(self):
        d = gate(Status.READY, [GOOD, SECOND], SOURCES, "engineer")
        self.assertEqual(d.outcome, "grounded")
        self.assertEqual(len(d.approved), 2)
    def test_unsupported_claim_rejected(self):
        d = gate(Status.READY, [GOOD, BAD], SOURCES, "engineer")
        self.assertEqual(d.outcome, "partial_grounded")
        self.assertEqual(d.blocked, (BAD,))
    def test_only_false_claim_abstains(self):
        self.assertEqual(gate(Status.READY, [BAD], SOURCES, "engineer").outcome, "abstain")
    def test_fake_handle_rejected(self):
        c = Claim(GOOD.text, "FAKE", 3)
        self.assertEqual(gate(Status.READY, [c], SOURCES, "engineer").blocked, (c,))
    def test_wrong_source_rejected(self):
        c = Claim(GOOD.text, "S2", 7)
        self.assertEqual(gate(Status.READY, [c], SOURCES, "engineer").outcome, "abstain")
    def test_old_revision_rejected(self):
        c = Claim(GOOD.text, "S1", 2)
        self.assertEqual(gate(Status.READY, [c], SOURCES, "engineer").outcome, "abstain")
    def test_revocation_prevents_answer(self):
        self.assertEqual(gate(Status.READY, [GOOD], SOURCES, "guest").outcome, "abstain")
    def test_restricted_source_does_not_leak(self):
        c = Claim("A timeout does not prove the charge failed.", "S3", 1)
        self.assertEqual(gate(Status.READY, [c], SOURCES, "engineer").approved, ())
    def test_retrieval_outage_distinct(self):
        self.assertEqual(gate(Status.UNAVAILABLE, [GOOD], SOURCES, "engineer").outcome, "retrieval_unavailable")
    def test_no_evidence_distinct(self):
        self.assertEqual(gate(Status.NO_EVIDENCE, [GOOD], SOURCES, "engineer").outcome, "no_authorized_evidence")
    def test_stale_version_distinct(self):
        self.assertEqual(gate(Status.STALE, [GOOD], SOURCES, "engineer").outcome, "stale_evidence")
    def test_empty_ready_abstains(self):
        self.assertEqual(gate(Status.READY, [], SOURCES, "engineer").outcome, "abstain")
    def test_unknown_status_rejected(self):
        with self.assertRaises(ValueError):
            gate("other", [GOOD], SOURCES, "engineer")

if __name__ == "__main__":
    unittest.main()
