from typing import List, Optional
from services.order_service.app.core.utils.models import update_model_from_schema
from fastapi import Depends
from services.order_service.app.core.db.models.delivery import Delivery
from services.order_service.app.core.db.session import get_session
from services.order_service.app.modules.delivery.exceptions import DeliveryNotFoundError
from services.order_service.app.modules.delivery.repository import DeliveryRepository
from services.order_service.app.modules.delivery.schemas import DeliveryCreate, DeliveryUpdate


class DeliveryService:
    def __init__(self, repo: DeliveryRepository) -> None:
        self.repo = repo

    def get_all_deliveries(
        self,
        origin_latitude: Optional[float] = None,
        origin_longitude: Optional[float] = None,
        destination_latitude: Optional[float] = None,
        destination_longitude: Optional[float] = None,
        courier: Optional[str] = None,
    ) -> List[Delivery]:
        deliveries = self.repo.get_all_deliveries(
            origin_latitude,
            origin_longitude,
            destination_latitude,
            destination_longitude,
            courier,
        )
        return list(deliveries)

    def get_delivery_by_id(self, delivery_id: int) -> Delivery:
        delivery = self.repo.get_delivery_by_id(delivery_id)
        if not delivery:
            raise DeliveryNotFoundError

        return delivery

    def create_delivery(self, delivery_create: DeliveryCreate) -> Delivery:
        delivery = Delivery(**delivery_create.model_dump())
        delivery = self.repo.create_delivery(delivery)
        self.repo.session.commit()
        return delivery

    def update_delivery(
        self, delivery_id: int, delivery_update: DeliveryUpdate
    ) -> Delivery:
        delivery = self.get_delivery_by_id(delivery_id)

        update_model_from_schema(delivery, delivery_update)

        delivery = self.repo.update_delivery(delivery)
        self.repo.session.commit()

        return delivery

    def delete_delivery(self, delivery_id: int) -> None:
        delivery = self.get_delivery_by_id(delivery_id)
        self.repo.delete_delivery(delivery)
        self.repo.session.commit()
        return


def get_delivery_service(session=Depends(get_session)) -> DeliveryService:
    repo = DeliveryRepository(session)
    return DeliveryService(repo)
