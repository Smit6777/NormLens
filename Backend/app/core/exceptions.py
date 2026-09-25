"""
Centralized application exceptions.

These are plain Python exceptions with no third-party dependencies, so
this module is importable and unit-testable without FastAPI/Pydantic
installed. FastAPI exception-handler wiring (which does need FastAPI) is
provided by `register_exception_handlers`, which imports FastAPI lazily
inside the function body. It is called exactly once, from `app.main`
during application startup (Phase 6) -- never at module import time.
"""
from __future__ import annotations


class AppError(Exception):
    """Base class for all application-raised errors."""

    default_message = "An unexpected error occurred."
    status_code = 500

    def __init__(self, message: str | None = None, *, details: dict | None = None):
        self.message = message or self.default_message
        self.details = details or {}
        super().__init__(self.message)


class DataLoadError(AppError):
    """Raised when a knowledge-layer JSON file cannot be found or read, or is not valid JSON."""

    default_message = "Failed to load knowledge base data."
    status_code = 500


class DataValidationError(AppError):
    """Raised when a knowledge-layer JSON file parses but does not match the expected shape."""

    default_message = "Knowledge base data failed validation."
    status_code = 500


class UnsupportedFileTypeError(AppError):
    """Raised when an uploaded file's type/extension is not supported."""

    default_message = "Unsupported file type."
    status_code = 415


class FileTooLargeError(AppError):
    """Raised when an uploaded file exceeds the configured size limit."""

    default_message = "Uploaded file is too large."
    status_code = 413


class DocumentExtractionError(AppError):
    """Raised when text cannot be extracted from an input document."""

    default_message = "Failed to extract text from the document."
    status_code = 422


class StandardNotFoundError(AppError):
    """Raised when a specific IS number is requested but is not present in the local knowledge base.

    Per project Rule 2 ("NOT FOUND != DOES NOT EXIST"), callers must
    translate this into a NOT_VERIFIED result for the client -- never into
    a claim that the standard does not exist.
    """

    default_message = "Standard not found in local knowledge base."
    status_code = 404


class ModelNotReadyError(AppError):
    """Raised when an ML component (embedding model, vector index) is used before it has loaded."""

    default_message = "The ML component is not ready yet."
    status_code = 503


def register_exception_handlers(app) -> None:  # pragma: no cover - needs FastAPI installed
    """Attach centralized exception handlers to a FastAPI app instance.

    FastAPI is imported lazily inside this function so that this module
    has zero import-time dependency on FastAPI, keeping it testable in
    isolation. Call this once from `app.main` during startup (Phase 6).
    """
    from fastapi import Request, status
    from fastapi.responses import JSONResponse

    from app.core.logging import get_logger

    logger = get_logger(__name__)

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        logger.error(
            "Handled application error",
            extra={"context": {
                "path": str(request.url),
                "error_type": type(exc).__name__,
                "details": exc.details,
            }},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": type(exc).__name__, "message": exc.message, "details": exc.details},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        # Never leak stack traces to clients; log full detail internally only.
        logger.exception("Unhandled exception", extra={"context": {"path": str(request.url)}})
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "InternalServerError", "message": str(exc)},
        )
