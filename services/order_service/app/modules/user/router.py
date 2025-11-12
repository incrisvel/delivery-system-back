from typing import Annotated
from fastapi import APIRouter, Depends
from http import HTTPStatus

from app.modules.user.service import UserService, get_user_service


router = APIRouter(prefix="/users", tags=["Users"])

UserServiceDep = Annotated[UserService, Depends(get_user_service)]


@router.get("", status_code=HTTPStatus.OK)
def get_all(user_service: UserServiceDep):
    return


@router.get("/{user_id}", status_code=HTTPStatus.OK)
def get_by_id(user_id: int, user_service: UserServiceDep):
    return


@router.post("", status_code=HTTPStatus.CREATED)
def create_user(user_service: UserServiceDep):
    return


@router.put("/{user_id}", status_code=HTTPStatus.OK)
def update_user(user_service: UserServiceDep):
    return


@router.delete("/{user_id}", status_code=HTTPStatus.OK)
def delete_user(user_service: UserServiceDep):
    return
