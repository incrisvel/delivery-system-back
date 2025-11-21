from fastapi import FastAPI
from app.core.db.session import engine
from app.core.db.base import Base
from app.modules.maps.service import Coordinate, GeolocatorService
from app.modules.dish.router import router as dishes
from app.modules.delivery.router import router as deliveries
from app.modules.order.router import router as orders
from app.modules.establishment.router import router as establishments
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


@app.get("/teste")
async def read_root():
    geolocator = GeolocatorService()
    origin = geolocator.get_location_from_address("Furb")
    origin_coords = Coordinate(latitude=origin.latitude, longitude=origin.longitude)

    destination = geolocator.get_location_from_address("Shopping Neumarkt")
    destination_coords = Coordinate(
        latitude=destination.latitude, longitude=destination.longitude
    )

    return {"message": "Order Service!"}
