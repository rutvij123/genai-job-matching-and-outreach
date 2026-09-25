from pydantic import BaseModel, Field, HttpUrl, field_validator


class Job(BaseModel):
    role: str = ""
    experience: str = ""
    skills: list[str] = Field(default_factory=list)
    description: str = ""

    @field_validator("role", "experience", "description", mode="before")
    @classmethod
    def _to_str(cls, v):
        return "" if v is None else str(v)

    @field_validator("skills", mode="before")
    @classmethod
    def _to_list(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return [str(s) for s in v]

    def as_text(self) -> str:
        return (
            f"{self.role}. {self.experience}. Skills: {', '.join(self.skills)}. {self.description}"
        )


class ExtractRequest(BaseModel):
    url: HttpUrl


class ExtractResponse(BaseModel):
    url: str
    count: int
    jobs: list[Job]


class ResumeResponse(BaseModel):
    chars: int
    text: str


class Match(BaseModel):
    rank: int
    score: float = Field(description="Cosine similarity between resume and job (higher is better)")
    job: Job


class MatchResponse(BaseModel):
    jobs_found: int
    matches: list[Match]


class EmailRequest(BaseModel):
    job: Job
    resume_text: str = Field(min_length=50)
    candidate_name: str | None = None


class EmailResponse(BaseModel):
    email: str


class PipelineResponse(MatchResponse):
    email: str | None = None


class HealthResponse(BaseModel):
    status: str
    version: str
    llm_configured: bool
