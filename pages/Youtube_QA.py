import streamlit as st

from services.agent import set_current_video_url
from services.youtube_rag import (
    process_video,
    ask_video
)

st.title("🎥 YouTube QA")

video_url = st.text_input(
    "YouTube URL"
)

if st.button("Process Video"):

    with st.spinner("Processing..."):

        chunks = process_video(video_url)
        
        set_current_video_url(video_url)
    
    st.success(
        f"Video processed. {chunks} chunks stored."
    )

question = st.text_input(
    "Ask a question"
)

if st.button("Ask"):

    answer = ask_video(
        video_url,
        question
    )

    st.write(answer)