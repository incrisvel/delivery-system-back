from typing import Annotated, List
from fastapi import APIRouter, Depends
from http import HTTPStatus

from app.modules.order.schemas import OrderCreate, OrderRead, OrderUpdate
from app.modules.order.service import OrderService, get_order_service


router = APIRouter(prefix="/orders", tags=["Orders"])

OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]


@router.get("", response_model=List[OrderRead], status_code=HTTPStatus.OK)
def get_all(order_service: OrderServiceDep):
    orders = order_service.get_all_orders()
    return orders


@router.get("/{order_id}", response_model=OrderRead, status_code=HTTPStatus.OK)
def get_by_id(order_id: int, order_service: OrderServiceDep):
    order = order_service.get_order_by_id(order_id)
    return order


@router.post("", response_model=OrderRead, status_code=HTTPStatus.CREATED)
def create_order(order_create: OrderCreate, order_service: OrderServiceDep):
    order = order_service.create_order(order_create)
    return order


@router.put("/{order_id}", response_model=OrderRead, status_code=HTTPStatus.OK)
def update_order(
    order_id: int, order_update: OrderUpdate, order_service: OrderServiceDep
):
    order = order_service.update_order(order_id, order_update)
    return order


@router.delete("/{order_id}", status_code=HTTPStatus.OK)
def delete_order(order_id: int, order_service: OrderServiceDep):
    order_service.delete_order(order_id)
    return
