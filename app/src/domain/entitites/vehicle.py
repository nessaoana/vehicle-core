"""Domain entity for a vehicle."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class Vehicle(BaseModel):
    """Representa um veículo de negócio sem preocupações de persistência."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: int | None = Field(default=None, description="Unique vehicle identifier.")
    license_plate: str = Field(default="", description="Vehicle license plate.")
    brand: str | None = Field(default=None, description="Vehicle brand. Ex: Fiat, Ford, Toyota.")
    model: str = Field(default="", description="Vehicle model name.")
    year: int = Field(default=0, description="Vehicle manufacturing year.")
    price: Decimal = Field(default=Decimal("0.00"), description="Vehicle sale price.")
    color: str | None = Field(default=None, description="Vehicle exterior color.")
    notes: str | None = Field(default=None, description="Additional vehicle notes.")
    status: str | None = Field(default="available", description="Current vehicle status.")
    active: bool = Field(default=True, description="Whether the vehicle is active.")
