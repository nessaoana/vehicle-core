"""HTTP controller for vehicles."""

import logging

from fastapi import APIRouter, HTTPException, status

from src.adapters.schemas.vehicle import (
    VehicleAvailabilityRequest,
    VehicleCreateRequest,
    VehicleResponse,
    VehicleUpdateRequest,
)
from src.application.exceptions.vehicle_exceptions import (
    VehicleAlreadyExistsError,
    VehicleNotFoundError,
)
from src.application.use_case.change_vehicle_availability import (
    ChangeVehicleAvailabilityUseCase,
)
from src.application.use_case.create_vehicle import (
    CreateVehicleInput,
    CreateVehicleUseCase,
)
from src.application.use_case.get_vehicle import GetVehicleUseCase
from src.application.use_case.update_vehicle import (
    UpdateVehicleInput,
    UpdateVehicleUseCase,
)


logger = logging.getLogger("vehicle-core")
VEHICLE_NOT_FOUND_DETAIL = "Vehicle not found"


def create_vehicle_router(
    create_use_case: CreateVehicleUseCase,
    get_use_case: GetVehicleUseCase,
    update_use_case: UpdateVehicleUseCase,
    availability_use_case: ChangeVehicleAvailabilityUseCase,
) -> APIRouter:
    """Build the vehicle routes with an injected use case."""

    router = APIRouter(prefix="/vehicles", tags=["vehicles"])

    @router.post("", status_code=status.HTTP_201_CREATED)
    def create_vehicle(payload: VehicleCreateRequest) -> VehicleResponse:
        try:
            vehicle = create_use_case.execute(
                CreateVehicleInput(
                    license_plate=payload.license_plate,
                    brand=payload.brand,
                    model=payload.model,
                    year=payload.year,
                    price=payload.price,
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

    @router.get("/{vehicle_id}")
    def get_vehicle(vehicle_id: int) -> VehicleResponse:
        try:
            return VehicleResponse.model_validate(get_use_case.execute(vehicle_id))
        except VehicleNotFoundError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=VEHICLE_NOT_FOUND_DETAIL) from error

    @router.patch("/{vehicle_id}")
    def update_vehicle(vehicle_id: int, payload: VehicleUpdateRequest) -> VehicleResponse:
        try:
            vehicle = update_use_case.execute(
                vehicle_id,
                UpdateVehicleInput(**payload.model_dump(exclude_unset=True)),
            )
            return VehicleResponse.model_validate(vehicle)
        except VehicleNotFoundError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=VEHICLE_NOT_FOUND_DETAIL) from error
        except VehicleAlreadyExistsError as error:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A vehicle with this license plate already exists.") from error
        except ValueError as error:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error

    @router.patch("/{vehicle_id}/availability", tags=["internal"])
    def change_availability(vehicle_id: int, payload: VehicleAvailabilityRequest) -> VehicleResponse:
        try:
            vehicle = availability_use_case.execute(
                vehicle_id,
                status=payload.status,
                active=payload.active,
            )
            return VehicleResponse.model_validate(vehicle)
        except VehicleNotFoundError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=VEHICLE_NOT_FOUND_DETAIL) from error

    return router