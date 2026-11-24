from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


class DuplicateResourceError(HTTPException):
    """Raised when a unique constraint violation occurs (DIO standard: HTTP 303 See Other)."""

    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_303_SEE_OTHER, detail=detail)


class ResourceNotFoundError(HTTPException):
    """Raised when a requested domain entity cannot be located."""

    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


async def global_integrity_error_handler(
    _request: Request,
    exc: IntegrityError,
) -> JSONResponse:
    """Fallback global handler for uncaught SQLAlchemy IntegrityError -> HTTP 303 See Other."""
    return JSONResponse(
        status_code=status.HTTP_303_SEE_OTHER,
        content={
            "detail": f"Erro de integridade de dados: registro duplicado ou referência inválida ({exc.orig})."
        },
    )
