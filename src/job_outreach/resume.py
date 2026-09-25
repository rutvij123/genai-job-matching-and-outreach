from io import BytesIO

from pypdf import PdfReader

from .exceptions import ResumeError


def read_pdf_text(data: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(data))
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception as e:
        raise ResumeError("File is not a readable PDF") from e
    if len(text) < 50:
        raise ResumeError("Could not extract text from the PDF (is it a scanned image?)")
    return text


def chunk_text(text: str, max_words: int = 150, overlap: int = 30) -> list[str]:
    """Split text into overlapping word windows.

    The embedding model truncates long inputs (~256 tokens for MiniLM), so embedding a
    whole resume at once ignores everything past the first section.
    """
    words = text.split()
    if len(words) <= max_words:
        return [" ".join(words)]
    step = max_words - overlap
    return [" ".join(words[i : i + max_words]) for i in range(0, len(words) - overlap, step)]
