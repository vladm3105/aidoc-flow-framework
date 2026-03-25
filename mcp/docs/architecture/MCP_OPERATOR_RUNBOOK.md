# MCP Operator Runbook

| Field | Value |
| --- | --- |
| Status | Active |
| Version | 1.0 |
| Date | 2026-03-24 |
| Scope | Operational procedures and troubleshooting for mcp init, create-build, and review-build |

---

## 1. Purpose

Provide deterministic operational procedures for MCP command execution and failure handling.

Implementation complexity: 3/5.

---

## 2. Preconditions

- Runtime environment can execute mcp CLI command.
- Project path is available and writable for output operations.
- For create-build and review-build, project contains project-local docs/UCX assets or operator has permission to run init.

---

## 3. Standard Operating Procedures

### 3.1 Initialize project assets

Procedure:
1. Run mcp init with project path.
2. Confirm output reports created and skipped counts.
3. Verify required directories exist under docs/UCX.

Success condition:
- docs/UCX structure exists and command returns successful exit.

### 3.2 Create-build with sections payload

Procedure:
1. Prepare sections-json file with required fields.
2. Run create-build with project, persona, doc-type, layer, template, sections-json, and out.
3. Confirm creation prompt artifacts are present in output directory.
4. Review inspection output for warnings.

Success condition:
- creation_prompt.txt and sidecar artifacts are present.

### 3.3 Create-build without sections payload

Procedure:
1. Run create-build without sections-json argument.
2. Confirm command completes and writes output artifacts.
3. Validate prompt output includes expected template and layer assets.

Constraint:
- This mode does not provide direct markdown ingestion semantics.

### 3.4 Review-build

Procedure:
1. Prepare sections-json payload.
2. Run review-build with required arguments.
3. Confirm review prompt, sidecar, and inspection artifacts are written.

Success condition:
- review artifacts exist and inspection is parseable JSON.

---

## 4. Troubleshooting Scenarios

### Scenario A: sections-json provided

Expected behavior:
- Source sections are loaded from payload and mapped into prompt context.

Troubleshooting checks:
- Validate payload JSON syntax and required keys.
- Validate file path readability.

### Scenario B: sections-json omitted for create-build

Expected behavior:
- Command runs with internal fallback section behavior.

Troubleshooting checks:
- Confirm command invocation did not include malformed sections-json flag.
- Inspect resulting prompt for fallback section presence.

### Scenario C: missing project UCX path

Error indicator:
- ProjectSkillsNotFound

Resolution:
1. Run mcp init --project path
2. Re-run failed command

---

## 5. Failure Modes and Responses

| Failure Mode | Detection | Response |
| --- | --- | --- |
| ProjectSkillsNotFound | command error payload includes missing_paths | run init, then retry |
| Invalid sections-json payload | parser or deserialization error | correct payload and retry |
| Missing template or persona | loader error via missing path | add required file under docs/UCX and retry |
| Output write failure | file I/O error | validate output directory permissions |

---

## 6. Escalation Criteria

Escalate to runtime maintainer when:
- ContractValidationError persists after input correction.
- Repeated command failures occur with valid payload and valid project UCX structure.
- Output artifacts are produced but sidecar schema appears malformed.
