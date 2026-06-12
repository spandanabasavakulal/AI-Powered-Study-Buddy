"""Revision recommendations based on weak quiz topics."""
from __future__ import annotations

import streamlit as st

from database.db import low_score_topics
from modules.gemini_client import generate_text


def render() -> None:
    st.title("💡 Recommendations")
    st.caption("Topics to revise based on your quiz performance.")

    threshold = st.slider("Weakness threshold (%)", 30, 90, 60, step=5)
    weak = low_score_topics(threshold=float(threshold))

    if not weak:
        st.success("🎉 No weak topics detected. Keep up the great work!")
        return

    st.subheader("You should revise:")
    for w in weak:
        st.markdown(
            f"- **{w['topic']}** — avg {w['pct']:.0f}% over {w['attempts']} attempts"
        )

    if st.button("✨ Get AI revision tips", type="primary"):
        topics = ", ".join(w["topic"] for w in weak)
        with st.spinner("Generating tips…"):
            try:
                tips = generate_text(
                    f"Give targeted revision strategies (bullet points) "
                    f"for these weak topics: {topics}."
                )
                st.markdown(tips)
            except Exception as e:
                st.error(f"Failed: {e}")
