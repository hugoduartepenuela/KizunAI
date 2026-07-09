import streamlit as st
import uuid

from services.agent import ask_agent


st.set_page_config(
    page_title="KizunAI Agent",
    page_icon="◆",
    layout="wide"
)


st.markdown(
    """
    <style>
    .block-container {
        max-width: 1180px;
        padding-top: 3rem;
        padding-bottom: 7rem;
    }

    .agent-hero {
        padding: 2rem;
        border-radius: 24px;
        border: 1px solid rgba(145, 164, 255, 0.22);
        background: linear-gradient(135deg, rgba(18, 24, 45, 0.96), rgba(7, 10, 20, 0.96));
        box-shadow: 0 18px 55px rgba(0, 0, 0, 0.35);
        margin-bottom: 1.8rem;
    }

    .agent-label {
        font-size: 0.75rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: #91a4ff;
        font-weight: 800;
        margin-bottom: 0.45rem;
    }

    .agent-title {
        font-size: 3rem;
        line-height: 1;
        font-weight: 850;
        color: #f7f8ff;
        margin-bottom: 0.6rem;
    }

    .agent-subtitle {
        color: #b8c0d9;
        max-width: 760px;
        font-size: 1rem;
    }

    .tool-card {
        padding: 1.1rem 1.15rem;
        border-radius: 18px;
        border: 1px solid rgba(145, 164, 255, 0.18);
        background: rgba(18, 25, 45, 0.72);
        min-height: 128px;
    }

    .tool-kicker {
        color: #91a4ff;
        font-size: 0.68rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }

    .tool-title {
        color: #f7f8ff;
        font-size: 1.05rem;
        font-weight: 850;
        margin-bottom: 0.35rem;
    }

    .tool-text {
        color: #aab4d4;
        font-size: 0.88rem;
        line-height: 1.45;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 850;
        color: #f7f8ff;
        margin-top: 1.4rem;
        margin-bottom: 0.35rem;
    }

    .section-text {
        color: #aab4d4;
        margin-bottom: 1rem;
    }

    .stButton > button {
        border-radius: 12px;
        font-weight: 750;
        border: 1px solid rgba(145, 164, 255, 0.35);
        background: rgba(18, 25, 45, 0.78);
        color: white;
    }

    .stButton > button:hover {
        border-color: rgba(145, 164, 255, 0.75);
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="agent-hero">
        <div class="agent-label">LANGCHAIN AGENT · TOOL ORCHESTRATION · MEMORY</div>
        <div class="agent-title">KizunAI Agent Console</div>
        <div class="agent-subtitle">
            One AI interface for inventory analysis, SKU generation, video intelligence and currency conversion.
            The agent decides which specialized tool to use.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


tool_col1, tool_col2, tool_col3, tool_col4 = st.columns(4)

with tool_col1:
    st.markdown(
        """
        <div class="tool-card">
            <div class="tool-kicker">Tool 01</div>
            <div class="tool-title">Inventory Search</div>
            <div class="tool-text">Analyze stock, prices, quantities, margins and SKUs from saved inventory.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with tool_col2:
    st.markdown(
        """
        <div class="tool-card">
            <div class="tool-kicker">Tool 02</div>
            <div class="tool-title">SKU Generator</div>
            <div class="tool-text">Create deterministic SKUs using product name, raw/slab status and grade.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with tool_col3:
    st.markdown(
        """
        <div class="tool-card">
            <div class="tool-kicker">Tool 03</div>
            <div class="tool-title">Video RAG</div>
            <div class="tool-text">Answer questions about processed YouTube videos using transcript retrieval.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with tool_col4:
    st.markdown(
        """
        <div class="tool-card">
            <div class="tool-kicker">Tool 04</div>
            <div class="tool-title">FX Converter</div>
            <div class="tool-text">Convert currencies using external exchange-rate data and deterministic calculation.</div>
        </div>
        """,
        unsafe_allow_html=True
    )


if "agent_thread_id" not in st.session_state:
    st.session_state.agent_thread_id = str(uuid.uuid4())

if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = []


chat_header_col, clear_col = st.columns([0.82, 0.18])

with chat_header_col:
    st.markdown('<div class="section-title">Conversation</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-text">Try: “How many Pikachu cards do I have?”, “Generate a SKU for a raw Mario Pikachu card”, or “How much is 5000 EUR in AED?”</div>',
        unsafe_allow_html=True
    )

with clear_col:
    st.write("")
    st.write("")
    if st.button("Clear chat", use_container_width=True):
        st.session_state.agent_messages = []
        st.session_state.agent_thread_id = str(uuid.uuid4())
        st.rerun()


for message in st.session_state.agent_messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


user_question = st.chat_input(
    "Ask KizunAI about inventory, SKUs, currencies or processed videos..."
)


if user_question:
    st.session_state.agent_messages.append({
        "role": "user",
        "content": user_question
    })

    with st.chat_message("user"):
        st.write(user_question)

    with st.chat_message("assistant"):
        with st.spinner("KizunAI Agent is selecting the right tool..."):
            response = ask_agent(
                user_question,
                thread_id=st.session_state.agent_thread_id
            )

            st.write(response)

    st.session_state.agent_messages.append({
        "role": "assistant",
        "content": response
    })
