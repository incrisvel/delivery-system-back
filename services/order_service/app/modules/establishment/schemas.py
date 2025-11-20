from typing import Optional
from pydantic import BaseModel


class EstablishmentRead(BaseModel):
    id: int
    address: str
    name: str
    image: Optional[str] = None
    latitude: float
    longitude: float


class EstablishmentCreate(BaseModel):
    name: str
    address: str
    image: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class EstablishmentUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    image: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
