from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from app.core.db.models.order import OrderStatus
from app.modules.order_item.schemas import OrderItemCreate


class OrderRead(BaseModel):
    id: int
    client: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    status: OrderStatus
    total: float
    establishment_id: int
    delivery_id: Optional[int] = None


class OrderWithItemsCreate(BaseModel):
    client: str
    description: Optional[str] = None
    total: float
    establishment_id: int
    delivery_id: Optional[int] = None
    items: List[OrderItemCreate]


class OrderCreate(BaseModel):
    client: str
    description: Optional[str] = None
    total: float
    establishment_id: int
    delivery_id: Optional[int] = None


class OrderUpdate(BaseModel):
    client: Optional[str] = None
    description: Optional[str] = None
    total: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: Optional[OrderStatus] = None
    establishment_id: Optional[int] = None
    delivery_id: Optional[int] = None
