import hashlib
import math
import re

import pytest
from fastapi.testclient import TestClient
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from job_outreach.api.deps import get_embedder_dep, get_llm_dep, get_scraper
from job_outreach.api.main import app
from job_outreach.config import Settings, get_settings

JOBS_JSON = """```json
[
  {"role": "Data Engineer", "experience": "3+ years",
   "skills": ["python", "spark", "etl", "airflow"],
   "description": "Build spark etl data pipelines in python"},
  {"role": "Pastry Chef", "experience": "2 years",
   "skills": "baking, desserts, kitchen",
   "description": "Prepare desserts and bread in a busy kitchen"}
]
```"""

EMAIL_TEXT = "Subject: Data Engineer role\n\nHi, I build spark etl pipelines in python..."

RESUME_LINES = [
    "Ritz - Data Engineer",
    "5 years building spark and hadoop etl data pipelines in python at a bank.",
    "Built audience segmentation and ML predictive models.",
    "Skills: python, spark, sql, airflow, etl",
]


class HashEmbedder:
    """Deterministic bag-of-words embedder so tests don't download a model."""

    dim = 256

    def encode(self, texts):
        out = []
        for t in texts:
            v = [0.0] * self.dim
            for w in re.findall(r"[a-z]+", t.lower()):
                v[int(hashlib.md5(w.encode()).hexdigest(), 16) % self.dim] += 1
            n = math.sqrt(sum(x * x for x in v)) or 1.0
            out.append([x / n for x in v])
        return out


def make_pdf(lines: list[str]) -> bytes:
    """Build a minimal valid text PDF without extra dependencies."""
    esc = [line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") for line in lines]
    stream = "BT /F1 11 Tf 14 TL 50 750 Td " + " ".join(f"({s}) Tj T*" for s in esc) + " ET"
    objs = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out, offsets = "%PDF-1.4\n", []
    for i, body in enumerate(objs, 1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n{body}\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n"
    out += "".join(f"{o:010d} 00000 n \n" for o in offsets)
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"
    return out.encode("latin-1")


@pytest.fixture
def resume_pdf() -> bytes:
    return make_pdf(RESUME_LINES)


@pytest.fixture
def client():
    llm = FakeListChatModel(responses=[JOBS_JSON, EMAIL_TEXT])
    app.dependency_overrides[get_settings] = lambda: Settings(_env_file=None, groq_api_key="test")
    app.dependency_overrides[get_llm_dep] = lambda: llm
    app.dependency_overrides[get_embedder_dep] = lambda: HashEmbedder()
    app.dependency_overrides[get_scraper] = lambda: lambda url: "Careers page text ..."
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
