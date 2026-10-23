import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from m04_vector_lab import cosine, dot, squared_l2, search

class VectorTests(unittest.TestCase):
    def test_cosine_direction_ignores_scale(self):
        self.assertAlmostEqual(cosine((1, 0), (10, 0)), 1)

    def test_dot_rewards_magnitude(self):
        self.assertEqual(dot((1, 0), (10, 0)), 10)

    def test_l2_is_squared_distance(self):
        self.assertEqual(squared_l2((0, 0), (3, 4)), 25)

    def test_zero_vector_cosine_rejected(self):
        with self.assertRaises(ValueError):
            cosine((0, 0), (1, 0))

    def test_dimension_mismatch(self):
        with self.assertRaises(ValueError):
            dot((1, 2), (1,))

    def test_access_filter_before_ranking(self):
        self.assertNotIn("restricted", [id for _, id in search((1, 0, 0), "engineer", k=10)])
        self.assertEqual(search((1, 0, 0), "security")[0][1], "restricted")

    def test_stable_tie_break(self):
        self.assertEqual(search((1, 0, 0), metric="cosine")[0][1], "retry-runbook")

    def test_invalid_metric(self):
        with self.assertRaises(ValueError):
            search((1, 0, 0), metric="unknown")

    def test_invalid_nonfinite_vector(self):
        with self.assertRaises(ValueError):
            cosine((1, float("nan")), (1, 0))

if __name__ == "__main__":
    unittest.main()
