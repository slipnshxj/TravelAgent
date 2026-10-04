from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

import api
from middleware.authentication import ApiAuthenticationMiddleware
from middleware.rate_limit import RateLimitMiddleware
from middleware.security import SecurityHeadersMiddleware


def test_request_id_security_headers_and_metrics() -> None:
    client = TestClient(api.app)
    response = client.get("/api/health", headers={"X-Request-ID": "engineering-request"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "engineering-request"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "SAMEORIGIN"

    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200
    assert 'path="/api/health"' in metrics_response.text
    assert "http_request_duration_seconds" in metrics_response.text


def test_rate_limit_returns_429() -> None:
    app = FastAPI()
    app.add_middleware(
        RateLimitMiddleware,
        enabled=True,
        requests=1,
        window_seconds=60,
    )

    @app.get("/limited")
    def limited() -> dict:
        return {"status": "ok"}

    client = TestClient(app)
    assert client.get("/limited").status_code == 200
    assert client.get("/limited").status_code == 429


def test_api_authentication_protected_route() -> None:
    app = FastAPI()
    app.add_middleware(ApiAuthenticationMiddleware, token="secret-token")
    app.add_middleware(SecurityHeadersMiddleware)

    @app.get("/api/private")
    def private() -> dict:
        return {"status": "ok"}

    client = TestClient(app)
    unauthorized = client.get("/api/private")
    assert unauthorized.status_code == 401
    assert unauthorized.headers["X-Content-Type-Options"] == "nosniff"
    authorized = client.get("/api/private", headers={"X-API-Token": "secret-token"})
    assert authorized.status_code == 200


def test_audit_log_is_written(tmp_path: Path) -> None:
    from middleware.audit import AuditMiddleware

    app = FastAPI()
    app.add_middleware(AuditMiddleware, log_dir=tmp_path)

    @app.post("/api/operation")
    def operation() -> dict:
        return {"status": "ok"}

    TestClient(app).post("/api/operation")
    log_file = tmp_path / "audit.log"
    assert log_file.exists()
    assert "api_operation" in log_file.read_text(encoding="utf-8")
