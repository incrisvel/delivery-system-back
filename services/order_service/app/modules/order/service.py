from fastapi import Depends
from app.core.db.session import get_session
from app.modules.order.repository import OrderRepository


class OrderService:
    def __init__(self, repo: OrderRepository) -> None:
        self.repo = repo


def get_order_service(session=Depends(get_session)) -> OrderService:
    repo = OrderRepository(session)
    return OrderService(repo)
