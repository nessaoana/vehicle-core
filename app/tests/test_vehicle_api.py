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

    def find_by_id(self, vehicle_id: int) -> Vehicle | None:
        return next((vehicle for vehicle in self.vehicles if vehicle.id == vehicle_id), None)

    def update(self, vehicle: Vehicle) -> Vehicle:
        self.vehicles = [
            vehicle if current.id == vehicle.id else current for current in self.vehicles
        ]
        return vehicle

    def set_availability(self, vehicle_id: int, *, status: str, active: bool) -> Vehicle:
        vehicle = self.find_by_id(vehicle_id)
        assert vehicle is not None
        return self.update(vehicle.model_copy(update={"status": status, "active": active}))


def test_create_vehicle_endpoint_returns_created_vehicle() -> None:
    client = TestClient(create_app(InMemoryVehicleRepository()))

    response = client.post(
        "/vehicles",
        json={
            "license_plate": "abc1d23",
            "brand": "Toyota",
            "model": "Corolla",
            "year": 2024,
            "price": "75000.00",
        },
    )

    assert response.status_code == 201
    assert response.json()["license_plate"] == "ABC1D23"
    assert response.json()["status"] == "available"


def test_health_endpoints_report_application_status() -> None:
    client = TestClient(create_app(InMemoryVehicleRepository()))

    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/health/ready").json() == {
        "status": "ok",
        "database": "not_configured",
    }


def test_create_vehicle_endpoint_rejects_invalid_license_plate() -> None:
    client = TestClient(create_app(InMemoryVehicleRepository()))

    response = client.post(
        "/vehicles",
        json={"license_plate": "INVALID", "model": "Corolla", "year": 2024},
    )

    assert response.status_code == 422


def test_vehicle_lifecycle_endpoints_update_and_change_availability() -> None:
    repository = InMemoryVehicleRepository()
    client = TestClient(create_app(repository))
    created = client.post(
        "/vehicles",
        json={
            "license_plate": "ABC1D23",
            "model": "Corolla",
            "year": 2024,
            "price": "75000.00",
        },
    )

    vehicle_id = created.json()["id"]
    updated = client.patch(
        f"/vehicles/{vehicle_id}",
        json={"price": "82000.00", "model": "Yaris"},
    )
    sold = client.patch(
        f"/vehicles/{vehicle_id}/availability",
        json={"status": "sold", "active": False},
    )

    assert updated.status_code == 200
    assert updated.json()["price"] == "82000.00"
    assert sold.status_code == 200
    assert sold.json()["status"] == "sold"
    assert client.get(f"/vehicles/{vehicle_id}").status_code == 200