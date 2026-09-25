from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import AnyHttpUrl, TypeAdapter, ValidationError

from ..config import Settings, get_settings
from ..email import generate_email
from ..embeddings import Embedder
from ..extract import extract_jobs
from ..matching import rank_jobs
from ..resume import read_pdf_text
from ..schemas import (
    EmailRequest,
    EmailResponse,
    ExtractRequest,
    ExtractResponse,
    MatchResponse,
    PipelineResponse,
    ResumeResponse,
)
from .deps import get_embedder_dep, get_llm_dep, get_scraper

router = APIRouter(prefix="/api/v1")

SettingsDep = Annotated[Settings, Depends(get_settings)]
LLMDep = Annotated[object, Depends(get_llm_dep)]
EmbedderDep = Annotated[Embedder, Depends(get_embedder_dep)]
ScraperDep = Annotated[Callable[[str], str], Depends(get_scraper)]
UrlForm = Annotated[str, Form(description="Careers / job listings page URL")]
ResumeFile = Annotated[UploadFile, File(description="Resume as a PDF")]
TopKForm = Annotated[int, Form(ge=1, le=20)]

_url_adapter = TypeAdapter(AnyHttpUrl)


def _validate_url(url: str) -> str:
    try:
        return str(_url_adapter.validate_python(url))
    except ValidationError:
        raise HTTPException(422, "url must be a valid http(s) URL") from None


def _read_resume(file: UploadFile, settings: Settings) -> str:
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(415, "Resume must be a PDF file")
    data = file.file.read(settings.max_upload_bytes + 1)
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(413, f"Resume exceeds {settings.max_upload_mb} MB")
    return read_pdf_text(data)


# Routes are plain `def` so FastAPI runs them in a threadpool: embedding and LLM calls
# are blocking and would otherwise stall the event loop.


@router.post("/jobs/extract", response_model=ExtractResponse, tags=["jobs"])
def extract(req: ExtractRequest, llm: LLMDep, scrape: ScraperDep):
    """Scrape a careers page and extract structured job postings."""
    url = str(req.url)
    jobs = extract_jobs(llm, scrape(url))
    return ExtractResponse(url=url, count=len(jobs), jobs=jobs)


@router.post("/resume/parse", response_model=ResumeResponse, tags=["resume"])
def parse_resume(resume: ResumeFile, settings: SettingsDep):
    """Extract text from a PDF resume."""
    text = _read_resume(resume, settings)
    return ResumeResponse(chars=len(text), text=text)


@router.post("/match", response_model=MatchResponse, tags=["matching"])
def match(
    url: UrlForm,
    resume: ResumeFile,
    settings: SettingsDep,
    llm: LLMDep,
    embedder: EmbedderDep,
    scrape: ScraperDep,
    top_k: TopKForm = 5,
):
    """Rank the jobs on a careers page against a resume."""
    resume_text = _read_resume(resume, settings)  # validate cheap input before LLM calls
    jobs = extract_jobs(llm, scrape(_validate_url(url)))
    return MatchResponse(
        jobs_found=len(jobs), matches=rank_jobs(jobs, resume_text, embedder, top_k)
    )


@router.post("/emails", response_model=EmailResponse, tags=["email"])
def email(req: EmailRequest, llm: LLMDep, settings: SettingsDep):
    """Write a cold email for one job, grounded in the resume text."""
    body = generate_email(
        llm, req.job, req.resume_text, req.candidate_name, settings.max_resume_chars
    )
    return EmailResponse(email=body)


@router.post("/pipeline", response_model=PipelineResponse, tags=["pipeline"])
def pipeline(
    url: UrlForm,
    resume: ResumeFile,
    settings: SettingsDep,
    llm: LLMDep,
    embedder: EmbedderDep,
    scrape: ScraperDep,
    top_k: TopKForm = 5,
    candidate_name: Annotated[str | None, Form()] = None,
):
    """End to end: scrape → extract → match → draft an email for the best match."""
    resume_text = _read_resume(resume, settings)
    jobs = extract_jobs(llm, scrape(_validate_url(url)))
    matches = rank_jobs(jobs, resume_text, embedder, top_k)
    body = None
    if matches:
        body = generate_email(
            llm, matches[0].job, resume_text, candidate_name or None, settings.max_resume_chars
        )
    return PipelineResponse(jobs_found=len(jobs), matches=matches, email=body)
