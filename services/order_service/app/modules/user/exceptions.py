from app.core.exceptions.base import ForbiddenError, NotFoundError, ValidationError


class UserNotFoundError(NotFoundError):
    def __init__(self, message="Usuario não encontrado."):
        super().__init__(message)


class UserValidationError(ValidationError):
    def __init__(self, message="Usuario possui dados inválidos."):
        super().__init__(message)


class UserForbiddenError(ForbiddenError):
    def __init__(self, message="Acesso negado ao usuario."):
        super().__init__(message)
