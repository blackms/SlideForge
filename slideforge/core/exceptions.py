"""
Custom exceptions for the SlideForge application.
"""
from fastapi import HTTPException, status


class SlideForgeException(Exception):
    """Base exception for SlideForge application."""
    pass


class DatabaseError(SlideForgeException):
    """Exception for database-related errors."""
    pass


class AuthenticationError(SlideForgeException):
    """Exception for authentication-related errors."""
    pass


class PermissionDeniedError(SlideForgeException):
    """Exception for permission-related errors."""
    pass


class ResourceNotFoundError(SlideForgeException):
    """Exception for resource not found errors."""
    pass


class ValidationError(SlideForgeException):
    """Exception for validation errors."""
    pass


class ProcessingError(SlideForgeException):
    """Exception for processing errors."""
    pass


# HTTP Exceptions
def http_error_handler(status_code: int, detail: str):
    """Create an HTTPException with the given status code and detail."""
    return HTTPException(status_code=status_code, detail=detail)


def authentication_exception(detail: str = "Could not validate credentials"):
    """Create an HTTPException for authentication errors."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def permission_denied_exception(detail: str = "Permission denied"):
    """Create an HTTPException for permission denied errors."""
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail,
    )


def not_found_exception(detail: str = "Resource not found"):
    """Create an HTTPException for not found errors."""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail,
    )


def validation_exception(detail: str = "Validation error"):
    """Create an HTTPException for validation errors."""
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=detail,
    )


def processing_exception(detail: str = "Processing error"):
    """Create an HTTPException for processing errors."""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=detail,
    )