import openrouteservice as ors
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from services.order_service.app.core.config.settings import settings


class Coordinate:
    def __init__(self, latitude: float, longitude: float) -> None:
        self.latitude = latitude
        self.longitude = longitude


class GeolocatorService:
    def __init__(self) -> None:
        self.geolocator = Nominatim(user_agent="trabalho-final-SD")
        self.open_route_client = ors.Client(key=settings.open_route_key)

    def get_location_from_address(self, address: str):
        location = self.geolocator.geocode(address)
        return location

    def from_coordinates_to_address(self, latitude: float, longitude: float):
        location = self.geolocator.reverse((latitude, longitude))
        return location

    def calculate_distance(self, origin: Coordinate, destination: Coordinate):
        distance = geodesic(
            (origin.latitude, origin.longitude),
            (destination.latitude, destination.longitude),
        )
        return distance
