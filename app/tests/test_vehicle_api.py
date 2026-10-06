from fastapi.testclient import TestClient
from fastapi import FastAPI
from decimal import Decimal

from src.adapters.controllers.vehicle_controller import create_vehicle_router
from src.main import create_app
from src.infra.settings import settings
from src.application.exceptions.vehicle_exceptions import (
    VehicleAlreadyExistsError,
    VehicleNotFoundError,
)
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


class ErrorVehicleRepository(InMemoryVehicleRepository):
    def find_by_license_plate(self, license_plate: str) -> Vehicle | None:
        raise VehicleAlreadyExistsError(license_plate)

    def find_by_id(self, vehicle_id: int) -> Vehicle | None:
        raise VehicleNotFoundError(vehicle_id)

    def set_availability(self, vehicle_id: int, *, status: str, active: bool) -> Vehicle:
        raise VehicleNotFoundError(vehicle_id)


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


def test_create_vehicle_endpoint_maps_duplicate_error() -> None:
    client = TestClient(create_app(ErrorVehicleRepository()))

    response = client.post(
        "/vehicles",
        json={
            "license_plate": "ABC1D23",
            "model": "Corolla",
            "year": 2024,
            "price": "75000.00",
        },
    )

    assert response.status_code == 409


def test_vehicle_endpoints_map_not_found_errors() -> None:
    client = TestClient(create_app(ErrorVehicleRepository()))

    assert client.get("/vehicles/99").status_code == 404
    assert client.patch("/vehicles/99", json={"price": "75000.00"}).status_code == 404
    assert client.patch(
        "/vehicles/99/availability",
        json={"status": "sold", "active": False},
    ).status_code == 404


def test_update_endpoint_maps_duplicate_and_invalid_errors() -> None:
    repository = InMemoryVehicleRepository()
    existing = Vehicle(
        id=2,
        license_plate="XYZ1A23",
        model="Fiesta",
        year=2022,
        price=Decimal("50000.00"),
    )
    repository.vehicles.append(existing)
    repository.vehicles.append(
        Vehicle(
            id=1,
            license_plate="ABC1D23",
            model="Corolla",
            year=2024,
            price=Decimal("75000.00"),
        )
    )
    client = TestClient(create_app(repository))

    duplicate = client.patch("/vehicles/1", json={"license_plate": "XYZ1A23"})
    invalid = client.patch("/vehicles/1", json={"price": "0"})

    assert duplicate.status_code == 409
    assert invalid.status_code == 422


class RaisingCreateUseCase:
    def execute(self, data: object) -> Vehicle:
        raise ValueError("invalid vehicle")


class RaisingUpdateUseCase:
    def execute(self, vehicle_id: int, data: object) -> Vehicle:
        raise ValueError("invalid update")


class UnusedUseCase:
    def execute(self, *args: object, **kwargs: object) -> Vehicle:
        raise AssertionError("unused use case")


def test_controller_maps_domain_validation_errors() -> None:
    app = FastAPI()
    app.include_router(
        create_vehicle_router(
            RaisingCreateUseCase(),
            UnusedUseCase(),
            RaisingUpdateUseCase(),
            UnusedUseCase(),
        )
    )
    client = TestClient(app)

    create_response = client.post(
        "/vehicles",
        json={"license_plate": "ABC1D23", "model": "Corolla", "year": 2024, "price": "75000"},
    )
    update_response = client.patch("/vehicles/1", json={"model": "Yaris"})

    assert create_response.status_code == 422
    assert update_response.status_code == 422


def test_real_app_initializes_database_and_reports_readiness(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(settings, "DATABASE_URL", f"sqlite:///{tmp_path / 'vehicle.db'}")
    client = TestClient(create_app())

    with client:
        response = client.get("/health/ready")

    assert response.json() == {"status": "ok", "database": "ok"}