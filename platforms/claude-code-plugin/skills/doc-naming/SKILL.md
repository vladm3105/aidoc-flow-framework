---
name: doc-naming
description: Enforces unified ID naming standards and threshold naming rules for all SDD documentation artifacts
tags:
  - sdd-workflow
  - shared-architecture
  - quality-assurance
  - required-both-approaches
custom_fields:
  layer: null
  artifact_type: null
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: quality-assurance
  upstream_artifacts: []
  downstream_artifacts: []
  version: "1.8"
---

# doc-naming Skill

Enforces unified ID naming standards and threshold naming rules for all SDD documentation artifacts.

---

## 1. Purpose & Scope

### When to Invoke

Invoke this skill BEFORE creating or editing any SDD documentation artifact. Use it to:
- Verify element ID format compliance
- Check for removed/legacy patterns
- Validate threshold tag syntax
- Ensure document ID format correctness

### Coverage

This skill covers all 8 SDD documentation artifact types (Layers 1-8):

| Layer | Document Type | Description |
|-------|---------------|-------------|
| 1 | BRD | Business Requirements Document |
| 2 | PRD | Product Requirements Document |
| 3 | EARS | Easy Approach to Requirements Syntax |
| 4 | BDD | Behavior-Driven Development |
| 5 | ADR | Architecture Decision Record |
| 6 | SPEC | Technical Specification |
| 7 | TDD | Test-Driven Development Guide |
| 8 | IPLAN | Implementation Plan |

**Note**: Code is the output target, not a documentation artifact layer.

---

## 2. Reserved ID Exemption (TYPE-00_*)

### Scope

Documents with reserved ID `000` are FULLY EXEMPT from standard validation.

### Pattern

`{DOC_TYPE}-00_{slug}.{ext}`

### Document Types

- Index documents (e.g., `BRD-00_index.md`, `IPLAN-00_index.yaml`)
- Traceability matrix templates (e.g., `SPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md`)
- Glossaries, registries, checklists

### Rationale

Reserved ID 000 documents are framework infrastructure (indexes, templates, reference materials), not project artifacts requiring traceability or quality gates.

### Validation Behavior

Skip all element ID and traceability checks when filename matches `{TYPE}-00_*` pattern.

---

## 3. Document ID Format (TYPE-NN)

### Pattern

```
TYPE-NN
```

- **TYPE**: Uppercase document type acronym (BRD, PRD, EARS, etc.)
- **Separator**: Single dash `-`
- **NN**: 2+ digit sequential number with leading zeros

### Validation Regex

```regex
^[A-Z]{2,8}-[0-9]{2,}$
```

### Examples

| Document ID | Valid | Reason |
|-------------|-------|--------|
| `BRD-01` | ✅ | Correct format |
| `PRD-02` | ✅ | Correct format |
| `ADR-001` | ✅ | 3-digit ID allowed |
| `IPLAN-12` | ✅ | Correct format |
| `brd-01` | ❌ | Lowercase not allowed |
| `PRD_02` | ❌ | Underscore not allowed |
| `BRD-1` | ❌ | Single digit not allowed |
| `BRD01` | ❌ | Missing dash separator |

### Filename Convention

```
TYPE-NN_descriptive_slug.md
```

Example: `BRD-01_ib_stock_options_mcp_server.md`

### REF Document Pattern

Reference documents use a modified pattern within parent TYPE directories:

| Component | Pattern | Example |
|-----------|---------|---------|
| H1 ID | `{TYPE}-REF-NN` | `# BRD-REF-01: Project Overview` |
| Filename | `{TYPE}-REF-NN_{slug}.md` | `BRD-REF-01_project_overview.md` |
| Location | Within parent TYPE directory | `docs/BRD/BRD-REF-01_project_overview.md` |

**Notes**:
- REF documents are supplementary and do not participate in formal traceability chain
- Similar exemption treatment as `{TYPE}-000` index documents
- Numbering is independent per parent TYPE (BRD-REF-01, ADR-REF-01 are separate sequences)

---

## 4. Element ID Format (TYPE.NN.SS.xxxx)

Element IDs use the 4-segment standard from
`framework/governance/ID_NAMING_STANDARDS.md`. Hierarchical (element-level)
references apply to BRD, PRD, EARS, BDD, ADR, and TDD. SPEC and IPLAN are
referenced at the document level only — see Section 5.

### Pattern

```
{TYPE}.{doc_id}.{section_id}.{hash}
```

| Segment | Description | Format |
|---------|-------------|--------|
| TYPE | Artifact prefix | Uppercase {BRD, PRD, EARS, BDD, ADR, TDD} |
| doc_id | Document number | 2+ digits (e.g., 01) |
| section_id | Section number | 2+ digits (e.g., 07) |
| hash | Content hash (SHA256, first 4 chars) | 4-8 hex chars `[a-f0-9]` |

### Validation Regex

```regex
^[A-Z]+\.[0-9]{2,}\.[0-9]{2,}\.[a-f0-9]{4,8}$
```

### Examples

| Element ID | Valid | Breakdown |
|------------|-------|-----------|
| `BRD.01.07.a7f3` | ✅ | BRD doc 01, section 07, hash a7f3 |
| `PRD.01.09.1dbc` | ✅ | PRD doc 01, section 09, hash 1dbc |
| `EARS.01.03.5e2a` | ✅ | EARS doc 01, section 03, hash 5e2a |
| `BDD.01.03.8f4c` | ✅ | BDD doc 01, section 03, hash 8f4c |
| `ADR.01.03.e5b1` | ✅ | ADR doc 01, section 03, hash e5b1 |
| `TDD.01.04.a3c1` | ✅ | TDD doc 01, section 04, hash a3c1 |
| `AC-001` | ❌ | Legacy pattern - use TYPE.NN.SS.xxxx format |
| `FR-01` | ❌ | Legacy pattern - use TYPE.NN.SS.xxxx format |
| `BRD.01.0701` | ❌ | 3-segment legacy form - section + hash must be separate |
| `BRD-01-07-a7f3` | ❌ | Wrong separator (use dots) |
| `brd.01.07.a7f3` | ❌ | Lowercase type not allowed |

### Heading Format

Element IDs appear as markdown headings:

```markdown
### BRD.01.07.a7f3: User Authentication Acceptance Criteria
#### PRD.01.09.1dbc: User Login Story
```

---

## 5. Reference Granularity (Element vs Document)

The 8-layer model has **no numeric element-type codes**. There is no table
mapping numbers like 01/07/14/26/40 to element kinds. Element identity comes
from the 4-segment `TYPE.NN.SS.xxxx` form (Section 4), where `SS` is the source
**section number** and `xxxx` is a content hash — not a fixed type code.

How a layer is referenced depends only on its granularity:

| Layer | Reference granularity | Reference form | Example |
|-------|----------------------|----------------|---------|
| BRD | element (dotted) | `BRD.NN.SS.xxxx` | `BRD.01.07.a7f3` |
| PRD | element (dotted) | `PRD.NN.SS.xxxx` | `PRD.01.09.1dbc` |
| EARS | element (dotted) | `EARS.NN.SS.xxxx` | `EARS.01.03.5e2a` |
| BDD | element (dotted) | `BDD.NN.SS.xxxx` | `BDD.01.03.8f4c` |
| ADR | element (dotted) | `ADR.NN.SS.xxxx` | `ADR.01.03.e5b1` |
| SPEC | document (dash) | `SPEC-NN` | `SPEC-01` |
| TDD | element (dotted) | `TDD.NN.SS.xxxx` | `TDD.01.04.a3c1` |
| IPLAN | document (dash) | `IPLAN-NN` | `IPLAN-01` |

**Dash document refs** (`SPEC-NN`, `ADR-NN`, `IPLAN-NN`) point at a whole
document. **Dotted element refs** (`TYPE.NN.SS.xxxx`) point at a specific
element within a document. ADR supports both: the document `ADR-NN` and its
elements `ADR.NN.SS.xxxx`.

Test categories (unit / integration / smoke / functional, etc.) are **not** ID
codes in this model — they live as content/`test_focus` within TDD (Layer 7)
test cases, addressed by ordinary `TDD.NN.SS.xxxx` element IDs.

---

## 6. Removed/Legacy Patterns

These patterns are DEPRECATED. Do NOT use them in new documents.

| Removed Pattern | Migration Path | Applies To |
|-----------------|----------------|------------|
| `AC-XXX` | `TYPE.NN.SS.xxxx` | BRD, PRD |
| `FR-XXX` | `TYPE.NN.SS.xxxx` | BRD, PRD |
| `BC-XXX` | `TYPE.NN.SS.xxxx` | BRD, PRD |
| `BA-XXX` | `TYPE.NN.SS.xxxx` | BRD, PRD |
| `QA-XXX` | `TYPE.NN.SS.xxxx` | BRD, PRD |
| `BO-XXX` | `TYPE.NN.SS.xxxx` | BRD |
| `RISK-XXX` | `TYPE.NN.SS.xxxx` | BRD, PRD |
| `METRIC-XXX` | `TYPE.NN.SS.xxxx` | BRD, PRD |
| `Feature F-XXX` | `TYPE.NN.SS.xxxx` | BRD, PRD |
| `Event-XXX` | `TYPE.NN.SS.xxxx` | EARS |
| `State-XXX` | `TYPE.NN.SS.xxxx` | EARS |
| `DEC-XXX` | `TYPE.NN.SS.xxxx` | ADR |
| `ALT-XXX` | `TYPE.NN.SS.xxxx` | ADR |
| `CON-XXX` | `TYPE.NN.SS.xxxx` | ADR |
| `TYPE.NN.xxxx` (3-segment) | `TYPE.NN.SS.xxxx` (4-segment) | all element layers |

### Migration Examples

| Legacy | Unified Format |
|--------|----------------|
| `### AC-001: Login Validation` | `### BRD.01.06.a7f3: Login Validation` |
| `#### FR-01: User Auth` | `#### PRD.01.01.1dbc: User Auth` |
| `### Event-001: KYC Submission` | `### EARS.01.03.5e2a: KYC Submission` |
| `### DEC-01: Use PostgreSQL` | `### ADR.05.03.e5b1: Use PostgreSQL` |
| `### ALT-01: MongoDB Option` | `### ADR.05.04.9c2d: MongoDB Option` |
| `### BRD.02.0601: Login` (3-seg) | `### BRD.02.06.0601` → re-hash to `BRD.02.06.a7f3` |

---

## 7. Threshold Tag Format

### Tag Pattern

```
@threshold: {DOC_TYPE}.{DOC_NUM}.{threshold_key}
```

### Key Format

```
{category}.{subcategory}.{attribute}[.{qualifier}]
```

### Valid Categories

| Category | Description | Example Keys |
|----------|-------------|--------------|
| perf | Performance metrics | `perf.latency.p99` |
| timeout | Timeout values | `timeout.api.request` |
| rate | Rate limits | `rate.api.requests_per_second` |
| retry | Retry policies | `retry.max_attempts` |
| circuit | Circuit breaker | `circuit.failure_threshold` |
| alert | Alerting thresholds | `alert.error_rate.critical` |
| cache | Cache settings | `cache.ttl.session` |
| pool | Connection pools | `pool.max_connections` |
| queue | Queue settings | `queue.max_size` |
| batch | Batch processing | `batch.size.max` |

### Examples

| Threshold Tag | Valid | Breakdown |
|---------------|-------|-----------|
| `@threshold: PRD.035.timeout.partner.bridge` | ✅ | PRD doc 035, timeout category |
| `@threshold: BRD.02.perf.latency.p99` | ✅ | BRD doc 02, performance category |
| `@threshold: ADR.05.circuit.failure_threshold` | ✅ | ADR doc 05, circuit breaker |
| `@threshold: timeout.partner.bridge` | ❌ | Missing doc reference |
| `@threshold: PRD-035.timeout` | ❌ | Wrong separator (dash vs dot) |

### Source Documents for Thresholds

| Doc Type | Threshold Scope |
|----------|-----------------|
| BRD | Business-level thresholds (SLAs, business rules) |
| PRD | Product-level thresholds (user experience, product metrics) |
| ADR | Technical thresholds (architecture decisions, system limits) |

---

## 8. ISO 8601 Datetime Format Standard

### Purpose

All date and time fields in SDD documentation MUST use ISO 8601 datetime format for:
- Accurate upstream drift detection (same-day change tracking)
- Consistent timestamp comparison across tools
- Timezone-aware change tracking
- File system mtime compatibility

### Format Specification

**Required Format**: `YYYY-MM-DDTHH:MM:SS` (ISO 8601 with time)

| Component | Format | Example |
|-----------|--------|---------|
| Date | `YYYY-MM-DD` | `2026-02-10` |
| Separator | `T` | `T` |
| Time | `HH:MM:SS` | `14:30:00` |
| Timezone (optional) | `Z` or `±HH:MM` | `Z` (UTC) or `+05:00` |

### Full Format Options

| Format | Example | Use Case |
|--------|---------|----------|
| **Local time** | `2026-02-10T14:30:00` | Default for most documents |
| **UTC** | `2026-02-10T14:30:00Z` | Cross-timezone systems |
| **With offset** | `2026-02-10T14:30:00+05:00` | Explicit timezone |

### YAML Frontmatter Fields

All datetime fields in YAML frontmatter use ISO 8601:

```yaml
---
title: "BRD-01: Example Document"
custom_fields:
  created_date: "2026-02-10T09:15:00"
  last_updated: "2026-02-10T14:30:00"
  review_date: "2026-02-10T16:45:00"
  fix_date: "2026-02-10T17:00:00"
  approval_date: "2026-02-11T10:00:00"
---
```

### Affected Fields

| Field | Description | Location |
|-------|-------------|----------|
| `last_updated` | Document last modification time | YAML frontmatter |
| `created_date` | Document creation time | YAML frontmatter |
| `fix_date` | Fix report creation time | Fix reports |
| `review_date` | Review execution time | Review reports |
| `approval_date` | Document approval time | Document control |
| `decision_date` | ADR decision time | ADR documents |
| `release_date` | Release/deployment time | SPEC, IPLAN |

### Migration from Date-Only Format

**Deprecated** (date-only):
```yaml
last_updated: "2026-02-10"
```

**Required** (ISO 8601 datetime):
```yaml
last_updated: "2026-02-10T14:30:00"
```

### Validation Regex

```regex
^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$
```

### Placeholder Format

For templates, use `YYYY-MM-DDTHH:MM:SS` as placeholder:

```yaml
# Template placeholder (to be replaced during generation)
last_updated: "YYYY-MM-DDTHH:MM:SS"

# After generation
last_updated: "2026-02-10T14:30:00"
```

### Drift Detection Benefit

ISO 8601 datetime enables same-day drift detection:

| BRD Modified | PRD Created | Date-Only Detection | Datetime Detection |
|--------------|-------------|---------------------|-------------------|
| 2026-02-10T10:00:00 | 2026-02-10T08:00:00 | ❌ Same day, no drift | ✅ Drift detected (BRD newer) |
| 2026-02-10T08:00:00 | 2026-02-10T10:00:00 | ❌ Same day, no drift | ✅ No drift (PRD is newer) |

### Auto-Generation

When generating documents, use current timestamp:

```python
from datetime import datetime

# Generate ISO 8601 timestamp
timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
# Result: "2026-02-10T14:30:00"

# With UTC
timestamp_utc = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
# Result: "2026-02-10T09:30:00Z"
```

---

## 9. Validation Examples by Document Type

### BRD Examples

```markdown
### BRD.02.01.a7f3: User Authentication Requirement
### BRD.02.06.5e2a: Login Acceptance Criteria
### BRD.02.23.1dbc: Revenue Growth Objective
### BRD.02.09.8f4c: User Onboarding Story
@threshold: BRD.02.perf.response_time.max
```

### PRD Examples

```markdown
### PRD.01.09.1dbc: User Login Story
### PRD.01.22.a3c1: Dashboard Feature
### PRD.01.06.e5b1: Feature Acceptance Criteria
@threshold: PRD.01.timeout.session.idle
```

### EARS Examples

```markdown
#### EARS.06.03.5e2a: KYC Submission Event
#### EARS.06.03.9c2d: Pending Status State
```

### BDD Examples

```markdown
### BDD.01.03.8f4c: Successful Login Scenario
### BDD.01.03.b6e0: Login Step
```

### ADR Examples

```markdown
### ADR.05.03.e5b1: Use PostgreSQL Decision
### ADR.05.04.9c2d: MongoDB Alternative
### ADR.05.05.1f7a: Migration Consequence
@threshold: ADR.05.circuit.failure_threshold
```

### SPEC Examples

SPEC is referenced at the document level (dash form):

```markdown
@spec: SPEC-03
@spec: SPEC-06
```

### TDD Examples

```markdown
### TDD.01.04.a3c1: User Authentication Test Case
### TDD.01.04.c2f8: API Integration Test Case
```

### IPLAN Examples

IPLAN is referenced at the document level (dash form):

```markdown
@iplan: IPLAN-01
@iplan: IPLAN-02
```

---

## 10. Pre-Flight Checklist

Run this checklist BEFORE creating any SDD document:

### Document Setup

- [ ] Document ID follows `TYPE-NN` format
- [ ] Filename follows `TYPE-NN_descriptive_slug.md` pattern
- [ ] YAML frontmatter includes correct `artifact_type` and `layer`
- [ ] Not a reserved ID document (TYPE-00_*) requiring exemption

### Element IDs

- [ ] All element IDs use 4-segment dot notation: `TYPE.NN.SS.xxxx`
- [ ] Element hash is 4-8 hex characters (see Section 4)
- [ ] Element hashes are unique within the document
- [ ] Document-level layers (SPEC, IPLAN) use dash refs: `SPEC-NN`, `IPLAN-NN`
- [ ] No legacy patterns (AC-XXX, FR-XXX, DEC-XXX, 3-segment IDs, etc.) are used

### Threshold Tags

- [ ] All `@threshold:` tags include document reference: `TYPE.NN.key`
- [ ] Threshold keys follow category.subcategory.attribute format
- [ ] Categories are from the approved list (perf, timeout, rate, etc.)

### Cross-References

- [ ] Traceability tags use correct prefixes (@brd:, @prd:, @adr:, etc.)
- [ ] Referenced document IDs exist
- [ ] Element ID references are complete (all 4 segments)

---

## 11. Error Recovery

### Detecting Legacy Patterns

Use grep to find legacy patterns:

```bash
# Find all legacy patterns in a file (COMPREHENSIVE - run ALL commands)

# 1. Simple legacy patterns (e.g., FR-001, AC-002)
grep -E "(AC|FR|BC|BA|QA|BO|NFR|RISK|METRIC)-[0-9]+" file.md

# 2. Compound/domain-prefixed patterns (e.g., FR-CICD-001, NFR-PERF-002)
#    CRITICAL: These patterns have additional components between prefix and number
grep -E "(AC|FR|BC|BA|QA|BO|NFR)(-[A-Za-z0-9]+)+-[0-9]+" file.md

# 3. Other legacy patterns
grep -E "(Event|State|TASK|Phase|IP|IF|DM|CC)-[0-9]+" file.md
grep -E "(DEC|ALT|CON)-[0-9]+" file.md
grep -E "Feature F-[0-9]+" file.md
grep -E "T-[0-9]+" file.md

# 4. Combined single-command detection (recommended for automation)
grep -E "(AC|FR|BC|BA|QA|BO|NFR|RISK|METRIC)(-[A-Za-z0-9]+)*-[0-9]+" file.md
```

**Pattern Explanation**:

| Pattern Component | Matches | Example |
|-------------------|---------|---------|
| `(FR\|AC\|...)` | Legacy prefix | `FR`, `AC`, `NFR` |
| `(-[A-Za-z0-9]+)*` | Optional domain components | `-CICD`, `-AUTH-V2` |
| `-[0-9]+` | Numeric ID | `-001`, `-42` |

**Examples Caught**:

| Legacy Pattern | Detected By | Migration Target |
|----------------|-------------|------------------|
| `FR-001` | Simple pattern | `BRD.NN.SS.xxxx` |
| `FR-CICD-001` | Compound pattern | `BRD.NN.SS.xxxx` |
| `NFR-PERF-002` | Compound pattern | `BRD.NN.SS.xxxx` |
| `AC-AUTH-V2-003` | Compound pattern | `BRD.NN.SS.xxxx` |

### Migration Procedure

1. **Identify the document type and number** from the filename
   - Example: `BRD-02_requirements.yaml` → TYPE=BRD, doc_id=02

2. **Determine the source section** that contains the element
   - Example: an Acceptance Criteria item in Section 6 → section_id=06
   - Example: a Decision in Section 3 of an ADR → section_id=03

3. **Construct the unified ID** (4-segment)
   - Pattern: `{TYPE}.{doc_id}.{section_id}.{hash}` where `hash` is the
     first 4 hex chars of the element's content SHA256
   - Example: `AC-001` in BRD-02 (section 6) → `BRD.02.06.a7f3`
   - Example: `DEC-01` in ADR-05 (section 3) → `ADR.05.03.e5b1`
   - For SPEC/IPLAN, use document-level dash refs instead: `SPEC-NN`, `IPLAN-NN`

4. **Replace all occurrences**, then re-verify with the grep patterns above.

5. **Validate the result**
   ```bash
   # Verify no legacy patterns remain (COMPREHENSIVE check)
   # Must return empty for all commands
   grep -E "(AC|FR|BC|BA|QA|BO|NFR|DEC|ALT|CON)-[0-9]+" file.yaml
   grep -E "(AC|FR|BC|BA|QA|BO|NFR)(-[A-Za-z0-9]+)+-[0-9]+" file.yaml
   # Verify no 3-segment legacy element IDs remain
   grep -E "[A-Z]+\.[0-9]{2,}\.[a-z0-9]{4,}([^.]|$)" file.yaml
   ```

### Common Migration Errors

| Error | Cause | Fix |
|-------|-------|-----|
| 3-segment ID | `BRD.02.0601` (section + item fused) | Split: `BRD.02.06.a7f3` |
| Missing section segment | `BRD.02.a7f3` | Include section: `BRD.02.06.a7f3` |
| Dash instead of dot | `BRD-02-06-a7f3` | Use dots: `BRD.02.06.a7f3` |
| Lowercase type | `brd.02.06.a7f3` | Uppercase: `BRD.02.06.a7f3` |
| Dotted ref for SPEC/IPLAN | `SPEC.06.0101` | Use dash doc ref: `SPEC-06` |

---

## 12. Source References

### Primary Sources

| Document | Location | Content |
|----------|----------|---------|
| ID Naming Standards | `framework/governance/ID_NAMING_STANDARDS.md` | Canonical document IDs, element IDs, tag formats, file naming |
| Layer Registry | `framework/registry/LAYER_REGISTRY.yaml` | The 8-layer roster, chains, and per-layer folders/templates |
| Threshold Naming Rules | `framework/governance/THRESHOLD_NAMING_RULES.md` | Threshold tags, key formats, categories |

### Per-Layer Authoring Guidance

The framework is spec-only (no runtime validation scripts). Each layer's
template and README carry its declarative rules; this skill is the naming
validator. Per-layer sources live under `framework/layers/<NN>_<X>/`:

| Document Type | Layer Folder |
|---------------|-------------------------------|
| BRD | `framework/layers/01_BRD/` |
| PRD | `framework/layers/02_PRD/` |
| EARS | `framework/layers/03_EARS/` |
| BDD | `framework/layers/04_BDD/` |
| ADR | `framework/layers/05_ADR/` |
| SPEC | `framework/layers/06_SPEC/` |
| TDD | `framework/layers/07_TDD/` |
| IPLAN | `framework/layers/08_IPLAN/` |

### Related Skills

| Skill | Purpose |
|-------|---------|
| `../doc-validator/` | Cross-document validation of SDD documents |
| `../doc-flow/` | SDD workflow orchestration |
| `../trace-check/` | Traceability validation |

---

### Diagram Standards

All diagrams MUST use Mermaid syntax. Text-based diagrams (ASCII art, box drawings) are prohibited.
See the `mermaid-gen` skill and `framework/governance/DIAGRAM_STANDARDS.md`.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.8 | 2026-05-22 | **8-layer migration (PLM-B6)**: Retired the legacy 12-layer roster (removed SYS/REQ/CTR/TSPEC/TASKS); roster is now BRD(1)·PRD(2)·EARS(3)·BDD(4)·ADR(5)·SPEC(6)·TDD(7)·IPLAN(8)→Code. Deleted the numeric element-type-code system entirely; element IDs are now the 4-segment `TYPE.NN.SS.xxxx` (section + 4-hex-char hash) per `framework/governance/ID_NAMING_STANDARDS.md`, with dash document refs `SPEC-NN`/`ADR-NN`/`IPLAN-NN`. Repointed all paths to `framework/layers/<NN>_<X>/`; removed dead validation-script references (framework is spec-only). |
| 1.7 | 2026-02-27 | **Compound legacy pattern detection**: Enhanced Section 11 grep patterns to catch compound/domain-prefixed legacy IDs (e.g., `FR-CICD-001`, `NFR-PERF-002`); Added regex `(-[A-Za-z0-9]+)*` to match optional domain components; Added pattern explanation table and examples; Updated validation step to run comprehensive checks |
| 1.6 | 2026-02-10 | Added Section 8: ISO 8601 Datetime Format Standard - all date fields now require `YYYY-MM-DDTHH:MM:SS` format for precise drift detection; Deprecated date-only format |
| 1.5 | 2026-02-10 | Added element code 33 (Benefit Statement) for BRD Section 2.5; Updated BRD Quick Lookup to include code 33; Added BRD examples for code 33 |
| 1.4 | 2026-02-08 | Added element code 32 (Architecture Topic) for BRD Section 7.2; Updated BRD Quick Lookup to include code 32; Added BRD examples for code 32 |
| 1.3 | 2026-02-08 | (Superseded by 1.8) Adjusted layer assignments and element codes for the then-current registry; the legacy roster and numeric element codes referenced here were retired in 1.8. |
| 1.2 | 2026-01-17 | Updated to 11 active artifact types; Removed legacy element codes 19, 31 |
| 1.1 | 2025-12-29 | Added Reserved ID Exemption, REF document pattern, ADR removed patterns, fixed element type codes for BRD |
| 1.0 | 2025-12-19 | Initial release with all 31 element codes and 18 removed patterns |
