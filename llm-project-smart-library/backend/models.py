from pydantic import BaseModel
from typing import Optional, Literal

class Health(BaseModel):
    status: str

class ChatRequest(BaseModel):
    message: str
    language: Optional[Literal["ro", "en"]] = "ro"

class ChatResponse(BaseModel):
    title: str
    summary: str
