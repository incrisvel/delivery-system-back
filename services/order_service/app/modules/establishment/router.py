from typing import Annotated
from fastapi import APIRouter, Depends
from http import HTTPStatus

from app.modules.establishment.service import (
    EstablishmentService,
    get_establishment_service,
)


router = APIRouter(prefix="/establishments", tags=["Establishments"])

EstablishmentServiceDep = Annotated[
    EstablishmentService, Depends(get_establishment_service)
]


@router.get("", status_code=HTTPStatus.OK)
def get_all(establishment_service: EstablishmentServiceDep):
    return


@router.get("/{establishment_id}", status_code=HTTPStatus.OK)
def get_by_id(establishment_id: int, establishment_service: EstablishmentServiceDep):
    return


@router.post("", status_code=HTTPStatus.CREATED)
def create_establishment(establishment_service: EstablishmentServiceDep):
    return


@router.put("/{establishment_id}", status_code=HTTPStatus.OK)
def update_establishment(establishment_service: EstablishmentServiceDep):
    return


@router.delete("/{establishment_id}", status_code=HTTPStatus.OK)
def delete_establishment(establishment_service: EstablishmentServiceDep):
    return
