from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.domain.factories.vehicle_factory import VehicleFactory
from src.infra.database.base import Base
from src.infra.database.repositories.vehicle_repository import (
    SqlAlchemyVehicleRepository,
)


def test_sqlalchemy_repository_persists_and_reads_vehicle() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
    repository = SqlAlchemyVehicleRepository(session_factory)
    vehicle = VehicleFactory.create(
        license_plate="ABC1D23",
        brand="Toyota",
        model="Corolla",
        year=2024,
        color="Black",
        notes=None,
    )

    created = repository.create(vehicle)
    found = repository.find_by_license_plate("ABC1D23")

    assert created.id is not None
    assert found == created