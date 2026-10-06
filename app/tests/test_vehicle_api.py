from fastapi.testclient import TestClient

from src.main import create_app
from src.domain.entitites.vehicle import Vehicle


class InMemoryVehicleRepository:
    def __init__(self) -> None:
        self.vehicles: list[Vehicle] = []

    def find_by_license_plate(self, license_plate: str) -> Vehicle | None:
        return next(
            (vehicle for vehicle in self.vehicles if vehicle.license_plate == license_plate),
            None,
        )

    def create(self, vehicle: Vehicle) -> Vehicle:
        created = vehicle.model_copy(update={"id": len(self.vehicles) + 1})
        self.vehicles.append(created)
        return created


def test_create_vehicle_endpoint_returns_created_vehicle() -> None:
    client = TestClient(create_app(InMemoryVehicleRepository()))

    response = client.post(
        "/vehicles",
        json={
            "license_plate": "abc1d23",
            "brand": "Toyota",
            "model": "Corolla",
            "year": 2024,
        },
    )

    assert response.status_code == 201
    assert response.json()["license_plate"] == "ABC1D23"
    assert response.json()["status"] == "available"