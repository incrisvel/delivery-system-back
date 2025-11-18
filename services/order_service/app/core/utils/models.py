from typing import Any, Mapping, Optional
from pydantic import BaseModel


def update_model_from_schema(
    entity: Any,
    schema: BaseModel | Mapping[str, Any],
    exclude: Optional[set[str]] = None,
    skip_unchanged: Optional[bool] = False,
) -> None:
    """Atualiza um model SQLAlchemy a partir de um schema Pydantic ou dict.

    Args:
        entity (Any): SQLAlchemy model a ser atualizado.
        schema (BaseModel | Mapping[str, Any]): schema com atualizações.
        exclude (set[str] | None, optional): campos a serem ignorados.
        skip_unchanged (bool, optional): ignora campos inalterados.
    """
    data = (
        schema.model_dump(exclude_unset=True)
        if isinstance(schema, BaseModel)
        else dict(schema)
    )

    exclude = exclude or set()

    for field, value in data.items():
        if field in exclude or value is None:
            continue
        if skip_unchanged and getattr(entity, field, None) == value:
            continue
        setattr(entity, field, value)
