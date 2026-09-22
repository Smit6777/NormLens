"""
Structured logging setup for the application.

Uses only the standard library `logging` module with a JSON-line
formatter, so logs are easy to ingest without pulling in a heavyweight
dependency. Call `configure_logging()` once at startup (in the FastAPI
lifespan, Phase 6) before any other module logs.

Deliberately has zero third-party dependencies so it can be unit-tested
in isolation.
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

_CONFIGURED = False


class JsonFormatter(logging.Formatter):
    """Formats each log record as a single-line JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        # Callers can attach structured context via `extra={"context": {...}}`.
        context = getattr(record, "context", None)
        if context is not None:
            payload["context"] = context
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO") -> None:
    """Configure the root logger. Idempotent -- safe to call more than once."""
    global _CONFIGURED

    root = logging.getLogger()
    root.setLevel(level.upper())

    if _CONFIGURED:
        return

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(JsonFormatter())
    root.handlers = [handler]
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger. Call configure_logging() at startup first."""
    return logging.getLogger(name)
