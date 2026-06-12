"""Study Planner feature."""
from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from database.db import log_study_plan
from modules.gemini_client import generate_text


PROMPT = """Build a day-wise study plan from today ({today}) until the exam on {exam_date}
({days} days). Subjects: {subjects}.

Format as a Markdown table with columns: Day | Date | Subject | Focus / Tasks.
Distribute subjects evenly, include 1 revision day before the exam,
and keep each day's tasks concise (1-2 lines)."""


def render() -> None:
    st.title("📅 Study Planner")
    st.caption("AI-generated day-wise schedule.")

    subjects = st.text_area(
        "Subjects (comma-separated)",
        placeholder="Operating Systems, DBMS, Machine Learning",
    )
    exam_date = st.date_input("Exam date", value=date.today() + timedelta(days=14))

    days = (exam_date - date.today()).days
    if days <= 0:
        st.warning("Pick an exam date in the future.")

    if st.button("Generate Plan", type="primary",
                 disabled=not subjects.strip() or days <= 0):
        with st.spinner("Planning your study schedule…"):
            try:
                plan = generate_text(PROMPT.format(
                    today=date.today().isoformat(),
                    exam_date=exam_date.isoformat(),
                    days=days,
                    subjects=subjects.strip(),
                ))
                log_study_plan(subjects.strip(), exam_date.isoformat(), plan)
                st.success("Plan ready!")
                st.markdown(plan)
                st.download_button("⬇️ Download plan", plan, file_name="study_plan.md")
            except Exception as e:
                st.error(f"Failed: {e}")
