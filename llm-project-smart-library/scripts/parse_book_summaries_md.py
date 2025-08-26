
"""Parse `backend/data/book_summaries.md` into a JSON list for indexing.
Output: backend/data/book_summaries.json
Schema per item: {title, short_summary, themes}
"""
import re, json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "backend" / "data"
MD = DATA_DIR / "book_summaries.md"
OUT = DATA_DIR / "book_summaries.json"

def parse_md(text: str):
    # Split on lines starting with '## Title: ...'
    blocks = re.split(r"^##\s+Title:\s+", text, flags=re.MULTILINE)
    items = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        # First line until newline is the title
        first_newline = block.find("\n")
        if first_newline == -1:
            title = block.strip()
            body = ""
        else:
            title = block[:first_newline].strip()
            body = block[first_newline+1:].strip()
        # Themes line (optional) starts with 'Themes:'
        themes = []
        m = re.search(r"^Themes:\s*(.+)$", body, flags=re.MULTILINE)
        if m:
            themes = [t.strip() for t in re.split(r"[;,]", m.group(1)) if t.strip()]
            # Remove the themes line from body
            body = re.sub(r"^Themes:.*$", "", body, count=1, flags=re.MULTILINE).strip()
        # Normalize whitespace; keep body as a short paragraph (3–5 lines recommended by authoring).
        short_summary = body.strip()
        items.append({
            "title": title,
            "short_summary": short_summary,
            "themes": themes
        })
    return items

def main():
    text = MD.read_text(encoding="utf-8")
    items = parse_md(text)
    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(items)} items to {OUT}")

if __name__ == "__main__":
    main()
