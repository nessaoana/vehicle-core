"""Factories for creating valid vehicle aggregates."""

from decimal import Decimal

from src.domain.entitites.vehicle import Vehicle
from src.domain.validators.license_plate import normalize_license_plate


class VehicleFactory:
    """Create vehicles with the defaults required for a new registration."""

    @staticmethod
    def create(
        *,
        license_plate: str,
        brand: str | None,
        model: str,
        year: int,
        price: Decimal,
        color: str | None,
        notes: str | None,
    ) -> Vehicle:
        normalized_plate = normalize_license_plate(license_plate)
        normalized_model = model.strip()

        if not normalized_model:
            raise ValueError("Vehicle model is required")
        if year < 1886 or year > 2100:
            raise ValueError("Vehicle year must be between 1886 and 2100")
        if price <= 0:
            raise ValueError("Vehicle price must be greater than zero")

        return Vehicle(
            license_plate=normalized_plate,
            brand=brand.strip() if brand else None,
            model=normalized_model,
            year=year,
            price=price,
            color=color.strip() if color else None,
            notes=notes.strip() if notes else None,
        )