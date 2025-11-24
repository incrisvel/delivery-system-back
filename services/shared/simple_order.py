from typing import Optional
from random import randint, choice
from enum import Enum
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel

class OrderStatus(str, Enum):
    CONFIRMED = "confirmed"
    CREATED = "created"
    UPDATED = "updated"
    ASSIGNED = "assigned"
    ENROUTE = "enroute"
    DELIVERED = "delivered"

class SimpleOrder(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    estimated_arrival_at: Optional[datetime] = None
    delivery_id: Optional[int] = None
    courier: Optional[str] = None
    status: OrderStatus

    def generate_delivery_id(self):
        if self.delivery_id is None:
            self.delivery_id = randint(0, 99999)

    def assign_random_courier(self):
        if self.courier is not None:
            print(f"O pedido {self.delivery_id} já está atribuído a {self.courier}.")
        else:
            self.courier = choice(["Ademir", "Garibaldo", "Aristóteles", "Enzo", "Valentina", "Dolores", "Gertrudes"])

    def change_status(self, new_status: OrderStatus):
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)

    def calculate_estimated_arrival(self):
        estimated_minutes = randint(1, 5)
        self.estimated_arrival_at = datetime.now(timezone.utc) + timedelta(minutes=estimated_minutes)
