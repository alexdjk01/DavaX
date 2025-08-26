
"""Build a ChromaDB index from `book_summaries.json` using OpenAI embeddings.
Requirements:
  - OPENAI_API_KEY in environment (.env)
  - Optional: EMBEDDING_MODEL (default text-embedding-3-small)
"""
import os, json, uuid
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "backend" / "data" / "book_summaries.json"
VSTORE = ROOT / "backend" / "vectorstore" / "chroma"

def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    client = chromadb.PersistentClient(path=str(VSTORE))
    ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        api_base=os.getenv("OPENAI_API_BASE") or None,
        model_name=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
    )
    col = client.get_or_create_collection(name="books", metadata={"hnsw:space": "cosine"}, embedding_function=ef)

    # Clear existing docs to avoid duplicates during rebuilds.
    try:
        col.delete(where={})
    except Exception:
        pass

    ids, docs, metas = [], [], []
    for i, item in enumerate(data):
        doc = f"{item['title']}\n{item['short_summary']}\nThemes: {', '.join(item.get('themes', []))}"
        ids.append(str(uuid.uuid4()))
        docs.append(doc)
        metas.append({
            "title": item["title"],
            "short_summary": item["short_summary"],
            # CHANGED: store themes as CSV string, not list
            "themes_csv": ", ".join(item.get("themes", [])),
        })

    col.add(ids=ids, documents=docs, metadatas=metas)
    print(f"Indexed {len(ids)} documents into collection 'books' at {VSTORE}")

if __name__ == "__main__":
    main()
