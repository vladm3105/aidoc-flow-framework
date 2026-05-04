# SPEC-002: MCP Review, Scoring, Handoff, and Identity Contracts

| Field | Value |
| --- | --- |
| Canonical ID | SPEC-002 |
| Status | Active |
| Version | 1.6 |
| Date | 2026-05-04 |
| Source Basis | Canonical normative specification |
| Scope | Review scoring, multi-persona output, context engineering, handoff contracts, hash identity contracts |

---

## 1. Purpose

Define normative contracts for cross-layer review scoring, prompt construction, handoff behavior, and finding/action identity.

Implementation complexity: 4/5.

---

## 2. Scope and Boundaries

In scope:
- Category-weighted scoring contracts.
- Multi-persona finding and prompt structure contracts.
- Context-engineering contracts.
- Prompt inspection and diagnostics contracts.
- Fixer-to-LLM and layer action handoff contracts.
- Hash-based finding/action ID contracts.

Out of scope:
- Core lifecycle sequence and artifact immutability rules (defined by SPEC-001).
- Non-MCP UI concerns.

---

## 3. Scoring Contract

Rules:
- Category weights are document-type specific and sum to 100.
- Per-category deduction caps are enforced.
- Unsupported findings route to other non-scoring bucket.
- Output includes weighted score and category breakdown.
- Out-of-layer handoff actions carry zero direct score penalty.

Required output fields:
- weighted_score
- category_breakdown
- uncategorized_count
- threshold_status

Failure modes:
- Weight total not equal to 100.
- Score drift across repeated runs with identical inputs.

---

## 4. Multi-Persona Prompt and Finding Contract

Rules:
- Persona findings must be machine-parseable.
- Chair synthesis must include parseable action/finding manifest boundaries.
- Terminal prompt sections contain format instructions.
- Multiple personas may be assigned per review via `personas: list[str]` resolved from `persona_mappings.yaml`.

Required finding fields:
- finding_id
- priority
- category
- personas
- message
- target_layer

Priority domain:
- P0
- P1
- P2
- P3

### 4.1 Saga Parallel Reducer Output (Extension)

When review runs in saga-parallel mode, reducer outputs must include base finding fields plus provenance fields.

Required reducer finding fields:

- finding_id
- action_id
- priority
- category
- personas
- message
- target_layer
- recommended_action
- provenance.branch_id
- provenance.persona
- content_hash

Rules:

- reducer outputs must remain machine-parseable and deterministic for identical inputs
- reducer deduplication must preserve at least one provenance tuple per merged finding
- reducer outputs are valid handoff inputs only when `finding_id` and `action_id` satisfy Section 9 formats

---

## 5. Context Engineering Contract

Rules:
- Include mapped core sections per persona (each persona in the `personas` list receives its domain-relevant sections).
- Hybrid keyword scan discovers additional relevant snippets.
- Appendix defaults to index mode and optional verification tags.
- Dynamic mapping includes confidence scores.

Required context fields:
- sections_included
- sections_skipped
- discovered_snippets
- appendix_index
- token_estimate

---

## 6. Prompt Inspection Contract

Rules:
- Prompt generation emits deterministic metadata sidecar.
- Inspection supports structure, section, and token diagnostics.
- Quick checks emit warnings for format degradation risk.

Required metadata fields:
- personas
- persona_count
- persona_token_estimate
- persona_token_warning (str | None, emitted when token budget risk is detected)
- doc_type
- structure_blocks
- sections.included
- sections.skipped
- tokens.total

---

## 7. Fixer-to-LLM Handoff Contract

Rules:
- Validation output includes fixer session summary and machine context.
- Partial-fix and LLM-only work are explicitly separated.
- Script-applied protected changes are listed for guardrails.

Required handoff fields:
- session_id
- fixed_count
- partial_fix_count
- llm_completion
- llm_only
- fixer_applied

---

## 8. Layer Action Handoff Contract

Rules:
- Out-of-layer findings convert to handoff actions.
- Actions are deduplicated by content and target-layer tuple.
- Target layer must be resolved from the canonical downstream layer registry and be downstream of the source layer.
- Action extraction output is machine-parseable.

Canonical downstream layer progression:
- brd -> prd -> ears -> bdd -> adr -> sys -> req -> ctr -> spec -> tspec -> tasks

Rules:
- Implementations must reject same-layer and upstream-layer action targets.
- If a source layer permits only a subset of downstream layers, that subset must be declared in layer configuration rather than inferred ad hoc.

### 8.1 Optional Layer Skip Semantics

Rules:
- Optional layers declared by authoritative layer registry may be skipped when absent.
- For this framework, `ctr` is optional and may be skipped for downstream routing when artifact absence is confirmed.
- Skip behavior must reroute action targets to the next valid downstream layer while preserving source traceability.
- Skip decisions must be explicit in output metadata and must not silently drop actions.
- Rerouting must remain deterministic for identical input findings and registry state.

Required optional-skip output fields:
- skipped_optional_layers
- routing_reason
- source_layer
- original_target_layer
- resolved_target_layer

Failure modes:
- Action targeting fails when only an optional layer is missing.
- Optional-layer skip silently changes target without routing metadata.
- Action dropped instead of rerouted when optional-layer absence is the only blocker.
- Equivalent runs resolve different reroute targets for the same input.

Required action fields:
- action_id
- type
- target_layer
- priority
- source_ref
- personas
- context
- requirement
- skipped_optional_layers
- routing_reason

Failure modes:
- Invalid target layer.
- Duplicate unresolved actions.
- Score penalty incorrectly applied to handoff-only actions.

---

## 9. Hash Identity Contract

Rules:
- Finding and action IDs are deterministic hashes over normalized identity fields.
- Collision strategy increases hash length before fallback suffixing.
- Legacy sequential IDs remain parseable through compatibility validator.
- String identity fields are whitespace-normalized and case-folded before hashing.
- Remediation outputs that emit findings must emit both `finding_id` and `action_id` for each finding entry.

Required legacy finding-ID compatibility families:
- persona-prefixed sequential IDs: `{PERSONA}-P{0|1|2|3}-{NNN}`
- remediation sequential IDs: `REM-P{0|1|2|3}-{NNN}`
- hash IDs from prior runs: `P{0|1|2|3}-{hex}`

Required formats:
- Finding: P{0|1|2|3}-{hex}
- Action: ACT-{hex}

Failure modes:
- Non-deterministic ID generation for identical input.
- Collision not resolved by adaptive length policy.
- Remediation findings emitted without machine-parseable hash identities.

---

## 10. Namespace Compliance for Review Tools

All review-prefixed cross-layer tools must expose deterministic layer aliases:
- {layer}_{review_tool_name} for each layer prefix in SPEC-001.

Required behavior:
- Canonical review tool remains callable.
- Alias call records alias_invoked metadata.

---

## 11. Compliance Matrix

| Contract Area | Verification Method | Pass Condition |
| --- | --- | --- |
| Weight validity | Scoring config tests | All doc-type configs sum to 100 |
| Score determinism | Regression fixtures | Identical input yields identical score |
| Persona parseability | Contract parser tests | Manifests parsed without fallback |
| Context diagnostics | Integration tests | Required context fields present |
| Prompt diagnostics | Metadata schema tests | Required inspection fields present |
| Handoff integrity | Handoff schema tests | Required fixer/action fields present |
| Optional-layer skip routing | Layer-routing fixtures | Missing optional layer is rerouted with required skip metadata |
| Action zero-penalty | Scoring-action integration test | Handoff-only actions do not reduce score |
| ID determinism | Hash regression tests | Stable IDs for identical normalized input |
| ID compatibility | Legacy fixture tests | Persona-prefixed and remediation sequential IDs parse successfully |
| Review alias coverage | Alias registry tests | All review tools expose per-layer aliases |

---

## 12. Resource Requirements and Constraints

- CPU: moderate-to-high for full prompt diagnostics and integration checks.
- Memory: moderate for context assembly and report manifests.
- Storage: required for fixtures, sidecars, and regression outputs.
- Constraint: scoring and ID generation must remain deterministic under repeated execution.

---

## 13. Canonical Change Control

Change policy:
- Contract changes must be applied to this document first.
- Implementation plans may reference but must not redefine these contracts.
- Version must increment for normative contract updates.

---

## 14. References

- ucx_hermes/docs/specs/SPEC-001_mcp_core_architecture_workflow_contracts.md
- ucx_hermes/docs/specs/SPEC-003_mcp_creation_validation_profile_contracts.md
- ucx_hermes/docs/specs/SPEC-004_mcp_reporting_lineage_artifact_contracts.md
