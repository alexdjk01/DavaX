
# Placeholder for future tool functions (e.g., long summaries lookup).
# Currently, the system responds with the curated short summaries only.
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def _load_long_summaries():
    fp = DATA_DIR / "book_summaries_long.json"
    if not fp.exists():
        return {}
    with fp.open("r", encoding="utf-8") as f:
        return json.load(f)

def get_summary_by_title(title: str):
    data = _load_long_summaries()
    return data.get(title)
