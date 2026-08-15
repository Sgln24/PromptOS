from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from litellm import litellm

def setup_telemetry(app):
    # Setup OpenTelemetry Tracer
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
    
    # Instrument LiteLLM (Built-in OpenTelemetry support)
    litellm.success_callback = ["otel"]
    litellm.failure_callback = ["otel"]