from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any

class Health(BaseModel):
    status: str

class ContextChunk(BaseModel):
    chunk: str
    score: float

class Recommendation(BaseModel):
    title: str
    why: str

class ChatRequest(BaseModel):
    message: str
    language: Optional[Literal["ro", "en"]] = "ro"
    wantImage: Optional[bool] = False

class ChatResponse(BaseModel):
    recommendation: Recommendation
    summary: str
    context: List[ContextChunk] = []
    imageUrl: Optional[str] = None
