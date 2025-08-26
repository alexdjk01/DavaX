import json
import os
from datetime import datetime


# Supported backends:
#   - FILE (default): append JSON lines to "stream.jsonl"
#   - REDIS: XADD to Redis Stream (requires REDIS_URL), stream key defaults to "ops_stream"

# Usage:
#   export STREAM_BACKEND=FILE
#   export STREAM_BACKEND=REDIS
#   export REDIS_URL=redis://localhost:6379/0
#   export REDIS_STREAM_KEY=ops_stream
# publish_to_stream(payload) keeps the same signature.

_STREAM_BACKEND = os.getenv("STREAM_BACKEND", "FILE").upper()
_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_REDIS_STREAM_KEY = os.getenv("REDIS_STREAM_KEY", "ops_stream")

_redis_client = None
if _STREAM_BACKEND == "REDIS":
    try:
        import redis
        _redis_client = redis.Redis.from_url(_REDIS_URL, decode_responses=True)
        # quick debug ping; if fails, fall back to file
        _redis_client.ping()
    except Exception as _e:
        _STREAM_BACKEND = "FILE"
        _redis_client = None

def _publish_file(payload: dict):
    payload["streamed_at"] = datetime.utcnow().isoformat()
    with open("stream.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")

def _publish_redis(payload: dict):
    assert _redis_client is not None
    payload["streamed_at"] = datetime.utcnow().isoformat()
    # XADD requires flat string fields
    fields = {k: (json.dumps(v) if not isinstance(v, (str, int, float)) else v) for k, v in payload.items()}
    _redis_client.xadd(_REDIS_STREAM_KEY, fields)

def publish_to_stream(payload: dict):
    if _STREAM_BACKEND == "REDIS" and _redis_client is not None:
        try:
            _publish_redis(payload)
            return
        except Exception:
            pass
    _publish_file(payload)
