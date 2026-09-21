"""Tests for the plain-Python exception hierarchy (Phase 1)."""
from app.core.exceptions import AppError, DataLoadError, StandardNotFoundError


def test_app_error_default_message():
    err = AppError()
    assert err.message == AppError.default_message
    assert err.details == {}


def test_app_error_custom_message_and_details():
    err = DataLoadError("custom message", details={"path": "/x.json"})
    assert str(err) == "custom message"
    assert err.details == {"path": "/x.json"}
    assert err.status_code == 500


def test_standard_not_found_status_code():
    err = StandardNotFoundError()
    assert err.status_code == 404


def test_exception_hierarchy():
    assert issubclass(DataLoadError, AppError)
    assert issubclass(StandardNotFoundError, AppError)
