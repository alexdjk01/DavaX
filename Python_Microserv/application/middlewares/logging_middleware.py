import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Message

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Citește corpul requestului
        body_bytes = await request.body()
        try:
            parsed_body = json.loads(body_bytes)
        except Exception:
            parsed_body = body_bytes.decode()

        print("\n ===REQUEST===")
        print(f"→ {request.method} {request.url}")
        if parsed_body:
            print(f"Payload: {parsed_body}")

        # interceptarea raspunsului
        response = await call_next(request)

        # cloneaza body ul raspunsului
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        # response body
        new_response = Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )

        try:
            parsed_response = json.loads(response_body)
        except Exception:
            parsed_response = response_body.decode()
        print("\n ===RESPONSE===")
        print(f"Status code: {response.status_code}")
        print(f"Result: {parsed_response}")
        return new_response
