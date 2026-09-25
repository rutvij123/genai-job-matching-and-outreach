from .exceptions import ScrapeError


def fetch_page_text(url: str, max_chars: int = 20_000) -> str:
    """Fetch the visible text of a page, whitespace-normalised and truncated to fit the LLM."""
    from langchain_community.document_loaders import WebBaseLoader

    try:
        docs = WebBaseLoader(url, requests_kwargs={"timeout": 20}).load()
    except Exception as e:
        raise ScrapeError(f"Could not fetch {url}: {e}") from e

    text = " ".join(" ".join(d.page_content for d in docs).split())
    if not text:
        raise ScrapeError("Page returned no visible text; it may be rendered with JavaScript.")
    return text[:max_chars]
