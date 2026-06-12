"""Thin wrapper around Google Gemini for text generation + JSON parsing."""
from __future__ import annotations

import json
import os
import re
from functools import lru_cache

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "gemini-2.5-flash"


def _configure() -> None:
    key = os.getenv("GOOGLE_API_KEY")
    if not key or key == "your_gemini_api_key_here":
        raise RuntimeError(
            "GOOGLE_API_KEY missing. Add it to your .env file "
            "(see .env.example)."
        )
    genai.configure(api_key=key)


@lru_cache(maxsize=4)
def get_model(name: str = DEFAULT_MODEL):
    _configure()
    return genai.GenerativeModel(name)


def generate_text(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Return raw text response from Gemini."""
    m = get_model(model)
    resp = m.generate_content(prompt)
    return (resp.text or "").strip()


def generate_json(prompt: str, model: str = DEFAULT_MODEL):
    """Generate, then parse the first JSON array/object found in the reply."""
    raw = generate_text(
        prompt
        + "\n\nReply with ONLY valid JSON. No markdown, no commentary.",
        model=model,
    )
    # Strip ```json fences if present
    cleaned = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: find first {...} or [...] block
        match = re.search(r"(\{.*\}|\[.*\])", cleaned, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse JSON from model output:\n{raw}")
        return json.loads(match.group(1))
