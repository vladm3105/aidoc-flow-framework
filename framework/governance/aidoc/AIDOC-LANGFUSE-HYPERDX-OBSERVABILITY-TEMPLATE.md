# `.aidoc/` Blueprint: Langfuse Prompt CMS & HyperDX Observability Standard

## Document Control

| Field | Value |
|---|---|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-10-10 |
| Author | Framework Maintainer |
| Framework Version | 0.96.7 |
| Authority | [RECOMMENDED_PLATFORM_STACK.md](../RECOMMENDED_PLATFORM_STACK.md) & [ENGINE_TELEMETRY.md](../ENGINE_TELEMETRY.md) |

Operational blueprint for managing prompt manifests, LLM-as-a-judge evaluation datasets,
and distributed tracing pipelines across **Langfuse**, **HyperDX**, and **OpenTelemetry Collector Contrib**.

---

## 1. Architectural Invariants

1. **Prompt Manifest Immutability:**
   Prompts are never hardcoded in source files or passed as raw strings in workflow state. Workflows accept a `prompt_manifest_id` and optional version pin. Activities resolve prompt text dynamically from Langfuse Prompt CMS with local cache fallbacks.
2. **Unified Distributed Tracing:**
   Every workflow execution generates a root W3C `traceparent` header. This identifier propagates across HTTP calls, NATS CloudEvents, and Temporal activities, allowing operators to join infrastructure logs in **HyperDX** with prompt executions in **Langfuse** in a single ClickHouse SQL query.
3. **Zero Raw Content in Telemetry Spans:**
   OpenTelemetry spans sent to the central collector MUST NOT carry raw prompt text, user code diffs, or secrets. Spans carry token counts, model names, latency, cost microcents, and artifact store URIs only.

---

## 2. Dynamic Prompt Resolution Pattern (Python 3.15)

```python
"""
Langfuse Prompt CMS Client with In-Memory TTL Cache.
Ensures zero runtime failure if Langfuse is temporarily unreachable.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional
from langfuse import Langfuse

class PromptRegistry:
    def __init__(self, host: str, public_key: str, secret_key: str) -> None:
        self._client = Langfuse(host=host, public_key=public_key, secret_key=secret_key)
        self._cache: Dict[str, tuple[str, float]] = {}
        self._ttl_seconds = 300.0  # 5-minute local cache

    def get_prompt(self, name: str, version: Optional[int] = None) -> str:
        cache_key = f"{name}:{version or 'latest'}"
        now = time.time()

        if cache_key in self._cache:
            content, expiry = self._cache[cache_key]
            if now < expiry:
                return content

        try:
            prompt_obj = self._client.get_prompt(name=name, version=version)
            content = prompt_obj.compile()
            self._cache[cache_key] = (content, now + self._ttl_seconds)
            return content
        except Exception as exc:
            # Fallback to expired cache if network is down
            if cache_key in self._cache:
                return self._cache[cache_key][0]
            raise RuntimeError(f"Failed to fetch prompt '{name}': {exc}")
```

---

## 3. Layer 10 EVAL Dataset Benchmark Runner

```python
"""
Automated evaluation test runner integrating Layer 10 EVAL with Langfuse Datasets.
"""

from typing import Any, Dict
from langfuse import Langfuse

async def run_layer_10_eval(
    dataset_name: str,
    eval_model_alias: str,
    langfuse_client: Langfuse
) -> Dict[str, Any]:
    dataset = langfuse_client.get_dataset(dataset_name)
    total_items = len(dataset.items)
    passed_items = 0

    for item in dataset.items:
        # Run test case through candidate agent
        actual_output = await execute_candidate_agent(item.input)
        
        # Evaluate using LLM-as-a-Judge
        score = evaluate_criterion(
            expected=item.expected_output,
            actual=actual_output,
            model=eval_model_alias
        )

        # Record evaluation score back to Langfuse item
        item.link(actual_output.trace_id)
        langfuse_client.score(
            trace_id=actual_output.trace_id,
            name="accuracy",
            value=score.value,
            comment=score.rationale
        )

        if score.value >= 0.90:
            passed_items += 1

    accuracy_rate = passed_items / max(1, total_items)
    return {
        "dataset": dataset_name,
        "total_cases": total_items,
        "accuracy_rate": accuracy_rate,
        "gate_pass": accuracy_rate >= 0.95,
    }
```

---

## 4. OpenTelemetry Collector Contrib Configuration Snippet

In `otelcol-contrib.yaml`, stream `gen_ai.*` spans to ClickHouse and Langfuse:

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024
  
  # Content Sanitization Rule D14 (Strip sensitive prompt text from spans)
  transform:
    error_mode: ignore
    log_statements:
      - context: log
        statements:
          - replace_pattern(body, "Bearer [a-zA-Z0-9_.-]+", "Bearer [REDACTED]")
    trace_statements:
      - context: span
        statements:
          - delete_key(attributes, "gen_ai.prompt.content")
          - delete_key(attributes, "gen_ai.completion.content")

exporters:
  clickhouse:
    endpoint: "tcp://clickhouse:9000?database=hyperdx"
    table: "otel_traces"
    connection_timeout: 5s

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [transform, batch]
      exporters: [clickhouse]
```
