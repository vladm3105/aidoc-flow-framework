# MIGRATION_PLAN.md Gap Analysis

## Critical Gaps

### 1. REQ (L7) removal loses atomic requirement traceability
EARS formalizes individual requirements but doesn't carry cumulative traceability tags, acceptance criteria, implementation paths, quality attributes, or SPEC-readiness scoring that REQ provided. Where do per-requirement acceptance criteria live now?

### 2. TDD layer semantic mismatch
TDD is a development practice, not a documentation artifact. Placing it as a document layer between ADR and SPEC creates a non-sequitur: `Architecture Decisions → Test Guide → Specification` has no logical dependency flow. SPEC should be upstream of TDD (you specify what to build, then define tests for it), not the reverse.

### 3. No test specification definitions remain
TSPEC (with 6 subtypes) is replaced by a single 80-line TDD template containing a test pyramid diagram and BDD→test mapping. Actual test case specifications (unit, integration, smoke, performance, security) have no home. BDD covers behavior scenarios only — it doesn't cover unit tests, performance thresholds, or security test cases.

### 4. No implementation bridge from SPEC to Code
TASKS was removed because "AI generates implementation tasks from SPEC on-the-fly." But without a task artifact, there's no record of what was implemented, no implementation contracts for parallel work, and no audit trail between SPEC and the delivered code.

**Resolution (2026-04-29)**: Added optional Layer 8 IPLAN (Implementation Plan) — ~100-line YAML template with file manifest, execution commands, session handoff protocol, and code inventory audit trail. Created only for complex SPECs (3+ files, multi-session, or parallel work). See `08_IPLAN/`.

## Structural Issues

### 5. Cumulative tag count is wrong
The traceability diagram shows `@brd + @prd + @ears + @bdd + @adr + @tdd + @spec = 7 tags` at SPEC level, but the text claims "6 tags at deepest" and "57% reduction." The correct count is 7.

### 6. Missing MVP template migration path
The plan copies `*-TEMPLATE.yaml` files but the active v2 uses `*-MVP-TEMPLATE.md` variants (per Claude rules). No mention of whether MVP templates are deprecated or need migration.

### 7. Unified SPEC at L7 is overloaded
SPEC previously had 5 subtypes (CSPEC code, DSPEC docs, UXSPEC UX, RISKSPEC risk, PROCSPEC process). Collapsing all into one "simplified" SPEC template without designating subtype handling leaves ambiguity.

### 8. CTR removal lacks contingency
The plan says CTR is "only needed for multi-team API contracts." But even single-team projects benefit from interface contracts for type safety and AI-driven code generation. No mechanism to optionally include CTR.

### 9. Missing backward compatibility strategy
Existing projects using v2 have `@sys`, `@req`, `@ctr`, `@tspec`, `@tasks` tags and SYS/REQ/CTR/TSPEC/TASKS documents. The plan doesn't address migration of existing artifacts.

### 10. No IPLAN mention
The Claude rules define IPLAN (Implementation Plan) as a reserved layer. v2 had TASKS→IPLAN→Code. The plan cuts TASKS but doesn't state whether IPLAN is retained, moved, or dropped.

## Process Gaps

### 11. No phased migration with gates
The plan lists "copy," "create," and "drop" as actions but has no sequencing, dependencies, intermediate verification steps, or acceptance criteria.

### 12. No UCX MCP tool impact assessment
The SDD workflow requires MCP tools (`sdd_create`, `sdd_validate`, `sdd_run_lifecycle`). These tools would need layer registry updates for the 7-layer model, but the plan doesn't address tooling changes.

### 13. No rollback plan
A 50% reduction in layers is a breaking change. No contingency for reverting if the simplified model proves insufficient.

### 14. Missing file count validation
The "What Gets Created New" list shows 10 files. The "Copied" list shows 13. That's 23 files minus dropped layers. The "Document Reduction" table claims "9 templates" — there's a 9 vs 7 layers vs ~23 files inconsistency.

## Minor Issues

### 15. TDD-00_index.md naming doesn't follow TDD type convention
Index files use `TYPE-00_index.md` (e.g., `BRD-00_index.md`), but TDD isn't a document type with numbered instances — it's a single guide. No `TDD-01_*.yaml` documents are planned.

### 16. Source path reference may be wrong
The plan uses `ai_dev_ssd_flow/` as the source directory, but the v2 framework may actually live at `ai_dev_flow/`.
