from langchain_core.prompts import PromptTemplate

EXTRACT_TEMPLATE = PromptTemplate.from_template(
    """
    ### SCRAPED TEXT FROM WEBSITE:
    {page_data}
    ### INSTRUCTION:
    The scraped text is from a careers page.
    Extract job postings and return a JSON array of objects with keys:
    "role", "experience", "skills", "description".
    Return only VALID JSON. Aim for up to 50 postings if available.
    ### VALID JSON (NO PREAMBLE):
    """
)

def build_extract_chain(llm):
    return EXTRACT_TEMPLATE | llm
