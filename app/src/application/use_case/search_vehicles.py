"""Use case for searching vehicles."""

from src.application.interfaces.vehicle_repository import (
    VehicleRepository,
    VehicleSearchFilters,
)
from src.domain.entitites.vehicle import Vehicle


class SearchVehiclesUseCase:
    """List vehicles matching optional filters, cheapest first."""

    def __init__(self, repository: VehicleRepository) -> None:
        self._repository = repository

    def execute(self, filters: VehicleSearchFilters) -> list[Vehicle]:
        if (
            filters.min_year is not None
            and filters.max_year is not None
            and filters.min_year > filters.max_year
        ):
            raise ValueError("min_year must be less than or equal to max_year")
        return self._repository.search(filters)
