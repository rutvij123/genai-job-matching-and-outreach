from langchain_core.language_models import BaseChatModel

from .config import Settings
from .exceptions import LLMError, LLMNotConfiguredError


def get_llm(settings: Settings) -> BaseChatModel:
    if not settings.groq_api_key:
        raise LLMNotConfiguredError("GROQ_API_KEY is not set")
    from langchain_groq import ChatGroq

    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.model_name,
        temperature=settings.llm_temperature,
    )


def invoke_text(chain, inputs: dict) -> str:
    """Run a prompt|llm chain and return the text, wrapping provider errors."""
    try:
        res = chain.invoke(inputs)
    except Exception as e:  # network, rate limit, auth errors from the provider
        raise LLMError(f"LLM call failed: {e}") from e
    return getattr(res, "content", str(res))
