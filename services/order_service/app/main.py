from fastapi import FastAPI
from app.core.db.session import engine
from app.core.db.base import Base
from app.modules.maps.service import Coordinate, GeolocatorService

app = FastAPI()

Base.metadata.create_all(bind=engine)


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
