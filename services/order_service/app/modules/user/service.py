from fastapi import Depends
from app.core.db.session import get_session
from app.modules.user.repository import UserRepository


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo


def get_user_service(session=Depends(get_session)) -> UserService:
    repo = UserRepository(session)
    return UserService(repo)
