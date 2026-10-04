from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from core.context import request_id_var
from core.metrics import metrics


class ObservabilityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, logger) -> None:
        super().__init__(app)
        self.logger = logger

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request_token = request_id_var.set(request_id)
        started = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            duration = time.perf_counter() - started
            metrics.observe("http_request_duration_seconds", duration)
            metrics.increment(
                "http_requests_total",
                f'method="{request.method}",path="{request.url.path}",status="500"',
            )
            self.logger.exception(
                "request_failed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "client": request.client.host if request.client else "",
                    "duration_ms": round(duration * 1000, 2),
                },
            )
            request_id_var.reset(request_token)
            raise

        duration = time.perf_counter() - started
        labels = (
            f'method="{request.method}",path="{request.url.path}",'
            f'status="{response.status_code}"'
        )
        metrics.increment("http_requests_total", labels)
        metrics.observe("http_request_duration_seconds", duration)
        response.headers["X-Request-ID"] = request_id

        self.logger.info(
            "request_completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "client": request.client.host if request.client else "",
                "duration_ms": round(duration * 1000, 2),
            },
        )
        request_id_var.reset(request_token)
        return response
