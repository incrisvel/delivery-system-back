from typing import List, Optional
from fastapi import Depends
from app.core.db.models.order import Order
from app.core.db.session import get_session
from app.core.utils.models import update_model_from_schema
from app.modules.order.exceptions import OrderNotFoundError
from app.modules.order.repository import OrderRepository
from app.modules.order.schemas import OrderCreate, OrderUpdate


class OrderService:
    def __init__(self, repo: OrderRepository) -> None:
        self.repo = repo

    def get_all_orders(
        self,
    ) -> List[Order]:
        orders = self.repo.get_all_orders()
        return list(orders)

    def get_order_by_id(self, order_id: int) -> Order:
        order = self.repo.get_order_by_id(order_id)
        if not order:
            raise OrderNotFoundError

        return order

    def create_order(self, order_create: OrderCreate) -> Order:
        order = Order(**order_create.model_dump())
        order = self.repo.create_order(order)
        self.repo.session.commit()
        return order

    def update_order(self, order_id: int, order_update: OrderUpdate) -> Order:
        order = self.get_order_by_id(order_id)

        update_model_from_schema(order, order_update)
        order = self.repo.update_order(order)

        self.repo.session.commit()

        return order

    def delete_order(self, order_id: int) -> None:
        order = self.get_order_by_id(order_id)
        self.repo.delete_order(order)
        return


def get_order_service(session=Depends(get_session)) -> OrderService:
    repo = OrderRepository(session)
    return OrderService(repo)
