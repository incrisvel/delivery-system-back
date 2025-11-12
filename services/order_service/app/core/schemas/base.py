from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationRequest(BaseModel):
    skip: int = Field(0, ge=0, description="Número de itens a pular (offset)")
    limit: int = Field(
        100, ge=1, le=1000, description="Número máximo de itens por página"
    )
    sort_by: Optional[str] = Field(None, description="Campo de ordenação")
    order: Optional[str] = Field(
        "asc", pattern="^(asc|desc)$", description="Direção da ordenação"
    )


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    items: list[T]
    metadata: dict | None = None
