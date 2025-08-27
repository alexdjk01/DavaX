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
    long_summary: Optional[str] = None  # detailed summary

from typing import Optional
class BookCoverRequest(BaseModel):
    title: str
    summary: Optional[str] = None
    style: Optional[str] = "vintage paperback, limited palette, clean typography, high contrast"

class BookCoverResponse(BaseModel):
    data_url: str  # "data:image/png;base64,..."