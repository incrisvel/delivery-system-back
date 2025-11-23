from typing import Optional
from random import randint, choice
from enum import Enum
from datetime import datetime, timedelta
from pydantic import BaseModel

from services.shared.simple_order import SimpleOrder

class OrderStatus(str, Enum):
    CONFIRMADO = "confirmed"
    CRIADO = "created"
    ATUALIZADO = "updated"
    ATRIBUÍDO = "assigned"
    EM_ENTREGA = "enroute"
    ENTREGUE = "delivered"

class Notification(BaseModel):
    order: int
    notification_time: datetime
    status: OrderStatus

    def __init__(self, order: SimpleOrder):
        super().__init__(
            order=order.order,
            status=order.status,
            notification_time=datetime.now()
        )

    def to_json(self):
        return self.model_dump_json()
