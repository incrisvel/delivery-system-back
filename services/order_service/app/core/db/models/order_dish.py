from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db.base import Base


class OrderDish(Base):
    __tablename__ = "order_dishes"

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), primary_key=True, nullable=False)
    dish_id: Mapped[int] = mapped_column(ForeignKey("dishes.id"), primary_key=True, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    total: Mapped[int] = mapped_column(Integer, nullable=False)

