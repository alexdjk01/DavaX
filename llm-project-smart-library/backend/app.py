# backend/app.py
import os, json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import ChatRequest, ChatResponse, Health
from . import rag, tools
from . import safety_filter
from openai import OpenAI

app = FastAPI(title="Smart Librarian – Retro Terminal RAG")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI()  # picks up OPENAI_API_KEY/OPENAI_API_BASE from env

@app.get("/health", response_model=Health)
def health() -> Health:
    return Health(status="ok")

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    # 0) Safety gate: block profanity before hitting retrieval/LLM
    ok, bad = safety_filter.is_input_allowed(req.message or "")
    if not ok:
        return ChatResponse(
            title="Input not allowed",
            summary="Please rephrase your request politely.",
            long_summary=None,
        )

    # 1) Retrieve top candidates from vector store (no generation)
    candidates = rag.search(req.message, k=3)
    if not candidates:
        return ChatResponse(
            title="No match found",
            summary="Try being more specific (themes, genres, author, period).",
            long_summary=None,
        )

    # 2) Prepare a minimal tool spec for function calling
    candidate_titles = [c["title"] for c in candidates]
    tools_schema = [{
        "type": "function",
        "function": {
            "name": "get_summary_by_title",
            "description": "Return the long summary for an exact book title from local DB.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "enum": candidate_titles}
                },
                "required": ["title"]
            }
        }
    }]

    # 3) Ask GPT to pick ONE title from the candidates using tool calling
    system_msg = {
        "role": "system",
        "content": (
            "You are a helpful book recommender. "
            "Pick exactly one title from the provided candidates that best matches the user query. "
            "Then call get_summary_by_title with that exact title."
        ),
    }
    user_msg = {"role": "user", "content": req.message}
    assistant_context = {
        "role": "assistant",
        "content": "Candidates:\n" + "\n".join(f"- {t}" for t in candidate_titles),
    }

    resp = client.chat.completions.create(
        model=os.getenv("CHAT_MODEL", "gpt-4o-mini"),
        messages=[system_msg, user_msg, assistant_context],
        tools=tools_schema,
        tool_choice="auto",
    )

    # 4) Execute the tool call locally and assemble the final response
    chosen_title = candidate_titles[0]
    long_summary = None

    msg = resp.choices[0].message
    if msg.tool_calls:
        for call in msg.tool_calls:
            if call.function.name == "get_summary_by_title":
                args = json.loads(call.function.arguments or "{}")
                if "title" in args and args["title"] in candidate_titles:
                    chosen_title = args["title"]
                    long_summary = tools.get_summary_by_title(chosen_title)
                break  # use the first valid tool call

    # Fallback if no tool call (or invalid args)
    if not long_summary:
        long_summary = tools.get_summary_by_title(chosen_title)

    # 5) Return short summary (from RAG) + optional long summary (from tool)
    short = next((c["short_summary"] for c in candidates if c["title"] == chosen_title), candidates[0]["short_summary"])

    return ChatResponse(
        title=chosen_title,
        summary=short,
        long_summary=long_summary,
    )

