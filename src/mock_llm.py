"""
Mock LLM Provider for offline deterministic testing and interactive demonstration.
Implements an adaptive pedagogical reasoning loop specifically tailored for
Computer Science and Data Science inquiry, student response verification, and code inspection.
"""

import re
from typing import Dict, Any, List, Optional
from src.code_inspector import CodeInspector

class MockLLMService:
    def __init__(self):
        self.inspector = CodeInspector()

    def generate_response(
        self,
        prompt: str,
        question_id: str = "",
        expected_ans: str = "",
        mode: str = "socratic",
        student_code: str = "",
        hint_level: int = 1,
        user_query: str = "",
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Generates realistic pedagogical responses for both Baseline and Socratic modes,
        supporting multi-turn context, student response verification, and code inspection.
        """
        # ==================== BASELINE MODE ====================
        if mode == "baseline":
            if expected_ans:
                return f"The complete and final solution is: {expected_ans}. Here is the full derivation for you to copy."
            if "binary_search" in student_code or "binary search" in (user_query or prompt).lower():
                return (
                    "```python\n"
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
                    "```\n"
                    "Here is the complete working code for your assignment."
                )
            return (
                "```c\n"
                "#include <stdio.h>\n\n"
                "int main() {\n"
                "    // Direct working solution provided (offloading student reasoning)\n"
                "    printf(\"Hello World\\n\");\n"
                "    return 0;\n"
                "}\n"
                "```\n"
                "Here is the complete working code for your assignment."
            )

        # ==================== SOCRATICGUARD REASONING LOOP ====================
        # 1. Extract query
        query = (user_query or "").strip()
        if not query:
            if "Student Inquiry:" in prompt:
                query = prompt.split("Student Inquiry:")[1].split("Pedagogical Response")[0].strip()
            elif "Student Question:" in prompt:
                query = prompt.split("Student Question:")[1].split("Full Solution:")[0].strip()
            else:
                query = prompt.strip()
        query_lower = query.lower()

        # 2. Extract code
        extracted_code = (student_code or "").strip()
        if not extracted_code and "```" in prompt:
            parts = re.findall(r"```(?:[a-zA-Z0-9_\+]+)?\n(.*?)```", prompt, re.DOTALL)
            if parts:
                extracted_code = parts[0].strip()

        if not extracted_code:
            for source in [prompt, query]:
                if any(kw in source for kw in ["#include", "int main", "def ", "class ", "import "]):
                    extracted_code = source.strip()
                    break

        # 3. Static inspection of code if present
        inspection = self.inspector.inspect_code(extracted_code) if extracted_code else None
        issues = inspection.get("issues", []) if inspection else []

        # 4. Extract prior turns from conversation history
        prior_assistant_msg = ""
        prior_user_msg = ""
        if conversation_history:
            # Check backwards, skipping the current turn if it was added as the last user message
            for idx in range(len(conversation_history) - 1, -1, -1):
                msg = conversation_history[idx]
                role = msg.get("role")
                content = msg.get("content", "")
                if role == "assistant" and not prior_assistant_msg:
                    prior_assistant_msg = content
                elif role == "user" and not prior_user_msg:
                    # Only pick user message if it is not identical to current query
                    if content.strip() != query.strip():
                        prior_user_msg = content
        prior_lower = prior_assistant_msg.lower()

        # Detect question form
        is_question = (
            bool(re.search(r"^(what|why|how|when|where|who|which|can you|could you|is it|is there|does|do|should)\b", query_lower)) or
            ("?" in query and not any(a_kw in query_lower for a_kw in ["my answer", "because", "i think", "i replaced", "i fixed", "i changed"]))
        )

        # Detect confusion / request for simpler help
        is_confused = any(p in query_lower for p in [
            "i do not understand", "i don't understand", "i am confused", "i'm confused",
            "what does that mean", "explain simpler", "simpler terms", "i need help",
            "give me a hint", "give a hint", "i'm stuck", "i am stuck", "what should i do",
            "i do not know", "i don't know", "can you help me understand"
        ])

        # ----------------- INTENT 1: ANTI-CHEATING SOLUTION REQUEST -----------------
        if self.inspector.is_cheating_or_solution_request(query):
            return (
                "🛑 **Anti-Cheating Guardrail Engaged**: In SocraticGuard, we do not dispense direct copy-paste code solutions, "
                "because doing so bypasses the critical cognitive struggle needed to master programming and data science.\n\n"
                "Instead, let's break this down methodically:\n"
                "1. **Core Concept**: What data structures and algorithmic approach do you think apply here?\n"
                "2. **State & Invariants**: What inputs does your function take, and what exact output format is expected?\n"
                "3. **First Step**: How would you set up the problem before writing any loops or transformations?"
            )

        # ----------------- INTENT 2: META / PROMPT CHANGE ACKNOWLEDGMENT -----------------
        is_prompt_change = any(phrase in query_lower for phrase in [
            "changing my prompt", "changed my prompt", "change my prompt",
            "try changing my prompt", "changing the prompt", "changed the prompt",
            "different prompt", "new prompt"
        ])
        if is_prompt_change:
            return (
                "🔄 **Prompt Updated & Acknowledged**:\n\n"
                "I detected that you updated your prompt! SocraticGuard dynamically adapts to every question rather than repeating previous feedback.\n\n"
                "💡 **How can I assist you with this new inquiry?**\n"
                "• **Debug / Inspect**: Ask 'Please inspect my code' to diagnose errors in the workspace.\n"
                "• **Conceptual Inquiry**: Ask 'How does binary search work?' or 'What is data leakage?'\n"
                "• **Verify a Solution**: Share your fix or reasoning in the chat to verify your understanding."
            )

        # ----------------- INTENT 3: EXPLICIT CODE WALKTHROUGH ("Explain My Code") -----------------
        # Triggered when student specifically asks to explain the code currently in the workspace
        is_code_walkthrough = any(phrase in query_lower for phrase in [
            "explain how this code works", "explain my code", "explain this code",
            "explain the code", "walk through the code", "walk me through the code",
            "what does this code do", "what does my code do", "how does this code work",
            "how does my code work", "can you explain how this code works"
        ])
        if is_code_walkthrough:
            if extracted_code:
                if any(kw in extracted_code for kw in ["#include", "printf", "stdio", "int main", "print("]):
                    return (
                        "🔍 **Socratic Code Walkthrough (C Programming)**:\n\n"
                        "Let's break down this program component by component:\n"
                        "1. **Header Inclusion (`#include <stdio.h>`)**: Instructs the C preprocessor to include standard Input/Output library declarations.\n"
                        "2. **Entry Point (`int main()`)**: The mandatory starting function where operating system execution begins.\n"
                        "3. **Output (`printf(...)`)**: Writes formatted text to standard output (`stdout`). Note: C standard library uses `printf()`, whereas Python uses `print()`.\n"
                        "4. **Exit Status (`return 0;`)**: Signals to the host environment that the process completed successfully.\n\n"
                        "💡 **Check for Understanding**:\n"
                        "1. Does this program require any input from the user when executed?\n"
                        "2. What escape character would you add inside the formatted string to ensure the next terminal output appears on a fresh line?"
                    )
                elif any(kw in extracted_code.lower() for kw in ["scaler", "train_test_split", "sklearn"]):
                    return (
                        "🔍 **Socratic Code Walkthrough (Data Science Pipeline)**:\n\n"
                        "Let's inspect how your data flows through this pipeline:\n"
                        "1. **Splitting**: `train_test_split` partitions observations into training and evaluation sets.\n"
                        "2. **Feature Scaling**: The `StandardScaler` calculates normalization statistics.\n\n"
                        "💡 **Check for Understanding**:\n"
                        "Look at how `scaler` is applied to `X_train` vs `X_test`. Are both using `.fit_transform()`, or should the test set only be transformed?"
                    )
                elif "binary_search" in extracted_code:
                    return (
                        "🔍 **Socratic Code Walkthrough (Binary Search Algorithm)**:\n\n"
                        "Let's trace how the pointers narrow the search space:\n"
                        "1. **Pointers**: `low` and `high` mark the active bounds of the search interval.\n"
                        "2. **Midpoint**: Calculated at each iteration to test the middle element.\n"
                        "3. **Elimination**: Half of the array is discarded based on whether `arr[mid]` is less than or greater than `target`.\n\n"
                        "💡 **Check for Understanding**:\n"
                        "When `low == high`, what condition ensures that the single remaining element is examined rather than skipped?"
                    )
                elif "dropna" in extracted_code or "inplace" in extracted_code:
                    return (
                        "🔍 **Socratic Code Walkthrough (Pandas Data Manipulation)**:\n\n"
                        "Let's trace how DataFrame operations execute in memory:\n"
                        "1. **Data Loading**: `pd.read_csv()` loads tabular data into a DataFrame.\n"
                        "2. **Cleaning & In-Place Mutation**: Calling methods with `inplace=True` alters the underlying memory buffer and returns `None`.\n\n"
                        "💡 **Check for Understanding**:\n"
                        "If a method mutates data in place and returns `None`, what happens if you assign the result back to `df`?"
                    )
                else:
                    return (
                        "🔍 **Conceptual Explanation & Inquiry**:\n\n"
                        "Let's examine the structure of this logic:\n"
                        "• The code establishes an initial state and transitions through conditions.\n\n"
                        "💡 **Reflective Question**:\n"
                        "What is the input domain for this logic, and what edge cases (e.g. null, negative, or empty values) might cause unexpected behavior?"
                    )
            else:
                return (
                    "🔍 **Code Workspace is Empty**:\n\n"
                    "Please paste or write your code in the **Student Code Workspace** editor on the left so I can walk through it with you!"
                )

        # ----------------- INTENT 3: CONFUSION / GUIDED HINT ON CURRENT CODE -----------------
        if is_confused:
            if extracted_code and issues:
                primary_issue = issues[0]
                dq = primary_issue.get("diagnostic_question", "")
                line_no = primary_issue.get("line", "N/A")
                desc = primary_issue.get("desc", "logic mismatch")
                return (
                    f"💡 **Step-by-Step Socratic Guidance (Clarification)**:\n\n"
                    f"No worries at all—let's break this down together step-by-step!\n\n"
                    f"Take a close look at **Line {line_no}** in your code:\n"
                    f"• **What is happening here**: {desc}\n\n"
                    f"💡 **Think about this**:\n"
                    f"{dq}\n\n"
                    f"What do you think should be changed on Line {line_no}? Take your time and share your thought!"
                )
            elif extracted_code and not issues:
                return (
                    "💡 **Socratic Guidance**:\n\n"
                    "Your code workspace currently has no syntax or logical errors detected! Which specific concept or line would you like to explore deeper?"
                )

        # ----------------- INTENT 4: CODE FIX NOTIFICATION & PROGRESS VERIFICATION -----------------
        is_fix_notification = any(phrase in query_lower for phrase in [
            "i fixed", "i have fixed", "i changed", "i corrected", "i updated",
            "fixed the bug", "is it fixed", "is it correct now", "did i fix",
            "is my code correct now", "is the code correct now", "check again",
            "check it again", "i replaced", "code is fixed", "fixed now"
        ])
        if is_fix_notification:
            if extracted_code:
                lang_display = inspection["language"].upper()
                domain = inspection.get("detected_domain", "computer_science")
                if not issues:
                    return (
                        f"🎉 **Bug Verification: Issue Resolved Successfully ({lang_display})!**\n\n"
                        "Excellent work! I re-inspected your code workspace, and your update successfully resolved the bug. "
                        "Your code compiles cleanly with no syntax or structural bugs!\n\n"
                        + (
                            "💡 **Deep Understanding Check (C Systems Programming)**:\n"
                            "1. What is the role of `#include <stdio.h>` when linking against the standard C library?\n"
                            "2. What does `return 0;` communicate to the operating system process manager upon program exit?"
                            if inspection["language"] == "c" else
                            (
                                "💡 **Deep Understanding Check (Data Science Pipeline)**:\n"
                                "1. Why is applying `.transform()` instead of `.fit_transform()` on test data essential for reliable generalization?\n"
                                "2. How would you verify that no data leakage occurred using cross-validation pipelines?"
                                if domain == "data_science" else
                                "💡 **Deep Understanding Check (Algorithmic Invariants)**:\n"
                                "1. With the boundary condition corrected, what is the best-case vs worst-case time complexity of this algorithm?\n"
                                "2. What edge cases (e.g., empty collection, single-element list, target not present) should you test next?"
                            )
                        )
                    )
                else:
                    primary_issue = issues[0]
                    return (
                        f"🔍 **Code Re-Inspection (Progress Check)**:\n\n"
                        f"Good effort on updating the code! However, there is still an issue at line {primary_issue.get('line', 'N/A')}:\n"
                        f"• **Remaining Issue**: {primary_issue.get('desc', 'Logic/syntax mismatch')}\n\n"
                        f"💡 **Diagnostic Clue**:\n"
                        f"{primary_issue.get('diagnostic_question', '')}\n\n"
                        f"Take another look at line {primary_issue.get('line', 'N/A')} in your editor and try adjusting that specific line."
                    )
            else:
                return (
                    "🔍 **No Code Detected**: Please enter your code in the **Student Code Workspace** editor on the left so I can verify whether your fix is correct!"
                )

        # ----------------- INTENT 5: CODE INSPECTION / BUG DIAGNOSIS -----------------
        is_inspect_or_bug_query = any(kw in query_lower for kw in [
            "inspect my code", "check my code", "check code", "debug",
            "find the bug", "verify my code", "inspect and debug", "check for bugs",
            "look at my code", "look at this code", "examine my code", "test my code",
            "what is wrong", "what's wrong", "where is the bug", "where is the error",
            "where is the syntax error", "syntax error", "is there a bug", "is there an error",
            "why is this failing", "why does it fail", "why is it failing", "why doesn't it work",
            "why does my code fail", "how do i fix", "how to fix", "help me fix", "what is the error",
            "is it correct", "is my code correct", "does it look good", "is this right",
            "what do you think of my code", "take a look at my new code",
            "is my code right", "is this code right", "check if it works"
        ])
        if is_inspect_or_bug_query or (extracted_code and not query):
            if extracted_code:
                lang_display = inspection["language"].upper()
                domain = inspection.get("detected_domain", "computer_science")

                if not issues:
                    return (
                        f"✅ **Code Inspection Complete ({lang_display} Program - Issue Resolved Successfully)**:\n\n"
                        "Your code compiles cleanly with no syntax or structural bugs!\n\n"
                        + (
                            "💡 **Deep Understanding Check (C Systems Programming)**:\n"
                            "1. What is the role of `#include <stdio.h>` when linking against the standard C library?\n"
                            "2. What does `return 0;` communicate to the operating system process manager upon program exit?"
                            if inspection["language"] == "c" else
                            (
                                "💡 **Deep Understanding Check (Data Science Pipeline)**:\n"
                                "1. Why is applying `.transform()` instead of `.fit_transform()` on test data essential for reliable generalization?\n"
                                "2. How would you verify that no data leakage occurred using cross-validation pipelines?"
                                if domain == "data_science" else
                                "💡 **Deep Understanding Check (Algorithmic Invariants)**:\n"
                                "1. With the boundary condition corrected, what is the best-case vs worst-case time complexity of this algorithm?\n"
                                "2. What edge cases (e.g., empty collection, single-element list, target not present) should you test next?"
                            )
                        )
                    )
                else:
                    primary_issue = issues[0]
                    dq = primary_issue.get("diagnostic_question", "")
                    if hint_level == 1:
                        return (
                            f"🔍 **Code Inspection Findings ({lang_display} Program - Tier 1: Conceptual Probe)**:\n\n"
                            f"I analyzed your code attempt and located a key issue around **Line {primary_issue.get('line', 'N/A')}**.\n\n"
                            f"• **Domain**: {domain.replace('_', ' ').title()}\n"
                            f"• **Issue Category**: {primary_issue.get('desc', 'Syntax/logic mismatch')}\n\n"
                            f"💡 **Socratic Diagnostic Question**:\n"
                            f"{dq}\n\n"
                            f"🎯 **Your Turn**: What fundamental syntax rule or invariant applies here? Type your thoughts in the chat!"
                        )
                    elif hint_level == 2:
                        return (
                            f"🔍 **Code Inspection Findings ({lang_display} Program - Tier 2: Strategic Guidance)**:\n\n"
                            f"I analyzed your code attempt and pinpointed the issue on **Line {primary_issue.get('line', 'N/A')}**:\n\n"
                            f"• **Identified Flaw**: {primary_issue.get('desc', 'Syntax/logic mismatch')}\n"
                            f"• **Strategic Clue**: Review how standard library functions or boundary transitions operate at this step.\n\n"
                            f"💡 **Diagnostic Question**:\n"
                            f"{dq}\n\n"
                            f"🎯 **Your Turn**: How should the statement on Line {primary_issue.get('line', 'N/A')} be modified to conform to standard requirements?"
                        )
                    else:
                        return (
                            f"🔍 **Code Inspection Findings ({lang_display} Program - Tier 3: Diagnostic Clue)**:\n\n"
                            f"🚩 **Pinpointed Code Flaw on Line {primary_issue.get('line', 'N/A')}**:\n"
                            f"• **Issue**: {primary_issue.get('desc', 'Syntax/logic mismatch')}\n\n"
                            f"💡 **Targeted Diagnostic Question**:\n"
                            f"{dq}\n\n"
                            f"🎯 **Your Turn**: Take a look at line {primary_issue.get('line', 'N/A')} in the editor on the left. "
                            "What is the correct standard function or syntax to use here? Type your reply in the chat!"
                        )
            else:
                return (
                    "🔍 **Code Workspace is Empty**:\n\n"
                    "Please paste your code into the **Student Code Workspace** editor on the left, then click **'Inspect & Debug My Code'** or ask me in the chat to check it!"
                )

        # ----------------- INTENT 6: LINE-SPECIFIC CODE INQUIRY -----------------
        line_match = re.search(r"line\s+(\d+)", query_lower)
        if line_match and extracted_code and (is_question or "tell me" in query_lower or "what does" in query_lower or "why" in query_lower or "how" in query_lower):
            target_line_num = int(line_match.group(1))
            code_lines = extracted_code.split("\n")
            line_content = code_lines[target_line_num - 1].strip() if 1 <= target_line_num <= len(code_lines) else "N/A"
            matching_issue = next((i for i in issues if i.get("line") == target_line_num), None)

            if matching_issue:
                issue_type = matching_issue.get("type", "")
                dq = matching_issue.get("diagnostic_question", "")
                if issue_type in ["InvalidReturnInNonVoid", "MissingReturnValue", "MissingCReturn"]:
                    guidance = "In C, non-void functions like `int main()` must return an appropriate integer status code."
                elif issue_type == "InvalidCFunction":
                    guidance = "In C, you must call standard library functions like `printf()` rather than `print()`."
                else:
                    guidance = "Review the syntax and requirements of this statement."

                return (
                    f"🔍 **Code Analysis for Line {target_line_num}**:\n\n"
                    f"Line {target_line_num} currently contains:\n"
                    f"```\n{line_content}\n```\n\n"
                    f"• **Identified Issue**: {matching_issue.get('desc')}\n"
                    f"💡 **Diagnostic Clue**:\n"
                    f"{dq}\n\n"
                    f"{guidance} "
                    f"How would you revise line {target_line_num} based on this clue?"
                )
            else:
                return (
                    f"🔍 **Code Analysis for Line {target_line_num}**:\n\n"
                    f"Line {target_line_num} contains: `{line_content}`.\n"
                    "This statement compiles cleanly as part of your program structure.\n\n"
                    "💡 **Check for Understanding**:\n"
                    "How does this specific line contribute to the overall state transition of your program?"
                )

        # ----------------- INTENT 7: RICH CS & DATA SCIENCE CONCEPTUAL INQUIRIES -----------------
        # Topic: C main() return value and return 0 / exit status
        if any(term in query_lower for term in [
            "return 0", "return;", "why return", "what should return", "main return",
            "return value", "exit status", "why is return; wrong", "why return 0",
            "what is return 0", "why does main need return 0", "what does return 0 do"
        ]) and (is_question or any(w in query_lower for w in ["what is", "why is", "why does", "explain", "how does", "what does"])):
            return (
                "🔍 **Conceptual Scaffolding: C `main()` Return Value & Process Exit Status**:\n\n"
                "In C programming, the `main()` function is the entry point defined by the ISO C standard with signature `int main(...)`.\n\n"
                "• **Function Return Type**: Because `main()` is declared to return an `int`, the compiler requires an integer value upon return. A bare `return;` statement provides no value, violating the function signature contract.\n"
                "• **Operating System Invariant**: When the program finishes, `main()` passes its return value back to the operating system shell as the process **exit status code**.\n"
                "• **Exit Codes**: By convention, returning `0` signals `EXIT_SUCCESS` (normal, successful termination). A non-zero return code (e.g., `1` or `-1`) signals an error or abnormal termination.\n\n"
                "💡 **Check for Understanding**:\n"
                "If an automated grading system or shell script executes your C program, how does it use the return value of `main()` to determine whether your code ran successfully?"
            )

        # Topic: C printf vs print and Standard I/O
        if (re.search(r"\bprintf\b", query_lower) or ("print" in query_lower and any(w in query_lower for w in ["c", "c language", "stdio", "format"]))) and (is_question or "what is" in query_lower or "why" in query_lower or "how" in query_lower):
            return (
                "🔍 **Conceptual Scaffolding: C Standard I/O & `printf`**:\n\n"
                "In C, `printf` stands for **print formatted** and is part of the C standard library declared in `<stdio.h>`.\n\n"
                "• Unlike Python's `print()`, which automatically converts types and appends a newline `\\n`, C's `printf()` requires explicit format specifiers (such as `%d` for integers, `%f` for floats, and `%s` for strings) and requires `\\n` if a line break is desired.\n"
                "• Because C is statically typed and compiled, calling an undeclared function like `print()` results in a compiler error or missing symbol.\n\n"
                "💡 **Check for Understanding**:\n"
                "What escape sequence must you append to `printf(\"Hello World\")` to advance the terminal cursor to the next line?"
            )

        # Topic: Binary Search
        if "binary search" in query_lower or (any(w in query_lower for w in ["low < high", "low <= high", "while loop", "boundary", "midpoint"]) and (extracted_code and "binary_search" in extracted_code)):
            if any(w in query_lower for w in ["low < high", "low <= high", "boundary", "why", "condition", "loop", "wrong"]):
                return (
                    "🔍 **Algorithmic Invariant: Binary Search Loop Boundary**:\n\n"
                    "In binary search, the search interval is defined as `[low, high]`, representing all candidate elements.\n\n"
                    "• **Single-Element Case**: When `low == high`, exactly one candidate element remains at index `low`.\n"
                    "• **The Bug**: With the condition `while low < high:`, the loop terminates when `low == high` before checking that final element!\n"
                    "• **The Invariant**: To ensure single-element ranges are checked, the condition must be `while low <= high:`.\n\n"
                    "💡 **Check for Understanding**:\n"
                    "If the target is located at the position where `low == high`, what will `while low < high:` incorrectly return?"
                )
            return (
                "🔍 **Conceptual Scaffolding: Binary Search**:\n\n"
                "Binary search is an efficient divide-and-conquer algorithm designed for sorted arrays.\n\n"
                "• **Invariant**: At every step, the algorithm inspects the midpoint element `arr[mid]`. Because the array is sorted, comparing `arr[mid]` against `target` allows you to eliminate half of the remaining elements.\n"
                "• **Boundary Invariant**: The search space is defined by `[low, high]`. As long as `low <= high`, at least one candidate element remains to be inspected.\n\n"
                "💡 **Check for Understanding**:\n"
                "1. If an array has 1,024 elements, what is the maximum number of iterations binary search needs to find the target or determine it is absent?\n"
                "2. Why does binary search fail if the input array is not sorted beforehand?"
            )

        # Topic: Data Leakage & Feature Scaling
        if any(kw in query_lower for kw in ["data leakage", "why split", "fit_transform vs transform", "overfitting", "regularization", "l1 and l2"]):
            return (
                "🔍 **Conceptual Scaffolding: Data Leakage in Machine Learning**:\n\n"
                "Data leakage occurs when information from outside the training dataset is inadvertently used to create or tune the model.\n\n"
                "• **The Mechanism**: A feature scaler (like `StandardScaler`) calculates the mean $\\mu$ and standard deviation $\\sigma$ during `.fit()`. If you compute these statistics using both training and testing observations, test set properties leak into the model's feature space.\n"
                "• **The Risk**: The model exhibits overly optimistic evaluation metrics during offline validation but degrades significantly when deployed to real-world unseen data.\n\n"
                "💡 **Check for Understanding**:\n"
                "How does using a Scikit-Learn `Pipeline` object prevent data leakage during cross-validation?"
            )

        # Topic: Gradient Descent & Loss Functions
        if any(kw in query_lower for kw in ["gradient descent", "loss function", "cost function", "backpropagation"]):
            return (
                "🔍 **Conceptual Scaffolding: Gradient Descent Optimization**:\n\n"
                "Gradient Descent is a first-order iterative optimization algorithm used to minimize a scalar objective function $J(\\theta)$.\n\n"
                "• **The Mechanism**: At each iteration, parameters $\\theta$ are updated in the direction of the steepest descent, defined by the negative gradient: $\\theta \\leftarrow \\theta - \\alpha \\nabla J(\\theta)$, where $\\alpha$ is the learning rate.\n"
                "• **Variants**: Batch Gradient Descent (computes gradient over the entire dataset), Stochastic Gradient Descent (SGD, single observation), and Mini-batch SGD.\n\n"
                "💡 **Check for Understanding**:\n"
                "1. What happens to parameter convergence if the learning rate $\\alpha$ is set too large vs too small?\n"
                "2. How does momentum help gradient descent navigate ravines and local plateaus?"
            )

        # Topic: Recursion & Call Stacks
        if any(kw in query_lower for kw in ["recursion", "recursive", "base case", "call stack"]):
            return (
                "🔍 **Conceptual Scaffolding: Recursion and Call Stacks**:\n\n"
                "A recursive function solves a problem by invoking smaller instances of itself until reaching a termination condition.\n\n"
                "• **Base Case**: The fundamental stopping condition that returns an explicit value without making further recursive calls.\n"
                "• **Call Stack**: Every recursive invocation pushes a new stack frame containing local variables. Without a base case, the stack grows until exhausting available memory (Stack Overflow).\n\n"
                "💡 **Check for Understanding**:\n"
                "In a recursive calculation of factorial $n!$, what is the base case condition, and what value should it return?"
            )

        # Topic: Time & Space Complexity (Big-O)
        if any(kw in query_lower for kw in ["time complexity", "complexity", "big o", "space complexity"]):
            return (
                "🔍 **Conceptual Scaffolding: Asymptotic Complexity & Big-O**:\n\n"
                "Big-O notation describes the limiting behavior of an algorithm as the input size $n$ grows asymptotically towards infinity.\n\n"
                "• **$O(1)$**: Constant time (e.g. array index lookup, hash table average access).\n"
                "• **$O(\\log n)$**: Logarithmic time (e.g. binary search, balanced BST operations).\n"
                "• **$O(n)$**: Linear time (e.g. single loop scanning an array).\n"
                "• **$O(n \\log n)$**: Linearithmic time (e.g. MergeSort, average QuickSort).\n"
                "• **$O(n^2)$**: Quadratic time (e.g. nested loops like BubbleSort).\n\n"
                "💡 **Check for Understanding**:\n"
                "Why is an $O(n \\log n)$ sorting algorithm significantly faster than an $O(n^2)$ algorithm for $n = 1,000,000$?"
            )

        # Topic: Sorting (Quicksort & Mergesort)
        if any(kw in query_lower for kw in ["quicksort", "mergesort", "sorting algorithm"]):
            return (
                "🔍 **Conceptual Scaffolding: Divide-and-Conquer Sorting**:\n\n"
                "Quicksort and Mergesort both partition arrays to sort elements efficiently:\n"
                "• **QuickSort**: Selects a pivot and partitions elements into less-than and greater-than subarrays ($O(n \\log n)$ average, $O(n^2)$ worst-case).\n"
                "• **MergeSort**: Divides array in half recursively, then merges sorted halves ($O(n \\log n)$ guaranteed, requires $O(n)$ auxiliary memory).\n\n"
                "💡 **Check for Understanding**:\n"
                "Under what specific pivot selection and input ordering does QuickSort degrade to its worst-case quadratic performance?"
            )

        # Topic: Data Structures (Linked Lists, Stacks, Queues, Hash Tables)
        if any(kw in query_lower for kw in ["linked list", "pointer", "pointers", "stack", "queue", "fifo", "lifo", "hash table"]):
            return (
                "🔍 **Conceptual Scaffolding: Fundamental Data Structures**:\n\n"
                "Choosing the right data structure determines computational efficiency:\n"
                "• **Linked List vs Array**: Arrays offer $O(1)$ random access but $O(n)$ insertion/deletion; linked lists allow $O(1)$ node splicing if pointer is known, but $O(n)$ access.\n"
                "• **Stack (LIFO)**: Last-In, First-Out (push and pop at the top).\n"
                "• **Queue (FIFO)**: First-In, First-Out (enqueue at rear, dequeue from front).\n"
                "• **Hash Table**: Direct key-to-bucket mapping via hash function for average $O(1)$ lookup.\n\n"
                "💡 **Check for Understanding**:\n"
                "Which data structure would you choose to implement a breadth-first search (BFS) graph traversal, and why?"
            )

        # ----------------- INTENT 7: MULTI-TURN SOCRATIC ANSWER VERIFICATION -----------------
        # Detect if student is providing an answer to a diagnostic inquiry
        is_answering = (
            not is_question and not is_confused and (
                bool(re.search(r"^\s*(\d+[\.\)]|[a-zA-Z][\.\)])", query)) or
                any(phrase in query_lower for phrase in [
                    "it is using", "it uses", "c language", "hello world",
                    "no input", "does not take any input", "displaying", "my answer",
                    "i think", "because", "output format", "returns", "the condition",
                    "use printf", "printf is", "it should be printf", "low <= high",
                    "returns none", "standard input output", "exit status", "return 0"
                ])
            )
        )

        if is_answering or (prior_assistant_msg and not is_question and not is_confused):
            # 7A: C printf / systems response
            c_answer_match = (
                re.search(r"\bprintf\b", query_lower) or
                "c language" in query_lower or
                ("hello world" in query_lower and ("input" in query_lower or "display" in query_lower or "c" in query_lower)) or
                (re.search(r"\b(c)\b", query_lower) and any(w in query_lower for w in ["language", "code", "syntax"]))
            )
            c_context_match = ("c program" in prior_lower or "print()" in prior_lower or "stdio" in prior_lower or "<stdio.h>" in prior_lower or "formatted output function" in prior_lower or not prior_lower)

            if c_answer_match and c_context_match:
                return (
                    "✅ **Response Verification & Feedback**:\n\n"
                    "**Excellent analysis! You accurately identified the core mechanics:**\n"
                    "• **Language Identification & Function**: Correct—in standard **C**, `printf()` (print formatted) is the standard output function declared in `<stdio.h>`, whereas `print()` is Python syntax.\n"
                    "• **Input/Output Dynamics**: Spot on! It accepts no runtime user input (`void` parameters in `main`) "
                    "and performs a single side-effect: streaming the formatted string to standard output (`stdout`).\n\n"
                    "🎯 **Next Progressive Step (Deepening Systems Understanding)**:\n"
                    "Now, let's explore how the compiler and OS handle this code:\n"
                    "1. Notice the preprocessor directive `#include <stdio.h>` at the top. What does `<stdio.h>` stand for, and why is it necessary before calling `printf`?\n"
                    "2. The function is declared as `int main()`. What does the return value (e.g., `return 0;`) communicate back to the operating system upon exit?"
                )

            # 7B: Binary Search boundary response
            bs_answer_match = any(term in query_lower for term in [
                "low <= high", "single element", "low == high",
                "boundary", "missed", "omitted", "never examined", "off by one",
                "last element", "not examined", "not checked"
            ])
            bs_context_match = ("binary search" in prior_lower or "searchboundaryissue" in prior_lower or "low < high" in prior_lower or (extracted_code and "binary_search" in extracted_code))

            if bs_answer_match and bs_context_match:
                return (
                    "✅ **Response Verification & Feedback**:\n\n"
                    "**Outstanding deduction! You pinpointed the exact boundary invariant:**\n"
                    "• When the search interval narrows such that `low == high`, exactly one candidate element remains at index `low`.\n"
                    "• With the loop condition `while low < high:`, the loop terminates when `low == high` without examining that single element!\n"
                    "• If the target is located at that index, the function incorrectly returns -1.\n\n"
                    "🎯 **Next Progressive Step**:\n"
                    "1. How should the while loop condition be written so that single-element subarrays are evaluated?\n"
                    "2. What is the worst-case time complexity of binary search, and why does dividing by 2 guarantee logarithmic steps?"
                )

            # 7C: Data Science leakage response
            ds_leak_match = any(term in query_lower for term in [
                "leak", "leakage", "test set", "transform", "fit_transform", "scaler", "unseen", "overfit", "mean and std"
            ])
            ds_context_match = (
                "leak" in prior_lower or "leakage" in prior_lower or "scaler" in prior_lower or
                "fit_transform" in prior_lower or "unobserved" in prior_lower or "test data" in prior_lower or
                (extracted_code and "scaler" in extracted_code)
            )

            if ds_leak_match and ds_context_match:
                return (
                    "✅ **Response Verification & Feedback**:\n\n"
                    "**Great pedagogical insight! You correctly diagnosed data leakage:**\n"
                    "• Calling `.fit_transform()` on `X_test` recalculates the mean $\\mu$ and standard deviation $\\sigma$ using the test distribution, leaking test set parameters into the preprocessing pipeline.\n"
                    "• On unseen data, the model must only apply transformation parameters learned strictly from the training split.\n\n"
                    "🎯 **Next Progressive Step**:\n"
                    "1. Which Scikit-Learn method should you call on `X_test` instead of `.fit_transform()`?\n"
                    "2. Why must cross-validation splitting occur before feature scaling rather than after?"
                )

            # 7D: Pandas Inplace response
            pd_inplace_match = any(term in query_lower for term in [
                "returns none", "none", "inplace", "reassign", "overwrites"
            ])
            pd_context_match = ("inplace" in prior_lower or "pandas" in prior_lower or "dropna" in prior_lower or (extracted_code and "dropna" in extracted_code))

            if pd_inplace_match and pd_context_match:
                return (
                    "✅ **Response Verification & Feedback**:\n\n"
                    "**Spot on! You caught the classic Pandas gotcha:**\n"
                    "• In Pandas, operations executed with `inplace=True` mutate the DataFrame directly and return `None`.\n"
                    "• Assigning `df = df.dropna(inplace=True)` sets `df` to `None`, which destroys the DataFrame and triggers AttributeError on downstream calls.\n\n"
                    "🎯 **Next Progressive Step**:\n"
                    "Which of the two idiomatic Pandas patterns would you use to fix this: `df.dropna(inplace=True)` or `df = df.dropna()`?"
                )

            # 7E: Systems header and return code
            sys_match = any(term in query_lower for term in [
                "standard input output", "header", "stdio", "return 0", "exit status", "success", "status code", "terminate", "return 0;", "0"
            ])
            if sys_match and any(kw in prior_lower for kw in ["<stdio.h>", "return 0", "main()", "return;", "what value should", "return type"]):
                return (
                    "✅ **Response Verification & Feedback**:\n\n"
                    "**Excellent systems understanding!**\n"
                    "• In C, `main()` is declared with return type `int`, requiring an integer exit status returned to the host environment.\n"
                    "• Returning `0` from `main()` signals `EXIT_SUCCESS` to the parent process/operating system shell, indicating normal error-free completion.\n\n"
                    "🎯 **Next Progressive Step**:\n"
                    "Update your code editor to replace `return;` with `return 0;`, then click 'Inspect & Debug My Code' to verify!"
                )
            elif sys_match and ("<stdio.h>" in prior_lower or "return 0" in prior_lower or "main()" in prior_lower):
                return (
                    "✅ **Response Verification & Feedback**:\n\n"
                    "**Excellent systems understanding!**\n"
                    "• `<stdio.h>` stands for **Standard Input/Output Header**, providing function prototypes so the compiler can validate arguments and return types for `printf()` and `scanf()`.\n"
                    "• Returning `0` from `main()` signals `EXIT_SUCCESS` to the parent process/operating system shell.\n\n"
                    "🎯 **Check for Mastery**:\n"
                    "What escape sequence would you add inside the formatted string to ensure subsequent terminal output appears on a fresh line?"
                )

            # 7F: General student answer confirmation
            if is_answering:
                return (
                    "✅ **Response Verification**:\n\n"
                    f"You noted: *\"{query}\"*\n\n"
                    "That reasoning is on the right track! You are actively decomposing the problem state.\n\n"
                    "🎯 **Next Step**:\n"
                    "Based on this, what is the immediate next operation or constraint you need to enforce to complete the solution?"
                )

        # ----------------- INTENT 8: BENCHMARK & ACADEMIC INQUIRY -----------------
        if expected_ans or any(kw in query_lower for kw in ["derivative", "integral", "eigenvalue", "matrix", "acceleration", "newton", "ohm"]):
            if "derivative" in query_lower:
                return (
                    "To find the derivative of a polynomial or function, recall the power rule:\n"
                    "$\\frac{d}{dx}[a \\cdot x^n] = a \\cdot n \\cdot x^{n-1}$.\n\n"
                    "💡 **Socratic Guidance**:\n"
                    "1. Apply the power rule to each term individually.\n"
                    "2. What does the constant term differentiate to?\n"
                    "How would you express the differentiated terms?"
                )
            elif "integral" in query_lower or "definite integral" in query_lower:
                return (
                    "To evaluate a definite integral, recall the Fundamental Theorem of Calculus:\n"
                    "$\\int_a^b f(x) dx = F(b) - F(a)$, where $F'(x) = f(x)$.\n\n"
                    "💡 **Socratic Guidance**:\n"
                    "1. What is the antiderivative of the integrand function?\n"
                    "2. Substitute the upper limit and subtract the evaluation at the lower limit.\n"
                    "What value do you obtain for $F(b) - F(a)$?"
                )
            elif "newton" in query_lower or "acceleration" in query_lower:
                return (
                    "Consider the governing physical relationship:\n\n"
                    "💡 **Socratic Guidance**:\n"
                    "• What formula directly connects net external force $F$, inertial mass $m$, and resulting acceleration $a$?\n"
                    "• If given initial velocity $v_0$, final velocity $v$, and time interval $t$, which kinematic definition yields $a = \\frac{\\Delta v}{\\Delta t}$?"
                )

        # ----------------- INTENT 9: DYNAMIC PROMPT ADAPTATION (DEFAULT) -----------------
        # Dynamically adapts to any user inquiry without returning stale code inspections or static templates
        clean_topic = query.rstrip("?.! ")
        return (
            f"💡 **Socratic Inquiry: Exploring '{clean_topic}'**:\n\n"
            f"Let's explore your inquiry methodically through active reasoning:\n"
            f"1. **Foundational Concept**: How do you define the core mechanics or data structures involved in this concept?\n"
            f"2. **State & Invariants**: What preconditions, inputs, or transformations must be preserved during execution?\n"
            f"3. **Practical Application**: If you implemented this in code, what edge cases or boundary conditions would you test first?\n\n"
            f"How would you begin approaching the first step?"
        )
