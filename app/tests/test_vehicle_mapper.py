from decimal import Decimal

from src.domain.factories.vehicle_factory import VehicleFactory
from src.infra.database.mappers.vehicle_mapper import VehicleMapper


def test_vehicle_mapper_converts_domain_entity_to_model_and_back() -> None:
    vehicle = VehicleFactory.create(
        license_plate="ABC1D23",
        brand="Toyota",
        model="Corolla",
        year=2024,
        price=Decimal("75000.00"),
        color="Black",
        notes="One owner",
    )

    model = VehicleMapper.to_model(vehicle)
    model.id = 10
    converted_vehicle = VehicleMapper.to_entity(model)

    assert model.license_plate == vehicle.license_plate
    assert converted_vehicle.id == 10
    assert converted_vehicle == vehicle.model_copy(update={"id": 10})