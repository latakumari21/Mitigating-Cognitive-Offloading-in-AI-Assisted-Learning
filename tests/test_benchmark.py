import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from src.socratic_engine import SocraticEngine
from src.baseline_engine import BaselineEngine
from src.evaluator import PedagogicalEvaluator
from src.mock_llm import MockLLMService

class TestBenchmarkPipeline(unittest.TestCase):
    def test_dataset_integrity(self):
        data_path = os.path.join(os.path.dirname(__file__), "..", "data", "benchmark_dataset.json")
        self.assertTrue(os.path.exists(data_path), "Benchmark dataset file must exist")
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data), 30, "Dataset must contain exactly 30 benchmark problems")
        for item in data:
            self.assertIn("id", item)
            self.assertIn("subject", item)
            self.assertIn("question", item)
            self.assertIn("answer", item)

    def test_end_to_end_socratic_flow(self):
        engine = SocraticEngine()
        llm = MockLLMService()
        evaluator = PedagogicalEvaluator()
        
        q = "Evaluate the definite integral of 2x dx from 1 to 4"
        ans = "15"
        
        prompt = engine.build_prompt(q, hint_level=1)
        resp = llm.generate_response(prompt, question_id="MATH-03", expected_ans=ans, mode="socratic")
        sanitized = engine.sanitize_response(resp, ans)
        
        leakage = evaluator.calculate_answer_leakage(sanitized, ans)
        self.assertEqual(leakage, 0.0)
        self.assertGreaterEqual(evaluator.estimate_blooms_taxonomy_level(sanitized), 3)

if __name__ == "__main__":
    unittest.main()
