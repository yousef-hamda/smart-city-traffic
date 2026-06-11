"""OpenTelemetry wiring — active only when an OTLP endpoint is configured.

Local `pytest` runs and ad-hoc `uvicorn` sessions stay silent; inside
docker-compose / Kubernetes the endpoint env var points at Tempo.
"""

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from ai_assistant import __version__
from ai_assistant.config import settings


def setup_telemetry(app: FastAPI) -> None:
    """Install a tracer provider + FastAPI auto-instrumentation when enabled."""
    if not settings.otel_exporter_otlp_endpoint:
        return
    resource = Resource.create(
        {SERVICE_NAME: settings.service_name, SERVICE_VERSION: __version__}
    )
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint))
    )
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
