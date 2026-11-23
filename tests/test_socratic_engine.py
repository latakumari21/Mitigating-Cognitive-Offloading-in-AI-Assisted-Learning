import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.socratic_engine import SocraticEngine

class TestSocraticEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SocraticEngine()

    def test_build_prompt_contains_rules(self):
        prompt = self.engine.build_prompt("How do I find the derivative of x^2?", hint_level=1)
        self.assertIn("Never provide the direct solution", prompt)
        self.assertIn("How do I find the derivative of x^2?", prompt)

    def test_detect_answer_leakage_true(self):
        text = "The calculated final velocity is 4 m/s^2."
        self.assertTrue(self.engine.detect_answer_leakage(text, "4 m/s^2"))

    def test_detect_answer_leakage_false(self):
        text = "What is the formula connecting velocity and time?"
        self.assertFalse(self.engine.detect_answer_leakage(text, "4 m/s^2"))

    def test_sanitize_response_blocks_leak(self):
        leaked_text = "The answer is x = 3 or x = 4."
        sanitized = self.engine.sanitize_response(leaked_text, "x = 3 or x = 4")
        self.assertNotIn("x = 3 or x = 4", sanitized)
        self.assertIn("Let's pause and analyze", sanitized)

if __name__ == "__main__":
    unittest.main()
