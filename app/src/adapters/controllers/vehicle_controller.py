"""HTTP controller for vehicles."""

import logging

from fastapi import APIRouter, HTTPException, status

from src.adapters.schemas.vehicle import VehicleCreateRequest, VehicleResponse
from src.application.exceptions.vehicle_exceptions import VehicleAlreadyExistsError
from src.application.use_case.create_vehicle import (
    CreateVehicleInput,
    CreateVehicleUseCase,
)


logger = logging.getLogger("vehicle-core")


def create_vehicle_router(use_case: CreateVehicleUseCase) -> APIRouter:
    """Build the vehicle routes with an injected use case."""

    router = APIRouter(prefix="/vehicles", tags=["vehicles"])

    @router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
    def create_vehicle(payload: VehicleCreateRequest) -> VehicleResponse:
        try:
            vehicle = use_case.execute(
                CreateVehicleInput(
                    license_plate=payload.license_plate,
                    brand=payload.brand,
                    model=payload.model,
                    year=payload.year,
                    color=payload.color,
                    notes=payload.notes,
                )
            )
        except VehicleAlreadyExistsError as error:
            logger.warning(
                "vehicle_registration_conflict",
                extra={"license_plate": payload.license_plate.strip().upper()},
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A vehicle with this license plate already exists.",
            ) from error
        except ValueError as error:
            logger.info(
                "vehicle_registration_rejected_invalid_data",
                extra={"license_plate": payload.license_plate.strip().upper()},
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(error),
            ) from error

        response = VehicleResponse.model_validate(vehicle)
        logger.info(
            "vehicle_registration_response",
            extra={"vehicle_id": response.id, "status_code": status.HTTP_201_CREATED},
        )
        return response

    return router