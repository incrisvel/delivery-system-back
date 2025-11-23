from typing import Optional
from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.order_service.app.core.db.base import Base


class Dish(Base):
    __tablename__ = "dishes"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    image: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    establishment_id: Mapped[int] = mapped_column(
        ForeignKey("establishments.id"), nullable=False
    )

    establishment = relationship("Establishment", back_populates="dishes")
