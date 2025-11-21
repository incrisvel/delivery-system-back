from typing import Optional, Sequence
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db.models.establishment import Establishment


class EstablishmentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all_establishments(
        self,
        name: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius: Optional[int] = None,
    ):
        R = 6371000

        stmt = select(Establishment)

        if lat is not None and lon is not None and radius is not None:

            distance = R * func.acos(
                func.cos(func.radians(lat))
                * func.cos(func.radians(Establishment.latitude))
                * func.cos(func.radians(Establishment.longitude) - func.radians(lon))
                + func.sin(func.radians(lat))
                * func.sin(func.radians(Establishment.latitude))
            )

            stmt = stmt.add_columns(distance.label("distance"))
            stmt = stmt.where(distance <= radius)
            stmt = stmt.order_by(distance)

        if name:
            stmt = stmt.where(Establishment.name.ilike(f"%{name}%"))

        results = self.session.execute(stmt).all()

        establishments = [row[0] for row in results]

        return establishments


    def get_establishment_by_id(self, establishment_id: int) -> Establishment | None:
        stmt = select(Establishment).where(Establishment.id == establishment_id)
        establishment = self.session.execute(stmt).scalar_one_or_none()
        return establishment

    def create_establishment(self, establishment: Establishment) -> Establishment:
        self.session.add(establishment)
        self.session.flush()
        return establishment

    def update_establishment(self, establishment: Establishment) -> Establishment:
        self.session.merge(establishment)
        self.session.flush()
        return establishment

    def delete_establishment(self, establishment: Establishment) -> None:
        self.session.delete(establishment)
        self.session.flush()
        return
