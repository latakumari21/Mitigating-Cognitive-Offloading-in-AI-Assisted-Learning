"""
Mock LLM Provider for offline deterministic testing and benchmarking without external network dependencies.
"""

from typing import Dict, Any

class MockLLMService:
    def __init__(self):
        pass

    def generate_response(self, prompt: str, question_id: str = "", expected_ans: str = "", mode: str = "socratic") -> str:
        """
        Generates realistic responses for both Baseline and Socratic modes.
        """
        if mode == "baseline":
            return f"The complete and final solution is: {expected_ans}. Here is the full derivation for you to copy."
            
        # Socratic mode generates a scaffolding question without revealing the answer
        return (
            "What fundamental principle governs this phenomenon? "
            "Consider what variables are given in the problem statement and which formula connects them. "
            "How would you begin setting up the initial equation?"
        )
