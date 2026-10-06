"""Application composition root for vehicle-core."""

from collections.abc import Callable
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.adapters.controllers.vehicle_controller import create_vehicle_router
from src.application.interfaces.vehicle_repository import VehicleRepository
from src.application.use_case.create_vehicle import CreateVehicleUseCase
from src.infra.database.base import Base
from src.infra.database.models import vehicle as _vehicle_model  # noqa: F401
from src.infra.database.repositories.vehicle_repository import (
    SqlAlchemyVehicleRepository,
)
from src.infra.logging.formatter import LogConfig


logger = LogConfig(service_name="vehicle-core", environment="local").get_logger()


def create_app(repository: VehicleRepository | None = None) -> FastAPI:
    """Create the API with either a real or test repository."""

    lifespan = None
    session_factory: Callable[[], Session] | None = None

    if repository is None:
        from src.infra.settings import settings

        engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
        session_factory = sessionmaker(bind=engine, expire_on_commit=False)
        repository = SqlAlchemyVehicleRepository(session_factory)

        @asynccontextmanager
        async def lifespan(_: FastAPI):
            Base.metadata.create_all(engine)
            logger.info("database_schema_ready")
            yield

    app = FastAPI(title="vehicle-core", lifespan=lifespan)
    app.include_router(create_vehicle_router(CreateVehicleUseCase(repository)))
    return app


app = create_app()