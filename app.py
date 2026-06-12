"""
AI-Powered Study Buddy — main Streamlit entry point.

Run with:
    streamlit run app.py
"""
from __future__ import annotations

import os

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from database.db import get_stats, init_db, recent_activity, fetch_all
from modules import (
    explainer,
    summarizer,
    quiz_generator,
    flashcards,
    pdf_chat,
    study_planner,
    progress_tracker,
    recommendation,
)

load_dotenv()

# --- Page config & theme --------------------------------------------------
st.set_page_config(
    page_title="AI-Powered Study Buddy",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    /* Sidebar polish */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
    }
    /* Metric cards */
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; }
    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }
    /* Headings */
    h1, h2, h3 { letter-spacing: -0.01em; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- DB bootstrap ---------------------------------------------------------
init_db()


# --- Home -----------------------------------------------------------------
def render_home() -> None:
    st.title("🎓 AI-Powered Study Buddy")
    st.markdown(
        "Your generative-AI study companion — explain, summarize, quiz, "
        "chat with PDFs, plan, and track progress."
    )

    if not os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY") == "your_gemini_api_key_here":
        st.warning(
            "⚠️ `GOOGLE_API_KEY` not set. Copy `.env.example` to `.env` and add your Gemini key."
        )

    stats = get_stats()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📚 Topics studied", stats["topics_studied"])
    c2.metric("❓ Quizzes taken", stats["quizzes_taken"])
    c3.metric("🎯 Average score", f"{stats['average_score']}%")
    c4.metric("🃏 Flashcards", stats["flashcards"])

    st.divider()

    left, right = st.columns([2, 1])
    with left:
        st.subheader("📈 Score trend")
        quizzes = pd.DataFrame(fetch_all("quiz_history"))
        if quizzes.empty:
            st.info("Take a quiz to see your score trend.")
        else:
            quizzes["pct"] = quizzes["score"] / quizzes["total"] * 100
            quizzes["taken_at"] = pd.to_datetime(quizzes["taken_at"])
            fig = px.area(
                quizzes.sort_values("taken_at"),
                x="taken_at", y="pct",
                labels={"pct": "Score %", "taken_at": "Date"},
            )
            fig.update_layout(template="plotly_dark", height=320,
                              margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("🕒 Recent activity")
        feed = recent_activity(8)
        if not feed:
            st.caption("No activity yet — start studying!")
        else:
            for f in feed:
                st.markdown(f"**{f['kind']}** — {f['detail']}")
                st.caption(f["ts"][:19].replace("T", " "))


# --- Settings -------------------------------------------------------------
def render_settings() -> None:
    st.title("⚙️ Settings")
    st.write("Configuration & maintenance.")

    has_key = bool(os.getenv("GOOGLE_API_KEY")) and os.getenv("GOOGLE_API_KEY") != "your_gemini_api_key_here"
    st.markdown(f"**Gemini API key:** {'✅ Loaded' if has_key else '❌ Missing'}")
    st.code(".env\nGOOGLE_API_KEY=your_key_here", language="bash")

    st.divider()
    st.subheader("Danger zone")
    if st.button("🗑️ Reset database", type="secondary"):
        db_path = os.path.join(os.path.dirname(__file__), "database.db")
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
            init_db()
            st.success("Database reset. Reload the app.")
        except Exception as e:
            st.error(f"Failed to reset DB: {e}")


# --- Sidebar nav ----------------------------------------------------------
PAGES = {
    "🏠 Home": render_home,
    "📚 Concept Explainer": explainer.render,
    "📝 Notes Summarizer": summarizer.render,
    "❓ Quiz Generator": quiz_generator.render,
    "🃏 Flashcard Generator": flashcards.render,
    "📄 PDF Chat": pdf_chat.render,
    "📅 Study Planner": study_planner.render,
    "📊 Progress Tracker": progress_tracker.render,
    "💡 Recommendations": recommendation.render,
    "⚙️ Settings": render_settings,
}

with st.sidebar:
    st.markdown("## 🎓 Study Buddy")
    st.caption("Powered by Gemini")
    choice = st.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")
    st.divider()
    st.caption("v1.0 • Built with Streamlit")

PAGES[choice]()
