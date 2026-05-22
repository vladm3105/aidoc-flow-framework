# doc-iplan - Quick Reference

**Skill ID:** doc-iplan
**Layer:** 8 (Implementation Plan)
**Purpose:** Bridge a TDD/SPEC component into source code via an executable, session-resumable file manifest

## Quick Start

```bash
# Invoke skill
skill: "doc-iplan"

# Common requests
- "Create an IPLAN from SPEC-01 / TDD-01"
- "Generate an executable implementation plan for this component"
- "Build the Layer 8 file manifest and session handoff for implementation"
```

## What This Skill Does

1. Declare the file creation order (test-first, inherited from TDD)
2. Provide runnable bash commands (setup / implementation / validation)
3. Embed implementation contracts (when 3+ files share interfaces)
4. Seed the session-handoff protocol for stateless executor resumption
5. Maintain the code-inventory audit trail from specification to delivered files

## Output Location

```
docs/08_IPLAN/IPLAN-NN_{slug}/IPLAN-NN_{slug}.yaml
```

Temporary bugfix plans: `docs/08_IPLAN/tmp/TMP-IPLAN-YYYY-MM-DD_{slug}.yaml` (unregistered).

## File Manifest Format (test-first)

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
```

## Document & Reference ID Format

| Reference | Format | Example |
|-----------|--------|---------|
| IPLAN document | `IPLAN-NN` (dash) | `IPLAN-01` |
| SPEC document | `SPEC-NN` (dash) | `SPEC-01` |
| ADR document | `ADR-NN` (dash) | `ADR-03` |
| TDD test case | `TDD.NN.SS.xxxx` (4-segment, 4-hex hash) | `TDD.01.04.a3c1` |

## Six Sections (per IPLAN-TEMPLATE.yaml)

1. Document Control, 2. File Manifest, 3. Execution Commands
4. Implementation Contracts, 5. Session Handoff, 6. Traceability & Code Inventory

## Handoff Markers

`NOT_STARTED` | `IN_PROGRESS` | `DONE` | `PARTIAL`

## Required Fields (Document Control)

- `iplan_id` (`IPLAN-NN`), `source_spec` (`@spec: SPEC-NN`)
- Status, Version, Date Created, Last Updated, Author
- Complexity, Estimated Files, Session Count

## Cumulative Tags (in traceability.upstream)

```yaml
@brd: BRD.NN.SS.xxxx
@prd: PRD.NN.SS.xxxx
@ears: EARS.NN.SS.xxxx
@bdd: BDD.NN.SS.xxxx
@adr: ADR-NN
@spec: SPEC-NN
@tdd: TDD.NN.SS.xxxx   # PRIMARY SOURCE
```

Reference only documents that genuinely exist.

## Upstream/Downstream

```
BRD through TDD → IPLAN → Code
```

## Quick Validation

- [ ] `metadata.layer: 8` and `document_type: iplan-document`
- [ ] All 6 sections present
- [ ] File Manifest lists tests before implementation (test-first)
- [ ] Each manifest file has a status marker and `verified` flag
- [ ] Execution commands cover setup / implementation / validation
- [ ] Implementation Contracts declared (or "No implementation contracts")
- [ ] Session Handoff seeded with a `next_session_directive`
- [ ] Cumulative tags `@brd` through `@tdd` (only those that exist)
- [ ] Permanent plan registered in `IPLAN-00_index.yaml`

## Template Location

```
framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml
```

## Related Skills

- `doc-tdd` - Test design / test cases (upstream, primary source)
- `doc-spec` - Technical specifications (upstream)
- Implementation - Code, Tests, Validation (downstream)
