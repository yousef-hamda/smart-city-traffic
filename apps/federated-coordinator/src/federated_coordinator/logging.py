"""Structured JSON logging via structlog, with OTel trace correlation.

Every log line carries the service name plus ``trace_id``/``span_id`` when an
active span exists, so Loki lines can be pivoted to Tempo traces in Grafana.
"""

import logging

import structlog
from opentelemetry import trace
from structlog.types import EventDict, WrappedLogger

from federated_coordinator.config import settings


def _add_trace_context(
    _logger: WrappedLogger, _name: str, event_dict: EventDict
) -> EventDict:
    span = trace.get_current_span()
    ctx = span.get_span_context()
    if ctx.is_valid:
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")
    return event_dict


def configure_logging() -> None:
    """Configure stdlib + structlog to emit one JSON object per line."""
    logging.basicConfig(level=settings.log_level, format="%(message)s")
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            _add_trace_context,
            structlog.processors.EventRenamer("message"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level)
        ),
        cache_logger_on_first_use=True,
    )
    structlog.contextvars.bind_contextvars(service=settings.service_name)
