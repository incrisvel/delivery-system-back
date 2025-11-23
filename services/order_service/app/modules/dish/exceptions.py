from services.order_service.app.core.exceptions.base import NotFoundError

class DishNotFoundError(NotFoundError):
    def __init__(self, message="Prato não encontrado."):
        super().__init__(message)
