import pytest
from decimal import Decimal

from src.application.exceptions.vehicle_exceptions import VehicleAlreadyExistsError
from src.application.use_case.create_vehicle import CreateVehicleInput, CreateVehicleUseCase
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


def vehicle_input(license_plate: str = "ABC1D23") -> CreateVehicleInput:
    return CreateVehicleInput(
        license_plate=license_plate,
        brand="Toyota",
        model="Corolla",
        year=2024,
        price=Decimal("75000.00"),
        color="Black",
        notes=None,
    )


def test_create_vehicle_uses_factory_and_repository() -> None:
    repository = InMemoryVehicleRepository()

    created = CreateVehicleUseCase(repository).execute(vehicle_input(" abc1d23 "))

    assert created.id == 1
    assert created.license_plate == "ABC1D23"
    assert repository.vehicles == [created]


def test_create_vehicle_rejects_duplicate_plate() -> None:
    repository = InMemoryVehicleRepository()
    use_case = CreateVehicleUseCase(repository)
    use_case.execute(vehicle_input())

    with pytest.raises(VehicleAlreadyExistsError):
        use_case.execute(vehicle_input("abc1d23"))