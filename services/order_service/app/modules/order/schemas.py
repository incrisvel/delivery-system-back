from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.core.db.models.order import OrderStatus


class OrderRead(BaseModel):
    id: int
    description: str
    created_at: datetime
    updated_at: datetime
    status: OrderStatus
    establishment_id: int
    delivery_id: int


class OrderCreate(BaseModel):
    description: str
    status: OrderStatus
    establishment_id: int
    delivery_id: int


class OrderUpdate(BaseModel):
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: Optional[OrderStatus] = None
    establishment_id: Optional[int] = None
    delivery_id: Optional[int] = None
