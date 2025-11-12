from json import JSONDecodeError
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from .base import AppException


def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.message})


def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code, content={"message": exc.detail or "Erro HTTP."}
    )


def unprocessable_entity_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"message": "Dados inválidos."},
    )


def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail or "Erro interno do servidor."},
    )


def json_decode_error_handler(request: Request, exc: JSONDecodeError):
    return JSONResponse(status_code=400, content={"message": "Formato JSON inválido."})


def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500, content={"message": "Erro interno inesperado."}
    )
