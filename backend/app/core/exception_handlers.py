from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import AppBaseException


def _error_response(
    status_code: int, message: str, error_code: str, details: dict | None = None
) -> JSONResponse:
    body: dict = {
        "success": False,
        "message": message,
        "error_code": error_code,
    }
    if details:
        body["details"] = details
    return JSONResponse(status_code=status_code, content=body)


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(AppBaseException)
    async def app_exception_handler(
        request: Request, exc: AppBaseException
    ) -> JSONResponse:
        return _error_response(
            status_code=exc.status_code,
            message=exc.message,
            error_code=exc.error_code,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = [
            {"field": " -> ".join(str(loc) for loc in e["loc"]), "msg": e["msg"]}
            for e in exc.errors()
        ]
        return _error_response(
            status_code=422,
            message="Request validation failed.",
            error_code="VALIDATION_ERROR",
            details={"errors": errors},
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        return _error_response(
            status_code=500,
            message="A database error occurred. Please try again later.",
            error_code="DATABASE_ERROR",
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        return _error_response(
            status_code=500,
            message="An unexpected error occurred.",
            error_code="INTERNAL_SERVER_ERROR",
        )
