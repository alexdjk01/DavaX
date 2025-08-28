import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
LONG_PATH = DATA_DIR / "book_summaries_long.json"

def get_summary_by_title(title: str) -> str | None:
    """Return the long summary for an exact book title from local JSON."""
    if not LONG_PATH.exists():
        return None
    data = json.loads(LONG_PATH.read_text(encoding="utf-8"))
    return data.get(title)
