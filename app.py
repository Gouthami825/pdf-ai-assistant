"""
PDF AI Assistant — Streamlit app.

Upload a PDF, extract text with PyMuPDF, and ask questions answered via Groq (PDF content only).
"""

from __future__ import annotations

import streamlit as st

import config
from llm_utils import GroqClientError, answer_question
from pdf_utils import PDFExtractionError, extract_text_from_pdf, trim_context

# --- Page setup ---
st.set_page_config(
    page_title="PDF AI Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    .main-header { font-size: 2rem; font-weight: 600; margin-bottom: 0.25rem; }
    .sub-header { color: #6b7280; font-size: 1rem; margin-bottom: 1.5rem; }
    .stAlert { border-radius: 8px; }
    div[data-testid="stFileUploader"] section {
        border-radius: 8px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def init_session_state() -> None:
    """Initialize Streamlit session keys once."""
    defaults = {
        "pdf_text": None,
        "pdf_name": None,
        "page_count": None,
        "context_trimmed": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def validate_upload(uploaded_file) -> str | None:
    """Return an error message if the upload is invalid, else None."""
    if uploaded_file is None:
        return None
    name = (uploaded_file.name or "").lower()
    if not name.endswith(".pdf"):
        return "Please upload a file with a .pdf extension."
    if uploaded_file.size is not None and uploaded_file.size > config.MAX_PDF_BYTES:
        size_mb = uploaded_file.size / (1024 * 1024)
        return (
            f"This PDF exceeds the {config.MAX_PDF_SIZE_MB} MB upload limit "
            f"(your file is about {size_mb:.1f} MB). "
            "Please choose a smaller PDF."
        )
    return None


def process_upload(uploaded_file) -> None:
    """Extract text from an uploaded PDF into session state."""
    file_bytes = uploaded_file.getvalue()
    text, pages = extract_text_from_pdf(file_bytes)
    text, trimmed = trim_context(text, config.MAX_CONTEXT_CHARS)
    st.session_state.pdf_text = text
    st.session_state.pdf_name = uploaded_file.name
    st.session_state.page_count = pages
    st.session_state.context_trimmed = trimmed


def render_sidebar() -> None:
    with st.sidebar:
        st.header("About")
        st.markdown(
            "This **learning/demo** app extracts text from your PDF and uses the "
            "[Groq](https://groq.com/) API to answer questions **only** from that text."
        )
        st.divider()
        st.subheader("Configuration")
        if config.GROQ_API_KEY:
            st.success("Groq API key loaded from environment.")
        else:
            st.warning(
                "No `GROQ_API_KEY` found. Copy `.env.example` to `.env` and restart the app."
            )
        st.caption(f"Model: `{config.GROQ_MODEL}`")
        st.caption(f"Max upload: {config.MAX_PDF_SIZE_MB} MB")
        if st.button("Clear session", use_container_width=True):
            for key in ("pdf_text", "pdf_name", "page_count", "context_trimmed"):
                st.session_state[key] = None if key != "context_trimmed" else False
            st.rerun()


def main() -> None:
    init_session_state()
    render_sidebar()

    st.markdown('<p class="main-header">PDF AI Assistant</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Upload a PDF and ask questions grounded in its content.</p>',
        unsafe_allow_html=True,
    )

    col_upload, col_status = st.columns([2, 1])
    with col_upload:
        uploaded = st.file_uploader(
            "Choose a PDF",
            type=["pdf"],
            help=f"Maximum file size: {config.MAX_PDF_SIZE_MB} MB",
            max_upload_size=config.MAX_PDF_SIZE_MB,
        )

    upload_error = validate_upload(uploaded)
    if upload_error:
        st.error(upload_error)
        return

    if uploaded is not None:
        if st.session_state.pdf_name != uploaded.name:
            try:
                with st.spinner("Extracting text from PDF…"):
                    process_upload(uploaded)
                st.success(f"Loaded **{uploaded.name}** ({st.session_state.page_count} pages).")
            except PDFExtractionError as exc:
                st.error(str(exc))
                st.session_state.pdf_text = None
                return

    with col_status:
        if st.session_state.pdf_text:
            st.metric("Pages", st.session_state.page_count or "—")
            if st.session_state.context_trimmed:
                st.caption("Document was shortened for the model context limit.")

    if st.session_state.pdf_text:
        with st.expander("Preview extracted text", expanded=False):
            preview = st.session_state.pdf_text
            if len(preview) > 8000:
                st.text(preview[:8000] + "\n\n… (preview truncated)")
            else:
                st.text(preview)

    st.divider()
    st.subheader("Ask a question")

    question = st.text_area(
        "Your question",
        placeholder="e.g. What is the main conclusion of this document?",
        height=100,
        disabled=st.session_state.pdf_text is None,
    )

    ask_clicked = st.button(
        "Get answer",
        type="primary",
        disabled=st.session_state.pdf_text is None,
        use_container_width=False,
    )

    if ask_clicked:
        if not question or not question.strip():
            st.warning("Please enter a question.")
            return
        if not config.GROQ_API_KEY:
            st.error(
                "Missing Groq API key. Create a `.env` file with `GROQ_API_KEY=...` "
                "and restart Streamlit."
            )
            return

        try:
            with st.spinner("Thinking…"):
                answer = answer_question(
                    api_key=config.GROQ_API_KEY,
                    model=config.GROQ_MODEL,
                    document_text=st.session_state.pdf_text,
                    question=question,
                )
            st.markdown("### Answer")
            st.markdown(answer)
        except GroqClientError as exc:
            st.error(str(exc))
        except ValueError as exc:
            st.warning(str(exc))

    if st.session_state.pdf_text is None:
        st.info("Upload a PDF above to enable questions.")

    st.caption(
        "Educational demo — not intended for production use. "
        "Verify important answers against the original PDF."
    )


if __name__ == "__main__":
    main()
