from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from services.order_service.app.core.db.base import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), primary_key=True, nullable=False)
    dish_id: Mapped[int] = mapped_column(ForeignKey("dishes.id"), primary_key=True, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)

