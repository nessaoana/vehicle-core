import pytest

from src.domain.factories.vehicle_factory import VehicleFactory


def test_factory_normalizes_plate_and_applies_registration_defaults() -> None:
    vehicle = VehicleFactory.create(
        license_plate=" abc1d23 ",
        brand=" Toyota ",
        model=" Corolla ",
        year=2024,
        color=" Black ",
        notes=" One owner ",
    )

    assert vehicle.license_plate == "ABC1D23"
    assert vehicle.brand == "Toyota"
    assert vehicle.model == "Corolla"
    assert vehicle.status == "available"
    assert vehicle.active is True


def test_factory_rejects_invalid_registration_data() -> None:
    with pytest.raises(ValueError, match="model"):
        VehicleFactory.create(
            license_plate="ABC1D23",
            brand=None,
            model=" ",
            year=2024,
            color=None,
            notes=None,
        )