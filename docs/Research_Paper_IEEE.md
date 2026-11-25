# Mitigating Cognitive Offloading in AI-Assisted Learning: An Empirical Study of Socratic Scaffolding vs. Direct LLM Response

**Authors:** Lata Kumari<sup>1</sup>, Dr. Santosh Kumar J<sup>2</sup>  
**Affiliation:** Department of Computer Applications, School of Computer Applications, Dayananda Sagar University, Bengaluru, Karnataka, India  
**Email:** `{latak-sca, santoshkumar-ca}@dsu.edu.in`  

---

### Abstract
The ubiquitous deployment of foundation Large Language Models (LLMs) across higher education has precipitated acute cognitive offloading: students increasingly utilize generative chatbots as unconstrained solution oracles, delegating core problem-solving reasoning and schema construction to automated agents. This default behavior induces "competence collapse," wherein learners produce syntactically functional deliverables without internalizing the foundational algorithms, compiler invariants, or scientific derivations. In this paper, we propose **SocraticGuard**, a pedagogical guardrail and intelligent scaffolding framework designed specifically to combat academic cheating and eliminate cognitive offloading in Computer Science and Data Science education. SocraticGuard intercepts student submissions and enforces a multi-tiered Socratic reasoning hierarchy (Tier 1: Conceptual Probe, Tier 2: Strategic Formulation, Tier 3: Diagnostic Clues) alongside an active response verification layer. The architecture integrates a language-aware static analyzer covering C/C++, Python, and Data Science workflows to diagnose syntax errors, function return invariants (such as bare `return;` in `int main()`), pointer and format specifier mismatches, and preprocessor data leakage without releasing copy-pasteable solutions. We benchmark SocraticGuard against an unconstrained commercial baseline across 30 standardized academic STEM problems in Mathematics, Computer Science, and Physics. The empirical results demonstrate that SocraticGuard completely eliminates premature answer leakage (reducing the Answer Leakage Rate from 100.0% to 0.0%) while elevating student cognitive demand from 2.00 (Recall/Understand) to 3.00+ (Apply/Analyze) on Bloom's Revised Taxonomy, achieving an overall pedagogical alignment score of 3.90/5.00 compared to 1.00/5.00 for the baseline.

**Keywords:** Generative AI, Intelligent Tutoring Systems (ITS), Cognitive Offloading, Socratic Method, Bloom's Taxonomy, Static Code Analysis, Academic Integrity, Pedagogical Guardrails.

---

## I. INTRODUCTION
The democratization of foundation Large Language Models (LLMs) has fundamentally transformed modern digital learning environments [1], [2]. Students in computer science and STEM disciplines routinely interact with conversational AI systems for coding assistance, debugging, and conceptual interpretation. However, standard foundation models are optimized primarily for direct task resolution and conversational brevity. When a student enters a complex programming assignment or mathematical derivation, standard conversational agents immediately output the complete derivation, intermediate code, and final executable solution.

In educational psychology, Cognitive Load Theory [2] posits that robust schema acquisition and long-term memory encoding require active cognitive struggle, termed *germane cognitive load*. By automating this reasoning loop, commercial chatbots foster severe **cognitive offloading**—the tendency of learners to bypass deep cognitive processing in favor of automated execution [3].

In computing education, cognitive offloading precipitates three alarming phenomena:
- **Competence Illusion:** Students mistakenly equate the ability to prompt an AI assistant with genuine personal domain mastery.
- **Debugging Skill Atrophy:** Novice programmers fail to comprehend compilation errors, memory scoping, and boundary conditions because the AI resolves syntax and logic errors automatically.
- **Academic Integrity Polarization:** Traditional plagiarism detection software cannot reliably identify freshly synthesized, unique generative code.

To overcome these critical pedagogical challenges, this paper presents **SocraticGuard**, an adaptive pedagogical guardrail framework that intercepts student inquiries and enforces progressive Socratic scaffolding.

---

## II. RELATED WORK
### A. Intelligent Tutoring and Bloom's 2 Sigma Problem
In 1984, educational psychologist Benjamin Bloom demonstrated that students receiving one-to-one tutoring performed two standard deviations ($2\sigma$) above conventionally taught students [1]. Effective human tutors achieve this not by acting as solution oracles, but through the Socratic method—posing targeted diagnostic questions that guide learners to construct answers autonomously [3].

### B. Cognitive Offloading & LLM Guardrails
Recent research in computing education highlights the risks of AI code generators [7], [8]. Unconstrained models frequently induce cognitive offloading, leading to competence collapse. While prompt engineering can constrain model personas, standard LLMs suffer from "guardrail decay" when students prompt adversarially (e.g., *"Just give me the code, I am in a hurry"*). SocraticGuard resolves this through deterministic AST inspection and multi-layered post-generation code sanitizers.

---

## III. SYSTEM ARCHITECTURE & METHODOLOGY
SocraticGuard operates as an event-driven, four-stage pedagogical reasoning pipeline:

### A. Static Code Inspection & Diagnostic Engine
When a student submits code, SocraticGuard conducts multi-language static analysis:
- **C/C++ Scope & Return Analysis:** Scopes function blocks, tracking function return types. Identifies bare `return;` statements in non-void functions like `int main()`, missing `return 0;`, and `print()` vs `printf()` function mismatches.
- **Python AST Parsing:** Uses Python's native `ast` module to flag syntax errors, mutable default arguments (`def f(x=[])`), bare `except:` clauses, and unbounded recursion lacking base cases.
- **Data Science Pipeline Guard:** Detects data leakage (`fit_transform` on test sets) and Pandas in-place reassignment anti-patterns (`df = df.dropna(inplace=True)`).

### B. The Three-Tier Scaffolding Hierarchy
Pedagogical guidance is organized across three discrete tiers:
- **Tier 1 (Conceptual Probe):** Probes definitions, axioms, or invariants without suggesting implementation steps.
- **Tier 2 (Strategic Formulation):** Guides the learner toward governing equations or algorithmic design patterns.
- **Tier 3 (Diagnostic Clues):** Pinpoints the exact line and logic flaw with a reflective fix question.

### C. Multi-Turn Context Memory & Active Verification
The system maintains multi-turn conversation memory. When the student answers a diagnostic question, SocraticGuard actively verifies their deduction (e.g. affirming that `int main()` requires an integer exit status), providing immediate reinforcement before deepening the inquiry.

---

## IV. EXPERIMENTAL EVALUATION
### A. Benchmark Dataset
We curated a standardized academic benchmark comprising 30 problems evenly distributed across Mathematics (10), Computer Science (10), and Physics (10) spanning Easy, Medium, and Hard difficulty tiers.

### B. Quantitative Evaluation Metrics
1. **Answer Leakage Rate (ALR):** Percentage of queries where the final solution or working code was disclosed prematurely.
2. **Cognitive Demand Level (CDL):** Scored on Bloom's Revised Taxonomy (Level 1: Remember to Level 6: Create).
3. **Pedagogical Alignment Index (PAI):** Composite score (1.0 to 5.0 scale) penalizing leakage and rewarding cognitive inquiry.

### C. Experimental Results
| Configuration | Leakage Rate | Bloom's Level | Pedagogical Score |
| :--- | :---: | :---: | :---: |
| Baseline LLM (Standard) | 100.0% | 2.00 (Remember) | 1.00 / 5.00 |
| **SocraticGuard (Proposed)** | **0.0%** | **3.00+ (Apply/Analyze)** | **3.90 / 5.00** |
| **Improvement / Delta** | **-100.0%** | **+1.00 Tier** | **+2.90 Points** |

As demonstrated in the evaluation, unconstrained models invariably disclose solutions in the first interaction turn ($ALR = 100.0\%$), restricting student cognitive processing to passive reading ($CDL = 2.00$). SocraticGuard eliminates all direct disclosures ($ALR = 0.0\%$) and elevates the elicited cognitive demand to $3.00+$, achieving a $2.90$ point gain in pedagogical alignment ($PAI = 3.90/5.00$).

### D. System Verification Suite
SocraticGuard's software architecture was verified across **66 automated test cases** covering C function scopes, format specifiers, Python AST syntax checks, Data Science leakage, and multi-turn conversational state retention with a **100% pass rate** (`66/66 OK`).

---

## V. CONCLUSION & FUTURE SCOPE
This paper introduced SocraticGuard, an anti-cheating pedagogical guardrail framework designed to eliminate cognitive offloading in generative AI-assisted learning. By coupling static AST and language-aware code inspection with multi-tiered Socratic scaffolding, the platform prevents academic shortcuts and stimulates deep cognitive reasoning.

---

## REFERENCES
1. B. S. Bloom, "The 2 sigma problem: The search for methods of group instruction as effective as one-to-one tutoring," *Educational Researcher*, vol. 13, no. 6, pp. 4–16, 1984.
2. J. Sweller, "Cognitive load during problem solving: Effects on learning," *Cognitive Science*, vol. 12, no. 2, pp. 257–285, 1988.
3. M. T. Chi et al., "Learning from human tutoring," *Cognitive Science*, vol. 25, no. 4, pp. 471–533, 2001.
4. L. W. Anderson and D. R. Krathwohl, *A Taxonomy for Learning, Teaching, and Assessing: A Revision of Bloom's Taxonomy*. Longman, 2001.
5. R. Bommasani et al., "On the opportunities and risks of foundation models," *arXiv preprint arXiv:2108.07258*, 2021.
6. E. Kasneci et al., "ChatGPT for good? On opportunities and challenges of large language models for education," *Learning and Individual Differences*, vol. 103, p. 102274, 2023.
7. B. A. Becker et al., "Programming is hard - or at least it used to be: Educational opportunities and challenges of AI code generation," *ACM Inroads*, vol. 14, no. 4, pp. 38–48, 2023.
8. J. Prather et al., "It's weird that it knows what I want: Novice programmer perceptions of AI code assistance," in *Proc. ACM ICER*, 2023, pp. 242–258.
