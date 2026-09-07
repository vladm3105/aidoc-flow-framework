# SPEC-003: MCP Creation and Validation Profile Contracts

| Field | Value |
| --- | --- |
| Canonical ID | SPEC-003 |
| Status | Active |
| Version | 1.5 |
| Date | 2026-04-30 |
| Source Basis | Canonical normative specification |
| Scope | Prompt-driven creation contracts, validation-profile contracts, metadata identity rules, layer-boundary validation rules, subtype resolution and threshold precedence |

---

## 1. Purpose

Define normative contracts for prompt-driven document creation, profile-bound validation, metadata identity enforcement, and layer-boundary validation behavior.

Implementation complexity: 4/5.

---

## 2. Scope and Boundaries

In scope:

- Prompt-driven creation flow contracts.
- Template and validation-profile binding.
- Canonical source artifact creation rules.
- Metadata identity and frontmatter guardrails.
- Structural, corpus, and boundary validation contracts.
- Threshold and readiness-profile contracts.

Out of scope:

- Review scoring and multi-persona semantics (defined by SPEC-002).
- Report naming, lineage persistence, and stage-specific artifact discovery (defined by SPEC-004).
- Cross-layer namespace and response-envelope policy (defined by SPEC-001).

---

## 3. Creation Contract (Mandatory)

Rules:

- `{layer}_create` is prompt-driven and template-bound.
- Creation emits the canonical source artifact only.
- Creation must not emit validation-fixed or remediated document variants.
- Creation may trigger optional validation, but that validation must remain report-only.
- Creation input provenance must be recoverable from prompt/template/session metadata.

Required creation guarantees:

- active template/profile identifier
- upstream source references
- canonical document identity
- source processing stage
- create provenance artifact

Failure modes:

- Creation emits a derived artifact instead of source artifact.
- Creation output violates active template profile.
- Creation prompt overrides canonical identity fields inconsistently.

### 3.1 Input Source Precedence and Conflict Contract

Supported creation source modes:

- `iplan`
- `ref`
- `prompt`

Precedence order (highest to lowest):

1. `iplan`
2. `ref`
3. `prompt`

Rules:

- When multiple input modes are provided, effective creation context must resolve using this precedence order.
- If objective/scope statements from lower-precedence sources conflict with the selected higher-precedence source, creation must fail with explicit conflict diagnostics.
- Conflict handling must be blocking and must not silently merge contradictory scope/objective directives.

Required output fields for conflict failures:

- input_precedence_applied
- conflict_type
- conflict_fields
- blocking_reason

Failure modes:

- Runtime mixes contradictory scope/objective content without explicit failure.
- Non-deterministic precedence resolution for identical input sets.

### 3.2 Create Provenance Artifact Contract

Each canonical source artifact folder must support a creation provenance directory:

- `.mcp_create_session/`

Required files:

- `session_manifest.json`
- `prompt_trace.md`

Required `session_manifest.json` fields:

- session_id
- created_at
- layer
- template_profile
- upstream_sources
- output_artifact_file

Rules:

- Create provenance is not a report artifact and must not participate in report versioning.
- Create provenance must be retained alongside the canonical source artifact.
- Validation may read provenance artifacts for traceability checks but must not mutate them.
- If provenance capture is enabled for a layer, missing required provenance files are validation findings.

Failure modes:

- Create flow records no recoverable provenance when provenance capture is enabled.
- Provenance manifest points to a different output artifact than the canonical source file.

---

## 4. Validation Profile Contract (Mandatory)

Each supported layer must define a validation profile containing at minimum:

- required_sections
- section_order
- section_code_map
- required_metadata_fields
- required_tags
- forbidden_patterns
- legacy_pattern_map
- readiness_thresholds

Rules:

- Validation must execute against the declared active profile.
- Profile data, not ad-hoc code branches, defines required sections and thresholds.
- Profile data or a profile-declared formula key defines readiness score formulas and score-component definitions.
- A document with no resolvable profile is contract-invalid.
- Threshold logic must be deterministic for identical input and profile data.

Required profile outputs:

- profile_name
- profile_version
- checks_run
- threshold_status
- readiness_scores

V3 profile alignment updates:

- Canonical registry source path for profile binding is `framework/LAYER_REGISTRY.yaml`.
- Readiness mapping for active flow is `brd->prd`, `prd->ears`, `ears->bdd`, `bdd->adr`, `adr->spec`, `spec->tdd`, `tdd->iplan`.
- Cumulative metadata tag ceilings apply by layer with max 8 at IPLAN.

### 4.1 Authoritative Layer Registry Binding

Authoritative source:

- `framework/LAYER_REGISTRY.yaml`

Rules:

- Layer metadata in the registry is normative for profile resolution and validation behavior.
- Validation profile loading must bind to registry fields for layer identity, optionality, required tags, and allowed references.
- Subtype catalogs defined in the registry are normative for layers that support subtypes.
- Template declarations in the registry are normative for default profile/template mapping.
- If profile metadata conflicts with registry metadata, validation must fail with explicit registry-drift error.
- Registry binding must emit the concrete registry source path and bound layer key used for resolution.

Required bound registry fields:

- number
- artifact
- folder
- optional
- required_tags
- can_reference
- template
- test_types (when present)

Required registry-binding output fields:

- registry_source
- registry_layer_key
- registry_binding_status
- registry_drift_fields

Failure modes:

- Profile resolved without a matching registry layer definition.
- Runtime behavior contradicts registry optionality or dependency metadata.
- Subtype resolution path ignores a registry subtype catalog.

### 4.2 Subtype Resolution Contract

Rules:

- Layers with subtype families must resolve subtype before template/profile selection.
- Layer 09 subtype routing must resolve `deliverable_type` to a subtype profile.
- Layer 10 subtype routing must resolve test subtype and subtype code to a subtype profile.
- Subtype resolution must be deterministic for identical input and registry/profile state.
- Unknown or unsupported subtype values are contract-invalid.
- Subtype resolution must declare whether subtype came from explicit runtime input or bound profile defaults.

Required subtype outputs (when subtype layer):

- subtype_type
- subtype_code
- subtype_profile
- subtype_source

Failure modes:

- Defaulting to an implicit subtype when explicit subtype is required.
- Subtype profile selected from template hints instead of registry/profile bindings.

---

## 5. Metadata Identity Contract (Mandatory)

Canonical source artifacts must preserve identity across create and validate flows.

Required top-level fields:

- title
- doc_id
- version
- status
- tags

Required custom_fields minimum:

- document_type
- artifact_type
- layer
- processing_stage

Rules:

- Creation must normalize required identity fields before write.
- Validation must check the same fields and treat mismatch as identity drift.
- Derived-stage metadata rules are defined by SPEC-004, but source artifacts must always use `processing_stage: source`.

Failure modes:

- Folder identity and document `doc_id` mismatch.
- Missing top-level identity field.
- Missing or invalid `processing_stage`.

---

## 6. Structural and Corpus Validation Contract

Validation must support both file-level and corpus-level checks.

File-level checks include:

- required section presence
- section numbering and order
- metadata validity
- element identifier format
- mandatory-content enforcement

Layer-parity checks may add deterministic structure rules per artifact type. Current MCP parity minimums include:

- EARS: trigger clause (`WHEN`, `IF`, or `WHILE`) and explicit `THE SYSTEM SHALL` actor phrase
- SPEC: fenced YAML implementation block
- TASKS: markdown checkbox list item
- CTR: explicit `openapi`, `endpoint`, or `contract` token

Corpus-level checks include:

- duplicate identity detection
- downstream reference blocking
- cross-file consistency required by active profile
- required companion or session-path conventions when defined by the profile

Rules:

- Blocking structural failures must be machine-parseable.
- Corpus-level results must identify the file set and rule family evaluated.
- Validation output must distinguish deterministic script findings from advisory findings.
- Blocking folder-structure checks must execute before non-structural checks when folder-structure requirements are declared by active profile.
- If folder-structure checks fail, subsequent validation stages may emit advisory diagnostics but must return failed structural gate status.

---

## 7. Layer Boundary Contract

Rules:

- Each artifact must align to cumulative upstream layers defined by registry `required_tags` for that layer.
- Current-layer validation may require immediate-parent alignment checks, but must not discard cumulative upstream requirements.
- Current-layer documents must not embed downstream artifact syntax as authored content.
- Validation must detect forbidden downstream reference patterns declared by the active profile.
- Where current-layer guidance to the next layer is allowed, it must be descriptive rather than executable downstream syntax.
- Boundary checks must identify both offending source layer and attempted downstream target layer.

Required output fields for boundary violations:

- boundary_rule
- offending_pattern
- target_layer
- source_layer

Failure modes:

- PRD embeds BDD or EARS executable syntax.
- Artifact references downstream document IDs that cannot exist at the current layer.
- Layer guidance becomes implementation content instead of bounded traceability guidance.

---

## 8. Readiness Threshold Contract

Rules:

- Each validation profile defines one or more readiness scores and pass thresholds.
- Each readiness score must declare either a fully profile-defined formula or a canonical formula key with version.
- Threshold evaluation must be explicit per score.
- Output must report both numeric value and pass/fail state.
- Multiple readiness scores may coexist for a single document type.

Required output fields:

- readiness_scores
- threshold_targets
- threshold_status

Failure modes:

- Missing score for an active threshold.
- Hidden threshold defaults not declared in the profile.
- Hidden code-only score formula not declared by profile or formula key.
- Pass/fail state inconsistent with reported numeric score.

### 8.1 Threshold and Profile Precedence Contract

Precedence order (highest to lowest):

1. Explicit runtime profile selection (when allowed by command contract).
2. Layer/subtype validation profile thresholds and formula declarations.
3. Authoritative registry defaults in `LAYER_REGISTRY.yaml`.
4. Template hints and examples (non-normative for threshold values).

Rules:

- Threshold and formula conflicts must resolve using this precedence order.
- Implementations must report which precedence source determined each active threshold.
- Non-deterministic source switching across identical runs is contract-invalid.
- Reported threshold/formula source identifiers must be stable for identical inputs.

Required output fields:

- threshold_source
- formula_source
- precedence_trace

Failure modes:

- Silent fallback to template values when profile or registry values exist.
- Different precedence source selected for identical inputs.

---

## 9. Compliance Matrix

| Contract Area | Verification Method | Pass Condition |
| --- | --- | --- |
| Create provenance artifact | Create/validate integration tests | Required provenance files and manifest fields are present when enabled |
| Creation source-only behavior | Integration tests | Create emits canonical source artifact only |
| Input precedence and conflict blocking | Input-source conflict fixtures | Effective source follows precedence and contradictory scope/objective content fails explicitly |
| Registry binding | Registry/profile integration tests | Active profile matches authoritative registry metadata |
| Subtype resolution | Subtype routing fixtures | Subtype profile and subtype code resolve deterministically |
| Profile resolution | Profile registry tests | Every validated artifact resolves exactly one active profile |
| Identity normalization | Create/validate fixture tests | Required fields match canonical identity contract |
| Structural validation | Schema and fixture tests | Missing sections and order drift are detected deterministically |
| Structural gate order | Gate-order fixtures | Blocking folder-structure checks run before non-structural checks |
| Corpus validation | Multi-file fixture tests | Duplicates and blocked references are reported correctly |
| Layer boundary enforcement | Boundary-pattern fixtures | Downstream syntax and references are rejected |
| Readiness threshold logic | Regression fixtures | Scores and pass states remain deterministic |
| Threshold precedence | Conflict fixtures | Active thresholds and formula sources follow precedence order |

---

## 10. Resource Requirements and Constraints

- CPU: moderate for corpus-level validation runs.
- Memory: moderate for profile loading and multi-file analysis.
- Storage: low-to-moderate for session and validation artifacts.
- Constraint: validation rules must remain deterministic and profile-declared.

---

## 11. Canonical Change Control

Change policy:

- Contract changes must be applied to this document first.
- Layer-specific implementations may refine profile content but must not weaken this contract.
- Version must increment for normative contract updates.

---

## 12. References

- ucx_hermes/docs/specs/SPEC-001_mcp_core_architecture_workflow_contracts.md
- ucx_hermes/docs/specs/SPEC-004_mcp_reporting_lineage_artifact_contracts.md
