from fastapi import FastAPI

from app.core.exceptions.handlers import (
    RequestValidationError,
    JSONDecodeError,
    AppException,
    StarletteHTTPException,
    app_exception_handler,
    json_decode_error_handler,
    unprocessable_entity_handler,
    starlette_http_exception_handler,
)


def register_base_exception_handlers(app: FastAPI):
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, unprocessable_entity_handler)
    app.add_exception_handler(JSONDecodeError, json_decode_error_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
