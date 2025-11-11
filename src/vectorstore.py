from typing import List, Dict
import chromadb

def get_collection(path: str = "data/chroma_store", name: str = "job_postings"):
    client = chromadb.PersistentClient(path=path)
    return client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})

def add_jobs(collection, jobs: List[Dict], embeddings, docs: List[str], ids: List[str]):
    collection.add(ids=ids, documents=docs, metadatas=jobs, embeddings=embeddings)

def query_best(collection, query_embedding, n_results: int = 5):
    return collection.query(query_embeddings=query_embedding, n_results=n_results)
