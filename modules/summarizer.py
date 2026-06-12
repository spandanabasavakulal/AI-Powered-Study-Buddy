"""Notes Summarizer feature."""
from __future__ import annotations

import streamlit as st
from PyPDF2 import PdfReader

from modules.gemini_client import generate_text


PROMPT = """Summarize the following notes. Respond in markdown with:

## Short Summary
3-5 sentences.

## Important Points
- 5-8 bullet points.

## Keywords
A comma-separated list of 8-12 keywords.

NOTES:
{text}
"""


def _read_pdf(file) -> str:
    reader = PdfReader(file)
    return "\n".join((p.extract_text() or "") for p in reader.pages)


def render() -> None:
    st.title("📝 Notes Summarizer")
    st.caption("Paste text or upload a PDF.")

    tab1, tab2 = st.tabs(["✍️ Paste text", "📎 Upload PDF"])
    text = ""
    with tab1:
        text = st.text_area("Notes", height=240, placeholder="Paste your notes here…")
    with tab2:
        up = st.file_uploader("PDF file", type=["pdf"])
        if up:
            try:
                text = _read_pdf(up)
                st.info(f"Loaded {len(text):,} characters from PDF.")
            except Exception as e:
                st.error(f"Could not read PDF: {e}")

    if st.button("Summarize", type="primary", disabled=not text.strip()):
        with st.spinner("Summarizing…"):
            try:
                # Cap to ~20k chars for safety
                out = generate_text(PROMPT.format(text=text[:20000]))
                st.success("Summary ready")
                st.markdown(out)
                st.download_button(
                    "⬇️ Download summary", out, file_name="summary.md"
                )
            except Exception as e:
                st.error(f"Failed: {e}")
