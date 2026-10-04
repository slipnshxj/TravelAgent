from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        enabled: bool = True,
        requests: int = 300,
        window_seconds: int = 60,
    ) -> None:
        super().__init__(app)
        self.enabled = enabled
        self.requests = requests
        self.window_seconds = window_seconds
        self._buckets: dict[tuple[str, int], int] = {}

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        if not self.enabled or request.url.path == "/api/health":
            return await call_next(request)

        client = request.client.host if request.client else "unknown"
        window = int(time.time() // self.window_seconds)
        key = (client, window)
        count = self._buckets.get(key, 0) + 1
        self._buckets[key] = count

        for old_key in list(self._buckets):
            if old_key[1] < window:
                del self._buckets[old_key]

        if count > self.requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "请求过于频繁，请稍后再试"},
                headers={
                    "Retry-After": str(
                        self.window_seconds - int(time.time()) % self.window_seconds,
                    ),
                },
            )
        return await call_next(request)
