from decimal import Decimal

import pytest

from src.application.exceptions.vehicle_exceptions import VehicleNotFoundError
from src.application.use_case.change_vehicle_availability import (
    ChangeVehicleAvailabilityUseCase,
)
from src.application.use_case.get_vehicle import GetVehicleUseCase
from src.application.use_case.update_vehicle import UpdateVehicleInput, UpdateVehicleUseCase
from src.domain.entitites.vehicle import Vehicle


class InMemoryVehicleRepository:
    def __init__(self) -> None:
        self.vehicles: dict[int, Vehicle] = {}

    def find_by_license_plate(self, license_plate: str) -> Vehicle | None:
        return next(
            (vehicle for vehicle in self.vehicles.values() if vehicle.license_plate == license_plate),
            None,
        )

    def find_by_id(self, vehicle_id: int) -> Vehicle | None:
        return self.vehicles.get(vehicle_id)

    def create(self, vehicle: Vehicle) -> Vehicle:
        created = vehicle.model_copy(update={"id": 1})
        self.vehicles[1] = created
        return created

    def update(self, vehicle: Vehicle) -> Vehicle:
        self.vehicles[vehicle.id] = vehicle
        return vehicle

    def set_availability(self, vehicle_id: int, *, status: str, active: bool) -> Vehicle:
        vehicle = self.vehicles[vehicle_id].model_copy(update={"status": status, "active": active})
        self.vehicles[vehicle_id] = vehicle
        return vehicle


def registered_vehicle() -> Vehicle:
    return Vehicle(
        id=1,
        license_plate="ABC1D23",
        brand="Toyota",
        model="Corolla",
        year=2024,
        price=Decimal("75000.00"),
    )


def test_get_vehicle_returns_registered_vehicle() -> None:
    repository = InMemoryVehicleRepository()
    repository.vehicles[1] = registered_vehicle()

    assert GetVehicleUseCase(repository).execute(1) == registered_vehicle()


def test_update_vehicle_changes_price_and_model() -> None:
    repository = InMemoryVehicleRepository()
    repository.vehicles[1] = registered_vehicle()

    updated = UpdateVehicleUseCase(repository).execute(
        1,
        UpdateVehicleInput(model="Yaris", price=Decimal("82000.00")),
    )

    assert updated.model == "Yaris"
    assert updated.price == Decimal("82000.00")


def test_change_availability_marks_vehicle_as_sold() -> None:
    repository = InMemoryVehicleRepository()
    repository.vehicles[1] = registered_vehicle()

    updated = ChangeVehicleAvailabilityUseCase(repository).execute(
        1,
        status="sold",
        active=False,
    )

    assert updated.status == "sold"
    assert updated.active is False


def test_get_vehicle_rejects_unknown_id() -> None:
    with pytest.raises(VehicleNotFoundError):
        GetVehicleUseCase(InMemoryVehicleRepository()).execute(99)