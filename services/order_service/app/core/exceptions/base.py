from fastapi import HTTPException


class AppException(HTTPException):
    """Exceção base para erros de aplicação."""

    def __init__(self, status_code: int, message: str):
        super().__init__(status_code=status_code, detail=message)
        self.message = message


class UnauthorizedError(AppException):
    def __init__(self, message="Não autorizado."):
        super().__init__(401, message)


class UnavailableServiceError(AppException):
    def __init__(self, message="Serviço temporariamente indisponível."):
        super().__init__(503, message)


class NotFoundError(AppException):
    def __init__(self, message="Recurso não encontrado."):
        super().__init__(404, message)


class BadRequestError(AppException):
    def __init__(self, message="Solicitação inválida."):
        super().__init__(400, message)


class ForbiddenError(AppException):
    def __init__(self, message="Acesso negado."):
        super().__init__(403, message)


class ConflictError(AppException):
    def __init__(self, message="Conflito ao processar a requisição."):
        super().__init__(409, message)


class ValidationError(AppException):
    def __init__(self, message="Dados inválidos."):
        super().__init__(422, message)


class ServerError(AppException):
    def __init__(self, message="Erro interno no servidor."):
        super().__init__(500, message)


class PermissionDeniedError(ForbiddenError):
    def __init__(self, message="Usuário não possui permissão para realizar esta ação."):
        super().__init__(message)
