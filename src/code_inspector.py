"""
Code Inspector & Anti-Cheating Diagnostic Module for Computer Science & Data Science.
Analyzes student code submissions in C, C++, Python, Java, and Data Science.
Detects solution requests/cheating patterns, pinpoints language-specific syntax/logic errors,
and produces pedagogical diagnostic questions and progressive clues.
"""

import ast
import re
from typing import Dict, Any, List, Optional, Tuple

class CodeInspector:
    def __init__(self):
        # Anti-cheating intent detection regex (requesting complete solutions/code)
        self.cheating_patterns = [
            r"\b(write|give|provide|show|generate)\s+(me\s+)?(the\s+)?(full|complete|entire|final|working)?\s*(python\s+|java\s+|sql\s+|c\+\+\s+|c\s+)?(code|solution|answer|script|implementation|program)\b",
            r"\b(solve|do)\s+(this|my)?\s*(assignment|homework|exam|lab|problem|leetcode|question)\s*(for\s+me)?\b",
            r"\bjust\s+(give|write)\s+the\s+code\b",
            r"\bcode\s+(this|it)\s+for\s+me\b",
            r"\bfix\s+my\s+code\s+and\s+(give|send)\s+it\s+back\b"
        ]

    def is_cheating_or_solution_request(self, user_query: str) -> bool:
        """
        Determines if the student is attempting to elicit direct code generation/solution cheating.
        Exempts educational inquiries like checking code, asking to explain code, asking concepts, or answering questions.
        """
        if not user_query:
            return False

        query_clean = user_query.strip().lower()

        # Educational requests: checking code, explaining code, asking concepts
        educational_markers = [
            "check my code", "check code", "inspect", "debug", "explain", "what does",
            "how does", "help me understand", "why does", "is this correct",
            "find the bug", "verify", "can you check", "look at my code", "why is this failing"
        ]
        is_educational = any(m in query_clean for m in educational_markers)
        if is_educational:
            # Only flag if they explicitly ask for full code generation to replace doing the work
            if not any(x in query_clean for x in ["write the code", "give me the code", "do my homework", "solve my assignment", "code this for me"]):
                return False

        # Answers to previous Socratic questions
        if re.match(r"^\s*(\d+[\.\)]|[a-zA-Z][\.\)])", query_clean) or any(p in query_clean for p in ["it is using", "it uses", "it prints", "because"]):
            return False

        for pattern in self.cheating_patterns:
            if re.search(pattern, query_clean):
                return True
        return False

    def inspect_code(self, code: str, language: str = "auto") -> Dict[str, Any]:
        """
        Inspects student code structure, syntax, and logic using static analysis.
        Supports Python, C/C++, Java, and Data Science.
        """
        findings = {
            "has_code": bool(code and code.strip()),
            "syntax_valid": True,
            "syntax_error": None,
            "detected_domain": "computer_science",
            "language": "python",
            "issues": [],
            "scaffolding_hints": {
                1: "",
                2: "",
                3: ""
            }
        }

        if not code or not code.strip():
            return findings

        code_lower = code.lower()

        # 1. Detect language & domain
        if any(kw in code for kw in ["#include", "printf(", "scanf(", "cout <<", "cin >>", "int main("]) or (("int main" in code or "#include" in code) and "{" in code):
            findings["detected_domain"] = "systems_programming"
            findings["language"] = "c"
        elif any(kw in code_lower for kw in ["pandas", "dataframe", "pd.", "sklearn", "train_test_split", "scaler", "confusion_matrix", "fit_transform", "numpy", "np.", "sns.", "plt.", "dropna", "fillna", "read_csv", "df."]):
            findings["detected_domain"] = "data_science"
            findings["language"] = "python"
        elif any(kw in code for kw in ["public class", "System.out.println", "public static void main"]):
            findings["detected_domain"] = "computer_science"
            findings["language"] = "java"
        else:
            findings["detected_domain"] = "computer_science"
            findings["language"] = "python"

        # 2. C/C++ Static Checks
        if findings["language"] == "c":
            c_issues = self._analyze_c_cpp(code)
            findings["issues"].extend(c_issues)
            if c_issues:
                findings["syntax_valid"] = not any(i.get("is_syntax", False) for i in c_issues)

        # 3. Python-specific AST static analysis
        elif findings["language"] == "python":
            try:
                tree = ast.parse(code)
                compile(code, "<string>", "exec")
                ast_issues = self._analyze_ast(tree, code)
                findings["issues"].extend(ast_issues)
            except SyntaxError as se:
                findings["syntax_valid"] = False
                findings["syntax_error"] = f"Line {se.lineno}: {se.msg}"
                msg_lower = (se.msg or "").lower()

                if isinstance(se, IndentationError):
                    issue_type = "IndentationError"
                    dq = (
                        f"Python relies on strict, consistent indentation to delimit code blocks. "
                        f"Line {se.lineno} has an indentation mismatch ('{se.msg}'). "
                        "How should this statement be indented relative to the enclosing block header?"
                    )
                elif "return" in msg_lower and "outside" in msg_lower:
                    issue_type = "ReturnOutsideFunction"
                    dq = (
                        f"At line {se.lineno}, a 'return' statement is placed outside of any function body. "
                        "In Python, where can 'return' statements be legally placed?"
                    )
                elif any(w in msg_lower for w in ["unclosed", "never closed", "unterminated", "closing parenthesis", "unmatched"]):
                    issue_type = "UnclosedDelimiter"
                    dq = (
                        f"Python detected an unclosed delimiter (quote, parenthesis, or bracket) around line {se.lineno} ('{se.msg}'). "
                        "Which opening delimiter is missing its matching closure?"
                    )
                else:
                    issue_type = "SyntaxError"
                    dq = (
                        f"Python flagged a syntax issue at line {se.lineno} ('{se.msg}'). "
                        "What punctuation or keyword is missing or misplaced right around this statement?"
                    )

                findings["issues"].append({
                    "type": issue_type,
                    "line": se.lineno,
                    "desc": f"{issue_type} at line {se.lineno}: {se.msg}",
                    "diagnostic_question": dq,
                    "is_syntax": True
                })

        # 4. Regex / Heuristic checks for CS & Data Science
        heuristic_issues = self._analyze_heuristics(code, findings["detected_domain"])
        findings["issues"].extend(heuristic_issues)

        # 5. Synthesize 3-tier scaffolding hints from issues
        findings["scaffolding_hints"] = self._synthesize_hints(findings, code)
        return findings

    def _analyze_c_cpp(self, code: str) -> List[Dict[str, Any]]:
        issues = []
        lines = code.split("\n")

        # Strip comments and string literals for brace/paren/token matching
        code_no_comments = re.sub(r"//.*", "", code)
        code_no_comments = re.sub(r"/\*.*?\*/", "", code_no_comments, flags=re.DOTALL)
        code_clean = re.sub(r'"(\\.|[^"\\])*"', '""', code_no_comments)
        code_clean = re.sub(r"'(\\.|[^'\\])*'", "''", code_clean)

        # 1. Unclosed braces '{}' check
        open_b = code_clean.count("{")
        close_b = code_clean.count("}")
        if open_b != close_b:
            issues.append({
                "type": "UnclosedBrace",
                "line": len(lines),
                "desc": f"Mismatched curly braces '{{}}' ({open_b} opening vs {close_b} closing).",
                "diagnostic_question": (
                    f"Check the curly braces '{{}}' across your code ({open_b} '{{' vs {close_b} '}}'). "
                    "Are all code blocks properly enclosed and closed?"
                ),
                "is_syntax": True
            })

        # 2. Mismatched parentheses '()' check
        open_p = code_clean.count("(")
        close_p = code_clean.count(")")
        if open_p != close_p:
            issues.append({
                "type": "MismatchedParentheses",
                "line": len(lines),
                "desc": f"Mismatched parentheses '()' ({open_p} opening vs {close_p} closing).",
                "diagnostic_question": (
                    f"Check the parentheses '()' across your code ({open_p} '(' vs {close_p} ')'). "
                    "Is every function call and condition properly closed?"
                ),
                "is_syntax": True
            })

        # 3. Function & Return tracking + Statement analysis
        current_func = None
        func_ret_type = None
        func_brace_depth = 0
        func_has_return = False
        brace_depth = 0
        paren_depth = 0
        bracket_depth = 0

        func_header_regex = re.compile(
            r"(?:^|[;}])\s*(?:(?:static|inline|extern)\s+)?([a-zA-Z_]\w*(?:\s*\*+|\s+))\s*([a-zA-Z_]\w*)\s*\([^;{()]*\)\s*(\{)?",
            re.MULTILINE
        )

        for idx, line in enumerate(lines, 1):
            line_str = line.strip()
            clean_stmt = re.sub(r"/\*.*?\*/", "", line_str)
            clean_stmt = re.sub(r"//.*$", "", clean_stmt).strip()
            if not clean_stmt:
                continue

            l_no_str = re.sub(r'"(\\.|[^"\\])*"', '""', clean_stmt)
            l_no_str = re.sub(r"'(\\.|[^'\\])*'", "''", l_no_str)

            # Check function start
            if current_func is None and not clean_stmt.endswith(";"):
                m = func_header_regex.search(clean_stmt)
                if m:
                    r_type = m.group(1).strip()
                    f_name = m.group(2).strip()
                    if f_name not in ["if", "while", "for", "switch"]:
                        current_func = f_name
                        func_ret_type = r_type
                        func_brace_depth = brace_depth
                        func_has_return = False

            # Detect bare return;
            bare_ret = re.search(r"(?:^|[;{}\s])return\s*;", clean_stmt)
            val_ret = re.search(r"(?:^|[;{}\s])return\s+([^;]+);", clean_stmt)

            if bare_ret:
                if current_func == "main" or (current_func is None and ("main(" in code or "int main" in code)):
                    issues.append({
                        "type": "InvalidReturnInNonVoid",
                        "line": idx,
                        "desc": "Empty 'return;' statement in non-void function 'int main()'.",
                        "diagnostic_question": (
                            f"Notice line {idx}: `return;`. In C, your `main()` function is declared with return type `int`. "
                            "What value should `main()` return to the operating system upon successful completion?"
                        ),
                        "is_syntax": True
                    })
                    func_has_return = True
                elif current_func and func_ret_type == "void":
                    # Valid in void functions!
                    pass
                elif current_func:
                    issues.append({
                        "type": "InvalidReturnInNonVoid",
                        "line": idx,
                        "desc": f"Empty 'return;' statement in non-void function '{current_func}()'.",
                        "diagnostic_question": (
                            f"Notice line {idx}: `return;`. In C, your `{current_func}()` function is declared with return type `{func_ret_type}`. "
                            f"What value should `{current_func}()` return?"
                        ),
                        "is_syntax": True
                    })
                    func_has_return = True
            elif val_ret:
                func_has_return = True

            # Detect print() instead of printf()
            if re.search(r"\bprint\s*\(", clean_stmt) and not re.search(r"\bprintf\s*\(", clean_stmt):
                issues.append({
                    "type": "InvalidCFunction",
                    "line": idx,
                    "desc": "Using 'print()' instead of 'printf()'.",
                    "diagnostic_question": (
                        f"Look at line {idx}: in C programming, 'print()' is not a recognized standard library function. "
                        "What is the standard formatted output function provided by '<stdio.h>'?"
                    ),
                    "is_syntax": True
                })

            # Check missing semicolon
            paren_delta = l_no_str.count("(") - l_no_str.count(")")
            bracket_delta = l_no_str.count("[") - l_no_str.count("]")
            brace_delta = l_no_str.count("{") - l_no_str.count("}")

            prev_paren_depth = paren_depth
            prev_bracket_depth = bracket_depth
            paren_depth += paren_delta
            bracket_depth += bracket_delta
            brace_depth += brace_delta

            if not l_no_str.startswith("#") and prev_paren_depth == 0 and prev_bracket_depth == 0 and paren_depth == 0 and bracket_depth == 0:
                if not l_no_str.endswith("{") and not l_no_str.endswith("}") and not l_no_str.endswith(";"):
                    if not re.search(r"\b(if|else|for|while|do|switch|case|default)\b", l_no_str) or re.search(r"=\s*", l_no_str):
                        if not re.search(r"\b(?:int|void|char|float|double|bool)\s+[a-zA-Z_]\w*\s*\([^)]*\)\s*$", l_no_str):
                            issues.append({
                                "type": "MissingSemicolon",
                                "line": idx,
                                "desc": f"Line {idx} may be missing a terminating semicolon ';'.",
                                "diagnostic_question": f"In C, every statement must conclude with a specific termination symbol. Check the end of line {idx}: what punctuation is required?",
                                "is_syntax": True
                            })

            # Function boundary
            if current_func and brace_depth <= func_brace_depth:
                if current_func == "main" and not func_has_return:
                    issues.append({
                        "type": "MissingCReturn",
                        "line": idx,
                        "desc": "'main' function missing return statement (expected 'return 0;').",
                        "diagnostic_question": "In standard C, what return status value should the 'main()' function return to indicate successful program execution to the OS?",
                        "is_syntax": True
                    })
                current_func = None
                func_ret_type = None
                func_has_return = False

        if current_func == "main" and not func_has_return:
            issues.append({
                "type": "MissingCReturn",
                "line": len(lines),
                "desc": "'main' function missing return statement (expected 'return 0;').",
                "diagnostic_question": "In standard C, what return status value should the 'main()' function return to indicate successful program execution to the OS?",
                "is_syntax": True
            })

        # 4. Format specifiers in printf/scanf (multiline safe)
        call_iter = re.finditer(r"\b(printf|scanf)\s*\(", code)
        for c_match in call_iter:
            func_name = c_match.group(1)
            start_pos = c_match.start()
            line_num = code[:start_pos].count("\n") + 1

            p_depth = 1
            pos = c_match.end()
            arg_chars = []
            in_str = False
            str_quote = None
            escape = False

            while pos < len(code) and p_depth > 0:
                ch = code[pos]
                if escape:
                    escape = False
                    arg_chars.append(ch)
                elif ch == "\\":
                    escape = True
                    arg_chars.append(ch)
                elif in_str:
                    if ch == str_quote:
                        in_str = False
                    arg_chars.append(ch)
                elif ch in ['"', "'"]:
                    in_str = True
                    str_quote = ch
                    arg_chars.append(ch)
                elif ch == "(":
                    p_depth += 1
                    arg_chars.append(ch)
                elif ch == ")":
                    p_depth -= 1
                    if p_depth > 0:
                        arg_chars.append(ch)
                else:
                    arg_chars.append(ch)
                pos += 1

            args_str = "".join(arg_chars).strip()
            fmt_match = re.match(r'^("(\\.|[^"\\])*")', args_str)
            if fmt_match:
                fmt_literal = fmt_match.group(1)
                remainder_args = args_str[fmt_match.end():].lstrip()
                if remainder_args.startswith(","):
                    remainder_args = remainder_args[1:].strip()
                else:
                    remainder_args = ""

                cleaned_fmt = fmt_literal.replace("%%", "")
                specifiers = re.findall(r"%[-+0 #]*\d*(?:\.\d+)?[diuoxXfFeEgGaAcspn]", cleaned_fmt)

                parsed_args = []
                if remainder_args:
                    cur = []
                    d = 0
                    for ch in remainder_args:
                        if ch in "([{":
                            d += 1
                            cur.append(ch)
                        elif ch in ")]}":
                            d -= 1
                            cur.append(ch)
                        elif ch == "," and d == 0:
                            parsed_args.append("".join(cur).strip())
                            cur = []
                        else:
                            cur.append(ch)
                    if cur:
                        parsed_args.append("".join(cur).strip())
                    parsed_args = [a for a in parsed_args if a]

                if len(specifiers) != len(parsed_args):
                    issues.append({
                        "type": "FormatSpecifierMismatch",
                        "line": line_num,
                        "desc": f"Format specifier count mismatch: {len(specifiers)} specifier(s) for {len(parsed_args)} argument(s).",
                        "diagnostic_question": (
                            f"Look at line {line_num}: your format string contains {len(specifiers)} format specifiers, "
                            f"but {len(parsed_args)} arguments are provided. How many arguments should match the format string?"
                        ),
                        "is_syntax": True
                    })
                else:
                    for spec, arg in zip(specifiers, parsed_args):
                        if any(c in spec for c in ["d", "i", "u"]) and re.match(r'^".*"$', arg):
                            issues.append({
                                "type": "FormatSpecifierMismatch",
                                "line": line_num,
                                "desc": f"Type mismatch: integer specifier '{spec}' passed string literal {arg}.",
                                "diagnostic_question": f"At line {line_num}, you used integer format specifier '{spec}' with string literal {arg}. What format specifier is used for strings in C?",
                                "is_syntax": True
                            })
                            break
                        elif "s" in spec and re.match(r'^-?\d+$', arg):
                            issues.append({
                                "type": "FormatSpecifierMismatch",
                                "line": line_num,
                                "desc": f"Type mismatch: string specifier '%s' passed integer literal {arg}.",
                                "diagnostic_question": f"At line {line_num}, you used string format specifier '%s' with integer value {arg}. What format specifier is used for integers in C?",
                                "is_syntax": True
                            })
                            break

        # 5. Check for missing headers when standard functions are used
        header_requirements = [
            (r"\b(printf|scanf|puts|gets)\b", "stdio.h", "standard I/O functions"),
            (r"\b(malloc|free|exit|atoi)\b", "stdlib.h", "memory management / utility functions"),
            (r"\b(strlen|strcpy|strcat|strcmp)\b", "string.h", "string manipulation functions"),
            (r"\b(sqrt|pow|sin|cos|tan)\b", "math.h", "mathematical functions"),
            (r"\b(cout|cin|endl)\b", "iostream", "C++ stream I/O")
        ]
        for pattern, header, desc_type in header_requirements:
            match = re.search(pattern, code_clean)
            if match and not re.search(rf"#include\s*[<\"]\s*{re.escape(header)}\s*[>\"]", code):
                func_name = match.group(1)
                line_no = code[:match.start()].count("\n") + 1
                issues.append({
                    "type": "MissingCHeader",
                    "line": line_no,
                    "desc": f"Using {desc_type} ('{func_name}') without including '<{header}>'.",
                    "diagnostic_question": f"You are invoking standard function '{func_name}'. Which standard header file (like '<{header}>') must be included at the top of your program?"
                })

        # 6. Uninitialized variable detection
        var_decls = re.finditer(r"\b(?:int|float|double|char)\s+([a-zA-Z_]\w*)\s*;", code_clean)
        for vd in var_decls:
            v_name = vd.group(1)
            if v_name in ["main", "void", "return"]:
                continue
            v_end = vd.end()
            remainder = code_clean[v_end:]
            write_match = re.search(rf"\b{v_name}\s*=[^=]|\bscanf\s*\([^)]*&\s*{v_name}\b|\bcin\s*>>\s*{v_name}\b", remainder)
            write_pos = write_match.start() if write_match else float("inf")
            read_match = re.search(rf"\bprintf\s*\([^)]*\b{v_name}\b|\b{v_name}\s*[\+\-\*\/%]|=[^;]*\b{v_name}\b", remainder)
            if read_match and read_match.start() < write_pos:
                line_no = code[:v_end + read_match.start()].count("\n") + 1
                issues.append({
                    "type": "UninitializedVariable",
                    "line": line_no,
                    "desc": f"Variable '{v_name}' may be read before being initialized.",
                    "diagnostic_question": f"At line {line_no}, variable '{v_name}' is accessed before an initial value is assigned. In C, what happens when reading an uninitialized local variable?",
                    "is_syntax": False
                })

        # 7. Out-of-bounds array access heuristics
        arr_decls = re.finditer(r"\b(?:int|float|double|char)\s+([a-zA-Z_]\w*)\s*\[\s*(\d+)\s*\]\s*(?:=[^;]+)?;", code_clean)
        for ad in arr_decls:
            a_name = ad.group(1)
            a_size = int(ad.group(2))
            remainder = code_clean[ad.end():]
            acc_matches = re.finditer(rf"\b{a_name}\s*\[\s*(\d+)\s*\]", remainder)
            for acc in acc_matches:
                acc_idx = int(acc.group(1))
                if acc_idx >= a_size:
                    line_no = code[:ad.end() + acc.start()].count("\n") + 1
                    issues.append({
                        "type": "IndexOutOfBoundsRisk",
                        "line": line_no,
                        "desc": f"Potential out-of-bounds array access '{a_name}[{acc_idx}]' (declared size is {a_size}).",
                        "diagnostic_question": f"In C, arrays of size {a_size} have valid indices from 0 to {a_size - 1}. What happens when accessing index {acc_idx} at line {line_no}?",
                        "is_syntax": False
                    })

        issues.sort(key=lambda x: x.get("line", 0))
        return issues

    def _analyze_ast(self, tree: ast.AST, code: str) -> List[Dict[str, Any]]:
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    issues.append({
                        "type": "BareExcept",
                        "line": node.lineno,
                        "desc": "Bare except clause catching all exceptions.",
                        "diagnostic_question": "Catching every possible exception with a bare 'except:' can conceal unexpected errors like KeyboardInterrupt or NameError. Which specific error type do you anticipate here?"
                    })

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        issues.append({
                            "type": "MutableDefault",
                            "line": node.lineno,
                            "desc": f"Function '{node.name}' uses a mutable default argument.",
                            "diagnostic_question": f"In function '{node.name}', notice the default parameter is a mutable collection. In Python, when is that default evaluated: every call, or once at definition time? What side effect might that cause?"
                        })

                has_self_call = False
                has_return = False
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) and sub.func.id == node.name:
                        has_self_call = True
                    if isinstance(sub, ast.Return) and sub.value is not None:
                        has_return = True

                if has_self_call and not has_return:
                    issues.append({
                        "type": "MissingBaseCase",
                        "line": node.lineno,
                        "desc": f"Recursive function '{node.name}' may lack a terminating return condition.",
                        "diagnostic_question": f"In your recursive function '{node.name}', what base condition stops further recursion and returns an actual value back up the stack?"
                    })

                # Check for unreachable statements immediately after a return in the same block
                for i, stmt in enumerate(node.body[:-1]):
                    if isinstance(stmt, ast.Return):
                        next_stmt = node.body[i + 1]
                        issues.append({
                            "type": "UnreachableCode",
                            "line": next_stmt.lineno,
                            "desc": f"Unreachable code detected at line {next_stmt.lineno} following a return statement.",
                            "diagnostic_question": f"At line {next_stmt.lineno}, code appears immediately after a return statement. Under what condition will this code ever execute?"
                        })

            # Check for range(len(...) + 1) off-by-one error via AST
            if isinstance(node, ast.For):
                if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name) and node.iter.func.id == "range":
                    for arg in node.iter.args:
                        if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
                            if (isinstance(arg.left, ast.Call) and isinstance(arg.left.func, ast.Name) and arg.left.func.id == "len" and
                                isinstance(arg.right, ast.Constant) and arg.right.value == 1):
                                issues.append({
                                    "type": "IndexOutOfBoundsRisk",
                                    "line": node.lineno,
                                    "desc": "Off-by-one error: iterating up to len(...) + 1.",
                                    "diagnostic_question": f"At line {node.lineno}, your loop iterates up to len(...) + 1. In 0-indexed sequences, what is the maximum valid index? What exception occurs when accessing index len(...)?"
                                })
        return issues

    def _analyze_heuristics(self, code: str, domain: str) -> List[Dict[str, Any]]:
        issues = []
        lines = code.split("\n")
        code_lower = code.lower()

        for idx, line in enumerate(lines, 1):
            line_str = line.strip()

            # Data Science checks (applied if DS domain or if ML/Pandas keywords exist in code)
            if domain == "data_science" or any(kw in code_lower for kw in ["fit_transform", "scaler", "inplace", "dropna", "read_csv", "train_test_split", "df["]):
                if re.search(r"\.(?:fit_transform|fit)\s*\(\s*(?:X_test|test_|test_data|test_df|test_set|\w*test\w*)", line_str, re.IGNORECASE):
                    issues.append({
                        "type": "DataLeakage",
                        "line": idx,
                        "desc": "Fitting scaler or preprocessor on the test set.",
                        "diagnostic_question": f"Notice how you are fitting your preprocessor on test data at line {idx}. Why is it critical that test data statistics remain completely unobserved during model fitting?"
                    })

                if re.search(r"^\s*([a-zA-Z_]\w*)\s*=\s*[^#\n]*\binplace\s*=\s*True", line_str, re.IGNORECASE):
                    issues.append({
                        "type": "PandasInplaceReassignment",
                        "line": idx,
                        "desc": "Reassigning result of an in-place Pandas operation.",
                        "diagnostic_question": f"At line {idx}, you perform an operation with 'inplace=True' and reassign it to the variable. In Pandas, what does an in-place method return? What will your DataFrame variable become?"
                    })

                # Chained indexing check
                if re.search(r"(?:df|data|dataset|frame)\s*\[.*?\]\s*\[.*?\]\s*=", line_str) or re.search(r"(?:df|data|dataset|frame)\.(?:iloc|loc)\s*\[.*?\]\s*\[.*?\]\s*=", line_str):
                    issues.append({
                        "type": "ChainedIndexing",
                        "line": idx,
                        "desc": "Chained indexing assignment detected (risk of SettingWithCopyWarning).",
                        "diagnostic_question": f"At line {idx}, you are using chained indexing assignment ('df[...][...] = ...'). In Pandas, why can chained assignment fail to modify the original DataFrame, and how does '.loc[row_indexer, col_indexer]' guarantee safe assignment?"
                    })

                # Target leakage check
                if re.search(r"\btrain_test_split\s*\(\s*([a-zA-Z_]\w*)\s*,\s*\1\s*\[", line_str):
                    issues.append({
                        "type": "TargetLeakage",
                        "line": idx,
                        "desc": "Possible target leakage: target column may be retained inside feature DataFrame in train_test_split.",
                        "diagnostic_question": f"At line {idx}, 'train_test_split' is called with the full DataFrame alongside target labels without dropping the target column. Why must features strictly exclude target labels?"
                    })
                elif re.search(r"^\s*X\s*=\s*(?:df|data)\s*$", line_str) and re.search(r"\by\s*=\s*(?:df|data)\[", code) and "drop" not in code:
                    issues.append({
                        "type": "TargetLeakage",
                        "line": idx,
                        "desc": "Target leakage risk: feature matrix 'X' assigned entire DataFrame without dropping target.",
                        "diagnostic_question": f"Notice line {idx}: 'X' is assigned the entire DataFrame without dropping the target column. Why must feature matrices strictly exclude the target column during training?"
                    })

            # Unbounded while loop check
            if re.search(r"^while\s+True\s*:", line_str) and not re.search(r"\b(break|return)\b", code):
                issues.append({
                    "type": "UnboundedLoop",
                    "line": idx,
                    "desc": "'while True' loop without a clear exit break.",
                    "diagnostic_question": f"At line {idx}, your 'while True' loop runs continuously. Where and under what exact condition should the loop break or return?"
                })

            # Binary search boundary check: pinpoint on the specific loop line
            if re.search(r"while\s+.*low\s*<\s*high\b", line_str) and ("arr[mid]" in code or "nums[mid]" in code or "mid" in code) and "low <= high" not in code:
                issues.append({
                    "type": "SearchBoundaryIssue",
                    "line": idx,
                    "desc": "Binary search boundary condition check.",
                    "diagnostic_question": f"Consider what happens in binary search when the subarray narrows to a single remaining element (where low == high) at line {idx}. With your loop condition 'low < high', will that single element ever be examined?"
                })

            # Off-by-one index error in range(len(...) + 1)
            if re.search(r"for\s+\w+\s+in\s+range\s*\(\s*(?:0\s*,\s*)?len\s*\(\w+\)\s*\+\s*1\s*\)\s*:", line_str):
                issues.append({
                    "type": "IndexOutOfBoundsRisk",
                    "line": idx,
                    "desc": "Off-by-one error: iterating up to len(sequence) + 1.",
                    "diagnostic_question": f"At line {idx}, your loop iterates up to len(...) + 1. In 0-indexed sequences, what is the maximum valid index? What exception occurs when accessing index len(...)?"
                })

        return issues

    def _synthesize_hints(self, findings: Dict[str, Any], code: str = "") -> Dict[int, str]:
        hints = {1: "", 2: "", 3: ""}
        issues = findings.get("issues", [])

        if not issues:
            lang = findings.get("language", "programming")
            if findings["detected_domain"] == "data_science":
                hints[1] = "What is the primary objective of your data transformation or model pipeline? Walk through the inputs and intended outputs."
                hints[2] = "Consider the assumptions of your model and how data preprocessing (scaling, imputation, splits) should flow."
                hints[3] = "Inspect your data shapes and distributions before and after each transformation. Does each step preserve data integrity?"
            elif findings["detected_domain"] == "systems_programming":
                hints[1] = "Your C program structure looks clean! What does each line contribute from preprocessor directives to process termination?"
                hints[2] = "Consider how standard output handles character streams. What escape sequences control formatting?"
                hints[3] = "How would you modify this program to accept dynamic user input from standard input?"
            else:
                hints[1] = "What are the core preconditions and invariants that your algorithm must maintain at each step?"
                hints[2] = "Consider tracing the logic with a minimal edge case (e.g. empty input, single element, or boundary values)."
                hints[3] = "Look closely at how state or variables transition from one iteration to the next. Does every branch make forward progress?"
            return hints

        primary_issue = issues[0]
        dq = primary_issue.get("diagnostic_question", "")

        hints[1] = "Let's examine the design: what is the expected function call or statement behavior here?"
        hints[2] = f"Notice the highlighted statement at line {primary_issue.get('line', 'N/A')}: {dq.split('?')[0]}?" if "?" in dq else dq
        hints[3] = dq or "Review the highlighted line and trace variable values step-by-step."

        return hints

    def sanitize_code_leakage(self, response_text: str) -> str:
        """
        Anti-cheating guardrail: strips full executable solutions or complete function bodies from responses,
        replacing them with Socratic scaffolding and guided pseudocode.
        """
        pattern = r"```(?:python|py|c|cpp|java)?\s*(def\s+\w+\(.*?\):|int\s+main\(.*?\)\s*\{)(?:\n\s+.*)+\s*```"
        match = re.search(pattern, response_text, re.DOTALL)
        if match:
            replacement = (
                "```python\n"
                "# [SOCRATIC GUARD: Direct Solution Hidden to Protect Learning]\n"
                "# Step 1: Initialize your variables / data structures\n"
                "# Step 2: Set up your loop or transformation condition\n"
                "# Step 3: Implement the core state transition\n"
                "# Step 4: Return or output the verified result\n"
                "```\n\n"
                "💡 **Guiding Question**: Instead of having the full code handed to you, try writing the first 2 lines of the setup above. What variables will you need?"
            )
            return re.sub(pattern, replacement, response_text)
        return response_text
