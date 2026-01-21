# Headless Tracing (Phoenix)

OpenTelemetry configuration for Agent Observability.

## Setup

1. **Start Phoenix Server** (Background):
   ```bash
   python -m phoenix.server.main serve
   ```
   *UI available at http://localhost:6006*

2. **Instrument Agent**:
   ```python
   from dev_tools.tracing.tracer import instrument
   instrument()
   ```

## Headless Mode
The tracer sends data via OTLP (HTTP). If the server is not running, traces are dropped (or buffered).
For CI/CD, you can run Phoenix in a container or use the ephemeral client.
