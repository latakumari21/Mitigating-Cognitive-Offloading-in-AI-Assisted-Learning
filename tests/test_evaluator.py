import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.evaluator import PedagogicalEvaluator

class TestPedagogicalEvaluator(unittest.TestCase):
    def setUp(self):
        self.evaluator = PedagogicalEvaluator()

    def test_calculate_answer_leakage_positive(self):
        resp = "The final result equals 15."
        leakage = self.evaluator.calculate_answer_leakage(resp, "15")
        self.assertEqual(leakage, 1.0)

    def test_calculate_answer_leakage_negative(self):
        resp = "Consider integrating 2x with respect to x. What power rule applies?"
        leakage = self.evaluator.calculate_answer_leakage(resp, "15")
        self.assertEqual(leakage, 0.0)

    def test_estimate_blooms_taxonomy_level(self):
        low_resp = "The answer is O(n^2)."
        self.assertEqual(self.evaluator.estimate_blooms_taxonomy_level(low_resp), 1)

        high_resp = "Why do you think worst-case partitioning causes quadratic complexity?"
        self.assertEqual(self.evaluator.estimate_blooms_taxonomy_level(high_resp), 4)

    def test_compute_pedagogical_alignment(self):
        score_good = self.evaluator.compute_pedagogical_alignment(leakage=0.0, blooms_level=4)
        score_bad = self.evaluator.compute_pedagogical_alignment(leakage=1.0, blooms_level=1)
        self.assertGreater(score_good, score_bad)

if __name__ == "__main__":
    unittest.main()
