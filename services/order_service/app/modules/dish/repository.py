from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.db.models.dish import Dish


class DishRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all_dishes(
        self,
        establishment_id: Optional[int] = None,
        name: Optional[str] = None,
        price: Optional[float] = None,
    ) -> Sequence[Dish]:
        stmt = select(Dish)

        if establishment_id is not None:
            stmt = stmt.where(Dish.establishment_id == establishment_id)

        if name is not None:
            stmt = stmt.where(Dish.name == name)

        if price is not None:
            stmt = stmt.where(Dish.price == price)

        dishes = self.session.execute(stmt).scalars().all()
        return dishes

    def get_dish_by_id(self, dish_id: int) -> Dish | None:
        stmt = select(Dish).where(Dish.id == dish_id)
        dish = self.session.execute(stmt).scalar_one_or_none()
        return dish

    def create_dish(self, dish: Dish) -> Dish:
        self.session.add(dish)
        self.session.flush()
        return dish

    def update_dish(self, dish: Dish) -> Dish:
        self.session.merge(dish)
        self.session.flush()
        return dish

    def delete_dish(self, dish: Dish) -> None:
        self.session.delete(dish)
        self.session.flush()
        return
