# Agent Development Tools

This directory contains a suite of tools designed to support the full lifecycle of AI Agent development, from mocking and testing to safety and debugging.

## 🛠️ Tool Index

### 1. Mocking & Simulation
*Tools to simulate the environment for agents.*

- **[Mock MCP Server](mcp/README.md)**: Simulates Model Context Protocol (MCP) tools via Stdio.
- **[Mock A2A Server](a2a/README.md)**: Simulates Agent-to-Agent interactions via HTTP/REST.
- **[Event Replay](event_replay/README.md)**: Replays historical data feeds (CSV/JSONL) with time-based simulation.

### 2. Testing & Evaluation (CI/CD)
*Tools to verify agent behavior automatically.*

- **[Agent Evaluator](evaluator/README.md)**: "LLM-as-a-Judge" semantic unit testing (powered by Promptfoo).
- **[Chaos Proxy](chaos_proxy/README.md)**: Network fault injection proxy (latency, errors) to test resilience.

### 3. Observability & Debugging
*Tools to understand what the agent is thinking.*

- **[Log Analyzer](log_analyzer/README.md)**: CLI to parse logs and calculate token usage/costs.
- **[Context Viewer](context_viewer/README.md)**: Web UI to inspect and debug raw agent prompt contexts.
- **[Headless Tracing](tracing/README.md)**: OpenTelemetry configuration for visual tracing (Arize Phoenix).

### 4. Safety & Security
*Tools to ensure agent outputs are safe.*

- **[Runtime Validator](safety/README.md)**: Pydantic-based runtime validation for structured outputs (JSON/Regex).

### 5. Manual Inspection
*Human-in-the-loop tools.*

- **[Human Inspector](inspector/README.md)**: Interactive REPL to pause automation and allow manual state modification (Breakpoints).

## 🚀 Quick Start

Most tools are Python-based and use `pyproject.toml`.

```bash
# Example: Using the Log Analyzer
cd log_analyzer
uv pip install -e .
python analyzer.py --help
```
