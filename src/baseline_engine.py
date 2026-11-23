"""
Baseline Direct Response Engine representing conventional unconstrained LLM behavior.
"""

class BaselineEngine:
    def __init__(self, model_client=None):
        self.model_client = model_client
        self.system_instructions = (
            "You are a helpful academic AI assistant. "
            "Provide the complete, direct, and explicit solution to the student's question immediately."
        )

    def build_prompt(self, user_question: str) -> str:
        return f"{self.system_instructions}\n\nStudent Question: {user_question}\n\nFull Solution:"
