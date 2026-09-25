from job_outreach.resume import chunk_text
from job_outreach.schemas import Job


def test_job_normalises_fields():
    job = Job.model_validate({"role": None, "skills": "a, b ,, c", "experience": 3})
    assert job.role == ""
    assert job.skills == ["a", "b", "c"]
    assert job.experience == "3"


def test_chunk_text_short():
    assert chunk_text("one two three") == ["one two three"]


def test_chunk_text_covers_all_words():
    words = [f"w{i}" for i in range(400)]
    chunks = chunk_text(" ".join(words), max_words=150, overlap=30)
    assert len(chunks) > 1
    assert all(len(c.split()) <= 150 for c in chunks)
    assert words[-1] in chunks[-1]
