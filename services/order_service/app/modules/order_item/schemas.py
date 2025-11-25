from typing import Optional
from pydantic import BaseModel


class OrderItemCreate(BaseModel):
    order_id: Optional[int] = None
    dish_id: int
    quantity: int
    total: float
