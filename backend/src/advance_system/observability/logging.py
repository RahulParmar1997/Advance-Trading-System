from __future__ import annotations

import json
import logging
from typing import Any


_SENSITIVE_KEYS = frozenset(
    {
        "access_token",
        "refresh_token",
        "authorization",
        "password",
        "secret",
        "api_key",
        "client_secret",
    }
)


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): "[REDACTED]" if str(key).lower() in _SENSITIVE_KEYS else _sanitize(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_sanitize(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


class StructuredFormatter(logging.Formatter):
    """JSON formatter with deterministic fields and secret redaction."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        context = getattr(record, "context", None)
        if context:
            payload["context"] = _sanitize(context)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, separators=(",", ":"), sort_keys=True)


def configure_logging(level: int = logging.INFO) -> None:
    """Configure application-wide structured logging once for the process."""
    root = logging.getLogger()
    root.setLevel(level)
    if any(isinstance(handler, logging.StreamHandler) and getattr(handler, "_advance_structured", False) for handler in root.handlers):
        return
    handler = logging.StreamHandler()
    handler._advance_structured = True  # type: ignore[attr-defined]
    handler.setFormatter(StructuredFormatter())
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_event(logger: logging.Logger, message: str, **context: Any) -> None:
    """Emit a structured event without allowing secrets into log context."""
    logger.info(message, extra={"context": _sanitize(context)})
