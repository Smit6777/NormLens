"""Tests for the logging setup (Phase 1)."""
import json
import logging

from app.core.logging import JsonFormatter, configure_logging, get_logger


def test_json_formatter_produces_valid_json():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname=__file__, lineno=1,
        msg="hello %s", args=("world",), exc_info=None,
    )
    line = formatter.format(record)
    parsed = json.loads(line)
    assert parsed["message"] == "hello world"
    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "test"


def test_configure_logging_is_idempotent():
    configure_logging("DEBUG")
    configure_logging("DEBUG")
    root = logging.getLogger()
    # Check that there is exactly one JsonFormatter attached by configure_logging
    json_handlers = [h for h in root.handlers if getattr(h.formatter, "__class__", None).__name__ == "JsonFormatter"]
    assert len(json_handlers) == 1


def test_get_logger_returns_named_logger():
    logger = get_logger("app.something")
    assert logger.name == "app.something"
