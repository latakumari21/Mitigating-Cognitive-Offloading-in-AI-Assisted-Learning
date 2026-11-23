# PROJECT SYNOPSIS

## 1. Project Title
**Mitigating Cognitive Offloading in AI-Assisted Learning: An Empirical Study of Socratic Scaffolding vs. Direct LLM Response**

## 2. Domain & Area of Study
- **Domain:** Artificial Intelligence in Education (AIEd) / Generative AI
- **Sub-area:** Pedagogical Alignment, Guardrail Engineering, Cognitive Load Theory

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
3. **Prevent Direct Answer Leakage:** Deploy an automated validation filter to detect and redact premature answer disclosures.
4. **Conduct Empirical Benchmarking:** Evaluate the system across 30 standardized academic problems in Mathematics, Computer Science, and Physics against an unconstrained baseline.

## 6. Proposed Methodology & Architecture
The system consists of three decoupled layers:
- **Interaction Layer:** Interactive Streamlit web interface supporting multi-turn pedagogical dialogue.
- **Scaffolding & Guardrail Engine:** Dynamic system prompt synthesis combined with regex-driven string and numerical leakage filters.
- **Evaluation Framework:** Automated scoring of Answer Leakage Rate, Bloom's Revised Taxonomy cognitive level (Tiers 1-6), and composite Pedagogical Alignment Scores.

## 7. Key Findings & Empirical Results
Benchmarking across 30 standardized STEM problems yielded:
- **Answer Leakage Rate:** Reduced from 100.0% (Baseline) to 0.0% (SocraticGuard).
- **Cognitive Demand (Bloom's Taxonomy):** Elevated from 2.00 (Recall/Understand) to 3.00+ (Apply/Analyze).
- **Pedagogical Alignment Index:** Increased from 1.00/5.00 to 3.90/5.00.

## 8. Hardware & Software Requirements
- **Language & Runtime:** Python 3.10+
- **Core Libraries:** `streamlit`, `google-genai`, `pandas`, `matplotlib`, `numpy`
- **Testing Harness:** Python `unittest` framework

## 9. Conclusion & Academic Significance
This project demonstrates that prompt-engineered pedagogical guardrails can prevent cognitive offloading in generative AI environments. By structuring interactions around Socratic inquiry, generative tools can foster genuine conceptual understanding rather than academic dependency.
