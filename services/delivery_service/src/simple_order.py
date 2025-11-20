from typing import Optional
from random import randint, choice
from enum import Enum
from datetime import datetime, timedelta
from pydantic import BaseModel

class OrderStatus(str, Enum):
    CONFIRMADO = "confirmed"
    CRIADO = "created"
    ATUALIZADO = "updated"
    ATRIBUÍDO = "assigned"
    EM_ENTREGA = "enroute"
    ENTREGUE = "delivered"

class SimpleOrder(BaseModel):
    order: int
    created_at: datetime
    updated_at: datetime
    estimated_arrival_at: datetime
    delivery: Optional[int] = None
    courier: Optional[str] = None
    status: OrderStatus

    def generate_delivery_id(self):
        if self.delivery is None:
            self.delivery = randint(0, 99999)

    def assign_random_courier(self):
        if self.courier is not None:
            print(f"O pedido {self.delivery} já está atribuído a {self.courier}.")
        else:
            self.courier = choice(["Ademir", "Garibaldo", "Aristóteles", "Enzo", "Valentina", "Dolores", "Gertrudes"])

    def change_status(self, new_status: OrderStatus):
        self.status = new_status
        self.updated_at = datetime.now()

    def calculate_estimated_arrival(self):
        estimated_minutes = randint(5, 90)
        self.estimated_arrival_at = datetime.now() + timedelta(minutes=estimated_minutes)

    def to_json(self):
        return self.model_dump_json()
