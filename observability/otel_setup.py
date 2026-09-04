"""Tracer provider wired to Langfuse's OTLP endpoint. If LANGFUSE_HOST/keys
are not set (e.g. before Checkpoint 5), falls back to a no-op tracer so the
rest of the app runs without observability rather than crashing.
"""
import base64
import os

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

_initialized = False


def init_tracing(service_name: str = "agentic-security-lab") -> None:
    global _initialized
    if _initialized:
        return
    _initialized = True

    host = os.environ.get("LANGFUSE_HOST", "")
    public_key = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
    secret_key = os.environ.get("LANGFUSE_SECRET_KEY", "")

    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))

    if host and public_key and secret_key:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        auth = base64.b64encode(f"{public_key}:{secret_key}".encode()).decode()
        exporter = OTLPSpanExporter(
            endpoint=f"{host}/api/public/otel/v1/traces",
            headers={"Authorization": f"Basic {auth}"},
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))

    trace.set_tracer_provider(provider)


def get_tracer():
    init_tracing()
    return trace.get_tracer("agentic-security-lab")
