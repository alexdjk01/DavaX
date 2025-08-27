
from __future__ import annotations
import os, json
from typing import List, Dict, Any
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

DATA_DIR = Path(__file__).parent / "data"
VSTORE_DIR = Path(__file__).parent / "vectorstore" / "chroma"

# Lazy initialized singleton
_client = None
_collection = None

def _ensure_collection():
    global _client, _collection
    if _client is None:
        _client = chromadb.PersistentClient(path=str(VSTORE_DIR))
    if _collection is None:
        ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            api_base=os.getenv("OPENAI_API_BASE") or None,
            model_name=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        )
        _collection = _client.get_or_create_collection(
            name="books",
            metadata={"hnsw:space": "cosine"},
            embedding_function=ef,
        )
    return _collection

def search(query: str, k: int = 3):
    col = _ensure_collection()
    res = col.query(query_texts=[query], n_results=k, include=["metadatas", "documents", "distances"])
    out = []
    got = zip(res.get("documents", [[]])[0], res.get("metadatas", [[]])[0], res.get("distances", [[]])[0])
    for doc, meta, dist in got:
        score = 1.0 - float(dist) if dist is not None else 0.0
        # (metadata must stay primitives)
        themes_csv = meta.get("themes_csv", "") if isinstance(meta, dict) else meta["themes_csv"]
        themes = [t.strip() for t in themes_csv.split(",") if t.strip()]

        item = {
            "title": meta.get("title") if isinstance(meta, dict) else meta["title"],
            "short_summary": meta.get("short_summary") if isinstance(meta, dict) else meta["short_summary"],
            "themes": themes,
            "score": score,
        }
        out.append(item)
    return out