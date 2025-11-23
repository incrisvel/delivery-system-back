from services.order_service.app.core.exceptions.base import ForbiddenError, NotFoundError, ValidationError


class OrderNotFoundError(NotFoundError):
    def __init__(self, message="Pedido não encontrado."):
        super().__init__(message)


class OrderValidationError(ValidationError):
    def __init__(self, message="Pedido possui dados inválidos."):
        super().__init__(message)


class OrderForbiddenError(ForbiddenError):
    def __init__(self, message="Acesso negado ao pedido."):
        super().__init__(message)
