from typing import List
from fastapi import Depends
from services.order_service.app.core.db.models.order import Order
from services.order_service.app.core.db.models.order_item import OrderItem
from services.order_service.app.core.db.session import get_session
from services.order_service.app.modules.order_item.repository import OrderItemRepository
from services.order_service.app.modules.order_item.schemas import OrderItemCreate


class OrderItemService:
    def __init__(self, repo: OrderItemRepository) -> None:
        self.repo = repo

    def create_order_item(
        self, order: Order, items: List[OrderItemCreate]
    ) -> List[OrderItem]:
        order_items: List[OrderItem] = []

        for item in items:
            item.order_id = order.id
            order_item = OrderItem(**item.model_dump())
            order_items.append(self.repo.create_order_item(order_item))

        return order_items


def get_order_item_service(session=Depends(get_session)) -> OrderItemService:
    repo = OrderItemRepository(session)
    return OrderItemService(repo)
