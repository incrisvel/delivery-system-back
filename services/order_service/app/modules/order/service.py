from typing import List, Optional
from fastapi import Depends
from app.core.db.models.order import Order, OrderStatus
from app.core.db.models.order_item import OrderItem
from app.core.db.session import get_session
from app.core.utils.models import update_model_from_schema
from app.modules.order.exceptions import OrderNotFoundError
from app.modules.order.repository import OrderRepository
from app.modules.order.schemas import OrderCreate, OrderWithItemsCreate, OrderUpdate


class OrderService:
    def __init__(self, repo: OrderRepository) -> None:
        self.repo = repo

    def get_all_orders(
        self,
        establishment_id: Optional[int] = None,
        delivery_id: Optional[int] = None,
        status: Optional[OrderStatus] = None,
    ) -> List[Order]:
        orders = self.repo.get_all_orders(establishment_id, delivery_id, status)
        return list(orders)

    def get_order_by_id(self, order_id: int) -> Order:
        order = self.repo.get_order_by_id(order_id)
        if not order:
            raise OrderNotFoundError

        return order

    def create_order(self, order_create_with_items: OrderWithItemsCreate) -> Order:
        order_create = OrderCreate(**order_create_with_items.model_dump())

        order = Order(**order_create.model_dump())
        order = self.repo.create_order(order)

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
