"""PDF Chat feature using FAISS + Gemini."""
from __future__ import annotations

import os

import streamlit as st
from PyPDF2 import PdfReader

UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "uploads"
)
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _build_vectorstore(text: str):
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import HuggingFaceEmbeddings

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    chunks = splitter.split_text(text)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return FAISS.from_texts(
        chunks,
        embedding=embeddings
    )


def _qa_chain(vs):
    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2
    )

    def ask(question: str):
        docs = vs.similarity_search(question, k=4)

        context = "\n\n".join(
            doc.page_content
            for doc in docs
        )

        prompt = f"""
You are an AI study assistant.

Answer ONLY from the context below.

Context:
{context}

Question:
{question}

Answer:
"""

        response = llm.invoke(prompt)

        return response.content

    return ask


def _read_pdf(path: str) -> str:
    reader = PdfReader(path)

    return "\n".join(
        (page.extract_text() or "")
        for page in reader.pages
    )


def render() -> None:
    st.title("📄 PDF Chat")
    st.caption(
        "Upload a PDF and ask questions about its contents."
    )

    uploaded_file = st.file_uploader(
        "PDF",
        type=["pdf"]
    )

    if uploaded_file and st.button(
        "Index PDF",
        type="primary"
    ):
        with st.spinner(
            "Reading and indexing PDF..."
        ):
            try:
                file_path = os.path.join(
                    UPLOAD_DIR,
                    uploaded_file.name
                )

                with open(
                    file_path,
                    "wb"
                ) as f:
                    f.write(
                        uploaded_file.getbuffer()
                    )

                text = _read_pdf(file_path)

                if not text.strip():
                    st.error(
                        "No extractable text found in this PDF."
                    )
                    return

                st.session_state.pdf_vs = (
                    _build_vectorstore(text)
                )

                st.session_state.pdf_name = (
                    uploaded_file.name
                )

                st.session_state.pdf_messages = []

                st.success(
                    f"Indexed {uploaded_file.name}"
                )

            except Exception as e:
                st.error(
                    f"Indexing failed: {e}"
                )

    vs = st.session_state.get("pdf_vs")

    if not vs:
        st.info(
            "Upload a PDF and click 'Index PDF' to start chatting."
        )
        return

    st.divider()

    st.subheader(
        f"Chat — {st.session_state.pdf_name}"
    )

    for message in st.session_state.get(
        "pdf_messages",
        []
    ):
        with st.chat_message(
            message["role"]
        ):
            st.markdown(
                message["content"]
            )

    question = st.chat_input(
        "Ask a question about the PDF..."
    )

    if question:

        st.session_state.pdf_messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        with st.chat_message(
            "user"
        ):
            st.markdown(question)

        with st.chat_message(
            "assistant"
        ):
            with st.spinner(
                "Thinking..."
            ):
                try:
                    chain = _qa_chain(vs)

                    answer = chain(question)

                except Exception as e:

                    answer = (
                        f"Error: {e}"
                    )

                st.markdown(answer)

        st.session_state.pdf_messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )