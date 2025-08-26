"""
Validează/dedup-ează JSON-ul generat: câmpuri esențiale, lungimi, și duplicări.
Rulare:
  python scripts/validate_dataset.py
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "backend" / "data"
OUT_SHORT = DATA_DIR / "book_summaries.json"
OUT_LONG = DATA_DIR / "book_summaries_long.json"

def load_json(path, default):
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return default
    return default

def main():
    short_list = load_json(OUT_SHORT, [])
    long_map = load_json(OUT_LONG, {})

    # dedup după (title, author)
    seen = set()
    dedup_short = []
    for x in short_list:
        key = (x.get("title"), x.get("author"))
        if key in seen:
            continue
        seen.add(key)
        dedup_short.append(x)

    # sanity checks simple
    missing_long = [x["title"] for x in dedup_short if x["title"] not in long_map]
    too_short = [x["title"] for x in dedup_short if len((x.get("short_summary","")).split()) < 30]
    no_themes = [x["title"] for x in dedup_short if not x.get("themes")]

    report = {
        "short_count_before": len(short_list),
        "short_count_after": len(dedup_short),
        "long_count": len(long_map),
        "missing_long": missing_long[:10],  # mostră
        "too_short_samples": too_short[:10],
        "no_themes_samples": no_themes[:10],
    }

    # salvăm lista dedup
    with OUT_SHORT.open("w", encoding="utf-8") as f:
        json.dump(dedup_short, f, ensure_ascii=False, indent=2)

    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
