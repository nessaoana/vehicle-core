import json
import logging
from io import StringIO

from src.infra.logging.formatter import LogConfig


def test_logs_are_structured_with_service_context() -> None:
    stream = StringIO()
    logger = LogConfig(
        service_name="vehicle-core-test",
        environment="test",
    ).get_logger()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logger.handlers[0].formatter)
    logger.addHandler(handler)

    try:
        logger.info(
            "vehicle_registered",
            extra={"vehicle_id": 1, "license_plate": "ABC1D23"},
        )
    finally:
        logger.removeHandler(handler)

    record = json.loads(stream.getvalue())
    assert record["message"] == "vehicle_registered"
    assert record["service"] == "vehicle-core-test"
    assert record["environment"] == "test"
    assert record["level"] == "INFO"
    assert record["vehicle_id"] == 1
    assert record["license_plate"] == "ABC1D23"
