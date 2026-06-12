"""Progress Tracker with Plotly charts."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from database.db import fetch_all, get_stats


def render() -> None:
    st.title("📊 Progress Tracker")
    st.caption("Visualize your learning journey.")

    stats = get_stats()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Topics studied", stats["topics_studied"])
    c2.metric("Quizzes taken", stats["quizzes_taken"])
    c3.metric("Average score", f"{stats['average_score']}%")
    c4.metric("Flashcards", stats["flashcards"])

    quizzes = pd.DataFrame(fetch_all("quiz_history"))
    topics = pd.DataFrame(fetch_all("topics"))

    if quizzes.empty and topics.empty:
        st.info("Take a quiz or study a topic to see charts here.")
        return

    if not quizzes.empty:
        quizzes["pct"] = quizzes["score"] / quizzes["total"] * 100
        quizzes["taken_at"] = pd.to_datetime(quizzes["taken_at"])

        st.subheader("Quiz scores over time")
        line = px.line(
            quizzes.sort_values("taken_at"),
            x="taken_at", y="pct", color="topic", markers=True,
            labels={"pct": "Score %", "taken_at": "Date"},
        )
        line.update_layout(template="plotly_dark", height=380)
        st.plotly_chart(line, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Average score per topic")
            avg = quizzes.groupby("topic")["pct"].mean().reset_index()
            bar = px.bar(avg, x="topic", y="pct",
                         labels={"pct": "Avg score %"}, color="topic")
            bar.update_layout(template="plotly_dark", height=350, showlegend=False)
            st.plotly_chart(bar, use_container_width=True)
        with col2:
            st.subheader("Difficulty distribution")
            pie = px.pie(quizzes, names="difficulty", hole=0.45)
            pie.update_layout(template="plotly_dark", height=350)
            st.plotly_chart(pie, use_container_width=True)

    if not topics.empty:
        st.subheader("Most studied topics")
        counts = topics["topic"].value_counts().reset_index()
        counts.columns = ["topic", "count"]
        bar2 = px.bar(counts.head(10), x="topic", y="count", color="topic")
        bar2.update_layout(template="plotly_dark", height=350, showlegend=False)
        st.plotly_chart(bar2, use_container_width=True)
