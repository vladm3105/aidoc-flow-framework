# `.aidoc/` Blueprint: Temporal + LangGraph Runtime Adapter

## Document Control

| Field | Value |
|---|---|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-10-10 |
| Author | Framework Maintainer |
| Framework Version | 0.96.8 |
| Authority | [RECOMMENDED_PLATFORM_STACK.md](../RECOMMENDED_PLATFORM_STACK.md) & [DURABLE_EXECUTION_STANDARD.md](../DURABLE_EXECUTION_STANDARD.md) |

Operational blueprint for translating declarative SDD Serverless Workflows (`.sw.yaml`)
into durable **Temporal Python Workflows** running **LangGraph Core** reasoning graphs inside plain activities.

---

## 1. Architectural Invariants

1. **Strict 3-Tier Execution Boundary:**
   - **Tier 1 (Temporal Workflow):** Owns state machine transitions, timeout enforcement, durable human gates, and reverse LIFO SAGA compensation. Never calls LLMs directly, never executes non-deterministic code.
   - **Tier 2 (LangGraph in Activity):** Owns non-deterministic reasoning, multi-persona review crews, and planning. Runs strictly inside plain Temporal activities (`@activity.defn`).
   - **Tier 3 (Deterministic Services):** Physical git worktree operations, linters (`sdd_doc_lint`, `swf_lint`), test runners, and forge APIs called as isolated activities.
2. **The History Compression Invariant:**
   A multi-turn LangGraph cognitive reasoning cycle (which may involve 10–20 internal LLM calls and tool evaluations) MUST compress into **exactly one Temporal Activity history event**. The activity returns only compact state tokens, artifact store URIs, and content hashes ($\le 2$ KB) to avoid bloating Temporal workflow history.
3. **Heartbeat Protocol:**
   Every LangGraph step callback MUST emit a heartbeat to the host Temporal activity via `activity.heartbeat()` to prevent activity execution timeouts during deep cognitive loops.
4. **SAGA Compensation Invariant:**
   Compensation activities are registered dynamically in reverse LIFO order as steps execute. Compensations MUST execute deterministically without LLMs in the loop.

---

## 2. CNCF `.sw.yaml` to Temporal Mapping Reference

| CNCF `.sw.yaml` State | Temporal Construct | Execution Details |
|---|---|---|
| `operation` (single action) | `workflow.execute_activity()` | Dispatched to worker task queue with retry policy and timeout budget. |
| `parallel` (concurrent actions) | `asyncio.gather(*[workflow.execute_activity(...)])` | Concurrent fan-out of review personas or validation tasks. |
| `switch` (conditional transition)| Standard Python `if/elif/else` | Evaluates deterministic gate floor returned by Tier 3 activities. |
| `event` (human gate / signal) | `workflow.wait_condition(...)` / `@workflow.signal` | Durable human-in-the-loop approval or rejection pause. |
| `compensatedBy` | `saga.add_compensation(...)` | Registered in LIFO list; executed sequentially on workflow failure. |

---

## 3. Reference Implementation: Temporal + LangGraph Activity Bridge

```python
"""
Runtime implementation template bridging Temporal Workflows with LangGraph Core.
Compatible with Python 3.15 / uv and Temporal Python SDK >= 1.9.0.
"""

from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import Any, Callable, Dict, List
from temporalio import activity, workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError, ApplicationError

# ---------------------------------------------------------------------------
# 1. LangGraph Heartbeat Handler
# ---------------------------------------------------------------------------
class LangGraphTemporalHeartbeatHandler:
    """Callback hook forwarding LangGraph node transitions to Temporal heartbeats."""
    
    def __init__(self, step_name: str) -> None:
        self.step_name = step_name
        self.iteration = 0

    def on_node_end(self, node_name: str, output: Dict[str, Any]) -> None:
        self.iteration += 1
        # Emit heartbeat with current progress details
        activity.heartbeat({
            "step": self.step_name,
            "active_node": node_name,
            "iteration": self.iteration,
        })


# ---------------------------------------------------------------------------
# 2. Tier 2: Cognitive Reasoning Activity (LangGraph Core)
# ---------------------------------------------------------------------------
@activity.defn(name="execute_cognitive_reasoning")
async def execute_cognitive_reasoning(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a LangGraph state graph inside a plain Temporal activity.
    The entire multi-turn conversation compresses to 1 Temporal event.
    """
    task_id = input_data["task_id"]
    prompt_manifest_id = input_data.get("prompt_manifest_id")
    heartbeat_handler = LangGraphTemporalHeartbeatHandler(step_name="review_crew")

    # In practice: build and compile standard LangGraph StateGraph
    # graph = build_review_crew_graph(prompt_manifest_id)
    # result = await graph.ainvoke(input_data, config={"callbacks": [heartbeat_handler]})
    
    # Simulate cyclical reasoning progress
    for step in ["plan", "critique", "synthesize"]:
        await asyncio.sleep(0.1)
        heartbeat_handler.on_node_end(step, {"status": "ok"})

    # Return thin token and artifact URI only (never unbounded prompt history)
    return {
        "status": "APPROVED",
        "score": 95,
        "artifact_uri": f"s3://artifacts/reviews/{task_id}/verdict.json",
        "content_hash": "sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
        "blocking_findings": 0,
    }


# ---------------------------------------------------------------------------
# 3. Tier 3: Deterministic Verification Activity
# ---------------------------------------------------------------------------
@activity.defn(name="verify_quality_floor")
async def verify_quality_floor(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Runs deterministic linters (sdd_doc_lint, swf_lint) and test suites."""
    # Evaluates: (structural_pass == true) and (blocking_findings == 0)
    return {
        "structural_pass": True,
        "blocking_findings": 0,
        "lint_exit_code": 0,
    }


# ---------------------------------------------------------------------------
# 4. SAGA Helper for Reverse LIFO Compensations
# ---------------------------------------------------------------------------
class Saga:
    def __init__(self) -> None:
        self._compensations: List[Callable[[], Any]] = []

    def add_compensation(self, func: Callable[[], Any]) -> None:
        self._compensations.append(func)

    async def compensate(self) -> None:
        """Executes registered compensations in reverse LIFO order."""
        for comp in reversed(self._compensations):
            try:
                await comp()
            except Exception as exc:
                workflow.logger.error(f"SAGA compensation failed: {exc}")


# ---------------------------------------------------------------------------
# 5. Tier 1: Durable Orchestration Workflow
# ---------------------------------------------------------------------------
@workflow.defn
class SddLayerExecutionWorkflow:
    """Orchestrates an SDD layer lifecycle with crash recovery and deterministic safety."""

    @workflow.run
    async def run(self, layer_input: Dict[str, Any]) -> Dict[str, Any]:
        saga = Saga()
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=2),
            backoff_coefficient=2.0,
            maximum_attempts=3,
        )

        try:
            # Step 1: Execute Cognitive Reasoning via LangGraph (Activity)
            cognitive_result = await workflow.execute_activity(
                execute_cognitive_reasoning,
                layer_input,
                start_to_close_timeout=timedelta(minutes=10),
                heartbeat_timeout=timedelta(seconds=30),
                retry_policy=retry_policy,
            )

            # Step 2: Run Deterministic Verification Floor (Activity)
            verification = await workflow.execute_activity(
                verify_quality_floor,
                {"artifact_uri": cognitive_result["artifact_uri"]},
                start_to_close_timeout=timedelta(minutes=2),
                retry_policy=retry_policy,
            )

            # Step 3: Evaluate Gate Floor
            is_valid = (
                verification["structural_pass"]
                and verification["blocking_findings"] == 0
                and cognitive_result["blocking_findings"] == 0
            )

            if not is_valid:
                raise ApplicationError("Quality floor gate failed")

            return {
                "layer_status": "COMPLETED",
                "verdict": cognitive_result["status"],
                "artifact_uri": cognitive_result["artifact_uri"],
            }

        except Exception as exc:
            workflow.logger.error(f"Workflow failed: {exc}. Initiating SAGA rollback...")
            await saga.compensate()
            raise exc
```
