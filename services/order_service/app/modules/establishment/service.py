from fastapi import Depends
from app.core.db.session import get_session
from app.modules.establishment.repository import EstablishmentRepository


class EstablishmentService:
    def __init__(self, repo: EstablishmentRepository) -> None:
        self.repo = repo


def get_establishment_service(session=Depends(get_session)) -> EstablishmentService:
    repo = EstablishmentRepository(session)
    return EstablishmentService(repo)
