from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

from core.context import request_id_var
from core.config import Settings


class JsonFormatter(logging.Formatter):
    SENSITIVE_FIELDS = {
        "apikey",
        "api_key",
        "token",
        "password",
        "secret",
        "authorization",
    }

    @classmethod
    def sanitize(cls, key: str, value: object) -> object:
        if key.lower() in cls.SENSITIVE_FIELDS:
            return "***"
        return value

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "requestId": request_id_var.get() or None,
        }
        reserved = {
            "message", "asctime", "levelname", "name", "module", "filename",
            "pathname", "lineno", "funcName", "created", "msecs",
            "relativeCreated", "exc_info", "exc_text", "stack_info", "args",
            "msg", "taskName",
        }
        for key, value in record.__dict__.items():
            if key not in reserved and not key.startswith("_"):
                payload[key] = self.sanitize(key, value)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(settings: Settings) -> logging.Logger:
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    formatter = JsonFormatter()

    root = logging.getLogger()
    root.setLevel(settings.log_level)
    root.handlers.clear()

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    app_file = RotatingFileHandler(
        settings.log_dir / "app.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    app_file.setFormatter(formatter)
    root.addHandler(app_file)

    return logging.getLogger(settings.app_name)
