from typing import List, Optional
from fastapi import Depends
from app.core.db.models.establishment import Establishment
from app.core.db.session import get_session
from app.core.utils.models import update_model_from_schema
from app.modules.establishment.repository import EstablishmentRepository
from app.modules.establishment.exceptions import EstablishmentNotFoundError
from app.modules.establishment.schemas import EstablishmentCreate, EstablishmentUpdate
from app.modules.maps.service import GeolocatorService


class EstablishmentService:
    def __init__(self, repo: EstablishmentRepository) -> None:
        self.repo = repo

    def get_all_establishments(self, name: Optional[str] = None) -> List[Establishment]:
        establishments = self.repo.get_all_establishments(name)
        return list(establishments)

    def get_establishment_by_id(self, establishment_id: int) -> Establishment:
        establishment = self.repo.get_establishment_by_id(establishment_id)
        if not establishment:
            raise EstablishmentNotFoundError

        return establishment

    async def create_establishment(
        self,
        establishment_create: EstablishmentCreate,
        address: str,
    ) -> Establishment:
        geolocator = GeolocatorService()
        location = geolocator.get_location_from_address(address)

        if location is None:
            raise EstablishmentNotFoundError

        establishment = Establishment(**establishment_create.model_dump())
        establishment.address = address
        establishment.latitude = location.latitude
        establishment.longitude = location.longitude
        establishment = self.repo.create_establishment(establishment)

        self.repo.session.commit()

        return establishment

    def update_establishment(
        self, establishment_id: int, establishment_update: EstablishmentUpdate
    ) -> Establishment:
        establishment = self.get_establishment_by_id(establishment_id)

        update_model_from_schema(establishment, establishment_update)
        establishment = self.repo.update_establishment(establishment)

        self.repo.session.commit()

        return establishment

    def delete_establishment(self, establishment_id: int) -> None:
        establishment = self.get_establishment_by_id(establishment_id)
        self.repo.delete_establishment(establishment)
        self.repo.session.commit()
        return


def get_establishment_service(session=Depends(get_session)) -> EstablishmentService:
    repo = EstablishmentRepository(session)
    return EstablishmentService(repo)
