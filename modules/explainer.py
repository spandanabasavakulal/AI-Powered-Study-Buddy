"""Concept Explainer feature."""
from __future__ import annotations

import streamlit as st

from database.db import log_topic
from modules.gemini_client import generate_text


PROMPT = """You are an expert tutor. Explain the topic: "{topic}".
Use this exact markdown structure with these headings:

## Definition
A precise 2-3 sentence definition.

## Simple Explanation
Explain like I'm 15, using an analogy.

## Key Points
- 5 concise bullet points.

## Real-World Example
A concrete example a student can relate to.

## Summary
A 2-sentence takeaway.
"""


def render() -> None:
    st.title("📚 Concept Explainer")
    st.caption("Get a structured breakdown of any topic.")

    topic = st.text_input("Topic", placeholder="e.g. Logistic Regression")
    if st.button("Explain", type="primary", disabled=not topic.strip()):
        with st.spinner("Thinking…"):
            try:
                out = generate_text(PROMPT.format(topic=topic.strip()))
                log_topic(topic.strip())
                st.success("Done!")
                st.markdown(out)
            except Exception as e:
                st.error(f"Failed to generate explanation: {e}")
