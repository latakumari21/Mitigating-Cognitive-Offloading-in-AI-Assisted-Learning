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

    def build_prompt(self, user_question: str, student_code: str = "") -> str:
        code_block = f"\n\nStudent Code:\n```\n{student_code.strip()}\n```" if student_code and student_code.strip() else ""
        return f"{self.system_instructions}\n\nStudent Question: {user_question}{code_block}\n\nFull Solution:"
