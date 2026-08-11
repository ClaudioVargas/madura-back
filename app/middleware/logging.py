import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response: Response = await call_next(request)
        elapsed = (time.time() - start) * 1000
        # Simple console log; can be enhanced to structured logging
        print(f"{request.method} {request.url.path} - {response.status_code} - {elapsed:.2f}ms")
        return response
