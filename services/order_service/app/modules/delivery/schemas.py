from typing import Optional
from pydantic import BaseModel


class DeliveryRead(BaseModel):
    id: int
    origin_latitude: float
    origin_longitude: float
    destination_latitude: float
    destination_longitude: float
    courier: str


class DeliveryCreate(BaseModel):
    origin_latitude: float
    origin_longitude: float
    destination_latitude: float
    destination_longitude: float
    courier: str


class DeliveryUpdate(BaseModel):
    origin_latitude: Optional[float] = None
    origin_longitude: Optional[float] = None
    destination_latitude: Optional[float] = None
    destination_longitude: Optional[float] = None
    courier: Optional[str] = None
