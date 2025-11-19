from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, Query

from app.modules.delivery.schemas import DeliveryCreate, DeliveryRead, DeliveryUpdate
from app.modules.delivery.service import DeliveryService, get_delivery_service
from http import HTTPStatus

router = APIRouter(prefix="/deliveries", tags=["Delivery"])

DeliveryServiceDep = Annotated[DeliveryService, Depends(get_delivery_service)]


@router.get("", response_model=List[DeliveryRead], status_code=HTTPStatus.OK)
def get_all_deliveries(
    delivery_service: DeliveryServiceDep,
    origin_latitude: Optional[float] = Query(None),
    origin_longitude: Optional[float] = Query(None),
    destination_latitude: Optional[float] = Query(None),
    destination_longitude: Optional[float] = Query(None),
    courier: Optional[float] = Query(None),
):
    deliveries = delivery_service.get_all_deliveries(
        origin_latitude,
        origin_longitude,
        destination_latitude,
        destination_longitude,
        courier,
    )
    return deliveries


@router.get("/{delivery_id}", response_model=DeliveryRead, status_code=HTTPStatus.OK)
def get_delivery_by_id(delivery_id: int, delivery_service: DeliveryServiceDep):
    delivery = delivery_service.get_delivery_by_id(delivery_id)
    return delivery


@router.post("", response_model=DeliveryRead, status_code=HTTPStatus.CREATED)
def create_delivery(
    delivery_create: DeliveryCreate, delivery_service: DeliveryServiceDep
):
    delivery = delivery_service.create_delivery(delivery_create)
    return delivery


@router.put("/{delivery_id}", response_model=DeliveryRead, status_code=HTTPStatus.OK)
def update_delivery(
    delivery_id: int,
    delivery_update: DeliveryUpdate,
    delivery_service: DeliveryServiceDep,
):
    delivery = delivery_service.update_delivery(delivery_id, delivery_update)
    return delivery


@router.delete("/{delivery_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_delivery(delivery_id: int, delivery_service: DeliveryServiceDep):
    delivery = delivery_service.delete_delivery(delivery_id)
    return delivery
