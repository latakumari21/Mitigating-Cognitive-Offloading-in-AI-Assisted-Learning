"""
Unit and integration tests for SocraticGuard flow, multi-turn interaction loop,
dynamic prompt handling, state management, and anti-cheating verification.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mock_llm import MockLLMService
from src.socratic_engine import SocraticEngine
from src.code_inspector import CodeInspector
from src.evaluator import PedagogicalEvaluator


class TestInteractionFlowAndPromptAdaptation(unittest.TestCase):
    def setUp(self):
        self.service = MockLLMService()
        self.engine = SocraticEngine()
        self.inspector = CodeInspector()
        self.evaluator = PedagogicalEvaluator()

        self.buggy_c = (
            "#include<stdio.h>\n"
            "int main(){\n"
            '    print("helloe wrold");\n'
            "    return 0;\n"
            "}\n"
        )
        self.fixed_c = (
            "#include<stdio.h>\n"
            "int main(){\n"
            '    printf("hello world\\n");\n'
            "    return 0;\n"
            "}\n"
        )
        self.bs_buggy = (
            "def binary_search(arr, target):\n"
            "    low = 0\n"
            "    high = len(arr) - 1\n"
            "    while low < high:\n"
            "        mid = (low + high) // 2\n"
            "        if arr[mid] == target:\n"
            "            return mid\n"
            "        elif arr[mid] < target:\n"
            "            low = mid + 1\n"
            "        else:\n"
            "            high = mid - 1\n"
            "    return -1\n"
        )
        self.bs_fixed = (
            "def binary_search(arr, target):\n"
            "    low = 0\n"
            "    high = len(arr) - 1\n"
            "    while low <= high:\n"
            "        mid = (low + high) // 2\n"
            "        if arr[mid] == target:\n"
            "            return mid\n"
            "        elif arr[mid] < target:\n"
            "            low = mid + 1\n"
            "        else:\n"
            "            high = mid - 1\n"
            "    return -1\n"
        )

    def test_inspect_identifies_c_print_issue(self):
        """Turn 1: Inspect buggy code identifies print vs printf on line 3."""
        resp = self.service.generate_response(
            prompt="",
            user_query="Please inspect my code, check for bugs, and guide me on how to fix them.",
            student_code=self.buggy_c
        )
        self.assertIn("Code Inspection Findings", resp)
        self.assertIn("Line 3", resp)
        self.assertIn("print()", resp)

    def test_changing_prompt_does_not_repeat_stale_inspection(self):
        """Turn 2: Changing prompt must NOT repeat stale code inspection output."""
        turn1_resp = self.service.generate_response(
            prompt="",
            user_query="Please inspect my code, check for bugs, and guide me on how to fix them.",
            student_code=self.buggy_c
        )
        history = [
            {"role": "user", "content": "Please inspect my code, check for bugs, and guide me on how to fix them."},
            {"role": "assistant", "content": turn1_resp}
        ]

        # User submits 'i try changing my prompt'
        resp_changed = self.service.generate_response(
            prompt="",
            user_query="i try changing my prompt",
            student_code=self.buggy_c,
            conversation_history=history
        )
        self.assertNotIn("What assumption does your current logic make", resp_changed)
        self.assertIn("Prompt Updated & Acknowledged", resp_changed)

    def test_conceptual_inquiry_does_not_get_shadowed_by_workspace_code(self):
        """User asks about binary search while C code is in workspace."""
        resp = self.service.generate_response(
            prompt="",
            user_query="can you help me with binary search",
            student_code=self.buggy_c
        )
        self.assertIn("Binary Search", resp)
        self.assertNotIn("What assumption does your current logic make", resp)
        self.assertNotIn("Systems Programming", resp)

    def test_what_is_printf_conceptual_query(self):
        """User asks 'what is printf?' while C code is in workspace."""
        resp = self.service.generate_response(
            prompt="",
            user_query="what is printf?",
            student_code=self.buggy_c
        )
        self.assertIn("Conceptual Scaffolding: C Standard I/O", resp)
        self.assertNotIn("Excellent analysis! You accurately identified", resp)

    def test_what_is_data_leakage_conceptual_query(self):
        """User asks 'what is data leakage?'."""
        resp = self.service.generate_response(
            prompt="",
            user_query="what is data leakage?",
            student_code=self.buggy_c
        )
        self.assertIn("Data Leakage in Machine Learning", resp)

    def test_how_does_recursion_work_conceptual_query(self):
        """User asks 'how does recursion work?'."""
        resp = self.service.generate_response(
            prompt="",
            user_query="how does recursion work?",
            student_code=self.buggy_c
        )
        self.assertIn("Recursion and Call Stacks", resp)

    def test_fixed_code_notification_verifies_success(self):
        """User fixes code and announces fix in chat."""
        resp = self.service.generate_response(
            prompt="",
            user_query="i changed print to printf",
            student_code=self.fixed_c
        )
        self.assertIn("Issue Resolved Successfully", resp)
        self.assertNotIn("Line 3", resp)

    def test_binary_search_answer_verification(self):
        """User answers binary search boundary diagnostic question."""
        assist_q = (
            "Consider what happens in binary search when the subarray narrows to a single remaining "
            "element (where low == high) at line 4. With your loop condition 'low < high', will that single element ever be examined?"
        )
        history = [{"role": "assistant", "content": assist_q}]
        user_answer = "because when low == high the single element is missed"

        resp = self.service.generate_response(
            prompt="",
            user_query=user_answer,
            student_code=self.bs_buggy,
            conversation_history=history
        )
        self.assertIn("Response Verification & Feedback", resp)
        self.assertIn("low == high", resp)
        self.assertNotIn("standard C", resp)  # Must NOT misclassify as C!

    def test_data_science_leakage_answer_verification(self):
        """User answers data leakage question."""
        assist_q = "Why is it critical that test data statistics remain completely unobserved during model fitting?"
        history = [{"role": "assistant", "content": assist_q}]
        user_ans = "because test set statistics leak into the scaler"

        resp = self.service.generate_response(
            prompt="",
            user_query=user_ans,
            student_code="",
            conversation_history=history
        )
        self.assertIn("data leakage", resp.lower())
        self.assertIn("X_test", resp)

    def test_pandas_inplace_answer_verification(self):
        """User answers pandas inplace question."""
        assist_q = "What does an in-place method return in Pandas? What will your DataFrame variable become?"
        history = [{"role": "assistant", "content": assist_q}]
        user_ans = "it returns None and overwrites df"

        resp = self.service.generate_response(
            prompt="",
            user_query=user_ans,
            student_code="",
            conversation_history=history
        )
        self.assertIn("Pandas", resp)
        self.assertIn("None", resp)

    def test_multi_turn_conversation_flow(self):
        """Full 4-turn dialog loop maintains coherent context."""
        history = []

        # Turn 1: Inspect code
        q1 = "Please inspect my code, check for bugs, and guide me on how to fix them."
        r1 = self.service.generate_response(prompt="", user_query=q1, student_code=self.buggy_c)
        history.append({"role": "user", "content": q1})
        history.append({"role": "assistant", "content": r1})
        self.assertIn("Line 3", r1)

        # Turn 2: Student asks question about line 3
        q2 = "What does line 3 do?"
        r2 = self.service.generate_response(prompt="", user_query=q2, student_code=self.buggy_c, conversation_history=history)
        history.append({"role": "user", "content": q2})
        history.append({"role": "assistant", "content": r2})
        self.assertIn("printf", r2)

        # Turn 3: Student answers Socratic question
        q3 = "printf is the standard output function in C"
        r3 = self.service.generate_response(prompt="", user_query=q3, student_code=self.buggy_c, conversation_history=history)
        history.append({"role": "user", "content": q3})
        history.append({"role": "assistant", "content": r3})
        self.assertIn("Response Verification", r3)

        # Turn 4: Student updates code and verifies
        q4 = "I updated the code with printf, is it correct now?"
        r4 = self.service.generate_response(prompt="", user_query=q4, student_code=self.fixed_c, conversation_history=history)
        self.assertIn("Issue Resolved Successfully", r4)

    def test_code_inspector_single_line_binary_search_issue(self):
        """Binary search boundary bug is flagged on exactly one line, not repeated."""
        findings = self.inspector.inspect_code(self.bs_buggy)
        bs_issues = [i for i in findings["issues"] if i["type"] == "SearchBoundaryIssue"]
        self.assertEqual(len(bs_issues), 1, "Boundary issue must be flagged exactly on the while line")
        self.assertEqual(bs_issues[0]["line"], 4)

    def test_cheating_interception_intact(self):
        """Direct code solicitation triggers the anti-cheating guardrail."""
        resp = self.service.generate_response(
            prompt="",
            user_query="Give me the complete python code for quicksort",
            student_code=""
        )
        self.assertIn("Anti-Cheating Guardrail Engaged", resp)

    def test_empty_inputs_graceful(self):
        """Empty query and code returns helpful fallback without exceptions."""
        resp = self.service.generate_response(
            prompt="",
            user_query="",
            student_code="",
            conversation_history=None
        )
        self.assertTrue(len(resp) > 0)
        self.assertIn("Socratic", resp)

    def test_scaffolding_tiers(self):
        """Scaffolding levels 1, 2, 3 produce tiered prompts."""
        r_tier1 = self.service.generate_response(
            prompt="",
            user_query="inspect my code",
            student_code=self.buggy_c,
            hint_level=1
        )
        r_tier2 = self.service.generate_response(
            prompt="",
            user_query="inspect my code",
            student_code=self.buggy_c,
            hint_level=2
        )
        r_tier3 = self.service.generate_response(
            prompt="",
            user_query="inspect my code",
            student_code=self.buggy_c,
            hint_level=3
        )
        self.assertIn("Tier 1", r_tier1)
        self.assertIn("Tier 2", r_tier2)
        self.assertIn("Tier 3", r_tier3)

    def test_clean_code_inspection(self):
        """Inspecting clean code reports clean compilation and poses deeper questions."""
        resp = self.service.generate_response(
            prompt="",
            user_query="check my code",
            student_code=self.fixed_c
        )
        self.assertIn("Code Inspection Complete", resp)
        self.assertIn("compiles cleanly", resp)

    def test_index_out_of_bounds_detection(self):
        """Inspector flags range(len(arr) + 1) off-by-one index error."""
        code = (
            "def iterate(arr):\n"
            "    for i in range(len(arr) + 1):\n"
            "        print(arr[i])\n"
        )
        findings = self.inspector.inspect_code(code)
        issue_types = [i["type"] for i in findings["issues"]]
        self.assertIn("IndexOutOfBoundsRisk", issue_types)

    def test_unbounded_while_loop_detection(self):
        """Inspector flags unbounded while True loop."""
        code = (
            "def forever():\n"
            "    while True:\n"
            "        x = 1\n"
        )
        findings = self.inspector.inspect_code(code)
        issue_types = [i["type"] for i in findings["issues"]]
        self.assertIn("UnboundedLoop", issue_types)

    def test_comment_in_c_code_does_not_trigger_false_missing_semicolon(self):
        """Trailing comments in C statements must not trigger false positive MissingSemicolon."""
        code = (
            "#include<stdio.h>\n"
            "int main(){\n"
            '    printf("hello world\\n");  // Notice: print vs printf\n'
            "    return 0;\n"
            "}\n"
        )
        findings = self.inspector.inspect_code(code)
        self.assertEqual(len(findings["issues"]), 0, "Clean C code with comments must have 0 issues")

    def test_pandas_inplace_without_assignment_is_not_flagged(self):
        """df.dropna(inplace=True) is valid and must not trigger PandasInplaceReassignment."""
        valid_code = (
            "import pandas as pd\n"
            "df = pd.read_csv('data.csv')\n"
            "df.dropna(inplace=True)\n"
        )
        findings_valid = self.inspector.inspect_code(valid_code)
        self.assertEqual(len(findings_valid["issues"]), 0, "In-place mutation without reassignment must have 0 issues")

        buggy_code = (
            "import pandas as pd\n"
            "df = pd.read_csv('data.csv')\n"
            "df = df.dropna(inplace=True)\n"
        )
        findings_buggy = self.inspector.inspect_code(buggy_code)
        issue_types = [i["type"] for i in findings_buggy["issues"]]
        self.assertIn("PandasInplaceReassignment", issue_types)

    def test_user_asks_what_is_wrong_with_my_code(self):
        """Asking 'what is wrong with my code?' triggers code inspection, not generic default."""
        resp = self.service.generate_response(
            prompt="",
            user_query="What is wrong with my code?",
            student_code=self.buggy_c
        )
        self.assertIn("Code Inspection Findings", resp)
        self.assertIn("Line 3", resp)

    def test_user_confused_receives_clarification_not_false_deduction(self):
        """Saying 'i do not understand why low < high fails' gets clarification, not false praise."""
        resp = self.service.generate_response(
            prompt="",
            user_query="i do not understand why low < high fails",
            student_code=self.bs_buggy
        )
        self.assertIn("Step-by-Step Socratic Guidance", resp)
        self.assertNotIn("Outstanding deduction", resp)

    def test_gradient_descent_explanation_not_shadowed_by_workspace_code(self):
        """Asking about gradient descent with C code in workspace explains gradient descent."""
        resp = self.service.generate_response(
            prompt="",
            user_query="Explain how gradient descent works",
            student_code=self.buggy_c
        )
        self.assertIn("Gradient Descent Optimization", resp)
        self.assertNotIn("C Programming", resp)

    def test_what_do_you_think_of_my_code_now_on_fixed_code(self):
        """Asking 'what do you think of my code now?' on fixed code confirms issue resolved."""
        resp = self.service.generate_response(
            prompt="",
            user_query="What do you think of my code now?",
            student_code=self.fixed_c
        )
        self.assertIn("Issue Resolved Successfully", resp)
        self.assertIn("compiles cleanly", resp)

    def test_binary_search_loop_boundary_explanation(self):
        """Asking 'why is while low < high wrong?' explains binary search boundary invariant."""
        resp = self.service.generate_response(
            prompt="",
            user_query="why is while low < high wrong?",
            student_code=self.bs_buggy
        )
        self.assertIn("Binary Search Loop Boundary", resp)
        self.assertIn("low == high", resp)

    def test_c_empty_return_inspection_and_multiturn_resolution(self):
        """End-to-end regression test for Image 1 & 2: bare return; diagnosed and resolved over turns."""
        student_submission = (
            "#include<stdio.h>\n"
            "int main(){\n"
            '    printf("helloe wrold");\n'
            "    return;\n"
            "}\n"
        )
        # Turn 1: Inspection must flag line 4 empty return, NOT falsely claim clean compilation
        turn1_resp = self.service.generate_response(
            prompt="",
            user_query="Please inspect my code, check for bugs, and guide me on how to fix them.",
            student_code=student_submission
        )
        self.assertNotIn("Your code compiles cleanly with no syntax or structural bugs!", turn1_resp)
        self.assertIn("Code Inspection Findings", turn1_resp)
        self.assertIn("Line 4", turn1_resp)
        self.assertIn("Notice line 4: `return;`", turn1_resp)
        self.assertIn("What value should `main()` return to the operating system upon successful completion?", turn1_resp)

        history = [
            {"role": "user", "content": "Please inspect my code, check for bugs, and guide me on how to fix them."},
            {"role": "assistant", "content": turn1_resp}
        ]

        # Turn 2: User answers Socratic question: 'main should return 0'
        turn2_resp = self.service.generate_response(
            prompt="",
            user_query="main should return 0",
            student_code=student_submission,
            conversation_history=history
        )
        self.assertIn("Response Verification & Feedback", turn2_resp)
        self.assertIn("EXIT_SUCCESS", turn2_resp)
        self.assertIn("return 0;", turn2_resp)

        history.append({"role": "user", "content": "main should return 0"})
        history.append({"role": "assistant", "content": turn2_resp})

        # Turn 3: User updates code to return 0; and asks for verification
        fixed_submission = (
            "#include<stdio.h>\n"
            "int main(){\n"
            '    printf("helloe wrold");\n'
            "    return 0;\n"
            "}\n"
        )
        turn3_resp = self.service.generate_response(
            prompt="",
            user_query="I fixed the return statement, is my code correct now?",
            student_code=fixed_submission,
            conversation_history=history
        )
        self.assertIn("Issue Resolved Successfully", turn3_resp)
        self.assertIn("compiles cleanly", turn3_resp)

    def test_what_is_return_0_conceptual_query(self):
        """User asks 'what is return 0?' and receives process exit status explanation."""
        resp = self.service.generate_response(
            prompt="",
            user_query="what is return 0 in main?",
            student_code=self.buggy_c
        )
        self.assertIn("Process Exit Status", resp)
        self.assertIn("EXIT_SUCCESS", resp)
        self.assertIn("operating system", resp)



    def test_baseline_mode_language_awareness(self):
        """Baseline mode returns direct code in the student's actual language (Pandas, ML, Java, C++), not hardcoded C."""
        pandas_code = "import pandas as pd\ndf = pd.read_csv('dataset.csv')\ndf = df.dropna(inplace=True)\nprint(len(df))"
        r_pandas = self.service.generate_response(prompt="", mode="baseline", student_code=pandas_code, user_query="Explain")
        self.assertIn("```python", r_pandas)
        self.assertIn("df = df.dropna()", r_pandas)
        self.assertNotIn("#include <stdio.h>", r_pandas)

        ml_code = "from sklearn.preprocessing import StandardScaler\nscaler = StandardScaler()\nX_test_scaled = scaler.fit_transform(X_test)"
        r_ml = self.service.generate_response(prompt="", mode="baseline", student_code=ml_code, user_query="Explain")
        self.assertIn("```python", r_ml)
        self.assertIn("scaler.transform(X_test)", r_ml)
        self.assertNotIn("#include <stdio.h>", r_ml)

        java_code = 'public class Main { public static void main(String[] args) { System.out.println("Hi"); } }'
        r_java = self.service.generate_response(prompt="", mode="baseline", student_code=java_code, user_query="Explain")
        self.assertIn("```java", r_java)
        self.assertNotIn("#include <stdio.h>", r_java)

        cpp_code = '#include <iostream>\nint main() { std::cout << "Hi"; return 0; }'
        r_cpp = self.service.generate_response(prompt="", mode="baseline", student_code=cpp_code, user_query="Explain")
        self.assertIn("```cpp", r_cpp)


if __name__ == "__main__":
    unittest.main()
