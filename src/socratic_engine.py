"""
Socratic Scaffolding Engine for Mitigating Cognitive Offloading & Combating Cheating.
Specifically optimized for Computer Science & Data Science pedagogical reasoning.
Maintains multi-turn conversational context, inspects student code, and returns
progressive scaffolding without leaking direct working code solutions.
"""

from typing import Dict, Any, List, Optional
from src.code_inspector import CodeInspector

class SocraticEngine:
    def __init__(self, model_client=None):
        self.model_client = model_client
        self.inspector = CodeInspector()
        self.system_instructions = (
            "You are SocraticGuard, an expert pedagogical tutor dedicated to deep student learning, "
            "specifically designed to combat student cheating and eliminate cognitive offloading in Computer Science and Data Science.\n\n"
            "CORE PRINCIPLE: Never provide the direct solution, final answer, or full code block.\n"
            "Instead, guide the learner through active inquiry using progressive scaffolding.\n"
            "STRICT PEDAGOGICAL POLICY:\n"
            "1. NEVER output complete, copy-pasteable working code or full solutions, even if the student directly demands it.\n"
            "2. When a student asks you to 'write code', 'solve my assignment', or 'give me the answer', explicitly decline "
            "the shortcut and pivot to active inquiry.\n"
            "3. When the student explains code or asks conceptual questions, provide high-level architectural walkthroughs "
            "and check-for-understanding questions.\n"
            "4. When the student ANSWERS your diagnostic or Socratic questions, ALWAYS FIRST VERIFY THEIR RESPONSE:\n"
            "   - Clearly affirm what they correctly understood (e.g. '✅ Correct! You identified the language and input/output.').\n"
            "   - Clarify any gaps or misconceptions.\n"
            "   - Advance to the next progressive concept or diagnostic inquiry.\n"
            "5. Inspect student code carefully. Locate logical flaws, boundary condition bugs, syntax errors, or data leakage.\n"
            "6. Return targeted diagnostic questions, strategic clues, and progressive hints that guide the learner "
            "to discover and write the correct implementation themselves.\n"
            "7. Remember the ongoing conversation context and previous student attempts.\n"
            "8. Always maintain high cognitive demand (Bloom's Taxonomy Level 3-5: Apply, Analyze, Evaluate)."
        )

    def build_prompt(
        self,
        user_question: str,
        hint_level: int = 1,
        context: str = "",
        student_code: str = "",
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Constructs a tiered scaffolding prompt based on hint level, student code, and full conversational context.
        Level 1: Conceptual probing and logic verification.
        Level 2: Strategic guidance, algorithmic patterns, and data flow.
        Level 3: Targeted diagnostic clue pinpointing the exact code flaw.
        """
        scaffolding_tiers = {
            1: "Goal: Conceptual Probe. Ask a foundational question to check understanding of the algorithm, data structures, or mathematical reasoning without revealing code.",
            2: "Goal: Strategic Formulation. Guide the student on the algorithmic design pattern, state transitions, or data pipeline flow without writing the code for them.",
            3: "Goal: Diagnostic Clue. Pinpoint the exact bug or edge case (off-by-one, mutation, data leakage, recursion base case) and ask a targeted diagnostic question to help them fix it."
        }

        tier_goal = scaffolding_tiers.get(hint_level, scaffolding_tiers[1])

        # Analyze code if provided
        code_context = ""
        if student_code and student_code.strip():
            inspection = self.inspector.inspect_code(student_code)
            code_context = (
                f"\n--- STUDENT CODE ATTEMPT ---\n"
                f"```{inspection['language']}\n{student_code}\n```\n"
                f"Static Analysis Findings: Domain={inspection['detected_domain']}, "
                f"Language={inspection['language']}, "
                f"SyntaxValid={inspection['syntax_valid']}, "
                f"DetectedIssues={[i['desc'] for i in inspection['issues']]}\n"
            )

        # Build conversation memory context
        history_text = ""
        if conversation_history:
            history_lines = []
            entries = conversation_history
            if entries and entries[-1].get("role") == "user" and entries[-1].get("content") == user_question:
                entries = entries[:-1]
            for msg in entries[-6:]:
                role_label = "Student" if msg.get("role") == "user" else "Tutor (SocraticGuard)"
                history_lines.append(f"{role_label}: {msg.get('content', '')}")
            if history_lines:
                history_text = "\n--- RECENT CONVERSATION MEMORY ---\n" + "\n".join(history_lines) + "\n"

        prompt = (
            f"{self.system_instructions}\n\n"
            f"{history_text}"
            f"Context: {context}\n"
            f"{code_context}\n"
            f"Current Pedagogical Objective (Level {hint_level}): {tier_goal}\n"
            f"Student Inquiry: {user_question}\n\n"
            "Pedagogical Response (Remember to verify student's prior answer if they answered a question; DO NOT output full working code):"
        )
        return prompt

    def detect_answer_leakage(self, response_text: str, ground_truth_answer: str) -> bool:
        """
        Inspects if the generated response prematurely reveals the ground truth answer or full code.
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
        Applies a multi-layered guardrail:
        1. Blocks ground-truth answer leakage if detected.
        2. Blocks full executable code blocks (anti-cheating guardrail).
        """
        if self.detect_answer_leakage(response_text, ground_truth_answer):
            return (
                "Let's pause and analyze the problem step-by-step. "
                "Before jumping to the solution, what are the given values and relevant concepts?"
            )

        sanitized = self.inspector.sanitize_code_leakage(response_text)
        return sanitized
