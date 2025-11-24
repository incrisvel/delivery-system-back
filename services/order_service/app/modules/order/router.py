from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends
from http import HTTPStatus

from services.order_service.app.modules.delivery.service import (
    DeliveryService,
    get_delivery_service,
)
from services.order_service.app.modules.establishment.service import (
    EstablishmentService,
    get_establishment_service,
)
from services.order_service.app.core.db.models.order import OrderStatus
from services.order_service.app.modules.order.schemas import (
    OrderWithItemsCreate,
    OrderRead,
    OrderUpdate,
)
from services.order_service.app.modules.order.service import (
    OrderService,
    get_order_service,
)
from services.order_service.app.modules.order_item.service import (
    OrderItemService,
    get_order_item_service,
)


router = APIRouter(prefix="/orders", tags=["Orders"])

OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]


@router.get("", response_model=List[OrderRead], status_code=HTTPStatus.OK)
def get_all(
    order_service: OrderServiceDep,
    establishment_id: Optional[int] = None,
    delivery_id: Optional[int] = None,
    status: Optional[OrderStatus] = None,
):
    orders = order_service.get_all_orders(establishment_id, delivery_id, status)
    return orders


@router.get("/{order_id}", response_model=OrderRead, status_code=HTTPStatus.OK)
def get_by_id(order_id: int, order_service: OrderServiceDep):
    order = order_service.get_order_by_id(order_id)
    return order


@router.post("", response_model=OrderRead, status_code=HTTPStatus.CREATED)
def create_order(
    order_create: OrderWithItemsCreate,
    order_service: OrderServiceDep,
    order_item_service: OrderItemService = Depends(get_order_item_service),
    establishment_service: EstablishmentService = Depends(get_establishment_service),
    delivery_service: DeliveryService = Depends(get_delivery_service),
):
    establishment = establishment_service.get_establishment_by_id(
        order_create.establishment_id
    )
    delivery = delivery_service.create_delivery(order_create, establishment)
    order = order_service.create_order(order_create, delivery.id)
    order_item_service.create_order_item(order, order_create.items)
    order_service.repo.session.commit()
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
