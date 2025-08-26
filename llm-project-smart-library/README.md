# Smart Librarian – Retro Terminal RAG (Scaffold)

Acesta este **scheletul** proiectului. Vom construi incremental, pas cu pas.

## Cum rulezi backend-ul (development)
1) Creează și activează un virtualenv (opțional, dar recomandat)
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```
2) Instalează dependențele:
```bash
pip install -r requirements.txt
```
3) Copiază `.env.example` în `.env` și setează cheia OpenAI:
```
OPENAI_API_KEY=sk-... (cheia ta)
OPENAI_API_BASE=   # lasă gol dacă folosești endpointul oficial
```
4) Pornește serverul:
```bash
uvicorn backend.app:app --reload
```
5) Deschide frontend-ul (oricare dintre opțiuni):
- folosește un server static simplu:
```bash
# din directorul frontend/
python -m http.server 8000
# apoi deschide http://localhost:8000
```
- sau deschide `frontend/index.html` direct în browser (poate necesita dezactivarea CORS strict pentru file://).

## Structură
- `backend/` – FastAPI + RAG (ChromaDB), tool-calling
- `frontend/` – UI retro „CRT” (HTML/CSS/JS)
- `scripts/` – generarea/validarea dataset-ului și indexare
- `tests/` – smoke & mini-evaluări

## Următorii pași
- Populăm `seed_titles.csv` la 250+ intrări.
- Implementăm `scripts/gen_dataset.py` (batch + resume), `validate_dataset.py` și `build_index.py`.
- Construim retriever-ul și endpointul `/chat`.
