from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppException(Exception):
    status_code = 400
    code = "BAD_REQUEST"

    def __init__(self, message: str, details=None):
        super().__init__(message)
        self.message = message
        self.details = details


class NotFoundError(AppException):
    status_code, code = 404, "NOT_FOUND"


class ConflictError(AppException):
    status_code, code = 409, "CONFLICT"


class BusinessRuleError(AppException):
    status_code, code = 422, "BUSINESS_RULE_VIOLATION"


class ValidationAppError(AppException):
    status_code, code = 422, "VALIDATION_ERROR"


def _error(status: int, code: str, message: str, details=None) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"success": False, "error": {"code": code, "message": message, "details": details}},
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exc(_: Request, exc: AppException):
        return _error(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def validation_exc(_: Request, exc: RequestValidationError):
        details = [
            {"field": ".".join(str(p) for p in e["loc"] if p not in ("body", "query")),
             "message": e["msg"]}
            for e in exc.errors()
        ]
        return _error(422, "VALIDATION_ERROR", "Request validation failed", details)

    @app.exception_handler(StarletteHTTPException)
    async def http_exc(_: Request, exc: StarletteHTTPException):
        return _error(exc.status_code, "HTTP_ERROR", str(exc.detail))

    @app.exception_handler(Exception)
    async def unhandled(_: Request, exc: Exception):
        return _error(500, "INTERNAL_ERROR", "Unexpected server error")
