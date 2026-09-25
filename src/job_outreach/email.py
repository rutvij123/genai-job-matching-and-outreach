from langchain_core.prompts import PromptTemplate

from .llm import invoke_text
from .schemas import Job

EMAIL_PROMPT = PromptTemplate.from_template(
    """### TARGET JOB
Role: {role}
Experience required: {experience}
Key skills: {skills}
Description: {description}

### CANDIDATE RESUME
{resume_text}

### INSTRUCTION
Write a cold email from the candidate to the hiring manager for this role.
- First line: "Subject: <subject>"
- 120-180 words, professional and specific, no generic filler.
- Reference 2-3 concrete experiences or skills FROM THE RESUME that match the job.
- Never invent experience, employers, or numbers that are not in the resume.
- End with a short call to action and sign off as: {signoff}
Return only the email.
"""
)


def generate_email(
    llm,
    job: Job,
    resume_text: str,
    candidate_name: str | None = None,
    max_resume_chars: int = 8_000,
) -> str:
    return invoke_text(
        EMAIL_PROMPT | llm,
        {
            "role": job.role,
            "experience": job.experience,
            "skills": ", ".join(job.skills),
            "description": job.description,
            "resume_text": resume_text[:max_resume_chars],
            "signoff": candidate_name or "the candidate's name as written on the resume",
        },
    ).strip()
