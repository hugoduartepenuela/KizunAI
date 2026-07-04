from youtube_transcript_api import YouTubeTranscriptApi
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.schema import Document
import re


def extract_video_id(url):

    patterns = [
        r"v=([^&]+)",
        r"youtu\.be/([^?]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, url)

        if match:
            return match.group(1)

    return None


def process_video(url):

    video_id = extract_video_id(url)

    ytt_api = YouTubeTranscriptApi()

    transcript = ytt_api.fetch(video_id)

    text = " ".join([item.text for item in transcript])

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_text(text)

    docs = [Document(page_content=chunk) for chunk in chunks]

    embeddings = OpenAIEmbeddings()

    vectordb = Chroma.from_documents(
        docs,
        embeddings,
        persist_directory=f"data/chroma/{video_id}"
    )

    vectordb.persist()

    return len(chunks)


def ask_video(url, question):

    video_id = extract_video_id(url)

    embeddings = OpenAIEmbeddings()

    vectordb = Chroma(
        persist_directory=f"data/chroma/{video_id}",
        embedding_function=embeddings
    )

    qa = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(temperature=0),
        retriever=vectordb.as_retriever()
    )

    return qa.run(question)