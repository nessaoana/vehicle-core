"""Application composition root for vehicle-core."""

from collections.abc import Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import Engine, create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from src.adapters.controllers.vehicle_controller import create_vehicle_router
from src.application.interfaces.vehicle_repository import VehicleRepository
from src.application.use_case.change_vehicle_availability import ChangeVehicleAvailabilityUseCase
from src.application.use_case.create_vehicle import CreateVehicleUseCase
from src.application.use_case.get_vehicle import GetVehicleUseCase
from src.application.use_case.update_vehicle import UpdateVehicleUseCase
from src.infra.database.base import Base
from src.infra.database.models import vehicle as _vehicle_model  # noqa: F401
from src.infra.database.repositories.vehicle_repository import (
    SqlAlchemyVehicleRepository,
)
from src.infra.logging.formatter import LogConfig


logger = LogConfig(service_name="vehicle-core", environment="local").get_logger()


def _prepare_schema(engine: Engine) -> None:
    """Create missing tables and columns."""

    Base.metadata.create_all(engine)
    if "vehicles" in inspect(engine).get_table_names():
        columns = {column["name"] for column in inspect(engine).get_columns("vehicles")}
        if "price" not in columns:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE vehicles ADD COLUMN price "
                        "NUMERIC(12, 2) NOT NULL DEFAULT 0"
                    )
                )


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
            try:
                _prepare_schema(engine)
                logger.info("database_schema_ready")
            except SQLAlchemyError as error:
                logger.error("database_schema_failed", extra={"error": str(error)})
            yield

    app = FastAPI(title="vehicle-core", lifespan=lifespan)

    @app.exception_handler(SQLAlchemyError)
    async def database_error_handler(_: Request, error: SQLAlchemyError) -> JSONResponse:
        logger.error("database_request_failed", extra={"error": str(error)})
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Database unavailable."},
        )

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready", tags=["health"])
    def readiness() -> dict[str, str]:
        if session_factory is None:
            return {"status": "ok", "database": "not_configured"}
        try:
            with session_factory() as session:
                session.connection()
        except SQLAlchemyError as error:
            logger.warning("database_readiness_failed", extra={"error": str(error)})
            return {"status": "unavailable", "database": "unavailable"}
        return {"status": "ok", "database": "ok"}

    app.include_router(
        create_vehicle_router(
            CreateVehicleUseCase(repository),
            GetVehicleUseCase(repository),
            UpdateVehicleUseCase(repository),
            ChangeVehicleAvailabilityUseCase(repository),
        )
    )
    return app


app = create_app()