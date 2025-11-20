from typing import Optional
from pydantic import BaseModel


class DishRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    establishment_id: int


class DishCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    establishment_id: int


class DishUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    establishment_id: Optional[int] = None
