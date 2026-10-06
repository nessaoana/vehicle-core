from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.domain.factories.vehicle_factory import VehicleFactory
from src.domain.entitites.vehicle import Vehicle
from src.application.exceptions.vehicle_exceptions import (
    VehicleAlreadyExistsError,
    VehicleNotFoundError,
)
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
        price=Decimal("75000.00"),
        color="Black",
        notes=None,
    )

    created = repository.create(vehicle)
    found = repository.find_by_license_plate("ABC1D23")

    assert created.id is not None
    assert found == created


def repository_with_vehicle() -> tuple[SqlAlchemyVehicleRepository, object, int]:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
    repository = SqlAlchemyVehicleRepository(session_factory)
    created = repository.create(
        VehicleFactory.create(
            license_plate="ABC1D23",
            brand="Toyota",
            model="Corolla",
            year=2024,
            price=Decimal("75000.00"),
            color="Black",
            notes=None,
        )
    )
    return repository, engine, created.id


def test_sqlalchemy_repository_updates_and_changes_availability() -> None:
    repository, _, vehicle_id = repository_with_vehicle()
    vehicle = repository.find_by_id(vehicle_id)
    assert vehicle is not None

    updated = repository.update(vehicle.model_copy(update={"price": Decimal("82000.00")}))
    sold = repository.set_availability(vehicle_id, status="sold", active=False)

    assert updated.price == Decimal("82000.00")
    assert sold.status == "sold"
    assert sold.active is False


def test_sqlalchemy_repository_rejects_missing_entities() -> None:
    repository, _, vehicle_id = repository_with_vehicle()
    missing_vehicle = Vehicle(
        id=999,
        license_plate="ZZZ1A23",
        model="Ka",
        year=2020,
        price=Decimal("1000"),
    )
    vehicle_without_id = Vehicle(
        license_plate="ZZZ1A23",
        model="Ka",
        year=2020,
        price=Decimal("1000"),
    )

    assert repository.find_by_id(999) is None
    with pytest.raises(VehicleNotFoundError):
        repository.update(missing_vehicle)
    with pytest.raises(VehicleNotFoundError):
        repository.set_availability(999, status="sold", active=False)
    with pytest.raises(VehicleNotFoundError):
        repository.update(vehicle_without_id)


def test_sqlalchemy_repository_rejects_duplicate_plate() -> None:
    repository, _, _ = repository_with_vehicle()
    duplicate_vehicle = VehicleFactory.create(
        license_plate="ABC1D23",
        brand=None,
        model="Fiesta",
        year=2022,
        price=Decimal("50000.00"),
        color=None,
        notes=None,
    )

    with pytest.raises(VehicleAlreadyExistsError):
        repository.create(duplicate_vehicle)