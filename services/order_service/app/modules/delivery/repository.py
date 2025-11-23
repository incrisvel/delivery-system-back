from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from services.order_service.app.core.db.models.delivery import Delivery


class DeliveryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all_deliveries(
        self,
        origin_latitude: Optional[float] = None,
        origin_longitude: Optional[float] = None,
        destination_latitude: Optional[float] = None,
        destination_longitude: Optional[float] = None,
        courier: Optional[str] = None,
    ) -> Sequence[Delivery]:
        stmt = select(Delivery)

        if origin_latitude is not None:
            stmt = stmt.where(Delivery.origin_latitude == origin_latitude)

        if origin_longitude is not None:
            stmt = stmt.where(Delivery.origin_longitude == origin_longitude)

        if destination_latitude is not None:
            stmt = stmt.where(Delivery.destination_latitude == destination_latitude)

        if destination_longitude is not None:
            stmt = stmt.where(Delivery.destination_longitude == destination_longitude)

        if courier is not None:
            stmt = stmt.where(Delivery.courier == courier)

        deliveries = self.session.execute(stmt).scalars().all()
        return deliveries

    def get_delivery_by_id(self, delivery_id: int) -> Delivery | None:
        stmt = select(Delivery).where(Delivery.id == delivery_id)
        delivery = self.session.execute(stmt).scalar_one_or_none()
        return delivery

    def create_delivery(self, delivery: Delivery) -> Delivery:
        self.session.add(delivery)
        self.session.flush()
        return delivery

    def update_delivery(self, delivery: Delivery) -> Delivery:
        self.session.merge(delivery)
        self.session.flush()
        return delivery

    def delete_delivery(self, delivery: Delivery) -> None:
        self.session.delete(delivery)
        self.session.flush()
        return
