**Description:**

A minimal retrieval-augmented chatbot that recommends a book title and shows its summary from a local knowledge base.
All summaries come from your own dataset; the model does not generate new descriptions. 
Frontend is a retro green-on-black chat.

**_Run configuration from terminal ! root dir:_**
 - pip install -r requirements.txt    
 - python scripts/parse_book_summaries_md.py
 - python scripts/build_index.py 
 - uvicorn backend.app:app --reload  
 - OPEN INDEX.HTML IN BROWSER AND ENJOY
 - !!!!!!!!!!!!! SET THE OPENAI KEY IN TERMINAL  !!!!!!!!!!!!!!!!!!!!!!!!

**What this project does**

- Data-only answers: returns the best-matching book title and its short summary from your curated file.
- Retrieval augmented generation (RAG) pipeline using OpenAI embeddings and ChromaDB.
- A minimal LLM step: the model picks one title from top-k candidates and then calls a local tool to fetch the long summary.
- Optional UI details: toggle to show long summary, text-to-speech, speech-to-text, and an AI-generated cover button.


**How each task is solved**
Source file: backend/data/book_summaries.md 

**Title**: 
2–5 lines short summary.
Themes: comma, separated, list

- Processed into JSON by scripts/parse_book_summaries_md.py → backend/data/book_summaries.json.
- Vector store and embeddings
- Script scripts/build_index.py reads book_summaries.json and indexes documents into ChromaDB using OpenAI text-embedding-3-small.
- Metadata values are primitives only (themes stored as themes_csv string) to satisfy Chroma validation.

**Retrieval (RAG)**

- backend/rag.py queries ChromaDB with the user query and returns top-k candidates containing title, short_summary, and a score.
- The system returns only what exists in your dataset; no descriptive text is generated.

**Chat endpoint**
- backend/app.py exposes POST /chat. (also added /cover /health but are not main route)

**Steps:**
- Safety gate checks user input for profanity.
- Retrieve top candidates from Chroma.
- The LLM receives the user query and candidate titles and picks exactly one.
- The backend calls a local tool to fetch the long summary by title.

**Response format:**
{ "title": "...", "summary": "...", "long_summary": "..." }


**Local tool: get_summary_by_title**

- Implemented in backend/tools.py.
- Reads backend/data/book_summaries_long.json (a dict from exact title to long summary) and returns the long summary for the selected title.

**Frontend UI**
- Plain HTML/CSS/JS retro chat.
- Calls /chat and renders:
- bold book title
- CORS enabled in FastAPI for local development.

**Safety filter**

- backend/safety.py blocks inputs containing a small set of profanities, including common variants and light obfuscations.
- If blocked, /chat returns: { "title": "Input not allowed", "summary": "Please rephrase your request politely.", "long_summary": null }


**Optional: TTS and STT**
- TTS: window.speechSynthesis reads the short or long summary when a toggle is enabled.
- STT: webkitSpeechRecognition fills the input with recognized speech and submits the query. 

**Optional: AI cover generation**
- POST /cover calls OpenAI Images with a style prompt and returns a data:image/png;base64,... URL.

Frontend shows a “Generate cover” button after each answer.



1. [ ] **_DEMO questions:_**

- “I want a dystopian novel about surveillance and totalitarian control.” → (1984, Brave New World, Fahrenheit 451)
- “Which book tells the story of a small hero going on a grand adventure?” → (The Hobbit)
- “Give me a novel that critiques the American Dream.” → (The Great Gatsby)
- “I want a classic love story with social obstacles.” → (Pride and Prejudice, Anna Karenina, Jane Eyre)
- “Which novel asks deep questions about morality, guilt, and redemption?” → (Crime and Punishment, The Brothers Karamazov)
- “I want an epic novel about war and peace in Russia.” → (War and Peace)
- “Suggest me a novel about a father and son surviving after the apocalypse.” → (The Road)
- “Which book features a hero’s long journey home from war?” → (The Odyssey)
- “I want a magical realist novel about history and identity.” → (One Hundred Years of Solitude, Midnight’s Children)

**etc...**

Author: Ionel Mihai Alexandru 