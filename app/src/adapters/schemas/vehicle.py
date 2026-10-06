"""HTTP schemas for vehicle registration."""

from pydantic import BaseModel, ConfigDict, Field


class VehicleCreateRequest(BaseModel):
    """Payload accepted by the vehicle registration endpoint."""

    license_plate: str = Field(min_length=1, max_length=10)
    brand: str | None = Field(default=None, max_length=80)
    model: str = Field(min_length=1, max_length=80)
    year: int = Field(ge=1886, le=2100)
    color: str | None = Field(default=None, max_length=40)
    notes: str | None = Field(default=None, max_length=500)


class VehicleResponse(BaseModel):
    """Vehicle returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int | None
    license_plate: str
    brand: str | None
    model: str
    year: int
    color: str | None
    notes: str | None
    status: str | None
    active: bool