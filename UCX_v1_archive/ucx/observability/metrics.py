"""OpenTelemetry metrics for UCX operations.

Provides counters, histograms, and gauges for monitoring UCX performance.
"""

from typing import Optional

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.metrics import Counter, Histogram, Meter

# Global metrics instance
_metrics: Optional["UCXMetrics"] = None
_provider: Optional[MeterProvider] = None


class UCXMetrics:
    """
    UCX metrics collection using OpenTelemetry.

    Provides counters, histograms, and gauges for:
    - LLM operations (tokens, latency, errors)
    - Document processing (create, review, remediate)
    - Validation results
    - Drift detection
    """

    def __init__(self, meter: Meter) -> None:
        """
        Initialize UCX metrics.

        Args:
            meter: OpenTelemetry meter instance
        """
        self._meter = meter

        # LLM Metrics
        self.llm_requests = meter.create_counter(
            name="ucx.llm.requests",
            description="Number of LLM API requests",
            unit="1",
        )
        self.llm_tokens_input = meter.create_counter(
            name="ucx.llm.tokens.input",
            description="Total input tokens sent to LLM",
            unit="tokens",
        )
        self.llm_tokens_output = meter.create_counter(
            name="ucx.llm.tokens.output",
            description="Total output tokens received from LLM",
            unit="tokens",
        )
        self.llm_latency = meter.create_histogram(
            name="ucx.llm.latency",
            description="LLM request latency",
            unit="ms",
        )
        self.llm_errors = meter.create_counter(
            name="ucx.llm.errors",
            description="Number of LLM API errors",
            unit="1",
        )

        # Document Processing Metrics
        self.documents_created = meter.create_counter(
            name="ucx.documents.created",
            description="Number of documents created",
            unit="1",
        )
        self.documents_reviewed = meter.create_counter(
            name="ucx.documents.reviewed",
            description="Number of documents reviewed",
            unit="1",
        )
        self.documents_remediated = meter.create_counter(
            name="ucx.documents.remediated",
            description="Number of documents remediated",
            unit="1",
        )
        self.document_processing_time = meter.create_histogram(
            name="ucx.documents.processing_time",
            description="Document processing time",
            unit="ms",
        )

        # Validation Metrics
        self.validation_runs = meter.create_counter(
            name="ucx.validation.runs",
            description="Number of validation runs",
            unit="1",
        )
        self.validation_errors = meter.create_counter(
            name="ucx.validation.errors",
            description="Number of validation errors found",
            unit="1",
        )
        self.validation_score = meter.create_histogram(
            name="ucx.validation.score",
            description="Validation scores",
            unit="1",
        )

        # Drift Metrics
        self.drift_checks = meter.create_counter(
            name="ucx.drift.checks",
            description="Number of drift checks performed",
            unit="1",
        )
        self.drift_detected = meter.create_counter(
            name="ucx.drift.detected",
            description="Number of drift detections",
            unit="1",
        )

        # Autopilot Metrics
        self.autopilot_runs = meter.create_counter(
            name="ucx.autopilot.runs",
            description="Number of autopilot runs",
            unit="1",
        )
        self.autopilot_iterations = meter.create_histogram(
            name="ucx.autopilot.iterations",
            description="Number of iterations per autopilot run",
            unit="1",
        )
        self.autopilot_success = meter.create_counter(
            name="ucx.autopilot.success",
            description="Number of successful autopilot runs",
            unit="1",
        )
        self.autopilot_failure = meter.create_counter(
            name="ucx.autopilot.failure",
            description="Number of failed autopilot runs",
            unit="1",
        )

    def record_llm_request(
        self,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float,
        model: str,
        phase: str,
        success: bool = True,
    ) -> None:
        """
        Record an LLM request with all metrics.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            latency_ms: Request latency in milliseconds
            model: Model name (opus, sonnet, haiku)
            phase: UCX phase (ucc, ucr, ucrem)
            success: Whether the request succeeded
        """
        attributes = {"model": model, "phase": phase}

        self.llm_requests.add(1, attributes)
        self.llm_tokens_input.add(input_tokens, attributes)
        self.llm_tokens_output.add(output_tokens, attributes)
        self.llm_latency.record(latency_ms, attributes)

        if not success:
            self.llm_errors.add(1, attributes)

    def record_document_created(self, doc_type: str, duration_ms: float) -> None:
        """Record a document creation."""
        attributes = {"doc_type": doc_type}
        self.documents_created.add(1, attributes)
        self.document_processing_time.record(duration_ms, attributes)

    def record_document_reviewed(
        self, doc_type: str, score: int, duration_ms: float
    ) -> None:
        """Record a document review."""
        attributes = {"doc_type": doc_type}
        self.documents_reviewed.add(1, attributes)
        self.document_processing_time.record(duration_ms, attributes)
        self.validation_score.record(score, attributes)

    def record_validation(
        self, doc_type: str, error_count: int, score: int
    ) -> None:
        """Record a validation run."""
        attributes = {"doc_type": doc_type}
        self.validation_runs.add(1, attributes)
        self.validation_errors.add(error_count, attributes)
        self.validation_score.record(score, attributes)

    def record_drift_check(self, doc_type: str, drift_found: bool) -> None:
        """Record a drift check."""
        attributes = {"doc_type": doc_type}
        self.drift_checks.add(1, attributes)
        if drift_found:
            self.drift_detected.add(1, attributes)

    def record_autopilot_run(
        self,
        doc_type: str,
        iterations: int,
        success: bool,
        final_score: int,
    ) -> None:
        """Record an autopilot run."""
        attributes = {"doc_type": doc_type}
        self.autopilot_runs.add(1, attributes)
        self.autopilot_iterations.record(iterations, attributes)

        if success:
            self.autopilot_success.add(1, attributes)
        else:
            self.autopilot_failure.add(1, attributes)


def setup_metrics(
    service_name: str = "ucx",
    service_version: str = "1.0.0",
    endpoint: Optional[str] = None,
    console_export: bool = False,
) -> MeterProvider:
    """
    Initialize OpenTelemetry metrics.

    Args:
        service_name: Name of the service
        service_version: Version of the service
        endpoint: OTLP exporter endpoint
        console_export: Export metrics to console

    Returns:
        Configured MeterProvider
    """
    global _provider

    if _provider is not None:
        return _provider

    resource = Resource.create({
        SERVICE_NAME: service_name,
        SERVICE_VERSION: service_version,
    })

    readers = []

    # Add console exporter for debugging
    if console_export:
        console_reader = PeriodicExportingMetricReader(
            ConsoleMetricExporter(),
            export_interval_millis=10000,
        )
        readers.append(console_reader)

    # Add OTLP exporter if configured
    if endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
                OTLPMetricExporter,
            )

            otlp_reader = PeriodicExportingMetricReader(
                OTLPMetricExporter(endpoint=endpoint),
                export_interval_millis=10000,
            )
            readers.append(otlp_reader)
        except ImportError:
            pass

    _provider = MeterProvider(resource=resource, metric_readers=readers)
    metrics.set_meter_provider(_provider)

    return _provider


def get_metrics(service_name: str = "ucx") -> UCXMetrics:
    """
    Get the UCX metrics instance.

    Args:
        service_name: Service name for the meter

    Returns:
        UCXMetrics instance
    """
    global _metrics

    if _metrics is None:
        meter = metrics.get_meter(service_name, "1.0.0")
        _metrics = UCXMetrics(meter)

    return _metrics
