from collections.abc import Callable
from functools import partial

from fastapi import Depends

from ..config import Settings, get_settings
from ..embeddings import Embedder, get_embedder
from ..llm import get_llm
from ..scraping import fetch_page_text


def get_llm_dep(settings: Settings = Depends(get_settings)):
    return get_llm(settings)


def get_embedder_dep(settings: Settings = Depends(get_settings)) -> Embedder:
    return get_embedder(settings.embedding_model)


def get_scraper(settings: Settings = Depends(get_settings)) -> Callable[[str], str]:
    return partial(fetch_page_text, max_chars=settings.max_page_chars)
