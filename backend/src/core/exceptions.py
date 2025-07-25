# Custom exceptions
from fastapi import HTTPException, status


class EmbeddedChatException(Exception):
    """Base exception for EmbeddedChat application"""
    pass


class AuthenticationError(EmbeddedChatException):
    """Authentication related errors"""
    pass


class AuthorizationError(EmbeddedChatException):
    """Authorization related errors"""
    pass


class ValidationError(EmbeddedChatException):
    """Data validation errors"""
    pass


class NotFoundError(EmbeddedChatException):
    """Resource not found errors"""
    pass


class DatabaseError(EmbeddedChatException):
    """Database operation errors"""
    pass


class RateLimitError(EmbeddedChatException):
    """Rate limiting errors"""
    pass


# HTTP Exception helpers
def http_404_not_found(detail: str = "Resource not found"):
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail
    )


def http_401_unauthorized(detail: str = "Unauthorized"):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"}
    )


def http_403_forbidden(detail: str = "Forbidden"):
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail
    )


def http_422_validation_error(detail: str = "Validation error"):
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=detail
    )


def http_429_rate_limit(detail: str = "Rate limit exceeded"):
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=detail
    )
