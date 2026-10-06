"""Persistence port for vehicles."""

from collections.abc import Callable
from typing import Protocol

from src.domain.entitites.vehicle import Vehicle


class VehicleRepository(Protocol):
    """Port used by application services to persist vehicles."""

    def find_by_license_plate(self, license_plate: str) -> Vehicle | None:
        """Return a vehicle by its normalized license plate."""

    def create(self, vehicle: Vehicle) -> Vehicle:
        """Persist and return a vehicle."""

    def find_by_id(self, vehicle_id: int) -> Vehicle | None:
        """Return a vehicle by its identifier."""

    def update(self, vehicle: Vehicle) -> Vehicle:
        """Update and return an existing vehicle."""

    def set_availability(self, vehicle_id: int, *, status: str, active: bool) -> Vehicle:
        """Change a vehicle availability state."""


VehicleRepositoryFactory = Callable[[], VehicleRepository]