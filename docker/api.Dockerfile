FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/home/app/.cache/huggingface

WORKDIR /app

# CPU-only torch keeps the image ~2 GB smaller than the default CUDA build
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install dependencies in their own layer so code changes don't reinstall them
COPY pyproject.toml README.md ./
RUN mkdir -p src/job_outreach && touch src/job_outreach/__init__.py && pip install . && pip uninstall -y job-outreach && rm -rf build src *.egg-info

COPY src ./src
RUN pip install --no-deps .

# Run as a non-root user and bake the embedding model into the image
RUN useradd --create-home app
USER app
ARG EMBEDDING_MODEL=all-MiniLM-L6-v2
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('${EMBEDDING_MODEL}')"

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "job_outreach.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
