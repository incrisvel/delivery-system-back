from sqlalchemy.orm import Session

from services.order_service.app.core.db.models.order_item import OrderItem


class OrderItemRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_order_item(self, order_item: OrderItem) -> OrderItem:
        self.session.add(order_item)
        self.session.flush()
        return order_item
