from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from services.order_service.app.core.config.settings import settings


engine = create_engine(settings.database_url, pool_pre_ping=True)


def get_session():
    with Session(engine) as session:
        yield session
