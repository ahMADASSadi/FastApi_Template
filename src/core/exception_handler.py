"""
Secure exception handling: logs full details internally,
returns sanitized messages to clients (no stack traces or sensitive info).
"""

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
        app_settings = get_setting("app")
        is_debug = app_settings.DEBUG

        if is_debug:
            # Development: include field names and error types for debugging
            messages = []
            for error in errors:
                loc = ".".join(str(l) for l in error.get("loc", []))
                msg_type = error.get("type", "unknown")
                messages.append(f"{loc}: {msg_type}")
            return messages
        else:
            # Production: generic message, no details
            return ["Invalid request data. Please check your input and try again."]

    @staticmethod
    def handle_validation_error(request: Any, exc: Exception) -> JSONResponse:
        """Handle RequestValidationError securely."""
        error_id = str(uuid.uuid4())
        app_settings = get_setting("app")

        # Always log full details internally
        logger.warning(
            "Validation error",
            extra={
                "error_id": error_id,
                **SecurityAwareExceptionHandler._get_request_context(request),
                "errors": exc.errors() if hasattr(exc, "errors") else str(exc),
            },
        )

        # Return sanitized response
        sanitized_errors = SecurityAwareExceptionHandler._sanitize_validation_errors(
            exc.errors() if hasattr(exc, "errors") else []
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ApiResponse(
                success=False,
                message="failure",
                error=sanitized_errors if app_settings.DEBUG else "Invalid request",
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                error_id=error_id if not app_settings.DEBUG else None,
            ).model_dump(exclude_none=True),
        )

    @staticmethod
    def handle_auth_error(request: Any, exc: Exception, status_code: int = 401) -> JSONResponse:
        """Handle auth errors (401, etc.) securely without leaking details."""
        error_id = str(uuid.uuid4())
        app_settings = get_setting("app")

        # Log full exception details internally (for investigation)
        logger.warning(
            f"Auth error (status {status_code})",
            extra={
                "error_id": error_id,
                **SecurityAwareExceptionHandler._get_request_context(request),
                "detail": str(exc.detail) if hasattr(exc, "detail") else str(exc),
            },
        )

        # Always return generic message to client
        generic_message = (
            "Authentication failed. Invalid or expired credentials."
            if status_code == 401
            else "Authorization denied."
        )

        return JSONResponse(
            status_code=status_code,
            content=ApiResponse(
                success=False,
                message="failure",
                error=None,  # Never expose auth details to client
                status=status_code,
                error_id=error_id if not app_settings.DEBUG else None,
            ).model_dump(exclude_none=True),
        )

    @staticmethod
    def handle_internal_error(
        request: Any, exc: BaseException, status_code: int = 500
    ) -> JSONResponse:
        """Handle 500 errors securely: log stack trace, return generic message."""
        error_id = str(uuid.uuid4())
        app_settings = get_setting("app")

        # Log full exception details including stack trace for debugging
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

        # Return generic message with error_id for user support
        return JSONResponse(
            status_code=status_code,
            content=ApiResponse(
                success=False,
                message="failure",
                error=None,  # Never expose stack trace or internal details
                status=status_code,
                error_id=error_id,  # Always include error_id for production support
            ).model_dump(exclude_none=True),
        )
