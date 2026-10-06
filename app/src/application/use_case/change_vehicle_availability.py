"""Use case for changing vehicle availability."""

from src.application.interfaces.vehicle_repository import VehicleRepository
from src.domain.entitites.vehicle import Vehicle


class ChangeVehicleAvailabilityUseCase:
    """Mark a vehicle as available or sold."""

    def __init__(self, repository: VehicleRepository) -> None:
        self._repository = repository

    def execute(self, vehicle_id: int, *, status: str, active: bool) -> Vehicle:
        if status not in {"available", "sold"}:
            raise ValueError("Vehicle status must be available or sold")
        return self._repository.set_availability(
            vehicle_id,
            status=status,
            active=active,
        )