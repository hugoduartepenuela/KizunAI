import streamlit as st

from services.agent import set_current_video_url
from services.youtube_rag import (
    process_video,
    ask_video
)


st.set_page_config(
    page_title="KizunAI Video Intelligence",
    page_icon="◆",
    layout="wide"
)


st.markdown(
    """
    <style>
    .block-container {
        max-width: 1180px;
        padding-top: 3rem;
        padding-bottom: 4rem;
    }

    .kizunai-hero {
        padding: 2rem 2rem;
        border: 1px solid rgba(120, 140, 255, 0.22);
        border-radius: 24px;
        background: linear-gradient(
            135deg,
            rgba(18, 24, 45, 0.95),
            rgba(7, 10, 20, 0.95)
        );
        box-shadow: 0 18px 55px rgba(0, 0, 0, 0.35);
        margin-bottom: 2rem;
    }

    .kizunai-label {
        font-size: 0.75rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: #91a4ff;
        font-weight: 700;
        margin-bottom: 0.45rem;
    }

    .kizunai-title {
        font-size: 3rem;
        line-height: 1;
        font-weight: 850;
        color: #f7f8ff;
        margin-bottom: 0.6rem;
    }

    .kizunai-subtitle {
        font-size: 1rem;
        color: #b8c0d9;
        max-width: 760px;
    }

    .pipeline-card {
        padding: 1.15rem;
        border-radius: 18px;
        border: 1px solid rgba(145, 164, 255, 0.18);
        background: rgba(18, 25, 45, 0.72);
        min-height: 126px;
        margin-bottom: 1rem;
    }

    .pipeline-number {
        color: #91a4ff;
        font-size: 0.7rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        font-weight: 800;
        margin-bottom: 0.35rem;
    }

    .pipeline-title {
        color: #f7f8ff;
        font-size: 1.05rem;
        font-weight: 850;
        margin-bottom: 0.35rem;
    }

    .pipeline-text {
        color: #aab4d4;
        font-size: 0.85rem;
        line-height: 1.45;
    }

    .status-card {
        padding: 1.2rem;
        border-radius: 18px;
        border: 1px solid rgba(145, 164, 255, 0.18);
        background: rgba(18, 25, 45, 0.72);
        margin-bottom: 1rem;
    }

    .status-label {
        color: #91a4ff;
        font-size: 0.72rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        font-weight: 800;
        margin-bottom: 0.4rem;
    }

    .status-value {
        color: #f7f8ff;
        font-size: 1.4rem;
        font-weight: 850;
        margin-bottom: 0.3rem;
    }

    .status-text {
        color: #aab4d4;
        font-size: 0.85rem;
    }

    .section-title {
        font-size: 1.5rem;
        font-weight: 820;
        color: #f7f8ff;
        margin-top: 1.5rem;
        margin-bottom: 0.4rem;
    }

    .section-text {
        color: #aab4d4;
        margin-bottom: 1rem;
    }

    .stButton > button {
        border-radius: 12px;
        font-weight: 750;
        border: 1px solid rgba(145, 164, 255, 0.35);
        background: linear-gradient(135deg, #5d6dff, #7c4dff);
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="kizunai-hero">
        <div class="kizunai-label">
            RETRIEVAL-AUGMENTED GENERATION · CHROMADB · EMBEDDINGS
        </div>
        <div class="kizunai-title">Video Intelligence</div>
        <div class="kizunai-subtitle">
            Turn YouTube content into searchable knowledge.
            KizunAI extracts the transcript, creates semantic chunks,
            stores embeddings in ChromaDB and retrieves relevant context
            before generating an answer.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


if "processed_video_url" not in st.session_state:
    st.session_state.processed_video_url = None

if "processed_video_chunks" not in st.session_state:
    st.session_state.processed_video_chunks = None

if "video_answer" not in st.session_state:
    st.session_state.video_answer = None


st.markdown(
    '<div class="section-title">RAG Pipeline</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-text">The video is transformed into a searchable vector knowledge base.</div>',
    unsafe_allow_html=True
)


pipeline_col1, pipeline_col2, pipeline_col3, pipeline_col4 = st.columns(4)

with pipeline_col1:
    st.markdown(
        """
        <div class="pipeline-card">
            <div class="pipeline-number">Step 01</div>
            <div class="pipeline-title">Transcript</div>
            <div class="pipeline-text">
                Extract the spoken content from the YouTube video.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with pipeline_col2:
    st.markdown(
        """
        <div class="pipeline-card">
            <div class="pipeline-number">Step 02</div>
            <div class="pipeline-title">Text Chunks</div>
            <div class="pipeline-text">
                Split long transcript content into retrieval-ready segments.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with pipeline_col3:
    st.markdown(
        """
        <div class="pipeline-card">
            <div class="pipeline-number">Step 03</div>
            <div class="pipeline-title">Embeddings</div>
            <div class="pipeline-text">
                Convert transcript chunks into semantic vector representations.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with pipeline_col4:
    st.markdown(
        """
        <div class="pipeline-card">
            <div class="pipeline-number">Step 04</div>
            <div class="pipeline-title">ChromaDB</div>
            <div class="pipeline-text">
                Store and retrieve the most relevant context for each question.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown(
    '<div class="section-title">YouTube Source</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-text">Paste a YouTube URL to build the video knowledge base.</div>',
    unsafe_allow_html=True
)


video_url = st.text_input(
    "YouTube URL",
    placeholder="https://www.youtube.com/watch?v=..."
)


if st.button(
    "Process Video",
    key="process_video_button",
    use_container_width=True
):

    if not video_url:
        st.warning("Please paste a YouTube URL first.")

    else:
        try:
            with st.spinner(
                "KizunAI is extracting the transcript and building the vector knowledge base..."
            ):
                chunks = process_video(video_url)

                set_current_video_url(video_url)

                st.session_state.processed_video_url = video_url
                st.session_state.processed_video_chunks = chunks
                st.session_state.video_answer = None

            st.success(
                f"Video processed successfully. {chunks} chunks stored in the vector knowledge base."
            )

        except Exception as error:
            st.error(
                f"Video processing failed: {str(error)}"
            )


if st.session_state.processed_video_url:

    st.markdown(
        '<div class="section-title">Knowledge Base Status</div>',
        unsafe_allow_html=True
    )

    status_col1, status_col2 = st.columns(2)

    with status_col1:
        st.markdown(
            """
            <div class="status-card">
                <div class="status-label">Vector Knowledge Base</div>
                <div class="status-value">Ready</div>
                <div class="status-text">
                    Transcript content has been processed for semantic retrieval.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with status_col2:
        st.markdown(
            f"""
            <div class="status-card">
                <div class="status-label">Stored Chunks</div>
                <div class="status-value">{st.session_state.processed_video_chunks}</div>
                <div class="status-text">
                    Retrieval-ready transcript segments available in ChromaDB.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


st.markdown(
    '<div class="section-title">Ask the Video</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-text">KizunAI retrieves relevant transcript context before generating the answer.</div>',
    unsafe_allow_html=True
)


question = st.text_input(
    "Question",
    placeholder="Example: What products does the creator recommend buying?"
)


if st.button(
    "Ask KizunAI",
    key="ask_video_button",
    use_container_width=True
):

    if not st.session_state.processed_video_url:
        st.warning("Process a YouTube video before asking a question.")

    elif not question:
        st.warning("Please write a question first.")

    else:
        try:
            with st.spinner(
                "Searching ChromaDB and generating a grounded answer..."
            ):
                st.session_state.video_answer = ask_video(
                    st.session_state.processed_video_url,
                    question
                )

        except Exception as error:
            st.error(
                f"Video question failed: {str(error)}"
            )


if st.session_state.video_answer:

    st.markdown(
        '<div class="section-title">KizunAI Answer</div>',
        unsafe_allow_html=True
    )

    st.info(
        st.session_state.video_answer
    )
