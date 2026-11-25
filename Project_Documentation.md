# SYSTEM DOCUMENTATION: SOCRATICGUARD

## 1. System Overview
**SocraticGuard** is a software framework and empirical benchmark designed to mitigate cognitive offloading in generative AI-assisted learning. The system transforms foundation language models from passive solution dispensers into interactive pedagogical tutors.

---

## 2. Directory & Component Structure

```
Mitigating-Cognitive-Offloading-in-AI-Assisted-Learning/
├── app.py                      # Main Streamlit web application
├── requirements.txt            # Python environment dependencies
├── README.md                   # Repository overview and quickstart
├── src/                        # Core system source modules
│   ├── __init__.py
│   ├── socratic_engine.py      # Scaffolding prompts & answer sanitization
│   ├── baseline_engine.py      # Standard unconstrained LLM baseline
│   ├── evaluator.py            # Quantitative metrics (Bloom's, Leakage, Score)
│   └── mock_llm.py             # Deterministic offline evaluation service
├── data/
│   └── benchmark_dataset.json  # 30 curated STEM benchmark questions
├── experiments/
│   ├── run_benchmark.py        # Automated benchmarking batch execution
│   └── generate_charts.py      # Publication-quality figure generation
├── results/
│   ├── benchmark_results.csv   # Raw experimental evaluation metrics
│   ├── leakage_comparison.png  # Figure 1: Answer Leakage Rate comparison
│   └── blooms_taxonomy_distribution.png # Figure 2: Bloom's Taxonomy comparison
├── tests/
│   ├── test_socratic_engine.py # Unit tests for scaffolding & leakage logic
│   ├── test_evaluator.py       # Unit tests for evaluation scoring functions
│   └── test_benchmark.py       # Integration tests for end-to-end flow
└── docs/                       # Project documentation, reports, and paper
```

---

## 3. Module Specifications

### 3.1 `src/socratic_engine.py`
- **Class `SocraticEngine`**:
  - `build_prompt(user_question, hint_level, context)`: Constructs dynamic system instructions based on the requested scaffolding tier (Tier 1: Conceptual Probe, Tier 2: Strategic Formulation, Tier 3: Diagnostic Clue).
  - `detect_answer_leakage(response_text, ground_truth_answer)`: Substring and token inspection checking whether the target solution has been leaked.
  - `sanitize_response(response_text, ground_truth_answer)`: Guardrail fallback filter replacing leaked text with a reflective pedagogical prompt.

### 3.2 `src/baseline_engine.py`
- **Class `BaselineEngine`**:
  - `build_prompt(user_question)`: Standard zero-shot instruction directing the model to generate the immediate, comprehensive solution.

### 3.3 `src/evaluator.py`
- **Class `PedagogicalEvaluator`**:
  - `calculate_answer_leakage(response, expected_answer)`: Binary scoring (0.0 or 1.0) of premature answer exposure.
  - `estimate_blooms_taxonomy_level(response)`: Heuristic assessment of cognitive engagement categorized into Bloom's Revised Taxonomy (Level 1: Recall to Level 5: Evaluate/Analyze).
  - `compute_pedagogical_alignment(leakage, blooms_level)`: Normalized composite index on a 1.0 to 5.0 scale.

### 3.4 `src/mock_llm.py`
- **Class `MockLLMService`**:
  - Provides deterministic, offline responses for both Baseline and Socratic modes to support reproducible testing and benchmarking in offline or air-gapped environments.

---

## 4. Benchmark Dataset

Located at `data/benchmark_dataset.json`, the dataset comprises 30 standardized academic problems evenly distributed across three STEM domains:
- **Mathematics (10 questions):** Calculus, Linear Algebra, Probability, Differential Equations.
- **Computer Science (10 questions):** Algorithms, Data Structures, Operating Systems, Cryptography.
- **Physics (10 questions):** Classical Mechanics, Electromagnetism, Thermodynamics, Quantum Mechanics.

Each entry contains:
- `id`: Unique identifier (e.g., `MATH-01`, `CS-05`, `PHYS-03`).
- `subject`: Domain discipline.
- `question`: Precise problem statement.
- `answer`: Ground truth solution string.
- `difficulty`: `Easy`, `Medium`, or `Hard`.

---

## 5. Execution & Verification

### Running Unit & Integration Tests:
```bash
python -m unittest discover -s tests
```

### Running the Empirical Benchmark:
```bash
python experiments/run_benchmark.py
```

### Generating Visualization Figures:
```bash
python experiments/generate_charts.py
```

### Launching the Streamlit Web Application:
```bash
streamlit run app.py
```
