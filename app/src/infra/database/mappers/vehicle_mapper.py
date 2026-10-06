"""Convert vehicles between the domain and SQLAlchemy representations."""

from src.domain.entitites.vehicle import Vehicle
from src.infra.database.models.vehicle import VehicleModel


class VehicleMapper:
    """Keep persistence details out of the vehicle domain entity."""

    @staticmethod
    def to_model(vehicle: Vehicle) -> VehicleModel:
        """Convert a domain vehicle into a persistence model."""
        model_data = vehicle.model_dump(exclude={"id"})
        if vehicle.id is not None:
            model_data["id"] = vehicle.id
        return VehicleModel(**model_data)

    @staticmethod
    def to_entity(model: VehicleModel) -> Vehicle:
        """Convert a persistence model into a domain vehicle."""
        return Vehicle.model_validate(model, from_attributes=True)