# 🎓 AI-Powered Study Buddy

A generative-AI study companion built with **Python + Streamlit + Google Gemini**.
Explain concepts, summarize notes, generate quizzes & flashcards, chat with PDFs,
plan your studies, and track progress — all in a polished dark-themed dashboard.

---

## ✨ Features

| | |
|---|---|
| 📚 Concept Explainer | Definition · Simple explanation · Key points · Example · Summary |
| 📝 Notes Summarizer  | Paste text or upload PDF → summary + keywords |
| ❓ Quiz Generator    | 10 MCQs with explanations, difficulty selector, score history |
| 🃏 Flashcard Generator | AI flashcards, exportable as CSV |
| 📄 PDF Chat          | LangChain + FAISS + Gemini retrieval-QA |
| 📅 Study Planner     | Day-wise schedule until your exam date |
| 📊 Progress Tracker  | Plotly line / bar / pie charts |
| 💡 Recommendations   | Suggests revision based on weak quiz topics |

## 🗂️ Project structure

```
AI-Powered-Study-Buddy/
├── app.py                     # Streamlit entry point
├── requirements.txt
├── .env.example               # copy to .env and add your Gemini key
├── database.db                # auto-created on first run
├── modules/
│   ├── gemini_client.py
│   ├── explainer.py
│   ├── summarizer.py
│   ├── quiz_generator.py
│   ├── flashcards.py
│   ├── pdf_chat.py
│   ├── study_planner.py
│   ├── recommendation.py
│   └── progress_tracker.py
├── database/
│   └── db.py                  # SQLite schema + helpers
├── uploads/                   # uploaded PDFs
├── assets/
└── README.md
```

## 🚀 Quick start

```bash
cd AI-Powered-Study-Buddy
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # then edit .env
streamlit run app.py
```

Get a free Gemini API key at <https://aistudio.google.com/app/apikey>.

## ☁️ Deploy

### Streamlit Community Cloud
1. Push this folder to a GitHub repo.
2. On [share.streamlit.io](https://share.streamlit.io), create a new app pointing at `app.py`.
3. Under **Settings → Secrets**, add:
   ```toml
   GOOGLE_API_KEY = "your_key_here"
   ```

### Render
1. Create a new **Web Service** from your repo.
2. Build command: `pip install -r requirements.txt`
3. Start command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
4. Add `GOOGLE_API_KEY` as an environment variable.

## 🧱 Tech stack

Python · Streamlit · Google Gemini API · SQLite · LangChain · FAISS · PyPDF2 · Plotly · Pandas

## 📝 Notes
- The SQLite DB (`database.db`) is created on first launch.
- PDF embeddings use `models/embedding-001` via `langchain-google-genai`.
- Dark theme is applied via custom CSS in `app.py`.
