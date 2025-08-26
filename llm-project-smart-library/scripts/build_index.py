"""Construiește indexul ChromaDB din book_summaries.json."""
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "backend" / "data"
VSTORE_DIR = Path(__file__).resolve().parents[1] / "backend" / "vectorstore" / "chroma"

def main():
    print("[TODO] build_index: încarcă JSON, calculează embeddings, populează Chroma…")

if __name__ == "__main__":
    main()
