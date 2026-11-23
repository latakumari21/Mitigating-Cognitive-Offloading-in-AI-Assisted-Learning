# Mitigating Cognitive Offloading in AI-Assisted Learning

Interactive educational tool and evaluation benchmark exploring Socratic inquiry versus direct solutions in artificial intelligence learning environments.

## Features
- **Scaffolding Ladder**: Three levels of guidance from conceptual inquiries to diagnostic hints.
- **Answer Guardrails**: Sanitizes outputs to prevent direct answers from spoiling student problem solving.
- **Cognitive Metrics**: Estimates cognitive depth on Bloom's taxonomy.

## Quickstart
1. Install requirements: `pip install -r requirements.txt`
2. Run test suite: `python -m unittest discover tests`
3. Execute benchmark: `python experiments/run_benchmark.py`
4. Generate evaluation plots: `python experiments/generate_charts.py`
5. Start user interface: `streamlit run app.py`

## Project Structure
- `app.py`: Interactive interface.
- `src/`: Core logic modules.
- `data/`: 30 academic benchmark questions.
- `experiments/`: Benchmark and charting scripts.
- `results/`: CSV outputs and generated figures.
- `tests/`: Automated unit and integration tests.
