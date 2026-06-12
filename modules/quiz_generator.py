"""Quiz Generator feature."""
from __future__ import annotations

import streamlit as st

from database.db import log_quiz, log_topic
from modules.gemini_client import generate_json


PROMPT = """Create 10 multiple-choice questions on the topic "{topic}" at {difficulty} difficulty.
Return a JSON array of 10 objects with these exact keys:
- "question": string
- "options": array of 4 distinct strings
- "answer": one of the options (exact match)
- "explanation": 1-2 sentence explanation

Do not include numbering inside the question text."""


def _generate(topic: str, difficulty: str):
    data = generate_json(PROMPT.format(topic=topic, difficulty=difficulty))
    # Defensive validation
    cleaned = []
    for q in data:
        if not all(k in q for k in ("question", "options", "answer", "explanation")):
            continue
        if len(q["options"]) != 4 or q["answer"] not in q["options"]:
            continue
        cleaned.append(q)
    if not cleaned:
        raise ValueError("Model did not return valid quiz items.")
    return cleaned


def render() -> None:
    st.title("❓ Quiz Generator")
    st.caption("10 MCQs tailored to your topic and difficulty.")

    col1, col2 = st.columns([2, 1])
    with col1:
        topic = st.text_input("Topic", placeholder="e.g. Operating Systems")
    with col2:
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

    if st.button("Generate Quiz", type="primary", disabled=not topic.strip()):
        with st.spinner("Building your quiz…"):
            try:
                st.session_state.quiz = _generate(topic.strip(), difficulty)
                st.session_state.quiz_topic = topic.strip()
                st.session_state.quiz_difficulty = difficulty
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                log_topic(topic.strip())
            except Exception as e:
                st.error(f"Failed to generate quiz: {e}")

    quiz = st.session_state.get("quiz")
    if not quiz:
        return

    st.divider()
    st.subheader(f"Quiz: {st.session_state.quiz_topic} ({st.session_state.quiz_difficulty})")

    with st.form("quiz_form"):
        for i, q in enumerate(quiz, start=1):
            st.markdown(f"**Q{i}. {q['question']}**")
            st.session_state.quiz_answers[i] = st.radio(
                f"q{i}", q["options"], key=f"q_{i}", label_visibility="collapsed"
            )
            st.write("")
        submitted = st.form_submit_button("Submit Answers", type="primary")

    if submitted:
        score = sum(
            1 for i, q in enumerate(quiz, start=1)
            if st.session_state.quiz_answers.get(i) == q["answer"]
        )
        total = len(quiz)
        st.session_state.quiz_submitted = True
        log_quiz(st.session_state.quiz_topic, st.session_state.quiz_difficulty, score, total)
        st.success(f"You scored {score} / {total} ({score / total * 100:.0f}%)")

        with st.expander("📖 Review answers", expanded=True):
            for i, q in enumerate(quiz, start=1):
                user = st.session_state.quiz_answers.get(i)
                ok = user == q["answer"]
                st.markdown(
                    f"**Q{i}.** {q['question']}  \n"
                    f"{'✅' if ok else '❌'} Your answer: *{user}*  \n"
                    f"Correct: **{q['answer']}**  \n"
                    f"_{q['explanation']}_"
                )
                st.divider()
