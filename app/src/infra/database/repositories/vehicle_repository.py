"""SQLAlchemy implementation of the vehicle persistence port."""

from collections.abc import Callable
import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.application.exceptions.vehicle_exceptions import (
    VehicleAlreadyExistsError,
    VehicleCreationError,
)
from src.domain.entitites.vehicle import Vehicle
from src.infra.database.mappers.vehicle_mapper import VehicleMapper
from src.infra.database.models.vehicle import VehicleModel


logger = logging.getLogger("vehicle-core")


class SqlAlchemyVehicleRepository:
    """Persist vehicles using SQLAlchemy sessions."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def find_by_license_plate(self, license_plate: str) -> Vehicle | None:
        with self._session_factory() as session:
            model = session.query(VehicleModel).filter_by(license_plate=license_plate).first()
            logger.debug(
                "vehicle_lookup_completed",
                extra={"license_plate": license_plate, "found": model is not None},
            )
            return VehicleMapper.to_entity(model) if model else None

    def create(self, vehicle: Vehicle) -> Vehicle:
        with self._session_factory() as session:
            model = VehicleMapper.to_model(vehicle)
            session.add(model)
            try:
                session.commit()
            except IntegrityError as error:
                session.rollback()
                logger.warning(
                    "vehicle_persistence_rejected_duplicate",
                    extra={"license_plate": vehicle.license_plate},
                )
                raise VehicleAlreadyExistsError(vehicle.license_plate) from error
            except Exception as error:
                session.rollback()
                logger.exception(
                    "vehicle_persistence_failed",
                    extra={"license_plate": vehicle.license_plate},
                )
                raise VehicleCreationError from error

            session.refresh(model)
            created_vehicle = VehicleMapper.to_entity(model)
            logger.debug(
                "vehicle_persistence_completed",
                extra={"vehicle_id": created_vehicle.id},
            )
            return created_vehicle
