import logging
import os
import time
import uuid

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .. import __version__
from ..config import Settings, get_settings
from ..exceptions import OutreachError
from ..schemas import HealthResponse
from .routes import router

logger = logging.getLogger("job_outreach")


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    app = FastAPI(
        title="Job Matching & Outreach API",
        version=__version__,
        description="Scrape job listings, match them to a resume with embeddings, "
        "and draft tailored cold emails with an LLM.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers["x-request-id"] = request_id
        logger.info(
            "%s %s -> %d (%.0f ms) [%s]",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
            request_id,
        )
        return response

    @app.exception_handler(OutreachError)
    async def handle_outreach_error(request: Request, exc: OutreachError):
        logger.warning("%s: %s", type(exc).__name__, exc)
        return JSONResponse(
            status_code=exc.status_code, content={"detail": str(exc), "error": type(exc).__name__}
        )

    @app.get("/health", response_model=HealthResponse, tags=["system"])
    def health(settings: Settings = Depends(get_settings)):
        return HealthResponse(
            status="ok", version=__version__, llm_configured=bool(settings.groq_api_key)
        )

    app.include_router(router)
    return app


app = create_app()


def run() -> None:
    """Console entry point: `job-outreach-api`."""
    import uvicorn

    uvicorn.run(
        "job_outreach.api.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
    )
