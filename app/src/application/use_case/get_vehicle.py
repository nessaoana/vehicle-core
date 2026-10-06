"""Use case for retrieving a vehicle."""

from src.application.exceptions.vehicle_exceptions import VehicleNotFoundError
from src.application.interfaces.vehicle_repository import VehicleRepository
from src.domain.entitites.vehicle import Vehicle


class GetVehicleUseCase:
    """Retrieve a vehicle by identifier."""

    def __init__(self, repository: VehicleRepository) -> None:
        self._repository = repository

    def execute(self, vehicle_id: int) -> Vehicle:
        vehicle = self._repository.find_by_id(vehicle_id)
        if vehicle is None:
            raise VehicleNotFoundError(vehicle_id)
        return vehicle