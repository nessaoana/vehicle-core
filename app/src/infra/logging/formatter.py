"""Structured logging configuration for the application."""

import logging

from ddtrace import tracer
from pythonjsonlogger import jsonlogger


class DatadogJsonFormatter(jsonlogger.JsonFormatter):
    """Adds service and trace metadata to JSON log records."""

    def __init__(self, service_name: str, environment: str) -> None:
        super().__init__()
        self.service_name = service_name
        self.environment = environment

    def add_fields(self, log_record, record, message_dict) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record["service"] = self.service_name
        log_record["environment"] = self.environment
        log_record["level"] = record.levelname

        span = tracer.current_span()
        if span is not None:
            log_record["dd.trace_id"] = span.trace_id
            log_record["dd.span_id"] = span.span_id


class DatadogLogConfig:
    """Creates the application logger with JSON output."""

    def __init__(self, service_name: str, environment: str) -> None:
        self.service_name = service_name
        self.environment = environment
        self.logger: logging.Logger | None = None

    def configure(self) -> logging.Logger:
        logger = logging.getLogger(self.service_name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                DatadogJsonFormatter(self.service_name, self.environment)
            )
            logger.addHandler(handler)

        self.logger = logger
        return logger

    def get_logger(self) -> logging.Logger:
        """Returns the configured logger, creating it on first use."""
        return self.logger or self.configure()
