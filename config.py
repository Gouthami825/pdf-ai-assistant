
"""Application configuration loaded from environment variables and Streamlit secrets."""

import os
from pathlib import Path

from dotenv import load_dotenv

_PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(_PROJECT_DIR / ".env")


def get_secret(name: str, default: str = "") -> str:
    try:
        import streamlit as st
        return str(st.secrets.get(name, os.getenv(name, default))).strip()
    except Exception:
        return os.getenv(name, default).strip()


GROQ_API_KEY: str | None = get_secret("GROQ_API_KEY") or None
GROQ_MODEL: str = get_secret("GROQ_MODEL", "openai/gpt-oss-20b")

MAX_PDF_SIZE_MB: int = 25
MAX_PDF_BYTES: int = MAX_PDF_SIZE_MB * 1024 * 1024

MAX_CONTEXT_CHARS: int = int(get_secret("MAX_CONTEXT_CHARS", "120000"))
