# PDF AI Assistant

A beginner-friendly **demo** web app that lets you upload a PDF, extract its text, and ask questions answered by a Groq-hosted language model **using only that PDF text**. If the document does not contain the answer, the assistant is instructed to say so clearly.

> **Note:** This project is for learning and prototyping. It is **not** production-ready (no auth, rate limiting, OCR, or enterprise PDF features).

## Features

- Streamlit UI for upload and Q&A
- Text extraction with [PyMuPDF](https://pymupdf.readthedocs.io/)
- Answers via [Groq](https://groq.com/) free-tier API
- API key from environment variables (`.env`)
- Basic validation and error handling

## Project layout

| File | Purpose |
|------|---------|
| `app.py` | Streamlit frontend |
| `config.py` | Environment settings |
| `pdf_utils.py` | PDF text extraction |
| `llm_utils.py` | Groq Q&A logic |
| `requirements.txt` | Dependencies |
| `.env.example` | Environment template |
| `.gitignore` | Keeps secrets and caches out of git |

## Prerequisites

- Python **3.10** or newer
- A free [Groq API key](https://console.groq.com/)

## Setup

1. **Open a terminal** in this folder:

   ```bash
   cd path/to/01_PDF_AI_Assistant
   ```

2. **Create and activate a virtual environment** (recommended):

   ```bash
   python -m venv .venv
   ```

   Windows (PowerShell):

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   macOS / Linux:

   ```bash
   source .venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure secrets:**

   ```bash
   copy .env.example .env
   ```

   On macOS/Linux use `cp .env.example .env`.

   Edit `.env` and set:

   ```env
   GROQ_API_KEY=gsk_...
   ```

   Never commit `.env` or paste keys into source code.

5. **Run the app:**

   ```bash
   streamlit run app.py
   ```

   Your browser should open to the local Streamlit URL (usually `http://localhost:8501`).

## Usage

1. Upload a text-based PDF (not a scanned image-only file).
2. Wait for extraction to finish.
3. Type a question and click **Get answer**.
4. Use the text preview expander to confirm what was extracted.

## Optional environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | *(required)* | Groq API key |
| `GROQ_MODEL` | `llama-3.1-8b-instant` | Chat model name |
| `MAX_PDF_SIZE_MB` | `25` | Upload size limit |
| `MAX_CONTEXT_CHARS` | `120000` | Trim long PDFs before sending to the model |

## Limitations

- Image-only (scanned) PDFs without a text layer will not work without OCR.
- Very long documents may be truncated (`MAX_CONTEXT_CHARS`).
- Answers depend on extraction quality and model behavior—always check the source PDF for critical use.

## License

Use and modify freely for portfolio and learning purposes.
