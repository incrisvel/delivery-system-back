from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Enum as SQLEnum, Float, ForeignKey
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db.base import Base
from zoneinfo import ZoneInfo


class OrderStatus(str, Enum):
    CONFIRMED = "cofirmed"
    CREATED = "created"
    UPDATED = "updated"
    ASSIGNED = "assigned"
    ENROUTE = "enroute"
    DELIVERED = "delivered"


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False
    )
    client: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=ZoneInfo("UTC")),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=ZoneInfo("UTC")),
        onupdate=lambda: datetime.now(tz=ZoneInfo("UTC")),
        nullable=False,
    )
    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus), nullable=False, default=OrderStatus.CONFIRMED
    )
    total: Mapped[float] = mapped_column(Float, nullable=False)

    establishment_id: Mapped[int] = mapped_column(
        ForeignKey("establishments.id"), nullable=False
    )
    delivery_id: Mapped[int] = mapped_column(ForeignKey("deliveries.id"), nullable=True)

    establishment = relationship("Establishment", back_populates="orders")
    delivery = relationship("Delivery", back_populates="order")
