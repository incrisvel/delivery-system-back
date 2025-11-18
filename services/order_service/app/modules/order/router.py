from typing import Annotated
from fastapi import APIRouter, Depends
from http import HTTPStatus

from app.modules.order.service import OrderService, get_order_service


router = APIRouter(prefix="/orders", tags=["Orders"])

OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]


@router.get("", status_code=HTTPStatus.OK)
def get_all(order_service: OrderServiceDep):
    return


@router.get("/{order_id}", status_code=HTTPStatus.OK)
def get_by_id(order_id: int, order_service: OrderServiceDep):
    return


@router.post("", status_code=HTTPStatus.CREATED)
def create_order(order_service: OrderServiceDep):
    return


@router.put("/{order_id}", status_code=HTTPStatus.OK)
def update_order(order_service: OrderServiceDep):
    return


@router.delete("/{order_id}", status_code=HTTPStatus.OK)
def delete_order(order_service: OrderServiceDep):
    return
