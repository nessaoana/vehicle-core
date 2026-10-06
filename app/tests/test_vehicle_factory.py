import pytest
from decimal import Decimal

from src.domain.factories.vehicle_factory import VehicleFactory


def test_factory_normalizes_plate_and_applies_registration_defaults() -> None:
    vehicle = VehicleFactory.create(
        license_plate=" abc-1d23 ",
        brand=" Toyota ",
        model=" Corolla ",
        year=2024,
        price=Decimal("75000.00"),
        color=" Black ",
        notes=" One owner ",
    )

    assert vehicle.license_plate == "ABC1D23"
    assert vehicle.brand == "Toyota"
    assert vehicle.model == "Corolla"
    assert vehicle.status == "available"
    assert vehicle.active is True


@pytest.mark.parametrize("license_plate", ["ABC-1234", "ABC1234", "ABC1D23"])
def test_factory_accepts_brazilian_license_plate_formats(license_plate: str) -> None:
    vehicle = VehicleFactory.create(
        license_plate=license_plate,
        brand=None,
        model="Corolla",
        year=2024,
        price=Decimal("75000.00"),
        color=None,
        notes=None,
    )

    assert vehicle.license_plate in {"ABC1234", "ABC1D23"}


def test_factory_rejects_invalid_license_plate() -> None:
    price = Decimal("75000.00")

    with pytest.raises(ValueError, match="Brazilian format"):
        VehicleFactory.create(
            license_plate="INVALID",
            brand=None,
            model="Corolla",
            year=2024,
            price=price,
            color=None,
            notes=None,
        )


def test_factory_rejects_invalid_registration_data() -> None:
    price = Decimal("75000.00")

    with pytest.raises(ValueError, match="model"):
        VehicleFactory.create(
            license_plate="ABC1D23",
            brand=None,
            model=" ",
            year=2024,
            price=price,
            color=None,
            notes=None,
        )