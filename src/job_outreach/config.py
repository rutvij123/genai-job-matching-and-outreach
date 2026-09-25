from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration, read from environment variables or a .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    groq_api_key: str | None = None
    model_name: str = "openai/gpt-oss-120b"
    llm_temperature: float = 0.0
    embedding_model: str = "all-MiniLM-L6-v2"
    max_page_chars: int = 20_000
    max_resume_chars: int = 8_000
    max_upload_mb: int = 5
    cors_origins: list[str] = ["*"]
    log_level: str = "INFO"

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
