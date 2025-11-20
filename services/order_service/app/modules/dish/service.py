from typing import List, Optional
from app.core.utils.models import update_model_from_schema
from app.core.db.models.dish import Dish
from app.modules.dish.exceptions import DishNotFoundError
from app.modules.dish.repository import DishRepository
from fastapi import Depends
from app.core.db.session import get_session
from app.modules.dish.schemas import DishCreate, DishUpdate


class DishService:
    def __init__(self, repo: DishRepository) -> None:
        self.repo = repo

    def get_all_dishes(
        self,
        establishment_id: Optional[int] = None,
        name: Optional[str] = None,
        price: Optional[float] = None,
    ) -> List[Dish]:
        dishes = self.repo.get_all_dishes(establishment_id, name, price)
        return list(dishes)

    def get_dish_by_id(self, dish_id: int) -> Dish:
        dish = self.repo.get_dish_by_id(dish_id)
        if not dish:
            raise DishNotFoundError
        return dish

    def create_dish(self, dish_create: DishCreate) -> Dish:
        dish = Dish(**dish_create.model_dump())
        dish = self.repo.create_dish(dish)
        self.repo.session.commit()
        return dish

    def update_dish(self, dish_id: int, dish_update: DishUpdate) -> Dish:
        dish = self.get_dish_by_id(dish_id)
        update_model_from_schema(dish, dish_update)
        dish = self.repo.update_dish(dish)
        self.repo.session.commit()
        return dish

    def delete_dish(self, dish_id: int) -> None:
        dish = self.get_dish_by_id(dish_id)
        self.repo.delete_dish(dish)
        self.repo.session.commit()
        return


def get_dish_service(session=Depends(get_session)) -> DishService:
    repo = DishRepository(session)
    return DishService(repo)
