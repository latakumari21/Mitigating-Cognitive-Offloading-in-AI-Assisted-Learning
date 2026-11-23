"""
Socratic Scaffolding Engine for Mitigating Cognitive Offloading.
Provides pedagogical hints, diagnostic questions, and prevents answer leakage.
"""

from typing import Dict, Any, List

class SocraticEngine:
    def __init__(self, model_client=None):
        self.model_client = model_client
        self.system_instructions = (
            "You are an expert pedagogical tutor dedicated to deep student learning. "
            "CORE PRINCIPLE: Never provide the direct solution, final answer, or full code block. "
            "Instead, guide the learner through active inquiry using progressive scaffolding. "
            "Assess what the student understands, diagnose errors, and provide guiding questions."
        )

    def build_prompt(self, user_question: str, hint_level: int = 1, context: str = "") -> str:
        """
        Constructs a tiered scaffolding prompt based on hint level.
        Level 1: Conceptual probing and definition check.
        Level 2: Strategic guidance and structural formulas.
        Level 3: Targeted diagnostic correction of student reasoning.
        """
        scaffolding_tiers = {
            1: "Goal: Ask a foundational question to check the student's conceptual understanding without revealing methods.",
            2: "Goal: Point toward the relevant theorem, equation, or algorithmic strategy, prompting them to set it up.",
            3: "Goal: Provide a structural hint or point out a common pitfall, but leave the final execution to the student."
        }
        
        tier_goal = scaffolding_tiers.get(hint_level, scaffolding_tiers[1])
        
        prompt = (
            f"{self.system_instructions}\n\n"
            f"Current Pedagogical Objective (Level {hint_level}): {tier_goal}\n"
            f"Context: {context}\n"
            f"Student Inquiry: {user_question}\n\n"
            "Pedagogical Response:"
        )
        return prompt

    def detect_answer_leakage(self, response_text: str, ground_truth_answer: str) -> bool:
        """
        Inspects if the generated response prematurely reveals the ground truth answer.
        """
        if not ground_truth_answer:
            return False
            
        clean_ans = ground_truth_answer.strip().lower()
        clean_resp = response_text.strip().lower()
        
        if len(clean_ans) > 2 and clean_ans in clean_resp:
            return True
        return False

    def sanitize_response(self, response_text: str, ground_truth_answer: str) -> str:
        """
        Applies a guardrail filter if leakage is detected.
        """
        if self.detect_answer_leakage(response_text, ground_truth_answer):
            return (
                "Let's pause and analyze the problem step-by-step. "
                "Before jumping to the solution, what are the given values and relevant concepts?"
            )
        return response_text
