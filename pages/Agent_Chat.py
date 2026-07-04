import streamlit as st
import uuid
from services.agent import ask_agent


st.set_page_config(page_title="KizunAI Agent", page_icon="🤖")

st.title("🤖 KizunAI Agent")

if "agent_thread_id" not in st.session_state:
    st.session_state.agent_thread_id = str(uuid.uuid4())

if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = []


if st.button("Clear chat"):
    st.session_state.agent_messages = []
    st.session_state.agent_thread_id = str(uuid.uuid4())
    st.rerun()


for message in st.session_state.agent_messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


user_question = st.chat_input("Ask anything about your inventory or YouTube video...")


if user_question:
    st.session_state.agent_messages.append({
        "role": "user",
        "content": user_question
    })

    with st.chat_message("user"):
        st.write(user_question)

    with st.chat_message("assistant"):
        with st.spinner("KizunAI is thinking..."):
            response = ask_agent(
                user_question,
                thread_id=st.session_state.agent_thread_id
            )

            st.write(response)

    st.session_state.agent_messages.append({
        "role": "assistant",
        "content": response
    })