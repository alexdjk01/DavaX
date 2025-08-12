import json
from datetime import datetime

def publish_to_stream(payload: dict):
    payload["streamed_at"] = datetime.utcnow().isoformat()
    with open("stream.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")
