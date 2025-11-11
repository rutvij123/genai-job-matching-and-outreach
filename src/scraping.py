from langchain_community.document_loaders import WebBaseLoader

def fetch_page_text(url: str) -> str:
    """
    Fetch visible webpage text using LangChain WebBaseLoader.
    Returns cleaned concatenated text from the site.
    """
    loader = WebBaseLoader(url)

    docs = loader.load()
    if not docs:
        return ""

    # Extract page content from all docs (WebBaseLoader returns a list)
    all_text = " ".join([d.page_content for d in docs])

    # remove excessive spaces
    clean_text = " ".join(all_text.split())

    return clean_text