from services.order_service.app.core.exceptions.base import ForbiddenError, NotFoundError, ValidationError


class EstablishmentNotFoundError(NotFoundError):
    def __init__(self, message="Estabelecimento não encontrado."):
        super().__init__(message)


class EstablishmentValidationError(ValidationError):
    def __init__(self, message="Estabelecimento possui dados inválidos."):
        super().__init__(message)


class EstablishmentForbiddenError(ForbiddenError):
    def __init__(self, message="Acesso negado ao estabelecimento."):
        super().__init__(message)
