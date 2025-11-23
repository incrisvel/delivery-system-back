from datetime import datetime
from pydantic import BaseModel

from services.shared.simple_order import OrderStatus, SimpleOrder


class Notification(BaseModel):
    order_id: int
    timestamp: datetime
    status: OrderStatus
    order: SimpleOrder

    def from_order_schema(self, order: SimpleOrder):
        super().__init__(
            order_id=order.id,
            status=order.status,
            timestamp=datetime.now(),
            order=order,
        )
