from job_outreach.api.deps import get_llm_dep
from job_outreach.api.main import app
from job_outreach.config import Settings, get_settings
from job_outreach.exceptions import ScrapeError

URL = "https://example.com/careers"


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert "x-request-id" in r.headers


def test_extract_jobs(client):
    r = client.post("/api/v1/jobs/extract", json={"url": URL})
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 2
    # comma-separated skills string is normalised to a list
    assert body["jobs"][1]["skills"] == ["baking", "desserts", "kitchen"]


def test_extract_rejects_bad_url(client):
    r = client.post("/api/v1/jobs/extract", json={"url": "not-a-url"})
    assert r.status_code == 422


def test_parse_resume(client, resume_pdf):
    r = client.post(
        "/api/v1/resume/parse", files={"resume": ("cv.pdf", resume_pdf, "application/pdf")}
    )
    assert r.status_code == 200
    assert "spark" in r.json()["text"]


def test_resume_must_be_pdf(client):
    r = client.post("/api/v1/resume/parse", files={"resume": ("cv.txt", b"hello", "text/plain")})
    assert r.status_code == 415


def test_corrupt_pdf(client):
    r = client.post(
        "/api/v1/resume/parse", files={"resume": ("cv.pdf", b"garbage", "application/pdf")}
    )
    assert r.status_code == 422
    assert r.json()["error"] == "ResumeError"


def test_match_ranks_relevant_job_first(client, resume_pdf):
    r = client.post(
        "/api/v1/match",
        data={"url": URL, "top_k": 2},
        files={"resume": ("cv.pdf", resume_pdf, "application/pdf")},
    )
    assert r.status_code == 200
    matches = r.json()["matches"]
    assert [m["job"]["role"] for m in matches] == ["Data Engineer", "Pastry Chef"]
    assert matches[0]["score"] > matches[1]["score"]


def test_pipeline_returns_email(client, resume_pdf):
    r = client.post(
        "/api/v1/pipeline",
        data={"url": URL, "candidate_name": "Ritz"},
        files={"resume": ("cv.pdf", resume_pdf, "application/pdf")},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["jobs_found"] == 2
    assert body["email"].startswith("Subject:")


def test_scrape_failure_maps_to_502(client):
    from job_outreach.api.deps import get_scraper

    def boom(url):
        raise ScrapeError("blocked")

    app.dependency_overrides[get_scraper] = lambda: boom
    r = client.post("/api/v1/jobs/extract", json={"url": URL})
    assert r.status_code == 502


def test_missing_api_key_returns_503(client):
    del app.dependency_overrides[get_llm_dep]
    app.dependency_overrides[get_settings] = lambda: Settings(_env_file=None, groq_api_key=None)
    r = client.post("/api/v1/jobs/extract", json={"url": URL})
    assert r.status_code == 503
