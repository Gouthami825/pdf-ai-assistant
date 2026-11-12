"""Application configuration loaded from environment variables."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load variables from a .env file in the project root (if present).
_PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(_PROJECT_DIR / ".env")

GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY", "").strip() or None
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b").strip()

# Safety limits for uploads (bytes). Must match `.streamlit/config.toml` → server.maxUploadSize.
MAX_PDF_SIZE_MB: int = 25
MAX_PDF_BYTES: int = MAX_PDF_SIZE_MB * 1024 * 1024

# Truncate very long documents before sending to the LLM (character count).
MAX_CONTEXT_CHARS: int = int(os.getenv("MAX_CONTEXT_CHARS", "120000"))
