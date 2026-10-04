from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from core.context import request_id_var
from core.logging import JsonFormatter


class AuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, log_dir: Path) -> None:
        super().__init__(app)
        log_dir.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(
            log_dir / "audit.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        handler.setFormatter(JsonFormatter())
        self.logger = logging.getLogger("agent.audit")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        self.logger.addHandler(handler)

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        response = await call_next(request)
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return response

        self.logger.info(
            "api_operation",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "client": request.client.host if request.client else "",
                "userAgent": request.headers.get("User-Agent", ""),
                "requestId": request_id_var.get(),
            },
        )
        return response
