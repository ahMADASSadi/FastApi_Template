import logging
import traceback
import uuid
from typing import Any

from fastapi.responses import JSONResponse
from starlette import status

from config.settings import get_setting
from core.response import ApiResponse

logger = logging.getLogger(__name__)


class SecurityAwareExceptionHandler:
    """Handles exceptions securely: logs details, returns generic client messages."""

    settings = get_setting("app")

    @staticmethod
    def _get_request_context(request: Any) -> dict[str, Any]:
        """Extract safe request context for logging."""
        return {
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else "unknown",
        }

    @staticmethod
    def _sanitize_validation_errors(errors: list[dict]) -> list[str]:
        """
        Convert detailed validation errors to generic messages in production.
        In development, return field names only (no values).
        """
        is_debug = SecurityAwareExceptionHandler.settings.DEBUG

        if is_debug:
            messages = []
            for error in errors:
                loc = ".".join(str(_loc) for _loc in error.get("loc", []))
                msg_type = error.get("type", "unknown")
                messages.append(f"{loc}: {msg_type}")
            return messages
        else:
            return ["Invalid request data. Please check your input and try again."]

    @staticmethod
    def handle_validation_error(request: Any, exc: Exception) -> JSONResponse:
        """Handle RequestValidationError securely."""
        error_id = str(uuid.uuid4())
        logger.warning(
            "Validation error",
            extra={
                "error_id": error_id,
                **SecurityAwareExceptionHandler._get_request_context(request),
                "errors": exc.errors() if hasattr(exc, "errors") else str(exc),
            },
        )

        sanitized_errors = SecurityAwareExceptionHandler._sanitize_validation_errors(
            exc.errors() if hasattr(exc, "errors") else []
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ApiResponse(
                success=False,
                message="failure",
                error=sanitized_errors
                if SecurityAwareExceptionHandler.settings.DEBUG
                else "Invalid request",
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                error_id=error_id if not SecurityAwareExceptionHandler.settings.DEBUG else None,
            ).model_dump(exclude_none=True),
        )

    @staticmethod
    def handle_auth_error(request: Any, exc: Exception, status_code: int = 401) -> JSONResponse:
        """Handle auth errors (401, etc.) securely without leaking details."""
        error_id = str(uuid.uuid4())

        logger.warning(
            f"Auth error (status {status_code})",
            extra={
                "error_id": error_id,
                **SecurityAwareExceptionHandler._get_request_context(request),
                "detail": str(exc.detail) if hasattr(exc, "detail") else str(exc),
            },
        )

        return JSONResponse(
            status_code=status_code,
            content=ApiResponse(
                success=False,
                message="failure",
                error=None,
                status=status_code,
                error_id=error_id if not SecurityAwareExceptionHandler.settings.DEBUG else None,
            ).model_dump(exclude_none=True),
        )

    @staticmethod
    def handle_internal_error(
        request: Any, exc: BaseException, status_code: int = 500
    ) -> JSONResponse:
        """Handle 500 errors securely: log stack trace, return generic message."""
        error_id = str(uuid.uuid4())
        logger.error(
            f"Internal server error (status {status_code})",
            extra={
                "error_id": error_id,
                **SecurityAwareExceptionHandler._get_request_context(request),
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "traceback": traceback.format_exc(),
            },
        )

        return JSONResponse(
            status_code=status_code,
            content=ApiResponse(
                success=False,
                message="failure",
                error="Internal server error",
                status=status_code,
                error_id=error_id,
            ).model_dump(exclude_none=True),
        )

    @staticmethod
    def handle_not_found_error(request: Any, exc: Exception) -> JSONResponse:
        """Handle 404 errors securely: log details, return generic message."""
        error_id = str(uuid.uuid4())
        logger.warning(
            "Not found error",
            extra={
                "error_id": error_id,
                **SecurityAwareExceptionHandler._get_request_context(request),
                "detail": str(exc.detail) if hasattr(exc, "detail") else str(exc),
            },
        )

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ApiResponse(
                success=False,
                message="failure",
                error="The requested resource was not found.",
                status=status.HTTP_404_NOT_FOUND,
                error_id=error_id if not SecurityAwareExceptionHandler.settings.DEBUG else None,
            ).model_dump(exclude_none=True),
        )
