"""Use case for registering a vehicle."""

from dataclasses import dataclass
import logging

from src.application.exceptions.vehicle_exceptions import VehicleAlreadyExistsError
from src.application.interfaces.vehicle_repository import VehicleRepository
from src.domain.entitites.vehicle import Vehicle
from src.domain.factories.vehicle_factory import VehicleFactory


logger = logging.getLogger("vehicle-core")


@dataclass(frozen=True)
class CreateVehicleInput:
    """Input required to register a vehicle."""

    license_plate: str
    brand: str | None
    model: str
    year: int
    color: str | None
    notes: str | None


class CreateVehicleUseCase:
    """Coordinate domain creation and vehicle persistence."""

    def __init__(self, repository: VehicleRepository) -> None:
        self._repository = repository

    def execute(self, data: CreateVehicleInput) -> Vehicle:
        logger.info(
            "vehicle_registration_started",
            extra={"license_plate": data.license_plate.strip().upper()},
        )
        vehicle = VehicleFactory.create(
            license_plate=data.license_plate,
            brand=data.brand,
            model=data.model,
            year=data.year,
            color=data.color,
            notes=data.notes,
        )

        if self._repository.find_by_license_plate(vehicle.license_plate):
            logger.warning(
                "vehicle_registration_rejected_duplicate",
                extra={"license_plate": vehicle.license_plate},
            )
            raise VehicleAlreadyExistsError(vehicle.license_plate)

        created_vehicle = self._repository.create(vehicle)
        logger.info(
            "vehicle_registered",
            extra={
                "vehicle_id": created_vehicle.id,
                "license_plate": created_vehicle.license_plate,
            },
        )
        return created_vehicle