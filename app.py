"""
SocraticGuard: Anti-Cheating & Adaptive Pedagogical Reasoning Platform
Specifically engineered for Computer Science & Data Science Education.
Combats cognitive offloading by replacing direct code generation with interactive Socratic scaffolding.
"""

import os
import streamlit as st
from src.socratic_engine import SocraticEngine
from src.baseline_engine import BaselineEngine
from src.evaluator import PedagogicalEvaluator
from src.mock_llm import MockLLMService
from src.code_inspector import CodeInspector

st.set_page_config(
    page_title="SocraticGuard: Anti-Cheating Pedagogical Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished educational UI and clear layout
st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.1rem;
    }
    .sub-header {
        font-size: 0.98rem;
        color: #475569;
        margin-bottom: 0.8rem;
    }
    .flow-banner {
        background: linear-gradient(90deg, #EFF6FF 0%, #F0FDF4 100%);
        border: 1px solid #BFDBFE;
        border-radius: 8px;
        padding: 8px 14px;
        font-size: 0.92rem;
        color: #1E40AF;
        margin-bottom: 1rem;
        display: flex;
        justify-content: space-between;
    }
    .badge-socratic {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-baseline {
        background-color: #FDE8E8;
        color: #9B1C1C;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .stTextArea textarea {
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 0.92rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🎓 SocraticGuard: Anti-Cheating Pedagogical Platform</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">'
    'Engineered for <b>Computer Science</b> and <b>Data Science</b> education to eliminate cognitive offloading. '
    'Instead of handing you raw code, SocraticGuard inspects your work, detects bugs, verifies your responses, '
    'and guides you to solve problems independently.'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="flow-banner">'
    '<span><b>Platform Workflow:</b> 1️⃣ Paste or write code ➔ 2️⃣ Click "Inspect My Code" ➔ 3️⃣ SocraticGuard diagnoses bugs ➔ 4️⃣ Answer questions in chat to fix your code</span>'
    '</div>',
    unsafe_allow_html=True
)

# ----------------- SIDEBAR CONFIGURATION -----------------
st.sidebar.header("⚙️ Pedagogical Control Center")

mode = st.sidebar.radio(
    "Operating Mode",
    ["SocraticGuard (Pedagogical Scaffolding)", "Standard LLM Baseline (Unconstrained Direct Code)"],
    help="Compare how SocraticGuard prevents cheating vs how standard LLMs dispense direct code."
)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Progressive Scaffolding Tier")
hint_level = st.sidebar.select_slider(
    "Scaffolding Level",
    options=[1, 2, 3],
    value=1,
    format_func=lambda x: {
        1: "Tier 1: Conceptual Probe",
        2: "Tier 2: Strategic Formulation",
        3: "Tier 3: Diagnostic Clue"
    }[x],
    help="Tier 1 probes definitions and assumptions; Tier 2 guides structural approaches; Tier 3 pinpoints code flaws."
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔑 Live Model Settings")
api_key = st.sidebar.text_input(
    "Google Gemini API Key (Optional)",
    type="password",
    help="Leave blank to use the internal offline Socratic reasoning and code inspection engine."
)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Anti-Cheating Telemetry")
if "SocraticGuard" in mode:
    st.sidebar.markdown('<span class="badge-socratic">🛡️ Anti-Cheating Shield: ACTIVE</span>', unsafe_allow_html=True)
    st.sidebar.caption("• Direct copy-paste code generation is intercepted and blocked.")
    st.sidebar.caption("• AST and C/Python/DS static analysis pinpoints logic bugs.")
    st.sidebar.caption("• Enforces active inquiry (Bloom's Taxonomy Tier 3-5).")
else:
    st.sidebar.markdown('<span class="badge-baseline">⚠️ Anti-Cheating Shield: DISABLED</span>', unsafe_allow_html=True)
    st.sidebar.caption("• Dispenses full working code directly, triggering cognitive offloading.")

DEFAULT_STUDENT_CODE = (
    "#include<stdio.h>\n"
    "int main(){\n"
    '    print("helloe wrold");  // Notice: print vs printf\n'
    "    return 0;\n"
    "}\n"
)

# ----------------- SESSION STATE -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "code_editor" not in st.session_state:
    st.session_state.code_editor = DEFAULT_STUDENT_CODE

if "student_code" not in st.session_state:
    st.session_state.student_code = st.session_state.code_editor

if st.sidebar.button("🗑️ Reset Chat & Context", use_container_width=True):
    st.session_state.messages = []
    st.session_state.code_editor = DEFAULT_STUDENT_CODE
    st.session_state.student_code = DEFAULT_STUDENT_CODE
    st.rerun()

# ----------------- MAIN TWO-COLUMN WORKSPACE -----------------
col_code, col_chat = st.columns([1.05, 1.15], gap="medium")

# ===================== LEFT COLUMN: CODE EDITOR =====================
with col_code:
    st.subheader("💻 Step 1: Student Code Workspace")
    
    st.caption("Load a quick example or write your own code below:")
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    with p_col1:
        if st.button("C Hello World", help="C program with print vs printf bug", use_container_width=True):
            st.session_state.code_editor = DEFAULT_STUDENT_CODE
            st.session_state.student_code = DEFAULT_STUDENT_CODE
            st.session_state.messages = []
            st.rerun()

    with p_col2:
        if st.button("CS: Binary Search", help="Binary search with boundary off-by-one bug", use_container_width=True):
            bs_sample = (
                "def binary_search(arr, target):\n"
                "    low = 0\n"
                "    high = len(arr) - 1\n\n"
                "    while low < high:  # Boundary bug\n"
                "        mid = (low + high) // 2\n"
                "        if arr[mid] == target:\n"
                "            return mid\n"
                "        elif arr[mid] < target:\n"
                "            low = mid + 1\n"
                "        else:\n"
                "            high = mid - 1\n"
                "    return -1\n"
            )
            st.session_state.code_editor = bs_sample
            st.session_state.student_code = bs_sample
            st.session_state.messages = []
            st.rerun()

    with p_col3:
        if st.button("DS: ML Leakage", help="Data leakage: fit_transform on test set", use_container_width=True):
            ml_sample = (
                "import pandas as pd\n"
                "from sklearn.preprocessing import StandardScaler\n"
                "from sklearn.model_selection import train_test_split\n\n"
                "scaler = StandardScaler()\n"
                "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)\n\n"
                "X_train_scaled = scaler.fit_transform(X_train)\n"
                "X_test_scaled = scaler.fit_transform(X_test)  # Data leakage\n"
            )
            st.session_state.code_editor = ml_sample
            st.session_state.student_code = ml_sample
            st.session_state.messages = []
            st.rerun()

    with p_col4:
        if st.button("DS: Pandas Inplace", help="Pandas inplace reassignment bug", use_container_width=True):
            pd_sample = (
                "import pandas as pd\n\n"
                "df = pd.read_csv('dataset.csv')\n"
                "df = df.dropna(inplace=True)\n"
                "print('Total cleaned rows:', len(df))\n"
            )
            st.session_state.code_editor = pd_sample
            st.session_state.student_code = pd_sample
            st.session_state.messages = []
            st.rerun()

    code_input = st.text_area(
        "Edit your code (C, Python, Java, Data Science):",
        key="code_editor",
        height=260,
        placeholder="Enter your program code here..."
    )
    st.session_state.student_code = code_input

    # Direct Action Buttons under code
    btn_col1, btn_col2 = st.columns(2)
    trigger_prompt = None

    with btn_col1:
        if st.button("🔍 Inspect & Debug My Code", type="primary", use_container_width=True):
            trigger_prompt = "Please inspect my code, check for bugs, and guide me on how to fix them."

    with btn_col2:
        if st.button("📖 Explain How This Code Works", use_container_width=True):
            trigger_prompt = "Can you explain how this code works and ask me questions to verify my understanding?"

    st.info(
        "💡 **Pedagogical Note:** SocraticGuard does not write or fix the code for you. "
        "It pinpoints bugs (like `print` vs `printf` or data leakage) and prompts you with diagnostic clues to help you fix it yourself."
    )

# ===================== RIGHT COLUMN: SOCRATIC CHAT & VERIFICATION =====================
with col_chat:
    st.subheader("💬 Step 2: Socratic Guidance & Verification")
    
    # Chat container for message history
    chat_container = st.container(height=380)
    with chat_container:
        if not st.session_state.messages:
            st.markdown(
                "👋 **Welcome to SocraticGuard!**\n\n"
                "1. On the left, view or paste your code.\n"
                "2. Click **'Inspect & Debug My Code'** or type a question below.\n"
                "3. When SocraticGuard asks you a diagnostic question, **reply in the chat** to verify your answer!"
            )
        else:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    if "metrics" in msg:
                        m = msg["metrics"]
                        st.caption(
                            f"📈 **Cognitive Demand**: Bloom's Tier {m['blooms']} ({m['blooms_name']}) | "
                            f"🛡️ **Guardrail**: `{m['leakage_status']}`"
                        )

    # Chat Input Box at the bottom of the right column
    chat_user_input = st.chat_input("Answer SocraticGuard's question or ask for a hint...")
    
    # Handle whichever input occurred (Button click or Chat input)
    active_input = trigger_prompt or chat_user_input

    if active_input:
        # Record user turn
        st.session_state.messages.append({"role": "user", "content": active_input})
        
        # Instantiate engines
        socratic_engine = SocraticEngine()
        baseline_engine = BaselineEngine()
        evaluator = PedagogicalEvaluator()
        mock_service = MockLLMService()

        with chat_container:
            with st.chat_message("user"):
                st.markdown(active_input)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing code and inquiry through Socratic reasoning loop..."):
                    if "SocraticGuard" in mode:
                        prompt = socratic_engine.build_prompt(
                            user_question=active_input,
                            hint_level=hint_level,
                            context="Computer Science and Data Science Tutoring",
                            student_code=st.session_state.student_code,
                            conversation_history=st.session_state.messages
                        )

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
                                raw_response = mock_service.generate_response(
                                    prompt=prompt,
                                    mode="socratic",
                                    student_code=st.session_state.student_code,
                                    hint_level=hint_level,
                                    user_query=active_input,
                                    conversation_history=st.session_state.messages
                                )
                        else:
                            raw_response = mock_service.generate_response(
                                prompt=prompt,
                                mode="socratic",
                                student_code=st.session_state.student_code,
                                hint_level=hint_level,
                                user_query=active_input,
                                conversation_history=st.session_state.messages
                            )

                        final_response = socratic_engine.sanitize_response(raw_response, "")
                        blooms = evaluator.estimate_blooms_taxonomy_level(final_response)
                        blooms_names = {1: "Remember", 2: "Understand", 3: "Apply", 4: "Analyze", 5: "Evaluate", 6: "Create"}
                        blooms_name = blooms_names.get(blooms, "Analyze")
                        leakage_status = "Active & Enforcing (Direct Solution Suppressed)"

                    else:
                        prompt = baseline_engine.build_prompt(active_input)
                        if api_key and len(api_key) > 5:
                            try:
                                from google import genai
                                client = genai.Client(api_key=api_key)
                                res = client.models.generate_content(
                                    model="gemini-2.5-flash",
                                    contents=prompt
                                )
                                raw_response = res.text
                            except Exception:
                                raw_response = mock_service.generate_response(prompt=prompt, mode="baseline")
                        else:
                            raw_response = mock_service.generate_response(prompt=prompt, mode="baseline")

                        final_response = raw_response
                        blooms = evaluator.estimate_blooms_taxonomy_level(final_response)
                        blooms_names = {1: "Remember", 2: "Understand", 3: "Apply", 4: "Analyze", 5: "Evaluate", 6: "Create"}
                        blooms_name = blooms_names.get(blooms, "Remember")
                        leakage_status = "Unfiltered Direct Answer (Cognitive Offloading)"

                    st.markdown(final_response)
                    st.caption(
                        f"📈 **Cognitive Demand**: Bloom's Tier {blooms} ({blooms_name}) | "
                        f"🛡️ **Guardrail**: `{leakage_status}`"
                    )

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": final_response,
                        "metrics": {
                            "blooms": blooms,
                            "blooms_name": blooms_name,
                            "leakage_status": leakage_status
                        }
                    })
        st.rerun()
