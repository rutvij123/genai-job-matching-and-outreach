import uuid
from functools import lru_cache

from .embeddings import Embedder
from .resume import chunk_text
from .schemas import Job, Match


@lru_cache
def _client():
    import chromadb
    from chromadb.config import Settings

    return chromadb.EphemeralClient(settings=Settings(anonymized_telemetry=False))


def rank_jobs(jobs: list[Job], resume_text: str, embedder: Embedder, top_k: int = 5) -> list[Match]:
    """Rank jobs by similarity to the resume.

    Each request gets its own throwaway Chroma collection, so results from different
    careers pages never mix. A job's score is its best similarity to any resume chunk.
    """
    if not jobs:
        return []

    job_embs = embedder.encode([j.as_text() for j in jobs])
    chunk_embs = embedder.encode(chunk_text(resume_text))

    client = _client()
    name = f"jobs_{uuid.uuid4().hex}"
    col = client.create_collection(name, metadata={"hnsw:space": "cosine"}, embedding_function=None)
    try:
        col.add(ids=[str(i) for i in range(len(jobs))], embeddings=job_embs)
        res = col.query(query_embeddings=chunk_embs, n_results=len(jobs))
    finally:
        client.delete_collection(name)

    best: dict[int, float] = {}
    for ids, dists in zip(res["ids"], res["distances"], strict=True):
        for job_id, dist in zip(ids, dists, strict=True):
            i = int(job_id)
            best[i] = max(best.get(i, -1.0), 1.0 - dist)

    ranked = sorted(best.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
    return [Match(rank=r + 1, score=round(s, 4), job=jobs[i]) for r, (i, s) in enumerate(ranked)]
