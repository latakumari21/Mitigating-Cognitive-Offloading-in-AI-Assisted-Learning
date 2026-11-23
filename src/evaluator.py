"""
Evaluation Metrics Framework for Pedagogical Scaffolding and Cognitive Demand.
"""

import re
from typing import Dict, Any

class PedagogicalEvaluator:
    @staticmethod
    def calculate_answer_leakage(response: str, expected_answer: str) -> float:
        """
        Returns 1.0 if answer is leaked, 0.0 otherwise.
        """
        if not expected_answer or not response:
            return 0.0
            
        target = expected_answer.strip().lower()
        text = response.strip().lower()
        
        # Check direct substring inclusion
        if target in text:
            return 1.0
            
        # Check numerical match if answer is purely numeric
        num_match = re.findall(r"[-+]?\d*\.\d+|\d+", target)
        if num_match:
            for n in num_match:
                if re.search(rf"\b{re.escape(n)}\b", text):
                    return 1.0
        return 0.0

    @staticmethod
    def estimate_blooms_taxonomy_level(response: str) -> int:
        """
        Estimates the cognitive demand level of the response on Bloom's Revised Taxonomy (1 to 6):
        1: Remember (direct recall, facts)
        2: Understand (explain, summarize)
        3: Apply (implement, calculate)
        4: Analyze (diagnose, contrast, compare, probe why)
        5: Evaluate (critique, justify, assess)
        6: Create (design, formulate, hypothesize)
        """
        text = response.lower()
        
        # Level 4-5 markers (High cognitive demand: Socratic inquiry, analytical prompts)
        eval_analyze_markers = [
            "why do you think", "what happens if", "how would you justify",
            "what is the difference", "diagnose", "compare", "under what condition",
            "what reasoning", "how does this relate", "what step stalled"
        ]
        
        # Level 2-3 markers (Medium cognitive demand)
        apply_understand_markers = [
            "can you identify", "which formula applies", "set up the equation",
            "explain the meaning", "recall the rule", "define"
        ]
        
        # Level 1 markers (Low cognitive demand / Direct answers)
        low_markers = [
            "the answer is", "here is the code", "here is the solution",
            "equals", "the result is", "step 1: do this"
        ]
        
        for marker in eval_analyze_markers:
            if marker in text:
                return 4
                
        for marker in apply_understand_markers:
            if marker in text:
                return 3
                
        for marker in low_markers:
            if marker in text:
                return 1
                
        # Default assessment based on question density
        if "?" in text:
            return 3
        return 2

    @staticmethod
    def compute_pedagogical_alignment(leakage: float, blooms_level: int) -> float:
        """
        Computes composite pedagogical score (1.0 to 5.0).
        Higher is better (low leakage + high cognitive demand).
        """
        base = blooms_level * 0.8
        penalty = 3.0 if leakage > 0.5 else 0.0
        score = max(1.0, min(5.0, base - penalty + 1.5))
        return round(score, 2)
