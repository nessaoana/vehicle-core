import pytest

from src.application.interfaces.vehicle_repository import VehicleSearchFilters
from src.application.use_case.search_vehicles import SearchVehiclesUseCase
from src.domain.entitites.vehicle import Vehicle


class RecordingVehicleRepository:
    def __init__(self) -> None:
        self.received: VehicleSearchFilters | None = None

    def search(self, filters: VehicleSearchFilters) -> list[Vehicle]:
        self.received = filters
        return []


def test_search_vehicles_delegates_filters_to_repository() -> None:
    repository = RecordingVehicleRepository()
    filters = VehicleSearchFilters(status="available", brand="Toyota", min_year=2020, max_year=2024)

    result = SearchVehiclesUseCase(repository).execute(filters)

    assert result == []
    assert repository.received == filters


def test_search_vehicles_rejects_inverted_year_range() -> None:
    repository = RecordingVehicleRepository()

    with pytest.raises(ValueError):
        SearchVehiclesUseCase(repository).execute(VehicleSearchFilters(min_year=2024, max_year=2020))

    assert repository.received is None
