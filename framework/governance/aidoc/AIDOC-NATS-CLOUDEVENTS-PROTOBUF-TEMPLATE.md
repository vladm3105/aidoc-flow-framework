# `.aidoc/` Blueprint: NATS JetStream CloudEvents & Protobuf Wire Contract Standard

## Document Control

| Field | Value |
|---|---|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-10-10 |
| Author | Framework Maintainer |
| Framework Version | 0.96.15 |
| Authority | [RECOMMENDED_PLATFORM_STACK.md](../RECOMMENDED_PLATFORM_STACK.md) & [SPEC_WORKFLOW_STANDARD.md](../../layers/06_SPEC/SPEC_WORKFLOW_STANDARD.md) |

Operational blueprint for specifying asynchronous inter-project message contracts
using **CloudEvents v1.0** envelopes, **Protocol Buffers (Protobuf)** binary wire schemas, and **NATS JetStream** messaging.

---

## 1. Architectural Invariants

1. **Standardized Envelope:** Every asynchronous message MUST be packaged in a **CloudEvents v1.0** compliant envelope.
2. **Binary Wire Contract:** Payloads are serialized using compiled **Protocol Buffers v3** for cross-language type safety, high compression, and backward compatibility.
3. **Idempotency & Deduplication:** Every message published to NATS JetStream MUST set the `Nats-Msg-Id` header to a unique UUIDv7 matching the CloudEvent `id`. Streams enforce deduplication over a rolling window.
4. **Distributed Context Propagation:** Senders MUST propagate the W3C `traceparent` header inside CloudEvents attributes to maintain end-to-end distributed tracing across microservices and agent workers.

---

## 2. CloudEvents Envelope & Protobuf Contract Schema

```protobuf
syntax = "proto3";

package ecosystem.interexchange.v1;

import "google/protobuf/timestamp.proto";
import "google/protobuf/any.proto";

// CloudEvents v1.0 Canonical Envelope
message CloudEventEnvelope {
  // Unique UUIDv7 identifier for message deduplication
  string id = 1;
  
  // URI identifying the originating service or agent (e.g. "urn:service:auth-worker")
  string source = 2;
  
  // Semantic event type name (e.g. "ecosystem.task.v1.TaskCreated")
  string type = 3;
  
  // Subject or resource identifier (e.g. "task/task-1234")
  string subject = 4;
  
  // RFC 3339 event creation timestamp
  google.protobuf.Timestamp time = 5;
  
  // MIME content type (e.g. "application/protobuf" or "application/json")
  string datacontenttype = 6;
  
  // W3C Trace Context traceparent (e.g. "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01")
  string traceparent = 7;
  
  // Concrete typed payload packed as protobuf Any
  google.protobuf.Any data = 8;
  
  // Optional extension attributes
  map<string, string> extensions = 9;
}

// Sample Domain Payload: Agent Task Execution Event
message AgentTaskExecutionEvent {
  string task_id = 1;
  string run_id = 2;
  string project_name = 3;
  string prompt_manifest_id = 4;
  string artifact_uri = 5;
  string content_hash = 6;
}
```

---

## 3. NATS JetStream Stream Definition

When configuring stream subjects in NATS JetStream:

```yaml
stream:
  name: "PROJECT_TASKS"
  subjects:
    - "proj.tasks.*"
  retention: "workqueue"          # or limits for fan-out
  max_consumers: -1
  max_msgs: -1
  max_bytes: 10737418240          # 10 GiB per project stream
  max_age: 604800000000000        # 7 days retention
  storage: "file"
  replicas: 3                     # Clustered across 3 nodes (set replicas: 1 in single-node/dev/CI)
  duplicate_window: 120000000000  # 2-minute deduplication window
```

---

## 4. Layer 06 SPEC Event Contract Specification Example

In a Layer 06 technical specification (`SPEC-NN.yaml`), declare asynchronous event contracts in Section 3:

```yaml
interfaces:
  exports:
    - name: "publish_task_completion"
      type: "async function"
      signature: "async def publish_task_completion(event: AgentTaskExecutionEvent) -> None:"
      description: "Emits task completion CloudEvent to NATS JetStream"

  event_contracts:
    events:
      - name: "TaskExecutionCompleted"
        type: "ecosystem.task.v1.TaskExecutionCompleted"
        envelope_standard: "CloudEvents v1.0"
        schema_format: "Protobuf v3"
        schema_definition: "contracts/interexchange.proto#AgentTaskExecutionEvent"
        nats_subject: "proj.tasks.completed"
        deduplication_key: "id" # Canonical CloudEvents UUIDv7 field (mapped to Nats-Msg-Id on wire)
        trace_propagation: "traceparent"
```

