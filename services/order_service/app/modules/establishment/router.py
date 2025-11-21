from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, Query
from http import HTTPStatus

from app.modules.establishment.schemas import (
    EstablishmentCreate,
    EstablishmentRead,
    EstablishmentUpdate,
)
from app.modules.establishment.service import (
    EstablishmentService,
    get_establishment_service,
)


router = APIRouter(prefix="/establishments", tags=["Establishments"])

EstablishmentServiceDep = Annotated[
    EstablishmentService, Depends(get_establishment_service)
]


@router.get("", response_model=List[EstablishmentRead], status_code=HTTPStatus.OK)
def get_all(
    establishment_service: EstablishmentServiceDep,
    name: Optional[str] = Query(None),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    radius: Optional[int] = Query(None),
):
    establishments = establishment_service.get_all_establishments(
        name, lat, lon, radius
    )
    return establishments


@router.get(
    "/{establishment_id}", response_model=EstablishmentRead, status_code=HTTPStatus.OK
)
def get_by_id(
    establishment_id: int,
    establishment_service: EstablishmentServiceDep,
):
    establishment = establishment_service.get_establishment_by_id(establishment_id)
    return establishment


@router.post("", response_model=EstablishmentRead, status_code=HTTPStatus.CREATED)
async def create_establishment(
    establishment_create: EstablishmentCreate,
    establishment_service: EstablishmentServiceDep,
):
    establishment = await establishment_service.create_establishment(
        establishment_create, establishment_create.address
    )
    return establishment


@router.put(
    "/{establishment_id}", response_model=EstablishmentRead, status_code=HTTPStatus.OK
)
def update_establishment(
    establishment_id: int,
    establishment_update: EstablishmentUpdate,
    establishment_service: EstablishmentServiceDep,
):
    establishment = establishment_service.update_establishment(
        establishment_id, establishment_update
    )
    return establishment


@router.delete("/{establishment_id}", status_code=HTTPStatus.OK)
def delete_establishment(
    establishment_id: int, establishment_service: EstablishmentServiceDep
):
    establishment_service.delete_establishment(establishment_id)
    return
