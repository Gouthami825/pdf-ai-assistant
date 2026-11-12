"""Groq API helpers for question answering over PDF content."""

from __future__ import annotations

from groq import Groq

SYSTEM_PROMPT = """You are a helpful assistant that answers questions about a PDF document.

Rules:
1. Use ONLY the document text provided in the user message. Do not use outside knowledge.
2. If the answer is not clearly supported by the document, respond with exactly this sentence
   (you may add a brief explanation after it): "The answer is not present in the uploaded PDF."
3. When the answer is in the document, be concise and accurate. Quote short phrases when helpful.
4. If the question is unclear, say what information you would need from the document."""


class GroqClientError(Exception):
    """Raised when the Groq API call fails."""


def answer_question(
    *,
    api_key: str,
    model: str,
    document_text: str,
    question: str,
) -> str:
    """
    Ask the Groq LLM a question grounded in document_text.

    Raises:
        GroqClientError: On API or configuration failures.
    """
    question = question.strip()
    if not question:
        raise ValueError("Question cannot be empty.")
    if not api_key:
        raise GroqClientError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    user_content = (
        f"DOCUMENT TEXT:\n\n{document_text}\n\n"
        f"---\n\nQUESTION: {question}\n\n"
        "Answer using only the document text above."
    )

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.2,
            max_tokens=1024,
        )
    except Exception as exc:  # noqa: BLE001
        raise GroqClientError(
            f"Could not get a response from Groq. Details: {exc}"
        ) from exc

    choice = response.choices[0] if response.choices else None
    if not choice or not choice.message or not choice.message.content:
        raise GroqClientError("Groq returned an empty response.")

    return choice.message.content.strip()
