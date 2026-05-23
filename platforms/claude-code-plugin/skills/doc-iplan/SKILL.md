---
name: doc-iplan
description: Create Implementation Plan (IPLAN) - Layer 8 artifact bridging TDD/SPEC to source code via an executable, session-resumable file manifest
metadata:
  tags:
    - sdd-workflow
    - layer-8-artifact
    - shared-architecture
  custom_fields:
    layer: 8
    artifact_type: IPLAN
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: core-workflow
    upstream_artifacts: [BRD,PRD,EARS,BDD,ADR,SPEC,TDD]
    downstream_artifacts: [Code]
    version: "2.0"
    last_updated: "2026-05-23"
    versioning_policy: "tracks IPLAN-TEMPLATE schema_version"
---

# doc-iplan

## Purpose

Create an **Implementation Plan (IPLAN)** - Layer 8 artifact in the SDD workflow, the mandatory execution bridge from TDD (Layer 7) and SPEC (Layer 6) to source code. Each IPLAN declares the file creation order (test-first, inherited from TDD), provides executable bash commands, tracks session progress across stateless executor calls, and maintains an audit trail from specification to delivered files.

**Layer**: 8

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3), BDD (Layer 4), ADR (Layer 5), SPEC (Layer 6), TDD (Layer 7)

**Downstream Artifacts**: Code

## Prerequisites

### Upstream Artifact Verification (CRITICAL)

**Before creating this document, you MUST:**

1. **List existing upstream artifacts**:
   ```bash
   ls docs/01_BRD/ docs/02_PRD/ docs/03_EARS/ docs/04_BDD/ docs/05_ADR/ docs/06_SPEC/ docs/07_TDD/ 2>/dev/null
   ```

2. **Reference only existing documents** in traceability tags
3. **Use `null`** only when upstream artifact type genuinely doesn't exist
4. **NEVER use placeholders** like `BRD-XXX` or `TBD`
5. **Do NOT create missing upstream artifacts** - skip functionality instead


Before creating an IPLAN, read:

1. **Shared Standards**: `../doc-flow/SHARED_CONTENT.md`
2. **Upstream TDD**: Read the test design / test cases to implement (PRIMARY SOURCE)
3. **Upstream SPEC**: Read the technical specification the TDD derives from
4. **Template**: `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml`
5. **Index Template**: `framework/layers/08_IPLAN/IPLAN-00_index.TEMPLATE.yaml`
6. **Layer Contract**: `framework/layers/08_IPLAN/README.md`
7. **ID & Tag Standards**: `framework/governance/ID_NAMING_STANDARDS.md`

## When to Use This Skill

Use `doc-iplan` when:
- Have completed BRD through TDD (Layers 1-7)
- The source TDD has reached IPLAN-Ready >=90/100
- Ready to bridge a TDD/SPEC component into source code
- Need an executable, session-resumable plan for AI coding agents
- You are at Layer 8 of the SDD workflow

## Permanent vs Temporary Plans

| | Permanent IPLAN (`IPLAN-NN_{slug}.yaml`) | Temporary IPLAN (`tmp/TMP-IPLAN-*.yaml`) |
|---|---|---|
| **Purpose** | Implement a SPEC component via TDD test cases | Bugfix, correction, investigation — no new functionality |
| **Requires TDD** | Yes — one IPLAN per TDD | No — standalone |
| **Registered in index?** | Yes — `IPLAN-00_index.yaml` | No |
| **Triggers audit trail?** | Yes — code inventory, session log | No — disposable |
| **Deleted when?** | Never — historical record (use ABANDONED) | Within 7 days of DONE/ABANDONED |
| **Naming** | `IPLAN-NN_{slug}.yaml` (NN sequential, never reused) | `TMP-IPLAN-YYYY-MM-DD_{slug}.yaml` |

**Rule of thumb**: Does the work implement a TDD test contract? → permanent. Does it restore intended behavior or fix a bug? → temporary.

## Reserved ID Exemption (IPLAN-00_*)

**Scope**: Documents with reserved ID `00` are FULLY EXEMPT from validation.

**Pattern**: `IPLAN-00_*`

**Document Types**:
- Index / registry documents (`IPLAN-00_index.yaml`)
- Templates (`IPLAN-00_index.TEMPLATE.yaml`)
- Glossaries, registries

**Rationale**: Reserved ID 00 documents are framework infrastructure (indexes, templates, reference materials), not project artifacts requiring traceability or quality gates.

**Validation Behavior**: Skip all checks when filename matches `IPLAN-00_*` pattern.

## Document & Element ID Format (MANDATORY)

**Document ID**: `IPLAN-NN` (document-level dash reference, two-digit sequential, never reused).

IPLAN itself is referenced at the document level — there is no hierarchical element-ID hash for an IPLAN. Upstream references inside an IPLAN use the standard formats:

| Reference | Format | Example |
|-----------|--------|---------|
| IPLAN document | `IPLAN-NN` | `IPLAN-01` |
| SPEC document | `SPEC-NN` | `SPEC-01` |
| ADR document | `ADR-NN` | `ADR-03` |
| TDD test case | `TDD.NN.SS.xxxx` (4-segment, 4-hex hash) | `TDD.01.04.a3c1` |

> **Reference**: [ID_NAMING_STANDARDS.md](../../../../framework/governance/ID_NAMING_STANDARDS.md)

## IPLAN-Specific Guidance

The IPLAN is a YAML document with six sections matching `IPLAN-TEMPLATE.yaml`. The sections below describe each.

### 1. Document Control

First section. Records `iplan_id` (IPLAN-NN), `source_spec` (`@spec: SPEC-NN`), status (`Draft | In Progress | Completed`), version, dates, author, complexity (1=1 file, 5=architectural), `estimated_files`, and `session_count` (incremented per session).

### 2. File Manifest (test-first order)

**Purpose**: Declare the file creation order. Tests come first (TDD principle inherited from Layer 7). Each file is tracked with a status marker that drives session handoff.

**Format**:
```yaml
file_manifest:
  files:
    - path: "tests/unit/test_data_validator.py"
      order: 1
      status: NOT_STARTED   # NOT_STARTED | IN_PROGRESS | DONE | PARTIAL
      session: null
      verified: false
    - path: "src/services/data_validator.py"
      order: 2
      status: NOT_STARTED
      session: null
      verified: false
    - path: "tests/integration/test_data_validator.py"
      order: 3
      status: NOT_STARTED
      session: null
      verified: false
```

One IPLAN per SPEC/TDD component — all files in the manifest belong to the same component.

### 3. Execution Commands

**Purpose**: Runnable bash commands — the actual bridge from specification to code. Three categories matching the implementation workflow.

**Format**:
```yaml
execution_commands:
  setup:
    - "python -m venv .venv && source .venv/bin/activate"
    - "pip install -r requirements.txt"
    - "mkdir -p src/services tests/unit tests/integration"
  implementation:
    - "# Create test file first (TDD): tests/unit/test_data_validator.py"
    - "# Create implementation: src/services/data_validator.py"
  validation:
    - "python -m pytest tests/ -v --cov=src/services --cov-report=term-missing"
    - "python -m mypy src/services --strict"
    - "python -m ruff check src/services"
```

### 4. Implementation Contracts

**Purpose**: Type interfaces, exception hierarchies, and state machines live in the IPLAN itself (no separate contract files). Optional — required when 3+ files depend on shared interfaces. State "No implementation contracts" if not applicable.

**Format**:
```yaml
implementation_contracts:
  provided:
    contracts: []     # interfaces this IPLAN exposes
  consumed:
    dependencies: []  # interfaces this IPLAN depends on
```

**Contract Types**:
1. **Protocol Interfaces**: `typing.Protocol` with method signatures
2. **Exception Hierarchies**: Typed exceptions with error codes
3. **State Machine Contracts**: `Enum` states with valid transitions
4. **Data Models**: Pydantic/TypedDict schemas
5. **DI Interfaces**: ABC classes for dependency injection

**Anti-patterns**:
- Contracts present but file count <3 — unnecessary overhead.
- Contracts missing but file manifest has 5+ files — guaranteed integration failures.

### 5. Session Handoff (stateless executor protocol)

**Purpose**: Critical for stateless executor calls. Each AI agent session is independent — no memory across invocations. This section is the bridge that lets a new session resume exactly where the last one stopped.

**Session startup protocol**:
1. **Read `session_handoff.sessions`** — identify the last session's state.
2. **Check `file_manifest.files`** — find the next `NOT_STARTED` or `PARTIAL` file.
3. **Read `partial_work`** description if resuming a `PARTIAL` step.
4. **Continue from that point** — do NOT regenerate completed work.
5. **Update file status** after completion or session end.
6. **Append to `session_handoff.sessions`** with a `next_session_directive`.

**Handoff markers**:
- `NOT_STARTED` — file not yet begun
- `IN_PROGRESS` — session actively working on this file
- `DONE` — file complete and verified (tests pass)
- `PARTIAL` — session ended mid-file (resume from `partial_work`)

**Format**:
```yaml
session_handoff:
  sessions:
    - date: "2026-05-22"
      agent: "[AI agent / session identifier]"
      files_touched:
        - path: "src/services/data_validator.py"
          action: created       # created | modified
          status: IN_PROGRESS
      partial_work: "[Exactly what's incomplete if session ended mid-step]"
      blockers: "[Any blockers preventing next session]"
      next_session_directive: "[What the next session should do first — cite file + step]"
      validation_results:
        tests_passing: false     # true | false | null
        coverage: null           # percentage or null
        lint_clean: false
```

### 6. Traceability & Code Inventory

**Purpose**: Cumulative upstream tags, downstream code/test paths, and an audit trail (`code_inventory`) recording every file created/modified with session attribution and verification status.

**Format**:
```yaml
traceability:
  upstream:
    spec_references:
      - "@spec: SPEC-01"
    tdd_references:
      - "@tdd: TDD.01.04.a3c1"
  downstream:
    code_paths:
      - "@code: src/services/"
    test_paths:
      - "@tests: tests/"
  code_inventory:
    files:
      - path: "src/services/data_validator.py"
        status: created       # created | modified
        session: 1
        verified: false       # true after tests pass + lint clean
```

## Tag Format Convention (By Design)

The SDD framework uses two distinct notation systems for cross-references:

| Notation | Format        | Artifacts                          | Purpose                                              |
|----------|---------------|------------------------------------|------------------------------------------------------|
| Dash     | TYPE-NN       | ADR, SPEC, IPLAN                   | Document-level references to files/documents         |
| Dot      | TYPE.NN.SS.xxxx | BRD, PRD, EARS, BDD, ADR, TDD     | Hierarchical references to elements inside documents |

**Key Distinction**:
- `@spec: SPEC-01` → Points to the document `SPEC-01_data_validation.yaml`
- `@tdd: TDD.01.04.a3c1` → Points to test case 04 (hash `a3c1`) inside document `TDD-01`

## Unified Element ID Format (MANDATORY)

**For hierarchical elements (BRD, PRD, EARS, BDD, ADR, TDD)**:
- **Always use**: `TYPE.NN.SS.xxxx` (4-segment: type, two-digit doc, two-digit section, 4-hex content hash)
- **Document-level artifacts (SPEC, ADR, IPLAN)** use the dash form `TYPE-NN`.

Examples:
- `@tdd: TDD.01.04.a3c1` ✅
- `@spec: SPEC-01` ✅
- `@tdd: TDD.01.40` ❌ (legacy numeric type-code — removed)

## Cumulative Tagging Requirements

**Layer 8 (IPLAN)**: Must carry upstream references from Layers 1-7 that genuinely exist.

**Minimum traceability** (in `traceability.upstream`):
```yaml
@brd: BRD.01.01.0103
@prd: PRD.01.07.0702
@ears: EARS.01.03.2501
@bdd: BDD.01.03.1401
@adr: ADR-03
@spec: SPEC-01
@tdd: TDD.01.04.a3c1
```

Reference only documents that exist; use upstream artifact types that are genuinely present in the project.

## Upstream/Downstream Artifacts

**Upstream Sources**:
- **BRD** (Layer 1) - Business requirements
- **PRD** (Layer 2) - Product features
- **EARS** (Layer 3) - Formal requirements
- **BDD** (Layer 4) - Test scenarios
- **ADR** (Layer 5) - Architecture decisions
- **SPEC** (Layer 6) - Technical specifications
- **TDD** (Layer 7) - Test design / test cases (PRIMARY SOURCE)

**Downstream Artifacts**:
- **Code** - Implementation source + tests (created in `src/` and `tests/`)

**Same-Type Document Relationships** (conditional):
- `@related-iplan: IPLAN-NN` - IPLANs sharing implementation context
- `@depends-iplan: IPLAN-NN` - IPLANs that must be completed first

## Validation Checks

The plugin skill *is* the validator — the framework ships no runtime validation scripts. Apply the declarative checklist below; the authoritative rule sources are `framework/layers/08_IPLAN/README.md` and `framework/governance/ID_NAMING_STANDARDS.md`.

### Tier 1: Errors (Blocking)

| Check | Description |
|-------|-------------|
| CHECK 1 | Filename format valid (`IPLAN-NN_{slug}.yaml`) |
| CHECK 2 | `metadata` block present with `schema_version`, `layer: 8`, `document_type` |
| CHECK 3 | `document_control` complete (`iplan_id`, `source_spec`, status, version, dates) |
| CHECK 4 | All 6 sections present (Document Control, File Manifest, Execution Commands, Implementation Contracts, Session Handoff, Traceability) |
| CHECK 5 | `file_manifest` lists tests before implementation (test-first order) |
| CHECK 6 | `session_handoff.sessions` present (at least one entry once work starts) |
| CHECK 7 | Parent SPEC/TDD references valid and files exist |
| CHECK 8 | ID format compliance (document `IPLAN-NN`; `@tdd` uses `TDD.NN.SS.xxxx`) |

### Tier 2: Warnings

| Check | Description |
|-------|-------------|
| CHECK W1 | Execution commands cover setup, implementation, and validation |
| CHECK W2 | `code_inventory` populated for every created/modified file |
| CHECK W3 | `validation_results` recorded per session |
| CHECK W4 | Implementation contracts present when file count >=3 |
| CHECK W5 | `next_session_directive` present in the latest session entry |

### Tier 3: Info

| Check | Description |
|-------|-------------|
| CHECK I1 | Complexity and `estimated_files` recorded in document control |
| CHECK I2 | Registered in `IPLAN-00_index.yaml` (permanent plans only) |
| CHECK I3 | Temporary plans live under `tmp/` and are deleted within 7 days of DONE |

## Creation Process

### Step 1: Read Upstream TDD and SPEC

Read the TDD (Layer 7) test cases and the SPEC (Layer 6) it derives from. The TDD is the primary source for the file manifest and test-first ordering.

### Step 2: Reserve ID Number

Check `docs/08_IPLAN/` (and `IPLAN-00_index.yaml`) for the next available ID number.

**ID Numbering Convention**: Two digits, sequential, never reused.
- Correct: `IPLAN-01`, `IPLAN-02`, `IPLAN-10`
- IPLAN ID typically matches its SPEC/TDD component (`IPLAN-01` for `SPEC-01`/`TDD-01`).

### Step 3: Create IPLAN File

**File naming**: `docs/08_IPLAN/IPLAN-NN_{slug}.yaml`

**Example**: `docs/08_IPLAN/IPLAN-01_data_validation.yaml`

Temporary bugfix plans go under `docs/08_IPLAN/tmp/TMP-IPLAN-YYYY-MM-DD_{slug}.yaml` and are NOT registered in the index.

### Step 4: Fill Document Control

Complete `metadata` and `document_control` (iplan_id, source_spec, status, version, dates, complexity, estimated_files, session_count).

### Step 5: Declare the File Manifest

List every file the component needs, in creation order, tests first. Set each `status: NOT_STARTED`.

### Step 6: Write Execution Commands

Provide runnable `setup`, `implementation`, and `validation` bash commands.

### Step 7: Define Implementation Contracts (if needed)

If 3+ files share interfaces, declare provided/consumed contracts. Otherwise state "No implementation contracts".

### Step 8: Initialize Session Handoff

Seed `session_handoff.sessions` so the first executor session has a clear `next_session_directive`.

### Step 9: Add Traceability

Add upstream `spec_references` / `tdd_references`, downstream `code_paths` / `test_paths`, and an empty `code_inventory` to be populated during implementation.

### Step 10: Register in the Index

**MANDATORY (permanent plans)**: Add the plan to `docs/08_IPLAN/IPLAN-00_index.yaml` (`registry.plans`), update `metadata.total_plans`, and place it in the correct `execution_path` tier.

### Step 11: Validate IPLAN

Apply the Validation Checks checklist above. The skill is the validator; consult `framework/layers/08_IPLAN/README.md` and `framework/governance/ID_NAMING_STANDARDS.md` for the authoritative rules.

### Step 12: Commit Changes

Commit the IPLAN file and the updated index.

## Validation

### Manual Checklist

- [ ] `metadata.layer: 8` and `document_type: iplan-document`
- [ ] Document Control complete (iplan_id, source_spec, status, dates)
- [ ] File Manifest lists tests before implementation (test-first)
- [ ] Each manifest file has a status marker and `verified` flag
- [ ] Execution commands cover setup / implementation / validation
- [ ] Implementation Contracts declared (or "No implementation contracts")
- [ ] Session Handoff seeded with a `next_session_directive`
- [ ] Traceability upstream references (`@spec`, `@tdd`, …) point to existing docs
- [ ] `code_inventory` ready to record created/modified files
- [ ] Permanent plan registered in `IPLAN-00_index.yaml`
- [ ] Temporary plan (if any) lives under `tmp/` and is unregistered

### Diagram Standards

If a dependency diagram is included, it MUST use Mermaid syntax. Text-based diagrams (ASCII art, box drawings) are prohibited. See the `mermaid-gen` skill.

## Common Pitfalls

1. **Implementation-first manifest**: tests MUST precede implementation files.
2. **Missing session handoff**: stateless executors cannot resume without it.
3. **Regenerating completed work**: always read prior session state first.
4. **Unverified code inventory**: mark `verified: true` only after tests pass + lint clean.
5. **Contracts overhead**: don't declare contracts for <3-file components.
6. **Missing contracts**: 5+ interdependent files without contracts cause integration failures.
7. **Unregistered permanent plan**: every permanent IPLAN must appear in `IPLAN-00_index.yaml`.
8. **Reusing plan numbers**: NN is sequential and never reused (abandoned plans stay as ABANDONED).
9. **Legacy element IDs**: use `TDD.NN.SS.xxxx` and `SPEC-NN`, not legacy numeric type-codes.

## Post-Creation Validation (MANDATORY - NO CONFIRMATION)

**CRITICAL**: Execute this validation loop IMMEDIATELY after document creation. Do NOT proceed to implementation until validation passes.

### Validation Loop

```
LOOP:
  1. Apply the Tier 1/2/3 checklist above to the IPLAN.
  2. IF errors found: fix them. GOTO LOOP (re-validate).
  3. IF warnings found: address or document. GOTO LOOP.
  4. IF unfixable issues: log for manual review, continue.
  5. IF clean: Mark VALIDATED, proceed.
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream References | Notes |
|------------|------------------------------|-------|
| IPLAN (Layer 8) | @brd, @prd, @ears, @bdd, @adr, @spec, @tdd | Reference only documents that exist |

### Common Fixes (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing upstream reference | Add with the existing upstream document ID |
| Invalid element-ID format | Correct to `TDD.NN.SS.xxxx` or document-level `SPEC-NN` / `IPLAN-NN` |
| Implementation listed before its test | Reorder manifest to test-first |
| Missing session handoff | Seed `session_handoff.sessions` from the template |
| Permanent plan absent from index | Add to `IPLAN-00_index.yaml` |

### Quality Gate

**Blocking**: YES - Cannot proceed to implementation until the IPLAN validates with 0 errors.

---

## Next Skill

After completing the IPLAN, proceed to implementation:
- **Code** - Execute the file manifest test-first, updating session handoff and code inventory as you go.

## Reference Documents

IPLAN artifacts do not support REF documents. Reference documents are limited to **BRD and ADR types only** per the SDD framework.

For supplementary documentation needs, create:
- **BRD-REF**: Business context documentation
- **ADR-REF**: Implementation-sequencing notes, dependency analysis reports

## Related Resources

- **Template**: `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` (primary authority)
- **Index Template**: `framework/layers/08_IPLAN/IPLAN-00_index.TEMPLATE.yaml`
- **Layer Contract**: `framework/layers/08_IPLAN/README.md`
- **ID & Tag Standards**: `framework/governance/ID_NAMING_STANDARDS.md`
- **Shared Standards**: `../doc-flow/SHARED_CONTENT.md`

## Quick Reference

**IPLAN Purpose**: Bridge a TDD/SPEC component into source code via an executable, session-resumable file manifest.

**Layer**: 8

**Document ID Format**: `IPLAN-NN` (document-level dash reference)

**Upstream References**: `@spec: SPEC-NN`, `@tdd: TDD.NN.SS.xxxx`

**Six Sections**:
1. Document Control
2. File Manifest (test-first)
3. Execution Commands (setup / implementation / validation)
4. Implementation Contracts
5. Session Handoff (stateless executor protocol)
6. Traceability & Code Inventory

**Permanent vs Temporary**: permanent IPLAN per TDD (registered in index); temporary `tmp/TMP-IPLAN-*` for bugfixes (disposable).

**Handoff Markers**: NOT_STARTED | IN_PROGRESS | DONE | PARTIAL

**Next**: Implementation (Code)

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 2.0 | 2026-05-22 | Migrated to the 8-layer model as the IPLAN (Layer 8) skill; aligned to IPLAN-TEMPLATE (file manifest, session handoff, code inventory, permanent vs tmp plans) | System |
| 1.0 | 2026-02-08 | Initial skill definition with YAML frontmatter standardization | System |
