# SPEC-001: MCP Core Architecture and Workflow Contracts

| Field | Value |
| --- | --- |
| Canonical ID | SPEC-001 |
| Status | Active |
| Version | 1.3 |
| Date | 2026-03-24 |
| Source Basis | Canonical normative specification |
| Scope | Core MCP architecture, namespace policy, lifecycle workflow, tool output contracts |

---

## 1. Purpose

Define normative contracts for MCP server architecture, namespace compliance, artifact lifecycle, and stage workflow execution.

Implementation complexity: 4/5.

---

## 2. Scope and Boundaries

In scope:
- Layer tool namespace model.
- Strict alias model for cross-layer tools.
- Global tool response envelope.
- Validation, review, remediation lifecycle contracts.
- Artifact immutability and derived-artifact policy.
- Stage sequence ownership and transition semantics.
- Source eligibility and upstream-missing execution policy.

Out of scope:
- Feature-specific scoring formulas.
- Multi-persona prompt internals (persona list resolution and `persona_mappings.yaml`).
- Hash identity generation algorithms.
- Detailed creation-template contracts.
- Detailed report naming and version allocation rules.

---

## 3. Normative Namespace Contracts

### 3.1 Layer Prefix Contract

All layer tools must use one of these prefixes:
- brd
- prd
- ears
- bdd
- adr
- sys
- req
- ctr
- spec
- tspec
- tasks

### 3.2 Cross-layer Canonical Namespaces

Canonical cross-layer namespaces:
- trace
- matrix
- code
- tests
- workflow
- report

### 3.3 Strict Alias Contract (Mandatory)

For each cross-layer tool named {cross_tool_name}, server must expose aliases:
- {layer}_{cross_tool_name} for every layer prefix in 3.1.

Required behavior:
- Canonical cross-layer name remains callable.
- Alias resolves to canonical implementation.
- Response includes canonical tool identity and alias_invoked metadata.

Failure mode:
- Missing alias for any layer is a compliance failure.

---

## 4. Tool Response Contract (Mandatory)

All tools must return:
- status: ok|warning|error
- tool
- layer
- path
- findings
- metrics
- artifacts
- next_step

### 4.1 Finding Contract

Finding minimum fields:
- finding_id
- severity
- code
- message
- location
- actionable

Severity domain:
- P0
- P1
- P2
- P3

Failure mode:
- Missing required field is contract-invalid output.

---

## 5. Lifecycle and Workflow Contracts

### 5.1 Required Stage Sequence

For layers implementing the full workflow:
1. {layer}_validate
2. {layer}_validate_fix
3. {layer}_review
4. {layer}_remediate_content
5. {layer}_remediate_apply

### 5.2 Supporting Stage Tools

Mandatory support tools:
- {layer}_artifacts
- {layer}_status

### 5.3 Transition Guard Contract

A stage call must fail with explicit transition error when prerequisite stage artifacts are missing.

### 5.4 Source Eligibility Contract

Rules:
- Runtime source discovery for workflow tools must exclude paths containing `archive` or `archived` (case-insensitive) unless explicit override is enabled by repository policy.
- Archived-path exclusion applies to source documents, intermediary artifacts, and candidate references.
- If explicit override is disabled, tools must not read, route to, or emit references to archived-path artifacts.

Required behavior:
- Tool output includes source-filter metadata describing archive exclusion behavior.
- Excluded archived candidates are counted in diagnostics but not used as workflow inputs.

Failure modes:
- Tool resolves an archived-path source without explicit override.
- Tool emits actionable references targeting archived paths when override is disabled.

### 5.5 Upstream-Missing Execution Contract

Rules:
- If a required upstream artifact is missing for a requested downstream operation, that downstream functionality must be skipped, not synthesized.
- Optional upstream artifacts may be omitted when optionality is declared by authoritative layer configuration.
- Skip decisions for missing required upstreams must be explicit and machine-parseable.

Required output fields for upstream-missing decisions:
- skipped_operation
- missing_upstream_type
- missing_upstream_id
- skip_reason

Failure modes:
- Tool fabricates downstream artifacts without required upstream chain.
- Tool silently drops functionality without upstream-missing diagnostics.

---

## 6. Artifact and Report Contracts

### 6.1 Artifact Immutability

Rules:
- Source artifact is immutable after creation.
- validate_fix writes derived validation-fixed artifact.
- remediate_apply writes derived remediated artifact.

### 6.2 Report Contracts

Rules:
- Validation reports are deterministic and report-only.
- Review and remediation reports are versioned artifacts.
- Every report contains source artifact identity and source processing stage.

Failure modes:
- Source overwrite.
- Missing lineage metadata.
- Report without source identity.

---

## 7. Compliance Matrix

| Contract Area | Verification Method | Pass Condition |
| --- | --- | --- |
| Prefix registry | Tool registry audit | All layer prefixes present |
| Alias coverage | Automated alias enumeration test | Every cross-layer tool has 11 aliases |
| Response envelope | Contract schema tests | Required keys present in all tool outputs |
| Severity domain | Finding schema validation | Only P0-P3 values used |
| Stage guards | Integration tests | Invalid transition returns explicit error |
| Source eligibility | Discovery/filter fixtures | Archived-path artifacts are excluded unless explicit override is enabled |
| Upstream-missing policy | Workflow transition fixtures | Missing required upstream yields explicit skip metadata, not synthesized output |
| Artifact immutability | File mutation tests | Source artifacts not overwritten |
| Report lineage | Report schema tests | Source identity and stage fields present |

---

## 8. Resource Requirements and Constraints

- CPU: moderate for full-layer validation and report generation.
- Memory: moderate for prompt/report payload handling.
- Storage: required for versioned derived artifacts and reports.
- Constraint: deterministic validation must not depend on non-deterministic model output.

---

## 9. Canonical Change Control

Change policy:
- Contract changes must be applied to this document first.
- Implementation plans may reference but must not redefine these rules.
- Version must increment for normative contract updates.

---

## 10. References

- mcp_sdd/docs/specs/SPEC-002_mcp_review_scoring_handoff_identity_contracts.md
- mcp_sdd/docs/specs/SPEC-003_mcp_creation_validation_profile_contracts.md
- mcp_sdd/docs/specs/SPEC-004_mcp_reporting_lineage_artifact_contracts.md
