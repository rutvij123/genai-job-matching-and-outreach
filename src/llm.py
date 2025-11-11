import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "app", ".env"))

def get_llm(temperature: float = 0.0, model_name: str | None = None) -> ChatGroq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set. Put it in app/.env")
    model = model_name or os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
    return ChatGroq(temperature=temperature, groq_api_key=api_key, model_name=model)
