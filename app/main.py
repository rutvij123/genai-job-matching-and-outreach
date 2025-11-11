import os
import json
import tempfile
import numpy as np
import streamlit as st
from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser

from src.llm import get_llm
from src.scraping import fetch_page_text
from src.extract import build_extract_chain
from src.resume import embed_resume, embed_texts
from src.vectorstore import get_collection, add_jobs, query_best
from src.email import build_email_chain
from src.utils import sanitize_metadata

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

st.set_page_config(page_title="Cold Email Generator", page_icon="📧", layout="wide")
st.title("📧 Cold Email Generator (Groq + LangChain + Chroma)")

with st.sidebar:
    st.header("Settings")
    model_name = st.text_input("Model name", os.getenv("MODEL_NAME", "llama-3.3-70b-versatile"))
    temperature = st.slider("Temperature", 0.0, 1.0, 0.0, 0.1)
    top_k = st.number_input("Top matches to show", min_value=1, max_value=10, value=5)
    st.markdown("---")
    st.caption("Provide a careers/jobs page URL and upload a resume (PDF).")

api_ok = bool(os.getenv("GROQ_API_KEY"))
if not api_ok:
    st.warning("Set `GROQ_API_KEY` in app/.env to enable LLM features.")

url = st.text_input("Careers URL", placeholder="https://www.naukri.com/software-developer-jobs")
resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
go = st.button("Extract → Match → Draft Email")

col1, col2 = st.columns([1, 1])

def try_parse_json(text: str):
    try:
        return json.loads(text)
    except Exception:
        # try LangChain parser for resilient parsing
        try:
            return JsonOutputParser().parse(text)
        except Exception:
            return []

if go:
    if not url or not resume_file:
        st.error("Please provide a URL and a resume PDF.")
        st.stop()

    with st.spinner("Fetching page..."):
        page_text = fetch_page_text(url)
        st.session_state["page_text_preview"] = page_text[:3000] + ("..." if len(page_text) > 3000 else "")

    with st.expander("🔎 Scraped page text (preview)"):
        st.code(st.session_state["page_text_preview"])

    with st.spinner("Extracting job postings with LLM..."):
        llm = get_llm(temperature=temperature, model_name=model_name)
        extract_chain = build_extract_chain(llm)
        res = extract_chain.invoke({"page_data": page_text})
        jobs_json = try_parse_json(res.content if hasattr(res, "content") else str(res))
        if not isinstance(jobs_json, list):
            st.error("Could not parse jobs JSON from LLM output.")
            st.stop()

    st.success(f"Extracted {len(jobs_json)} jobs")

    # Prepare job docs & embeddings
    job_texts = [f"{j.get('role','')} {j.get('experience','')} {j.get('skills','')} {j.get('description','')}" for j in jobs_json]
    with st.spinner("Embedding jobs..."):
        job_embs = embed_texts(job_texts)

    # Save resume to tmp and embed
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(resume_file.read())
        tmp_path = tmp.name

    with st.spinner("Embedding resume..."):
        resume_text, resume_emb = embed_resume(tmp_path)

    # Vector store
    with st.spinner("Indexing in Chroma..."):
        os.makedirs("data/chroma_store", exist_ok=True)
        col = get_collection(path="data/chroma_store", name="job_postings")
        ids = [f"job_{i}" for i in range(len(jobs_json))]
        metadatas = sanitize_metadata(jobs_json)
        add_jobs(col, metadatas, job_embs, job_texts, ids)

    # Retrieve
    with st.spinner("Retrieving best matches..."):
        results = query_best(col, resume_emb, n_results=int(top_k))
        matches = []
        for i in range(len(results["ids"][0])):
            md = results["metadatas"][0][i]
            doc = results["documents"][0][i]
            matches.append({"rank": i+1, "metadata": md, "doc": doc})
        st.session_state["matches"] = matches

    with col1:
        st.subheader("🎯 Top Matches")
        if matches:
            for m in matches:
                with st.expander(f"#{m['rank']} • {m['metadata'].get('role','Unknown Role')}"):
                    st.json(m["metadata"])

    # Build email on best match
    best = matches[0]["metadata"] if matches else None
    if best:
        job_role_name = best.get("role", "Unknown Role")
        job_role_desc = best.get("description", "")

        with st.spinner("Drafting cold email..."):
            email_chain = build_email_chain(llm)
            email_res = email_chain.invoke({
                "job_role_name": str(job_role_name),
                "job_role_desc": str(job_role_desc)
            })
            email_text = email_res.content if hasattr(email_res, "content") else str(email_res)

        with col2:
            st.subheader("✉️ Cold Email Draft")
            st.text_area("Generated Email", email_text, height=350)
            st.download_button("Download Email .txt", data=email_text.encode("utf-8"), file_name="cold_email.txt")

    st.success("Done!")

else:
    st.info("Fill the URL, upload a resume, then click the button.")
