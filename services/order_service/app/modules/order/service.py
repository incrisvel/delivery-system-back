from typing import List, Optional
from fastapi import Depends
from services.order_service.app.core.db.models.order import Order, OrderStatus
from services.order_service.app.core.db.session import get_session
from services.order_service.app.core.utils.models import update_model_from_schema
from services.order_service.app.dependencies.rabbitmq import get_rabbitmq_client
from services.order_service.app.modules.order.exceptions import OrderNotFoundError
from services.order_service.app.modules.order.repository import OrderRepository
from services.order_service.app.modules.order.schemas import (
    OrderCreate,
    OrderWithItemsCreate,
    OrderUpdate,
)
from services.shared.simple_order import SimpleOrder


class OrderService:
    def __init__(self, repo: OrderRepository, rabbitmq) -> None:
        self.repo = repo
        self.rabbitmq = rabbitmq

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

    def create_order(self, order_create_with_items: OrderWithItemsCreate, delivery_id: int) -> Order:
        order_create = OrderCreate(**order_create_with_items.model_dump())

        order = Order(**order_create.model_dump())
        order.delivery_id = delivery_id
        order = self.repo.create_order(order)

        self.rabbitmq.publish_order_status_changed(SimpleOrder.model_validate(order, from_attributes=True))
        return order

    def update_order(self, order_id: int, order_update: OrderUpdate) -> Order:
        order = self.get_order_by_id(order_id)

        update_model_from_schema(order, order_update)
        order = self.repo.update_order(order)
        self.repo.session.commit()

        self.rabbitmq.publish_order_status_changed(SimpleOrder.model_validate(order, from_attributes=True))
        return order

    def delete_order(self, order_id: int) -> None:
        order = self.get_order_by_id(order_id)
        self.repo.delete_order(order)
        return


def get_order_service(
    session = Depends(get_session),
    rabbitmq = Depends(get_rabbitmq_client),
) -> OrderService:
    repo = OrderRepository(session)
    return OrderService(repo, rabbitmq)
