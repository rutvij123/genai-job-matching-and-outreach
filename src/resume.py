from typing import Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import PyPDF2

def read_pdf_text(path: str) -> str:
    text = ""
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def embed_texts(texts: list[str], model_name: str = "all-MiniLM-L6-v2") -> np.ndarray:
    model = SentenceTransformer(model_name)
    return model.encode(texts, show_progress_bar=False)

def embed_resume(path: str) -> Tuple[str, np.ndarray]:
    txt = read_pdf_text(path)
    emb = embed_texts([txt])
    return txt, emb
