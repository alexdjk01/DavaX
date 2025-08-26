"""
Generează dataset-ul (200+ cărți) în batch-uri, folosind OpenAI pentru scurte rezumate + tag-uri.
Rulare:
  python scripts/gen_dataset.py --batch 25 --start 0 --limit 100
"""
import argparse, json, csv, time
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "backend" / "data"
SEED_CSV = DATA_DIR / "seed_titles.csv"
OUT_SHORT = DATA_DIR / "book_summaries.json"
OUT_LONG = DATA_DIR / "book_summaries_long.json"

# TODO: importă clientul OpenAI și implementează batching + resume.

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=25)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--limit", type=int, default=100)
    args = ap.parse_args()
    print("[TODO] Gen dataset: batch=", args.batch, "start=", args.start, "limit=", args.limit)

if __name__ == "__main__":
    main()
