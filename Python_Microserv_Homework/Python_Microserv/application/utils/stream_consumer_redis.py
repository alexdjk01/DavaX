"""
Example using Redis Stream consumer. (Nu am ales KAFKA pentru ca intampinam multiple erori)

Usage:
  export REDIS_URL=redis://localhost:6379/0
  export REDIS_STREAM_KEY=ops_stream
  python -m application.utils.stream_consumer_redis
"""
import os, json, time
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
STREAM_KEY = os.getenv("REDIS_STREAM_KEY", "ops_stream")
GROUP = os.getenv("REDIS_GROUP", "ops_group")
CONSUMER = os.getenv("REDIS_CONSUMER", "ops_consumer")

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

try:
    r.xgroup_create(STREAM_KEY, GROUP, id="$", mkstream=True)
except redis.ResponseError as e:
    if "BUSYGROUP" not in str(e):
        raise

print(f"Listening on stream={STREAM_KEY}, group={GROUP}, consumer={CONSUMER}")
while True:
    msgs = r.xreadgroup(GROUP, CONSUMER, {STREAM_KEY: ">"}, count=10, block=5000)
    for stream, items in msgs:
        for msg_id, fields in items:
            try:
                print("MSG", msg_id, fields)
                r.xack(STREAM_KEY, GROUP, msg_id)
            except Exception as e:
                print("ERR", e)
    time.sleep(0.2)
