from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
import os

def setup_tracing(endpoint="http://localhost:6006/v1/traces"):
    """
    Configure OpenTelemetry to send traces to Phoenix.
    """
    resource = None # Default resource
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)
    
    # OTLP Exporter (HTTP)
    span_exporter = OTLPSpanExporter(endpoint=endpoint)
    
    # Batch Processor
    span_processor = BatchSpanProcessor(span_exporter)
    tracer_provider.add_span_processor(span_processor)
    
    print(f"Tracing enabled. Sends to {endpoint}")
    return tracer_provider

def instrument():
    """Auto-instrument known libraries (LlamaIndex, LangChain, etc)"""
    # In a real agent, you'd use specific instrumentors.
    # For now, we just setup the provider.
    setup_tracing()

if __name__ == "__main__":
    # Test Tracer
    setup_tracing()
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("test_span") as span:
        span.set_attribute("test", "true")
        print("Generated test span.")
