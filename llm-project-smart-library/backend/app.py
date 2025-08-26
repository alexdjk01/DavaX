from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import ChatRequest, ChatResponse, Health
from . import rag

app = FastAPI(title="Smart Librarian – Retro Terminal RAG")

# Permissive CORS for local dev
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
    results = rag.search(req.message, k=1)
    if not results:
        return ChatResponse(
            title="No match found",
            summary="Try being more specific (themes, genres, author, period).",
        )
    top = results[0]
    return ChatResponse(
        title=top["title"],
        summary=top["short_summary"],
    )
