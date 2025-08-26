from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .models import ChatRequest, ChatResponse, Health
from . import tools

app = FastAPI(title="Smart Librarian – Retro Terminal RAG")

# CORS (poți restrânge la originile tale în production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=Health)
def health() -> Health:
    return Health(status="ok")

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    # TODO: RAG + LLM + extrage titlul + tool-calling
    # PENTRU ACUM: stub simplu care apelează tool-ul după un titlu „The Hobbit”
    title = "The Hobbit"
    full = tools.get_summary_by_title(title)
    return ChatResponse(
        recommendation={"title": title, "why": "exemplu stub – înlocuiește cu scorul RAG"},
        summary=full or "Rezumat indisponibil (încă).",
        context=[],
        imageUrl=None
    )
