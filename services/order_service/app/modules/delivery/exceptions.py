from app.core.exceptions.base import ForbiddenError, NotFoundError, ValidationError


class DeliveryNotFoundError(NotFoundError):
    def __init__(self, message="Entrega não encontrada."):
        super().__init__(message)


class DeliveryValidationError(ValidationError):
    def __init__(self, message="Entrega possui dados inválidos."):
        super().__init__(message)


class DeliveryForbiddenError(ForbiddenError):
    def __init__(self, message="Acesso negado a entrega."):
        super().__init__(message)
