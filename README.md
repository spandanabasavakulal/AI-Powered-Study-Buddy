# 🎓 AI-Powered Study Buddy

An AI-powered study companion built with **Python, Streamlit, Google Gemini, LangChain, and FAISS**. It helps students understand concepts, summarize notes, generate quizzes and flashcards, chat with PDFs, plan studies, and track learning progress through an interactive dashboard.

---

## ✨ Features

### 📚 Concept Explainer

* Definition
* Simple Explanation
* Key Points
* Real-world Example
* Summary

### 📝 Notes Summarizer

* Summarize text and notes
* Extract key points
* Generate concise explanations

### ❓ Quiz Generator

* Generate MCQs
* Difficulty selection
* Score tracking
* Answer explanations

### 🃏 Flashcard Generator

* AI-generated flashcards
* CSV export support

### 📄 PDF Chat

* Upload PDFs
* Ask questions from documents
* FAISS vector search
* Gemini-powered responses

### 📅 Study Planner

* Generate personalized study schedules
* Exam date planning

### 📊 Progress Tracker

* Learning statistics
* Charts and analytics

### 💡 Recommendations

* Suggest revision topics based on performance

---

## 🗂️ Project Structure

```
AI-Powered-Study-Buddy/
├── app.py
├── requirements.txt
├── .env.example
├── modules/
├── database/
├── uploads/
├── assets/
├── README.md
```

---

## 🚀 Installation

```bash
git clone https://github.com/yourusername/AI-Powered-Study-Buddy.git
cd AI-Powered-Study-Buddy

pip install -r requirements.txt

python -m streamlit run app.py
```

---

## 🔑 Gemini API Setup

1. Get an API key from:

https://aistudio.google.com/app/apikey

2. Create a `.env` file:

```env
GOOGLE_API_KEY=your_api_key_here
```

---

## 🛠️ Tech Stack

* Python
* Streamlit
* Google Gemini 2.5 Flash
* LangChain
* FAISS
* HuggingFace Embeddings
* PyPDF2
* Plotly
* SQLite

---

## 🌟 Developed For

**IBM SkillsBuild + Edunet Foundation AI Internship**

---

## 📌 Future Enhancements

* Voice Assistant
* OCR Support for Handwritten PDFs
* User Authentication
* Multi-language Support
* Gamification
* Cloud Deployment

---

Built with ❤️ using Python and Generative AI.
