from functools import lru_cache
from typing import Protocol


class Embedder(Protocol):
    def encode(self, texts: list[str]) -> list[list[float]]: ...


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer  # heavy import, load lazily

        self._model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(
            texts, normalize_embeddings=True, show_progress_bar=False
        ).tolist()


@lru_cache(maxsize=2)
def get_embedder(model_name: str) -> Embedder:
    """Load the model once per process instead of on every request."""
    return SentenceTransformerEmbedder(model_name)
