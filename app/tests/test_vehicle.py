from pydantic import ValidationError
import pytest

from src.domain.entitites.vehicle import Vehicle


def test_vehicle_uses_documented_defaults() -> None:
    vehicle = Vehicle()

    assert vehicle.id is None
    assert vehicle.license_plate == ""
    assert vehicle.status == "available"
    assert vehicle.active is True


def test_vehicle_serializes_its_fields() -> None:
    vehicle = Vehicle(
        license_plate="ABC1D23",
        brand="Toyota",
        model="Corolla",
        year=2024,
        color="Black",
        notes="Single owner",
        status="available",
        active=True,
    )

    assert vehicle.model_dump() == {
        "id": None,
        "license_plate": "ABC1D23",
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2024,
        "color": "Black",
        "notes": "Single owner",
        "status": "available",
        "active": True,
    }


def test_vehicle_rejects_extra_fields_and_mutation() -> None:
    with pytest.raises(ValidationError):
        Vehicle(unknown_field="value")

    vehicle = Vehicle()
    with pytest.raises(ValidationError):
        vehicle.active = False