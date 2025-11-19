from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db.models.order import Order


class OrderRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all_orders(self) -> Sequence[Order]:
        stmt = select(Order)
        orders = self.session.execute(stmt).scalars().all()
        return orders

    def get_order_by_id(self, order_id: int) -> Order | None:
        stmt = select(Order).where(Order.id == order_id)
        order = self.session.execute(stmt).scalar_one_or_none()
        return order

    def create_order(self, order: Order) -> Order:
        self.session.add(order)
        self.session.flush()
        return order

    def update_order(self, order: Order) -> Order:
        self.session.merge(order)
        self.session.flush()
        return order

    def delete_order(self, order: Order) -> None:
        self.session.delete(order)
        self.session.flush()
        return
