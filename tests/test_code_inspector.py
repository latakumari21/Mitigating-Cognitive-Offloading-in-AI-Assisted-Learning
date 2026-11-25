"""
Unit tests for the CodeInspector and Anti-Cheating Diagnostic Module.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.code_inspector import CodeInspector

class TestCodeInspector(unittest.TestCase):
    def setUp(self):
        self.inspector = CodeInspector()

    def test_detects_cheating_requests(self):
        cheating_queries = [
            "Give me the code for binary search",
            "Write the full solution for this LeetCode problem",
            "Solve this assignment for me please",
            "Just give the code",
            "Can you write the complete python script for data cleaning"
        ]
        for query in cheating_queries:
            self.assertTrue(
                self.inspector.is_cheating_or_solution_request(query),
                f"Failed to flag cheating request: {query}"
            )

    def test_allows_conceptual_queries(self):
        honest_queries = [
            "Why is quicksort O(n log n) on average?",
            "How does backpropagation update weights?",
            "What is the difference between L1 and L2 regularization?"
        ]
        for query in honest_queries:
            self.assertFalse(
                self.inspector.is_cheating_or_solution_request(query),
                f"Incorrectly flagged honest question: {query}"
            )

    def test_inspects_syntax_errors(self):
        buggy_code = "def bad_func(x)\n    return x + 1"
        findings = self.inspector.inspect_code(buggy_code)
        self.assertFalse(findings["syntax_valid"])
        self.assertIsNotNone(findings["syntax_error"])
        self.assertIn("missing or misplaced", findings["issues"][0]["diagnostic_question"])

    def test_detects_data_leakage(self):
        ml_code = (
            "from sklearn.preprocessing import StandardScaler\n"
            "scaler = StandardScaler()\n"
            "X_train_s = scaler.fit_transform(X_train)\n"
            "X_test_s = scaler.fit_transform(X_test)\n"
        )
        findings = self.inspector.inspect_code(ml_code)
        self.assertEqual(findings["detected_domain"], "data_science")
        issue_types = [i["type"] for i in findings["issues"]]
        self.assertIn("DataLeakage", issue_types)

    def test_detects_pandas_inplace_reassignment(self):
        pd_code = "df = df.dropna(inplace=True)"
        findings = self.inspector.inspect_code(pd_code)
        issue_types = [i["type"] for i in findings["issues"]]
        self.assertIn("PandasInplaceReassignment", issue_types)

    def test_sanitize_code_leakage_replaces_full_solution(self):
        leaked_response = (
            "Here is the function you requested:\n"
            "```python\n"
            "def binary_search(arr, target):\n"
            "    low = 0\n"
            "    high = len(arr) - 1\n"
            "    while low <= high:\n"
            "        mid = (low + high) // 2\n"
            "        if arr[mid] == target:\n"
            "            return mid\n"
            "    return -1\n"
            "```"
        )
        sanitized = self.inspector.sanitize_code_leakage(leaked_response)
        self.assertNotIn("low = 0", sanitized)
        self.assertIn("Direct Solution Hidden to Protect Learning", sanitized)

    def test_allows_code_explanation_queries(self):
        explanation_queries = [
            "explain this code",
            "can you explain how this works",
            "explain it to me please"
        ]
        for query in explanation_queries:
            self.assertFalse(
                self.inspector.is_cheating_or_solution_request(query),
                f"Explanation query incorrectly flagged as cheating: {query}"
            )

    def test_verifies_student_answer_response(self):
        from src.mock_llm import MockLLMService
        service = MockLLMService()
        student_answer = "1.It is using C language 2.it does not take any input it is just displaying hello world"
        response = service.generate_response(
            prompt=f"Student Inquiry: {student_answer}",
            mode="socratic",
            user_query=student_answer
        )
        self.assertIn("Response Verification", response)
        self.assertIn("C", response)
        self.assertIn("stdio", response)

    def test_detects_c_print_vs_printf_bug(self):
        c_code = (
            "#include<stdio.h>\n"
            "int main(){\n"
            'print("helloe wrold");\n'
            "return 0;\n"
            "}\n"
        )
        findings = self.inspector.inspect_code(c_code)
        self.assertEqual(findings["language"], "c")
        issue_types = [i["type"] for i in findings["issues"]]
        self.assertIn("InvalidCFunction", issue_types)
        self.assertIn("printf", findings["issues"][0]["desc"])
        self.assertIn("formatted output function", findings["issues"][0]["diagnostic_question"])

    def test_check_my_code_generates_socratic_inspection(self):
        from src.mock_llm import MockLLMService
        service = MockLLMService()
        c_code = (
            "#include<stdio.h>\n"
            "int main(){\n"
            'print("helloe wrold");\n'
            "return 0;\n"
            "}\n"
        )
        response = service.generate_response(
            prompt="Student Inquiry: check my code",
            mode="socratic",
            student_code=c_code,
            user_query="check my code"
        )
        self.assertIn("Code Inspection Findings", response)
        self.assertIn("print()", response)
        self.assertIn("Diagnostic Question", response)

    def test_detects_empty_return_in_c_main(self):
        """Image 1 & 2 regression test: bare return; in int main() must be flagged as InvalidReturnInNonVoid."""
        c_code = (
            "#include<stdio.h>\n"
            "int main(){\n"
            '    printf("helloe wrold");\n'
            "    return;\n"
            "}\n"
        )
        findings = self.inspector.inspect_code(c_code)
        self.assertEqual(findings["language"], "c")
        self.assertFalse(findings["syntax_valid"])
        issue_types = [i["type"] for i in findings["issues"]]
        self.assertIn("InvalidReturnInNonVoid", issue_types)

        issue = next(i for i in findings["issues"] if i["type"] == "InvalidReturnInNonVoid")
        self.assertEqual(issue["line"], 4)
        expected_question = (
            "Notice line 4: `return;`. In C, your `main()` function is declared with return type `int`. "
            "What value should `main()` return to the operating system upon successful completion?"
        )
        self.assertEqual(issue["diagnostic_question"], expected_question)

    def test_mock_llm_c_empty_return_generates_socratic_question(self):
        """Verify MockLLMService produces targeted Socratic clue for return; instead of false clean pass."""
        from src.mock_llm import MockLLMService
        service = MockLLMService()
        c_code = (
            "#include<stdio.h>\n"
            "int main(){\n"
            '    printf("helloe wrold");\n'
            "    return;\n"
            "}\n"
        )
        response = service.generate_response(
            prompt="Student Inquiry: check my code",
            mode="socratic",
            student_code=c_code,
            user_query="check my code"
        )
        self.assertNotIn("Your code compiles cleanly with no syntax or structural bugs!", response)
        self.assertIn("Notice line 4: `return;`", response)
        self.assertIn("What value should `main()` return to the operating system upon successful completion?", response)

    def test_detects_missing_return_in_c_main(self):
        """Detects missing return statement when int main() lacks return entirely."""
        c_code = (
            "#include<stdio.h>\n"
            "int main(){\n"
            '    printf("hello world\\n");\n'
            "}\n"
        )
        findings = self.inspector.inspect_code(c_code)
        issue_types = [i["type"] for i in findings["issues"]]
        self.assertIn("MissingCReturn", issue_types)

    def test_detects_unclosed_braces_and_parentheses(self):
        """Detects mismatched/unclosed braces and parentheses in C/C++."""
        code_brace = "#include<stdio.h>\nint main(){\n    printf(\"test\");\n"
        findings_brace = self.inspector.inspect_code(code_brace)
        self.assertIn("UnclosedBrace", [i["type"] for i in findings_brace["issues"]])

        code_paren = "#include<stdio.h>\nint main(){\n    printf(\"test\";\n    return 0;\n}"
        findings_paren = self.inspector.inspect_code(code_paren)
        self.assertIn("MismatchedParentheses", [i["type"] for i in findings_paren["issues"]])

    def test_detects_format_specifier_mismatch(self):
        """Detects count and type mismatches in printf format strings."""
        code_count = (
            "#include<stdio.h>\n"
            "int main(){\n"
            '    int x = 10;\n'
            '    printf("%d %d\\n", x);\n'
            "    return 0;\n"
            "}\n"
        )
        findings_count = self.inspector.inspect_code(code_count)
        self.assertIn("FormatSpecifierMismatch", [i["type"] for i in findings_count["issues"]])

        code_type = (
            "#include<stdio.h>\n"
            "int main(){\n"
            '    printf("%d\\n", "hello");\n'
            "    return 0;\n"
            "}\n"
        )
        findings_type = self.inspector.inspect_code(code_type)
        self.assertIn("FormatSpecifierMismatch", [i["type"] for i in findings_type["issues"]])

    def test_detects_missing_c_headers(self):
        """Detects usage of standard functions without proper header inclusion."""
        code = (
            "int main(){\n"
            "    char *p = malloc(100);\n"
            "    return 0;\n"
            "}\n"
        )
        findings = self.inspector.inspect_code(code)
        issue_types = [i["type"] for i in findings["issues"]]
        self.assertIn("MissingCHeader", issue_types)

    def test_detects_uninitialized_variable(self):
        """Detects reading an uninitialized local variable."""
        code = (
            "#include<stdio.h>\n"
            "int main(){\n"
            "    int total;\n"
            '    printf("%d", total);\n'
            "    return 0;\n"
            "}\n"
        )
        findings = self.inspector.inspect_code(code)
        self.assertIn("UninitializedVariable", [i["type"] for i in findings["issues"]])

    def test_detects_c_array_out_of_bounds(self):
        """Detects literal out-of-bounds indexing in C array declarations."""
        code = (
            "#include<stdio.h>\n"
            "int main(){\n"
            "    int arr[5];\n"
            "    arr[5] = 42;\n"
            "    return 0;\n"
            "}\n"
        )
        findings = self.inspector.inspect_code(code)
        self.assertIn("IndexOutOfBoundsRisk", [i["type"] for i in findings["issues"]])

    def test_detects_python_indentation_and_return_outside_function(self):
        """Detects IndentationError and ReturnOutsideFunction in Python."""
        code_indent = "def foo():\nreturn 1"
        findings_indent = self.inspector.inspect_code(code_indent)
        self.assertIn("IndentationError", [i["type"] for i in findings_indent["issues"]])

        code_return = "x = 10\nreturn x"
        findings_return = self.inspector.inspect_code(code_return)
        self.assertIn("ReturnOutsideFunction", [i["type"] for i in findings_return["issues"]])

    def test_detects_chained_indexing_and_target_leakage(self):
        """Detects Pandas chained indexing and target leakage in data science code."""
        code_chained = (
            "import pandas as pd\n"
            "df = pd.read_csv('data.csv')\n"
            "df['A']['B'] = 100\n"
        )
        findings_chained = self.inspector.inspect_code(code_chained)
        self.assertIn("ChainedIndexing", [i["type"] for i in findings_chained["issues"]])

        code_leakage = (
            "import pandas as pd\n"
            "from sklearn.model_selection import train_test_split\n"
            "df = pd.read_csv('data.csv')\n"
            "X_train, X_test, y_train, y_test = train_test_split(df, df['target'])\n"
        )
        findings_leakage = self.inspector.inspect_code(code_leakage)
        self.assertIn("TargetLeakage", [i["type"] for i in findings_leakage["issues"]])

    def test_void_function_with_empty_return_is_valid(self):
        """Empty return; inside a void function is standard and must not be flagged as an error."""
        code = (
            "#include <stdio.h>\n"
            "void log_msg() {\n"
            "    return;\n"
            "}\n"
            "int main() {\n"
            "    log_msg();\n"
            "    return 0;\n"
            "}\n"
        )
        findings = self.inspector.inspect_code(code)
        issue_types = [i["type"] for i in findings["issues"]]
        self.assertNotIn("InvalidReturnInNonVoid", issue_types)

    def test_missing_return_in_main_with_other_functions(self):
        """When helper() returns a value but main() lacks return, main() must be flagged with MissingCReturn."""
        code = (
            "#include <stdio.h>\n"
            "int helper() {\n"
            "    return 1;\n"
            "}\n"
            "int main() {\n"
            "    helper();\n"
            "}\n"
        )
        findings = self.inspector.inspect_code(code)
        issue_types = [i["type"] for i in findings["issues"]]
        self.assertIn("MissingCReturn", issue_types)

    def test_empty_return_in_non_main_function(self):
        """Empty return; in non-void helper function must be flagged with helper's name."""
        code = (
            "#include <stdio.h>\n"
            "int compute() {\n"
            "    return;\n"
            "}\n"
            "int main() {\n"
            "    return 0;\n"
            "}\n"
        )
        findings = self.inspector.inspect_code(code)
        issue = next((i for i in findings["issues"] if i["type"] == "InvalidReturnInNonVoid"), None)
        self.assertIsNotNone(issue)
        self.assertIn("compute", issue["desc"])

    def test_multiline_printf_format_mismatch(self):
        """Multiline printf calls are parsed across linebreaks without false missing semicolon."""
        code = (
            "#include <stdio.h>\n"
            "int main() {\n"
            '    printf("Num: %d, Str: %s",\n'
            "           42);\n"
            "    return 0;\n"
            "}\n"
        )
        findings = self.inspector.inspect_code(code)
        issue_types = [i["type"] for i in findings["issues"]]
        self.assertIn("FormatSpecifierMismatch", issue_types)
        self.assertNotIn("MissingSemicolon", issue_types)

    def test_missing_semicolon_on_assignment(self):
        """Missing semicolon on variable assignment statements is detected."""
        code = (
            "#include <stdio.h>\n"
            "int main() {\n"
            "    int x = 5;\n"
            "    x = 10\n"
            "    return 0;\n"
            "}\n"
        )
        findings = self.inspector.inspect_code(code)
        issue_types = [i["type"] for i in findings["issues"]]
        self.assertIn("MissingSemicolon", issue_types)

    def test_comment_does_not_trigger_missing_header(self):
        """Comments referencing standard functions must not trigger false MissingCHeader."""
        code = (
            "#include <stdio.h>\n"
            "int main() {\n"
            "    // malloc could be used here\n"
            '    printf("hello");\n'
            "    return 0;\n"
            "}\n"
        )
        findings = self.inspector.inspect_code(code)
        issue_types = [i["type"] for i in findings["issues"]]
        self.assertNotIn("MissingCHeader", issue_types)

    def test_cin_initialization_prevents_uninitialized_variable(self):
        """Input streams like std::cin >> var count as initialization."""
        code = (
            "#include <iostream>\n"
            "int main() {\n"
            "    int x;\n"
            "    std::cin >> x;\n"
            "    int y = x + 1;\n"
            "    return 0;\n"
            "}\n"
        )
        findings = self.inspector.inspect_code(code)
        issue_types = [i["type"] for i in findings["issues"]]
        self.assertNotIn("UninitializedVariable", issue_types)

    def test_initialized_array_literal_out_of_bounds(self):
        """Initialized array literal declarations are checked for out-of-bounds indexing."""
        code = (
            "#include <stdio.h>\n"
            "int main() {\n"
            "    int arr[5] = {1, 2, 3, 4, 5};\n"
            "    arr[5] = 42;\n"
            "    return 0;\n"
            "}\n"
        )
        findings = self.inspector.inspect_code(code)
        issue_types = [i["type"] for i in findings["issues"]]
        self.assertIn("IndexOutOfBoundsRisk", issue_types)

    def test_python_ast_checks_mutable_default_and_bare_except(self):
        """Detects mutable defaults and bare except clauses in Python."""
        code_mutable = "def append_item(x, lst=[]):\n    lst.append(x)\n    return lst"
        findings_mutable = self.inspector.inspect_code(code_mutable)
        self.assertIn("MutableDefault", [i["type"] for i in findings_mutable["issues"]])

        code_except = "try:\n    x = 1 / 0\nexcept:\n    pass"
        findings_except = self.inspector.inspect_code(code_except)
        self.assertIn("BareExcept", [i["type"] for i in findings_except["issues"]])

if __name__ == "__main__":
    unittest.main()
