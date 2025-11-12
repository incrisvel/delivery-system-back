from fastapi import FastAPI
from app.core.db.session import engine
from app.core.db.base import Base

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("")
async def read_root():
    return {"message": "Order Service!"}
