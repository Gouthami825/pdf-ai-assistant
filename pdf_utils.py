"""PDF text extraction helpers using PyMuPDF."""

from __future__ import annotations

import fitz  # PyMuPDF


class PDFExtractionError(Exception):
    """Raised when a PDF cannot be read or has no extractable text."""


def extract_text_from_pdf(file_bytes: bytes) -> tuple[str, int]:
    """
    Extract plain text from a PDF file.

    Returns:
        A tuple of (full_text, page_count).

    Raises:
        PDFExtractionError: If the file is invalid or contains no text.
    """
    if not file_bytes:
        raise PDFExtractionError("The uploaded file is empty.")

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:  # noqa: BLE001 — surface a friendly message to the UI
        raise PDFExtractionError(
            "Could not open this file. Please upload a valid PDF."
        ) from exc

    try:
        page_count = doc.page_count
        if page_count == 0:
            raise PDFExtractionError("This PDF has no pages.")

        parts: list[str] = []
        for page_index in range(page_count):
            page = doc.load_page(page_index)
            text = page.get_text("text").strip()
            if text:
                parts.append(f"--- Page {page_index + 1} ---\n{text}")

        full_text = "\n\n".join(parts).strip()
        if not full_text:
            raise PDFExtractionError(
                "No readable text was found in this PDF. "
                "Scanned image-only PDFs may need OCR (not supported here)."
            )

        return full_text, page_count
    finally:
        doc.close()


def trim_context(text: str, max_chars: int) -> tuple[str, bool]:
    """
    Trim text to a maximum length for the LLM context window.

    Returns:
        (trimmed_text, was_trimmed)
    """
    if len(text) <= max_chars:
        return text, False
    notice = (
        "\n\n[... Document truncated for length. "
        "Answers may miss content from later pages. ...]\n\n"
    )
    keep = max_chars - len(notice)
    if keep < 1000:
        keep = max_chars
        notice = ""
    return text[:keep] + notice, True
