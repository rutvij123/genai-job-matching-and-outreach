from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import ValidationError

from .exceptions import ExtractionError
from .llm import invoke_text
from .schemas import Job

EXTRACT_PROMPT = PromptTemplate.from_template(
    """### SCRAPED TEXT FROM A CAREERS PAGE:
{page_data}

### INSTRUCTION:
Extract the job postings from the text above. Return a JSON array of objects with keys
"role" (string), "experience" (string), "skills" (array of strings), "description" (string).
If there are no job postings, return [].
Return ONLY valid JSON, no preamble.
"""
)


def extract_jobs(llm, page_text: str) -> list[Job]:
    raw = invoke_text(EXTRACT_PROMPT | llm, {"page_data": page_text})
    try:
        data = JsonOutputParser().parse(raw)
    except OutputParserException as e:
        raise ExtractionError("LLM did not return valid JSON for job postings") from e

    if isinstance(data, dict):
        data = data.get("jobs", [data])
    if not isinstance(data, list):
        raise ExtractionError("Expected a JSON array of job postings")

    jobs = []
    for item in data:
        if not isinstance(item, dict):
            continue
        try:
            jobs.append(Job.model_validate(item))
        except ValidationError:
            continue  # skip malformed entries rather than failing the whole request
    return jobs
