import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("madura_back")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Registra cada petición: método, ruta, estado y tiempo de respuesta (ms)."""

    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response: Response = await call_next(request)
        elapsed = (time.time() - start) * 1000
        logger.info(
            "%s %s - %s - %.2fms",
            request.method,
            request.url.path,
            response.status_code,
            elapsed,
        )
        return response
