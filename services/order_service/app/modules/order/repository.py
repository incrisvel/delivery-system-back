from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db.models.order import Order, OrderStatus


class OrderRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all_orders(
        self,
        establishment_id: Optional[int] = None,
        delivery_id: Optional[int] = None,
        status: Optional[OrderStatus] = None,
    ) -> Sequence[Order]:
        stmt = select(Order)

        if establishment_id is not None:
            stmt = stmt.where(Order.establishment_id == establishment_id)

        if delivery_id is not None:
            stmt = stmt.where(Order.delivery_id == delivery_id)

        if status is not None:
            stmt = stmt.where(Order.status == status)

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
