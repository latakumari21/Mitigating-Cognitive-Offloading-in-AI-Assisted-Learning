# Mitigating Cognitive Offloading in AI-Assisted Learning

Interactive educational platform, static code inspection engine, and evaluation benchmark exploring Socratic scaffolding versus direct LLM response in artificial intelligence learning environments.

Developed at **Dayananda Sagar University (DSU)**, School of Computer Applications, Bengaluru, Karnataka, India.

---

## Key Features

- **Multi-Language Bug Inspector & Static Guard (src/code_inspector.py)**:
  - Deterministic AST inspection for Python (syntax errors, mutable defaults, bare exceptions, unbounded recursion).
  - Scope and return type invariant analysis for C/C++ (identifies missing 
eturn 0;, bare 
eturn; in non-void int main(), print vs. printf mismatches, format specifier discrepancies).
  - Machine learning and data science pipeline guards (detects data leakage across train/test splits and improper inplace mutations).
- **Three-Tier Scaffolding Ladder (src/socratic_engine.py)**:
  - **Tier 1 (Conceptual Probing)**: Tests foundational definitions, invariants, and mental models without revealing syntax.
  - **Tier 2 (Strategic Formulation)**: Guides algorithms, data structures, and edge-case reasoning.
  - **Tier 3 (Diagnostic Clues)**: Isolates the specific line/mechanism causing the bug with reflective questions.
- **Active Verification & Multi-Turn Context**:
  - Validates student deductions in real-time before advancing to subsequent problem-solving stages.
- **Cognitive Demand & Leakage Evaluation**:
  - Benchmarked across 30 standardized academic STEM problems in Mathematics, Computer Science, and Physics.
  - Reduces Answer Leakage Rate (ALR) from **100.0% to 0.0%** and elevates Bloom\'s Taxonomy level to **3.00+ (Apply/Analyze)**.

---

## Quickstart

1. **Install requirements**:
   `ash
   pip install -r requirements.txt
   `
2. **Run complete verification test suite (66 tests)**:
   `ash
   python -m unittest discover -s tests
   `
3. **Execute empirical benchmark**:
   `ash
   python experiments/run_benchmark.py
   `
4. **Generate evaluation charts**:
   `ash
   python experiments/generate_charts.py
   `
5. **Start interactive web application**:
   `ash
   streamlit run app.py
   `

---

## Project Structure

`	ext
├── app.py                     # Streamlit web interface with dual workspace & inspector
├── requirements.txt           # Project dependencies (streamlit, pandas, matplotlib, etc.)
├── src/                       # Core engine modules
│   ├── code_inspector.py      # Multi-language static analyzer (C/C++, Python, Data Science)
│   ├── socratic_engine.py     # Three-tier Socratic scaffolding & active verification
│   ├── mock_llm.py            # Conversational reasoning and pedagogical mock LLM
│   ├── baseline_engine.py     # Unconstrained direct LLM solution baseline
│   └── evaluator.py           # Bloom\'s taxonomy, cognitive demand, and leakage metrics
├── tests/                     # Automated test suite (66 unit & integration tests)
│   ├── test_code_inspector.py # Tests for AST analysis, C returns, and DS leakage
│   ├── test_flow_and_interaction.py # Tests for interactive workflow & state retention
│   ├── test_socratic_engine.py# Tests for tier ladders and prompt generation
│   ├── test_evaluator.py      # Tests for scoring algorithms
│   └── test_benchmark.py      # Tests for dataset integrity
├── data/                      # 30 curated STEM problems across Math, CS, and Physics
├── experiments/               # Empirical benchmark execution and visualization scripts
├── results/                   # Benchmark CSVs and comparison figures
├── figures/                   # DSU institutional branding and report assets
└── docs/                      # Formal academic documentation and publications
    ├── Research_Paper_IEEE.pdf# Publication-ready IEEE 2-column conference paper
    ├── Research_Paper_IEEE.tex# Standard IEEEtran LaTeX source code
    ├── Research_Paper_IEEE.md # Markdown version of the IEEE research paper
    ├── Project_Report.pdf     # Complete MCA Academic Project Report (with DSU cover)
    ├── Project_Report.md      # Full markdown project report
    ├── Project_Synopsis.pdf   # Academic Project Synopsis
    └── Project_Synopsis.md    # Full markdown project synopsis
`

---

## Publications & Academic Documentation

All academic documentation and research papers are available in [docs/](docs/):
- **IEEE Conference Research Paper**: [docs/Research_Paper_IEEE.pdf](docs/Research_Paper_IEEE.pdf) | [docs/Research_Paper_IEEE.tex](docs/Research_Paper_IEEE.tex)
- **Project Report**: [docs/Project_Report.pdf](docs/Project_Report.pdf) | [docs/Project_Report.md](docs/Project_Report.md)
- **Project Synopsis**: [docs/Project_Synopsis.pdf](docs/Project_Synopsis.pdf) | [docs/Project_Synopsis.md](docs/Project_Synopsis.md)
