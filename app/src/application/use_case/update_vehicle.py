"""Use case for editing a vehicle."""

from dataclasses import dataclass
from decimal import Decimal

from src.application.exceptions.vehicle_exceptions import (
    VehicleAlreadyExistsError,
    VehicleNotFoundError,
)
from src.application.interfaces.vehicle_repository import VehicleRepository
from src.domain.entitites.vehicle import Vehicle
from src.domain.validators.license_plate import normalize_license_plate


@dataclass(frozen=True)
class UpdateVehicleInput:
    """Optional fields that can be changed on a vehicle."""

    license_plate: str | None = None
    brand: str | None = None
    model: str | None = None
    year: int | None = None
    price: Decimal | None = None
    color: str | None = None
    notes: str | None = None


class UpdateVehicleUseCase:
    """Validate and persist vehicle changes."""

    def __init__(self, repository: VehicleRepository) -> None:
        self._repository = repository

    def execute(self, vehicle_id: int, data: UpdateVehicleInput) -> Vehicle:
        current = self._repository.find_by_id(vehicle_id)
        if current is None:
            raise VehicleNotFoundError(vehicle_id)

        changes = {
            key: value for key, value in data.__dict__.items() if value is not None
        }
        if data.license_plate is not None:
            changes["license_plate"] = normalize_license_plate(data.license_plate)
        if data.brand is not None:
            changes["brand"] = data.brand.strip()
        if data.model is not None:
            changes["model"] = data.model.strip()
        if data.color is not None:
            changes["color"] = data.color.strip()
        if data.notes is not None:
            changes["notes"] = data.notes.strip()
        if data.year is not None and not 1886 <= data.year <= 2100:
            raise ValueError("Vehicle year must be between 1886 and 2100")
        if data.price is not None and data.price <= 0:
            raise ValueError("Vehicle price must be greater than zero")

        if "license_plate" in changes and self._repository.find_by_license_plate(changes["license_plate"]):
            existing = self._repository.find_by_license_plate(changes["license_plate"])
            if existing and existing.id != vehicle_id:
                raise VehicleAlreadyExistsError(changes["license_plate"])

        updated = current.model_copy(update={key: value for key, value in changes.items() if value is not None})
        return self._repository.update(updated)