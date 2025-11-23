from http import HTTPStatus
from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, Query

from services.order_service.app.modules.dish.schemas import DishCreate, DishRead, DishUpdate
from services.order_service.app.modules.dish.service import DishService, get_dish_service


router = APIRouter(prefix="/dishes", tags=["Dishes"])
DishServiceDep = Annotated[DishService, Depends(get_dish_service)]


@router.get("", response_model=List[DishRead], status_code=HTTPStatus.OK)
def get_all_dishes(
    dish_service: DishServiceDep,
    establishment_id: Optional[int] = Query(None),
    name: Optional[str] = Query(None),
    price: Optional[float] = None,
):
    dishes = dish_service.get_all_dishes(establishment_id, name, price)
    return dishes


@router.get("/{dish_id}", response_model=DishRead, status_code=HTTPStatus.OK)
def get_dish_by_id(dish_id: int, dish_service: DishServiceDep):
    dish = dish_service.get_dish_by_id(dish_id)
    return dish


@router.post("", response_model=DishRead, status_code=HTTPStatus.CREATED)
def create_dish(dish_create: DishCreate, dish_service: DishServiceDep):
    dish = dish_service.create_dish(dish_create)
    return dish


@router.put("/{dish_id}", response_model=DishRead, status_code=HTTPStatus.OK)
def update_dish(dish_id: int, dish_update: DishUpdate, dish_service: DishServiceDep):
    dish = dish_service.update_dish(dish_id, dish_update)
    return dish


@router.delete("/{dish_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_dish(dish_id: int, dish_service: DishServiceDep):
    dish_service.delete_dish(dish_id)
    return
