---
name: doc-iplan-validator
description: Validate Implementation Plan (IPLAN) documents against Layer 8 schema standards
tags:
  - sdd-workflow
  - layer-8-artifact
  - quality-assurance
custom_fields:
  layer: 8
  artifact_type: IPLAN
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: quality-assurance
  upstream_artifacts: [IPLAN]
  downstream_artifacts: []
  version: "2.0"
  last_updated: "2026-05-22"
  versioning_policy: "tracks IPLAN-TEMPLATE schema_version"
---

# doc-iplan-validator

Validate Implementation Plan (IPLAN) documents against Layer 8 schema standards.

## Activation

Invoke when user requests validation of IPLAN documents or after creating/modifying IPLAN artifacts.

## Validation Schema Reference

Template: `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml`
Layer Contract: `framework/layers/08_IPLAN/README.md`
ID & Tag Standards: `framework/governance/ID_NAMING_STANDARDS.md`
Layer: 8
Artifact Type: IPLAN

The plugin skill *is* the validator — the framework ships no runtime validation
scripts. Apply the declarative checklist below; the authoritative rule sources
are the template, the layer README, and the ID & tag standards above.

## Validation Checklist

### 0. Folder Structure Validation (BLOCKING)

**Nested Folder Rule**: ALL IPLAN documents MUST be in nested folders regardless of size.

**Required Structure**:

| IPLAN Type | Required Location |
|------------|-------------------|
| Permanent | `docs/08_IPLAN/IPLAN-NN_{slug}/IPLAN-NN_{slug}.yaml` |
| Temporary | `docs/08_IPLAN/tmp/TMP-IPLAN-YYYY-MM-DD_{slug}.yaml` (unregistered) |

**Validation**:

```
1. Check permanent document is inside a nested folder: docs/08_IPLAN/IPLAN-NN_{slug}/
2. Verify folder name matches IPLAN ID pattern: IPLAN-NN_{slug}
3. Verify file name matches folder: IPLAN-NN_{slug}.yaml
4. Parent path must be: docs/08_IPLAN/
5. Temporary plans live under docs/08_IPLAN/tmp/ and are NOT registered in the index
```

**Example Valid Structure**:

```
docs/08_IPLAN/
├── IPLAN-01_f1_iam/
│   ├── IPLAN-01_f1_iam.yaml         ✓ Valid
│   ├── IPLAN-01.R_review_report_v001.md
│   └── .drift_cache.json
├── IPLAN-02_f2_session/
│   └── IPLAN-02_f2_session.yaml     ✓ Valid
└── tmp/
    └── TMP-IPLAN-2026-05-22_hotfix.yaml  ✓ Valid (unregistered)
```

**Invalid Structure**:

```
docs/08_IPLAN/
├── IPLAN-01_f1_iam.yaml             ✗ NOT in nested folder
```

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| IPLAN-E020 | ERROR | IPLAN not in nested folder (BLOCKING) |
| IPLAN-E021 | ERROR | Folder name doesn't match IPLAN ID |
| IPLAN-E022 | ERROR | File name doesn't match folder name |
| VAL-H001 | ERROR | Drift cache missing hash for upstream document |
| VAL-H002 | ERROR | Invalid hash format (must be sha256:<64 hex chars>) |

**This check is BLOCKING** - IPLAN must pass folder structure validation before other checks proceed.

**Reserved ID Exemption**: Documents matching `IPLAN-00_*` (index/registry, templates) are FULLY EXEMPT from validation.

---

### 1. Metadata Validation

```yaml
Required metadata:
  - schema_version: present
  - document_type: "iplan-document"
  - layer: 8
  - total_sections: 6

Required custom_fields (skill frontmatter):
  - artifact_type: "IPLAN"
  - layer: 8
  - architecture_approaches: [array format]
  - priority: ["primary", "shared", "fallback"]
  - development_status: ["active", "draft", "deprecated", "reference"]

Required tags:
  - iplan-document
  - layer-8-artifact

Forbidden tag patterns:
  - "^task-breakdown$"
  - "^implementation-tasks$"
  - "^iplan-\\d{3}$"
```

### 2. Structure Validation

**Required Sections (6 sections, per `IPLAN-TEMPLATE.yaml`):**
- Section 1: Document Control
- Section 2: File Manifest (test-first order)
- Section 3: Execution Commands (setup, implementation, validation)
- Section 4: Implementation Contracts
- Section 5: Session Handoff (stateless executor protocol)
- Section 6: Traceability & Code Inventory

**Document Control Required Fields:**
- `iplan_id` (`IPLAN-NN`)
- `source_spec` (`@spec: SPEC-NN`)
- `status` (Draft | In Progress | Completed)
- `version`
- `date_created`
- `last_updated`
- `author`
- `complexity` (1=1 file, 5=architectural)
- `estimated_files`
- `session_count`

**File Naming:**
Pattern: `IPLAN-NN_{slug}.yaml` (permanent) / `TMP-IPLAN-YYYY-MM-DD_{slug}.yaml` (temporary)

### 3. Content Validation

**File Manifest Format** (per `file_manifest.files` entry):
- `path`, `order`, `status`, `session`, `verified`
- Tests MUST be ordered before their implementation files (test-first principle inherited from TDD).

**File Status Values:**
- NOT_STARTED
- IN_PROGRESS
- DONE
- PARTIAL

**Execution Commands:**
- `setup`, `implementation`, and `validation` categories present.
- Commands are runnable bash (not prose placeholders).

**Session Handoff:**
- Each `sessions` entry records `files_touched` with status markers.
- `partial_work` described when a step ended mid-file (PARTIAL).
- `next_session_directive` cites a concrete file + step.
- `validation_results` populated per session (tests_passing, coverage, lint_clean).

**Implementation Contracts Categories** (required when 3+ files depend on shared interfaces):
- Protocol Interfaces: `typing.Protocol` with type hints
- Exception Hierarchies: `class XxxError(BaseError)` with error codes
- State Machine Contracts: `enum State` with transitions
- Data Models: Pydantic BaseModel with validation
- Dependency Injection: ABC interface patterns

State "No implementation contracts" if file count < 3.

**Code-Ready Score:**
- Minimum threshold: 90%
- Components: File manifest completeness (20%), Test-first ordering (15%), Execution commands (15%), Implementation contracts (15%), Session handoff integrity (10%), Traceability (15%), Code inventory readiness (10%)

### 4. Traceability Validation

**Layer 8 (IPLAN) Cumulative Tags** (in `traceability.upstream`):
- @brd: BRD.NN.SS.xxxx (required if exists)
- @prd: PRD.NN.SS.xxxx (required if exists)
- @ears: EARS.NN.SS.xxxx (required if exists)
- @bdd: BDD.NN.SS.xxxx (required if exists)
- @adr: ADR-NN (required if exists)
- @spec: SPEC-NN (required)
- @tdd: TDD.NN.SS.xxxx (required — PRIMARY SOURCE)

Reference only documents that genuinely exist; never use placeholders.

**Implementation Contracts Tags:**
- @icon: IPLAN-NN:ContractName
- @icon-role: provider|consumer (optional)

**Downstream Expected:**
- Code (src/...)
- Tests (tests/...)

**Same-Type References:**
- @related-iplan: IPLAN-NN
- @depends-iplan: IPLAN-NN

## Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| IPLAN-E001 | error | Missing required tag 'iplan-document' |
| IPLAN-E002 | error | Missing required tag 'layer-8-artifact' |
| IPLAN-E003 | error | Invalid document_type |
| IPLAN-E004 | error | Invalid architecture_approaches format |
| IPLAN-E005 | error | Forbidden tag pattern detected |
| IPLAN-E006 | error | Missing required section (of 6) |
| IPLAN-E007 | error | metadata.layer not 8 |
| IPLAN-E008 | error | total_sections not 6 |
| IPLAN-E009 | error | Document Control missing required fields |
| IPLAN-E010 | error | Missing File Manifest (Section 2) |
| IPLAN-E011 | error | Missing Traceability (Section 6) |
| IPLAN-E012 | error | File manifest lists implementation before its test (test-first violation) |
| IPLAN-E013 | warning | File name does not match format |
| IPLAN-E014 | error | source_spec not in valid format (`@spec: SPEC-NN`) |
| IPLAN-W001 | warning | Manifest file missing required element (path/order/status/session/verified) |
| IPLAN-W002 | warning | Status marker not assigned on a manifest file |
| IPLAN-W003 | warning | Session entry missing acceptance/next_session_directive |
| IPLAN-W004 | warning | Missing upstream tags (require those that exist) |
| IPLAN-W005 | warning | Code-Ready Score below 90% |
| IPLAN-W006 | warning | Execution commands missing a category (setup/implementation/validation) |
| IPLAN-W007 | warning | Implementation Contracts empty but file count >= 3 |
| IPLAN-I001 | info | Consider defining Implementation Contracts |
| IPLAN-I002 | info | code_inventory not yet populated |
| IPLAN-I003 | info | Consider using @icon tags for contracts |

## Validation Workflow

1. Parse the IPLAN YAML document and the skill frontmatter
2. Check required metadata fields (`schema_version`, `document_type`, `layer: 8`)
3. Validate tag taxonomy
4. Verify section structure (all 6 sections present)
5. Validate `document_control` fields
6. Check File Manifest (test-first ordering, status markers)
7. Validate Execution Commands (setup / implementation / validation)
8. Validate Session Handoff integrity (markers, next_session_directive, validation_results)
9. Validate Implementation Contracts (if file count >= 3)
10. Validate upstream references (only those that genuinely exist)
11. Calculate Code-Ready Score
12. Verify file naming + nested-folder convention
13. Generate validation report

## Integration

- Invoked by: doc-flow, doc-iplan (post-creation)
- Feeds into: trace-check (cross-document validation)
- Reports to: quality-advisor

## Output Format

```
IPLAN Validation Report
=======================
Document: IPLAN-01_example.yaml
Status: PASS/FAIL

File Manifest:
- Files declared: N
- Test-first ordering: PASS/FAIL
- Status markers assigned: N/N

Execution Commands:
- setup / implementation / validation: present?

Session Handoff:
- Sessions recorded: N
- next_session_directive present: yes/no
- validation_results populated: N/N

Implementation Contracts:
- Protocols: N
- Exceptions: N
- State Machines: N
- Data Models: N

Code-Ready Score: N%

Errors: N
Warnings: N
Info: N

[Details listed by severity]
```

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 2.0 | 2026-05-22 | Migrated to the 8-layer model: validate IPLAN (Layer 8) against `IPLAN-TEMPLATE.yaml` (6 YAML sections, file manifest, session handoff, code inventory); replaced runtime-script invocation with the declarative checklist + pointers to the layer README and ID standards; reworked error codes to IPLAN-* | System |
| 1.1 | 2026-02-11 | **Nested Folder Rule**: Added Section 0 Folder Structure Validation (BLOCKING); documents must be in nested folders; added structure error codes | System |
| 1.0 | 2026-02-08 | Initial validator skill definition with YAML frontmatter | System |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths such as `docs-v2.0/00_REF`.
