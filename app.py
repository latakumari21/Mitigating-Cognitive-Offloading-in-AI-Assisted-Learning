"""
Interactive Web Application for SocraticGuard:
Mitigating Cognitive Offloading in AI-Assisted Learning.
"""

import os
import streamlit as st
from src.socratic_engine import SocraticEngine
from src.baseline_engine import BaselineEngine
from src.evaluator import PedagogicalEvaluator
from src.mock_llm import MockLLMService

st.set_page_config(
    page_title="SocraticGuard: Mitigating Cognitive Offloading",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 SocraticGuard: AI-Assisted Pedagogical Scaffolding")
st.markdown(
    "**Mitigating Cognitive Offloading in AI-Assisted Learning**: "
    "An interactive framework designed to replace unconstrained answer generation with Socratic inquiry and progressive scaffolding."
)

# Sidebar Configuration
st.sidebar.header("⚙️ Configuration")
mode = st.sidebar.radio(
    "Select Operating Mode",
    ["SocraticGuard (Pedagogical Intervention)", "Standard LLM (Unconstrained Baseline)"]
)

api_key = st.sidebar.text_input("Gemini API Key (Optional)", type="password", help="Leave blank to use internal offline demonstration engine")
hint_level = st.sidebar.slider("Scaffolding Hint Level", min_value=1, max_value=3, value=1, help="1: Concept Probe, 2: Strategic Formula, 3: Diagnostic Clue")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Live Metrics Explained")
st.sidebar.markdown("- **Answer Leakage:** Whether final answers are prematurely yielded.")
st.sidebar.markdown("- **Bloom's Level:** Cognitive demand (1: Recall to 5: Evaluate).")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "metrics" in msg:
            st.caption(f"📈 *Cognitive Level: Bloom's Tier {msg['metrics']['blooms']} | Leakage Guardrail: {msg['metrics']['leakage_status']}*")

user_input = st.chat_input("Enter your academic inquiry (Math, CS, Physics)...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    socratic_engine = SocraticEngine()
    baseline_engine = BaselineEngine()
    evaluator = PedagogicalEvaluator()
    mock_service = MockLLMService()

    with st.chat_message("assistant"):
        with st.spinner("Generating pedagogical response..."):
            if "SocraticGuard" in mode:
                prompt = socratic_engine.build_prompt(user_input, hint_level=hint_level)
                
                # Check for live client or fallback
                if api_key and len(api_key) > 5:
                    try:
                        from google import genai
                        client = genai.Client(api_key=api_key)
                        res = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt
                        )
                        raw_response = res.text
                    except Exception as e:
                        st.warning(f"API Error ({str(e)}). Utilizing internal engine.")
                        raw_response = mock_service.generate_response(prompt, mode="socratic")
                else:
                    raw_response = mock_service.generate_response(prompt, mode="socratic")
                
                final_response = socratic_engine.sanitize_response(raw_response, "")
                blooms = evaluator.estimate_blooms_taxonomy_level(final_response)
                leakage_status = "Active & Guarded"
            else:
                prompt = baseline_engine.build_prompt(user_input)
                if api_key and len(api_key) > 5:
                    try:
                        from google import genai
                        client = genai.Client(api_key=api_key)
                        res = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt
                        )
                        raw_response = res.text
                    except Exception as e:
                        raw_response = mock_service.generate_response(prompt, mode="baseline")
                else:
                    raw_response = mock_service.generate_response(prompt, mode="baseline")
                
                final_response = raw_response
                blooms = evaluator.estimate_blooms_taxonomy_level(final_response)
                leakage_status = "Unfiltered Direct Answer"

            st.markdown(final_response)
            st.caption(f"📈 *Cognitive Level: Bloom's Tier {blooms} | Leakage Guardrail: {leakage_status}*")
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": final_response,
                "metrics": {"blooms": blooms, "leakage_status": leakage_status}
            })
