from sqlalchemy.orm import Session


class EstablishmentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
