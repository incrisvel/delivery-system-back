from fastapi import FastAPI
from services.order_service.app.core.db.session import engine
from services.order_service.app.core.db.base import Base
from services.order_service.app.modules.dish.router import router as dishes
from services.order_service.app.modules.delivery.router import router as deliveries
from services.order_service.app.modules.order.router import router as orders
from services.order_service.app.modules.establishment.router import router as establishments
from services.order_service.app.core.messaging import container
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dishes)
app.include_router(deliveries)
app.include_router(orders)
app.include_router(establishments)


@app.on_event("startup")
def start_rabbit():
    container.rabbitmq_client.run()
    
@app.on_event("shutdown")
def shutdown_rabbit():
    container.rabbitmq_client.stop()

@app.get("/")
async def read_root():
    return {"message": "Bem-vindo(a)!"}
