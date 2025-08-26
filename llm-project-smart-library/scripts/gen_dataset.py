"""
Generează dataset-ul (200+ cărți) în batch-uri, cu resume și backoff.

Exemple de rulare:
  python scripts/gen_dataset.py --batch 25 --start 0 --limit 120
  python scripts/gen_dataset.py --batch 20 --start 120 --limit 260 --model gpt-4o-mini

Fișiere de I/O:
  - IN : backend/data/seed_titles.csv
  - OUT: backend/data/book_summaries.json            (listă cu obiecte scurte)
        backend/data/book_summaries_long.json       (dict: title -> rezumat lung)
"""
from __future__ import annotations
import argparse, csv, json, os, time, sys, re, math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List, Optional

# OpenAI client (ieftin: model mini pentru generare)
try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # va da eroare prietenoasă mai jos

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "backend" / "data"
SEED_CSV = DATA_DIR / "seed_titles.csv"
OUT_SHORT = DATA_DIR / "book_summaries.json"
OUT_LONG = DATA_DIR / "book_summaries_long.json"

CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")  # low-cost
TEMPERATURE = float(os.getenv("GEN_TEMP", "0.3"))
MAX_RETRIES = 4

VOCAB_THEMES = [
    "prietenie","magie","curaj","familie","dragoste","sacrificiu","război","mister",
    "investigație","dezvoltare personală","călătorie","trădare","libertate","supraviețuire",
    "politică","etică","memorie","identitate","alienare","viitor","tehnologie","mitologie"
]
VOCAB_MOODS = [
    "found family","quest","melancholy","hopeful","dark","whimsical","noir","satirical",
    "philosophical","romance-slow-burn","epic","introspective","fast-paced","grim","uplifting"
]

JSON_SCHEMA_DOC = """
Ești un asistent care produce STRICT JSON valid. Nu include explicații, comentarii sau text în afara JSON-ului.
CÂMPURI:
{
  "short_summary": string (40-120 cuvinte, în limba de intrare: 'ro' sau 'en'),
  "themes": string[] (3-6 elemente din vocabularul dat),
  "mood_tags": string[] (2-5 elemente din vocabularul dat),
  "genres": string[] (include genul dat și eventual altele relevante),
  "language": "ro" | "en",
  "long_summary": string (3-6 paragrafe scurte, în limba de intrare)
}
Vocabular pt 'themes': {themes}
Vocabular pt 'mood_tags': {moods}
Ieșire: DOAR JSON, fără markdown, fără ```.
""".strip()

def _load_seed() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with SEED_CSV.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "title": r["title"].strip(),
                "author": r["author"].strip(),
                "year": int(r["year"]),
                "language": r["language"].strip(),
                "genre": r["genre"].strip(),
            })
    return rows

def _load_json_file(path: Path, default):
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return default
    return default

def _save_json(path: Path, obj):
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    tmp.replace(path)

def _already_done(short_list: List[Dict[str, Any]], long_map: Dict[str, str], title: str) -> bool:
    in_short = any(x.get("title") == title for x in short_list)
    in_long = title in long_map
    return in_short and in_long

def _strip_code_fences(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        s = s.strip("`")
        # try to remove possible language hint
        s = re.sub(r"^\w+\s*", "", s)
    return s.strip()

def _ask_llm(client, item: Dict[str, Any]) -> Dict[str, Any]:
    sys_prompt = JSON_SCHEMA_DOC.format(themes=VOCAB_THEMES, moods=VOCAB_MOODS)
    user_prompt = (
        "Generează metadate pentru cartea de mai jos.\n"
        f"Titlu: {item['title']}\n"
        f"Autor: {item['author']}\n"
        f"An: {item['year']}\n"
        f"Gen (seed): {item['genre']}\n"
        f"Limbă: {item['language']} (scrie rezumatele în această limbă)\n"
        "Ieșire: STRICT un obiect JSON conform schema, fără alte explicații."
    )
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=TEMPERATURE,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = resp.choices[0].message.content or ""
    content = _strip_code_fences(content)
    try:
        data = json.loads(content)
    except Exception as e:
        # ultimul efort: găsește primul obiect JSON din text
        m = re.search(r"\{.*\}", content, re.S)
        if not m:
            raise
        data = json.loads(m.group(0))
    return data

def _validate_piece(x: Dict[str, Any], seed_lang: str, seed_genre: str) -> Optional[str]:
    # reguli simple: câmpuri esențiale + lungimi
    miss = [k for k in ("short_summary","themes","mood_tags","genres","language","long_summary") if k not in x]
    if miss:
        return f"câmpuri lipsă: {miss}"
    if len(x["short_summary"].split()) < 30:
        return "short_summary prea scurt"
    if not (3 <= len(x["themes"]) <= 6):
        return "themes dimensiune invalidă"
    if not (2 <= len(x["mood_tags"]) <= 6):
        return "mood_tags dimensiune invalidă"
    if seed_genre not in x.get("genres", []):
        # asigurăm păstrarea genului seed
        x["genres"] = list(dict.fromkeys([seed_genre] + list(x.get("genres", []))))
    # limbă: păstrăm limbajul cerut
    x["language"] = seed_lang
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=25)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--limit", type=int, default=260)
    ap.add_argument("--model", type=str, default=CHAT_MODEL)
    args = ap.parse_args()

    if OpenAI is None:
        print("Eroare: biblioteca 'openai' nu este instalată. Rulează: pip install openai", file=sys.stderr)
        sys.exit(2)

    client = OpenAI()

    seed = _load_seed()
    total = min(len(seed), args.limit)
    start = args.start
    end = total

    short_list = _load_json_file(OUT_SHORT, [])
    long_map = _load_json_file(OUT_LONG, {})

    processed = 0
    for i in range(start, end):
        item = seed[i]
        title = item["title"]

        if _already_done(short_list, long_map, title):
            continue

        # batching control
        if processed and processed % args.batch == 0:
            # checkpoint pe OUT files
            _save_json(OUT_SHORT, short_list)
            _save_json(OUT_LONG, long_map)
            print(f"[checkpoint] salvat până la index {i-1} (processed batch={processed}).")

        # retry cu backoff
        delay = 2.0
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                data = _ask_llm(client, item)
                err = _validate_piece(data, item["language"], item["genre"])
                if err:
                    raise ValueError(f"validare eșuată: {err}")
                # adaugă în structuri
                short_list.append({
                    "title": title,
                    "author": item["author"],
                    "year": item["year"],
                    "short_summary": data["short_summary"],
                    "themes": data["themes"],
                    "mood_tags": data["mood_tags"],
                    "genres": data["genres"],
                    "language": data["language"],
                    "source": "seed_titles.csv"
                })
                long_map[title] = data["long_summary"]
                print(f"[ok] {title}")
                break
            except Exception as e:
                if attempt == MAX_RETRIES:
                    print(f"[fail] {title}: {e}")
                else:
                    print(f"[retry {attempt}] {title}: {e} → sleep {delay:.1f}s")
                    time.sleep(delay)
                    delay *= 1.8  # backoff
        processed += 1

    # final save
    _save_json(OUT_SHORT, short_list)
    _save_json(OUT_LONG, long_map)
    print(f"Terminat. Total intrări scurte: {len(short_list)}; rezumate lungi: {len(long_map)}.")

if __name__ == "__main__":
    main()
