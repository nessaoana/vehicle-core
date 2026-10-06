"""HTTP schemas for vehicle registration."""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.domain.validators.license_plate import normalize_license_plate


class VehicleCreateRequest(BaseModel):
    """Payload accepted by the vehicle registration endpoint."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "license_plate": "ABC1D23",
                    "brand": "Toyota",
                    "model": "Corolla",
                    "year": 2024,
                    "price": "75000.00",
                    "color": "Black",
                    "notes": "Single owner",
                }
            ]
        }
    )

    license_plate: str = Field(min_length=1, max_length=10)
    brand: str | None = Field(default=None, max_length=80)
    model: str = Field(min_length=1, max_length=80)
    year: int = Field(ge=1886, le=2100)
    price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    color: str | None = Field(default=None, max_length=40)
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("license_plate")
    @classmethod
    def validate_license_plate(cls, value: str) -> str:
        return normalize_license_plate(value)


class VehicleResponse(BaseModel):
    """Vehicle returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int | None
    license_plate: str
    brand: str | None
    model: str
    year: int
    price: Decimal
    color: str | None
    notes: str | None
    status: str | None
    active: bool


class VehicleUpdateRequest(BaseModel):
    """Payload for partial vehicle updates."""

    license_plate: str | None = Field(default=None, min_length=1, max_length=10)
    brand: str | None = Field(default=None, max_length=80)
    model: str | None = Field(default=None, min_length=1, max_length=80)
    year: int | None = Field(default=None, ge=1886, le=2100)
    price: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    color: str | None = Field(default=None, max_length=40)
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("license_plate")
    @classmethod
    def validate_update_license_plate(cls, value: str | None) -> str | None:
        return normalize_license_plate(value) if value is not None else None


class VehicleAvailabilityRequest(BaseModel):
    """Internal request to update vehicle availability."""

    status: Literal["available", "sold"]
    active: bool