# DAYANANDA SAGAR UNIVERSITY
### SCHOOL OF COMPUTER APPLICATIONS
**Kudlu Gate, Hosur Road, Bengaluru &ndash; 560068**

---

# A Project Synopsis On
## MITIGATING COGNITIVE OFFLOADING IN AI-ASSISTED LEARNING
**An Empirical Study of Socratic Scaffolding vs. Direct LLM Response**

*Submitted as part of the RTD Open Elective subject*  
**MASTER OF COMPUTER APPLICATIONS (MCA)**

**Submitted by:**  
**Lata Kumari**  
**USN / Reg. No:** SCA25MCA157  

**Under the guidance of:**  
**Dr. Santosh Kumar J**  

**Date:** 24-Nov-2026  
**Institution:** Dayananda Sagar University, Bengaluru &ndash; 560068  

---

## 1. Project Title
**Mitigating Cognitive Offloading in AI-Assisted Learning: An Empirical Study of Socratic Scaffolding vs. Direct LLM Response**

## 2. Domain & Area of Study
- **Domain:** Artificial Intelligence in Education (AIEd) / Generative AI
- **Sub-area:** Pedagogical Alignment, Guardrail Engineering, Cognitive Load Theory, Computing Education

## 3. Introduction & Background
The widespread adoption of foundation Large Language Models (LLMs) across secondary and tertiary education has reshaped student learning workflows. While these systems offer rapid query resolution, their default configuration operates as direct solution oracles. Consequently, students routinely exhibit "cognitive offloading"—the practice of bypassing metacognitive struggle and problem-solving reasoning in favor of copy-pasting automated outputs. This trend induces what cognitive psychologists term "competence collapse," wherein learners produce correct academic deliverables without internalizing foundational knowledge.

## 4. Problem Statement
Current generative AI interfaces lack pedagogical constraints. When presented with standard academic inquiries in STEM disciplines, unconstrained LLMs exhibit an Answer Leakage Rate approaching 100%, directly supplying equations, numerical answers, and code blocks. There is an urgent need for an automated, lightweight pedagogical scaffolding layer that preserves learner agency by enforcing the Socratic method and active inquiry.

## 5. Objectives
1. **Design and Implement SocraticGuard:** Develop a modular pedagogical guardrail system that intercepts student prompts and enforces tiered Socratic guidance.
2. **Implement a 3-Tier Scaffolding Engine:**
   - *Tier 1 (Conceptual Probe):* Evaluate understanding of fundamental principles without revealing procedures.
   - *Tier 2 (Strategic Formulation):* Direct attention to governing equations or algorithmic structures.
   - *Tier 3 (Diagnostic Correction):* Identify and address specific misconceptions.
3. **Multi-Language Static Code Inspection:**
   - *C/C++:* Non-void `return;` detection, missing `return 0;`, `print` vs `printf`, format specifiers, and uninitialized variables.
   - *Python:* Abstract Syntax Tree (AST) inspection, bare except, and recursion termination.
   - *Data Science:* Machine learning data leakage and Pandas in-place reassignment checks.
4. **Active Student Response Verification:** Parse and affirm correct student deductions, escalating inquiry depth.
5. **Conduct Empirical Benchmarking:** Evaluate the system across 30 standardized academic problems in Mathematics, Computer Science, and Physics against an unconstrained baseline.

## 6. Proposed Methodology & Architecture
The system consists of three decoupled layers:
- **Interaction Layer:** Interactive Streamlit web interface with a side-by-side code editor and Socratic dialogue workspace.
- **Scaffolding & Guardrail Engine:** Static AST parsing, dynamic system prompt synthesis, and regex-driven code leakage filters.
- **Evaluation Framework:** Automated scoring of Answer Leakage Rate, Bloom's Revised Taxonomy cognitive level (Tiers 1-6), and composite Pedagogical Alignment Scores.

## 7. Key Findings & Empirical Results
Benchmarking across 30 standardized STEM problems yielded:
- **Answer Leakage Rate:** Reduced from 100.0% (Baseline) to **0.0% (SocraticGuard)**.
- **Cognitive Demand (Bloom's Taxonomy):** Elevated from 2.00 (Recall/Understand) to **3.00+ (Apply/Analyze)**.
- **Pedagogical Alignment Index:** Increased from 1.00/5.00 to **3.90/5.00**.

| Metric | Baseline LLM | SocraticGuard (Proposed) | Pedagogical Impact |
| :--- | :---: | :---: | :--- |
| **Answer Leakage Rate (%)** | 100.0% | **0.0%** | Direct answer disclosure completely eliminated |
| **Bloom's Taxonomy Level (1-6)** | 2.00 | **3.00+** | +1.00 Tier elevation in cognitive demand |
| **Pedagogical Alignment Index (1-5)** | 1.00 / 5.00 | **3.90 / 5.00** | +2.90 points improvement in active learning |

## 8. Hardware & Software Requirements
- **Language & Runtime:** Python 3.10+ (tested on Python 3.14.3)
- **Core Libraries:** `streamlit`, `google-genai`, `pandas`, `matplotlib`, `numpy`
- **Testing Harness:** Python `unittest` framework (66 automated test cases, 100% passing)

## 9. Conclusion & Academic Significance
This project demonstrates that prompt-engineered pedagogical guardrails can prevent cognitive offloading in generative AI environments. By structuring interactions around Socratic inquiry, generative tools can foster genuine conceptual understanding rather than academic dependency.
