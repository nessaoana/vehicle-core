"""Application exceptions related to vehicle registration."""


class VehicleAlreadyExistsError(Exception):
    """Raised when a vehicle with the same license plate already exists."""


class VehicleCreationError(Exception):
    """Raised when persistence fails while creating a vehicle."""


class VehicleNotFoundError(Exception):
    """Raised when a requested vehicle does not exist."""