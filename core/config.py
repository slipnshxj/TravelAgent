from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _load_environment_files(environment: str) -> None:
    load_dotenv(".env", override=False)
    load_dotenv(f".env.{environment}", override=True)


def _bool(value: str, default: bool) -> bool:
    if not value:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _int(value: str, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _list(value: str, default: list[str]) -> list[str]:
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_name: str
    environment: str
    version: str
    default_user_id: str
    cors_origins: list[str]
    api_auth_token: str
    rate_limit_enabled: bool
    rate_limit_requests: int
    rate_limit_window_seconds: int
    amap_js_key: str
    amap_security_js_code: str
    amap_rest_api_key: str
    amap_timeout_seconds: float
    amap_max_retries: int
    chat_timeout_seconds: float
    tool_timeout_seconds: float
    log_level: str
    log_dir: Path
    metrics_enabled: bool


def load_settings() -> Settings:
    environment = os.getenv("APP_ENV", "dev").lower()
    _load_environment_files(environment)

    return Settings(
        app_name=os.getenv("APP_NAME", "Agent Object API"),
        environment=environment,
        version=os.getenv("APP_VERSION", "1.0.0"),
        default_user_id=os.getenv("AGENT_USER_ID", "memory_test_user"),
        cors_origins=_list(
            os.getenv("CORS_ORIGINS"),
            ["http://127.0.0.1:8000", "http://localhost:8000"],
        ),
        api_auth_token=os.getenv("API_AUTH_TOKEN", ""),
        rate_limit_enabled=_bool(os.getenv("RATE_LIMIT_ENABLED"), True),
        rate_limit_requests=_int(os.getenv("RATE_LIMIT_REQUESTS"), 300),
        rate_limit_window_seconds=_int(
            os.getenv("RATE_LIMIT_WINDOW_SECONDS"),
            60,
        ),
        amap_js_key=os.getenv("AMAP_JS_KEY", ""),
        amap_security_js_code=os.getenv("AMAP_SECURITY_JS_CODE", ""),
        amap_rest_api_key=os.getenv("AMAP_REST_API_KEY", ""),
        amap_timeout_seconds=float(
            os.getenv("AMAP_TIMEOUT_SECONDS", "5"),
        ),
        amap_max_retries=_int(os.getenv("AMAP_MAX_RETRIES"), 2),
        chat_timeout_seconds=float(
            os.getenv("CHAT_TIMEOUT_SECONDS", "120"),
        ),
        tool_timeout_seconds=float(
            os.getenv("TOOL_TIMEOUT_SECONDS", "30"),
        ),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        log_dir=Path(os.getenv("LOG_DIR", "logs")),
        metrics_enabled=_bool(os.getenv("METRICS_ENABLED"), True),
    )


settings = load_settings()
