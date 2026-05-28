"""
Domain exception hierarchy.

Services raise these; the global exception handler in main.py translates
them to the appropriate HTTP response — keeping FastAPI concerns out of
the business-logic layer.
"""


class AppError(Exception):
    """Base class for all application domain errors."""

    status_code: int = 500
    default_message: str = "An unexpected error occurred"

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)


class NotFoundError(AppError):
    """Resource could not be found (→ 404)."""

    status_code = 404
    default_message = "Resource not found"


class DuplicateError(AppError):
    """Resource already exists / unique constraint violation (→ 400)."""

    status_code = 400
    default_message = "Resource already exists"


class AuthenticationError(AppError):
    """Invalid credentials or token (→ 401)."""

    status_code = 401
    default_message = "Authentication failed"


class AuthorizationError(AppError):
    """Authenticated but not permitted (→ 403)."""

    status_code = 403
    default_message = "Permission denied"


class BusinessLogicError(AppError):
    """Generic business rule violation (→ 400)."""

    status_code = 400
    default_message = "Business logic error"
