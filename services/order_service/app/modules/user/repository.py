from sqlalchemy.orm import Session


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
