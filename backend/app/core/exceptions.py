"""Application exception hierarchy.

Every exception carries a stable machine-readable ``code`` alongside its
human-readable detail, so clients can branch on the code while the prose stays
free to change.

Detail strings are written for the *client*. Upstream exception text, service
names and connection strings belong in logs only - ``DatabaseConnectionError``
previously rendered ``f"Failed to connect to {service}. Reason: {message}"``
straight into the HTTP response, which disclosed internal topology to anyone
who could trigger an outage.
"""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status


class BaseAppException(HTTPException):
    code: str = "error"

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: dict[str, str] | None = None,
        code: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.code = code or self.__class__.code
        self.extra = extra or {}


class AuthenticationError(BaseAppException):
    code = "authentication_failed"

    def __init__(self, detail: str = "Invalid authentication credentials.") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class PermissionDeniedError(BaseAppException):
    code = "permission_denied"

    def __init__(self, detail: str = "You do not have permission to access this resource.") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundError(BaseAppException):
    code = "not_found"

    def __init__(self, resource: str, resource_id: Any = None) -> None:
        # The identifier is intentionally omitted from the message. Echoing it
        # back turns a 404 into a confirmation oracle for probed IDs.
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The requested {resource.lower()} was not found.",
            extra={"resource": resource, "resource_id": str(resource_id) if resource_id else None},
        )


class ConflictError(BaseAppException):
    code = "conflict"

    def __init__(self, detail: str = "The request conflicts with the current state of the resource.") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class ValidationFailedError(BaseAppException):
    code = "validation_failed"

    def __init__(self, detail: str = "The request payload failed validation.") -> None:
        # Numeric literals rather than starlette.status constants: the names for
        # 413 and 422 were renamed, so the constants warn on new versions and
        # are missing on old ones.
        super().__init__(status_code=422, detail=detail)


class PayloadTooLargeError(BaseAppException):
    code = "payload_too_large"

    def __init__(self, limit_bytes: int) -> None:
        super().__init__(
            status_code=413,
            detail=f"Request body exceeds the maximum permitted size of {limit_bytes // (1024 * 1024)} MB.",
        )


class UnsupportedMediaTypeError(BaseAppException):
    code = "unsupported_media_type"

    def __init__(self, detail: str = "The uploaded file type is not supported.") -> None:
        super().__init__(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=detail)


class RateLimitExceededError(BaseAppException):
    code = "rate_limit_exceeded"

    def __init__(self, retry_after_seconds: int, detail: str | None = None) -> None:
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail or "Too many requests. Please slow down and try again shortly.",
            headers={"Retry-After": str(max(1, retry_after_seconds))},
        )
        self.retry_after_seconds = retry_after_seconds


class QuotaExceededError(BaseAppException):
    code = "quota_exceeded"

    def __init__(self, detail: str = "You have reached your usage allowance for today.") -> None:
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)


class DatabaseConnectionError(BaseAppException):
    code = "service_unavailable"

    def __init__(self, service_name: str, message: str = "") -> None:
        # service_name and message are captured for logging and never rendered
        # into the client-facing detail.
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="A required service is temporarily unavailable. Please try again shortly.",
            extra={"service": service_name, "reason": message},
        )


class UpstreamServiceError(BaseAppException):
    code = "upstream_error"

    def __init__(self, service_name: str, message: str = "") -> None:
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="An upstream service returned an unexpected response. Please try again.",
            extra={"service": service_name, "reason": message},
        )


class EvaluationExecutionError(BaseAppException):
    code = "evaluation_failed"

    def __init__(self, detail: str = "") -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The evaluation could not be completed. Please try again.",
            extra={"reason": detail},
        )
