from __future__ import annotations

import hmac

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class ApiAuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, token: str) -> None:
        super().__init__(app)
        self.token = token

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        protected = request.url.path.startswith("/api")
        public_paths = {"/api/health", "/api/config"}
        if protected and request.url.path not in public_paths:
            provided = request.headers.get("X-API-Token", "")
            if not hmac.compare_digest(provided, self.token):
                return JSONResponse(status_code=401, content={"detail": "未授权"})
        return await call_next(request)
