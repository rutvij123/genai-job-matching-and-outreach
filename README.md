# Cold Email Generator (Groq + LangChain + ChromaDB + Streamlit)

A small app that:
1) Scrapes a careers/jobs URL
2) Extracts job postings with an LLM
3) Parses a PDF resume and embeds it
4) Stores job vectors in Chroma
5) Finds the best-matching job
6) Generates a tailored cold email

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
cp app/.env.example app/.env                        # put your actual key in app/.env
streamlit run app/main.py
```

## Env Vars

Create `app/.env`:
```
GROQ_API_KEY=your_groq_key_here
MODEL_NAME=llama-3.3-70b-versatile
```

## Notes
- This repo structure is inspired by codebasics's project (educational). This version adds a modular `src/` and a complete Streamlit UI.
- Do **not** commit your real API keys.
