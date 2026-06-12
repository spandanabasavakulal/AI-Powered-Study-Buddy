"""Flashcard Generator feature."""
from __future__ import annotations

import io

import pandas as pd
import streamlit as st

from database.db import log_flashcards, log_topic
from modules.gemini_client import generate_json


PROMPT = """Create {n} study flashcards for the topic "{topic}".
Return a JSON array of objects with keys "front" (a question or term)
and "back" (the concise answer or definition)."""


def render() -> None:
    st.title("🃏 Flashcard Generator")
    st.caption("Generate flashcards and export them as CSV.")

    col1, col2 = st.columns([3, 1])
    with col1:
        topic = st.text_input("Topic", placeholder="e.g. Data Structures")
    with col2:
        n = st.number_input("Count", min_value=5, max_value=30, value=10, step=1)

    if st.button("Generate Flashcards", type="primary", disabled=not topic.strip()):
        with st.spinner("Crafting flashcards…"):
            try:
                cards = generate_json(PROMPT.format(n=n, topic=topic.strip()))
                cards = [c for c in cards if "front" in c and "back" in c]
                st.session_state.flashcards = cards
                st.session_state.flashcards_topic = topic.strip()
                log_topic(topic.strip())
                log_flashcards(topic.strip(), cards)
            except Exception as e:
                st.error(f"Failed: {e}")

    cards = st.session_state.get("flashcards")
    if not cards:
        return

    st.divider()
    st.subheader(f"Flashcards — {st.session_state.flashcards_topic}")

    for i, c in enumerate(cards, start=1):
        with st.expander(f"Card {i}: {c['front']}"):
            st.write(c["back"])

    df = pd.DataFrame(cards)
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    st.download_button(
        "⬇️ Download CSV",
        buf.getvalue(),
        file_name=f"flashcards_{st.session_state.flashcards_topic}.csv",
        mime="text/csv",
    )
