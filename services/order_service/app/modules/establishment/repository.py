from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db.models.establishment import Establishment


class EstablishmentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all_establishments(
        self, name: Optional[str] = None
    ) -> Sequence[Establishment]:
        stmt = select(Establishment)

        if name is not None:
            stmt = stmt.where(Establishment.name.ilike(f"%{name}%"))

        establishments = self.session.execute(stmt).scalars().all()
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
