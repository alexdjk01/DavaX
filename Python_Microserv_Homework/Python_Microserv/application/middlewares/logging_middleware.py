import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Message

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # ignores /export path for example, taken into account only mathematical opperation into Python consle.
        if request.method != "POST":
            return await call_next(request)
        # read request body once and transmits it further
        body_bytes = await request.body()
        try:
            parsed_body = json.loads(body_bytes)
        except Exception:
            parsed_body = body_bytes.decode(errors="ignore")
        async def receive() -> Message:
            return {"type": "http.request", "body": body_bytes, "more_body": False}
        request._receive = receive
        print("\n===REQUEST===")
        print(f"{request.method} {request.url.path} :: {parsed_body}")
        response = await call_next(request)
        print("===RESPONSE===")
        print(f"{request.method} {request.url.path} -> {response.status_code}")
        return response
