# Implementation Plan - Feature-Level Traceability Tag Fix

**Created**: 2025-12-01 20:06:09 EST
**Status**: Ready for Implementation

## Objective

Fix 4 critical inconsistencies in feature-level traceability tags across the SDD framework, implementing:
- Unified internal feature ID standard (simple numeric `001`, `002`, `003`)
- Categorical NFR prefixes with AI auto-assignment (`NFR-PERF-001`, `NFR-SEC-001`, etc.)
- Clear cross-reference format documentation

## Context

### Problem Statement
The framework has **two competing paradigms** for internal feature IDs:

| Paradigm | Format | Where Defined | Example |
|----------|--------|---------------|---------|
| **Simple Numeric** | `001`, `002`, `003` | `ID_NAMING_STANDARDS.md` lines 360-381 | `### 001: Feature Name` |
| **Prefixed Compound** | `FR-NNN-NN`, `BO-NNN`, `NFR-NNN` | Various SCHEMA and TEMPLATE files | `FR-022-015`, `BO-001`, `NFR-PERF-001` |

### 4 Critical Conflicts Identified

1. **FR Format Mismatch** (CRITICAL): PRD_SCHEMA uses `FR-\d{3}-\d{2,3}`, SYS_SCHEMA uses `FR-\d{3}`
2. **Simple vs Prefixed Internal IDs** (CRITICAL): ID_NAMING_STANDARDS says simple, PRD_SCHEMA says compound
3. **NFR Format Inconsistency** (HIGH): BRD uses `NFR-001`, EARS/SYS use categorical `NFR-PERF-001`
4. **Cross-Reference Ambiguity** (HIGH): Unclear if `@brd: BRD-017:001` refers to simple or shortened compound

### Key Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Internal Feature IDs | Simple numeric (`001`, `002`, `003`) | Document context provides namespace |
| NFR Format | Embedded categorical (`NFR-PERF-001`) | Self-documenting, clear traceability |
| AI Category Assignment | Keyword matching + context analysis | Automated, accurate |

### NFR Category Standard

| Category | Prefix | Keywords for AI Detection |
|----------|--------|---------------------------|
| Performance | `NFR-PERF-` | latency, response time, throughput, p95, p99, milliseconds, TPS |
| Reliability | `NFR-REL-` | uptime, availability, MTBF, MTTR, error rate, failover, recovery |
| Scalability | `NFR-SCAL-` | concurrent users, horizontal scaling, load, capacity, volume |
| Security | `NFR-SEC-` | authentication, authorization, encryption, audit, compliance, RBAC |
| Observability | `NFR-OBS-` | logging, monitoring, alerting, tracing, metrics, dashboard |
| Maintainability | `NFR-MAINT-` | code coverage, documentation, deployment, testing, CI/CD |

## Task List

### Completed
- [x] Audit all CREATION_RULES files for feature ID formats
- [x] Audit all TEMPLATE files for feature ID formats
- [x] Audit SCHEMA files for feature ID validation patterns
- [x] Audit TRACEABILITY.md and related docs
- [x] Create gap analysis report

### Pending
- [ ] Phase 1: Update ID_NAMING_STANDARDS.md with NFR section (IN PROGRESS)
- [ ] Phase 2: Update PRD_SCHEMA.yaml and SYS_SCHEMA.yaml
- [ ] Phase 3: Update CREATION_RULES files
- [ ] Phase 4: Update TEMPLATE files
- [ ] Phase 5: Update reference docs (TRACEABILITY.md)
- [ ] Phase 6: Verify consistency and cleanup

### Notes
- ~260 lines of changes across 12 files
- Schema files are authoritative - update first
- Templates must align with schemas

## Implementation Guide

### Prerequisites
- Access to `/opt/data/docs_flow_framework/ai_dev_flow/`
- Understanding of SDD framework 16-layer structure
- Review gap analysis: `work_plans/feature-level-traceability-gap-analysis_20251201.md`
- Review audit report: `FEATURE_ID_AUDIT_REPORT.md`

### Execution Steps

#### Phase 1: Update ID_NAMING_STANDARDS.md (Authoritative Standard)
**File**: `ai_dev_flow/ID_NAMING_STANDARDS.md`
**Action**: Add new section after line 381

Add NFR Category Auto-Assignment section with:
```markdown
## NFR Category Auto-Assignment

AI assistants should automatically assign NFR categories based on:

### 1. Keyword Matching (Primary)

| Category | Trigger Keywords |
|----------|-----------------|
| PERF | latency, response time, throughput, p50, p95, p99, milliseconds, TPS, RPS |
| REL | uptime, availability, MTBF, MTTR, error rate, failover, recovery, redundancy |
| SCAL | concurrent, horizontal, vertical, scaling, load, capacity, volume, elasticity |
| SEC | auth, encrypt, RBAC, compliance, audit, token, certificate, vulnerability |
| OBS | log, monitor, alert, trace, metric, dashboard, APM, health check |
| MAINT | coverage, deploy, CI/CD, documentation, refactor, technical debt |

### 2. Context Analysis (Secondary)

When keywords are ambiguous, analyze:
- Section header context (e.g., "## Performance Requirements" → PERF)
- Related requirements in same document
- Upstream BRD/PRD categorization
```

#### Phase 2: Update SCHEMA Files (Validation Patterns)

**File 1**: `ai_dev_flow/PRD/PRD_SCHEMA.yaml` (lines 151-159)
- Change FR pattern from `^FR-\d{3}-\d{2,3}$` to allow simple numeric
- Add comment explaining simple format preference

**File 2**: `ai_dev_flow/SYS/SYS_SCHEMA.yaml` (lines 220-266)
- Update NFR categories to use full prefixes: `NFR-PERF-`, `NFR-REL-`, `NFR-SCAL-`, `NFR-SEC-`, `NFR-OBS-`, `NFR-MAINT-`
- Align FR pattern documentation

#### Phase 3: Update CREATION_RULES (Guidance)

**File 1**: `ai_dev_flow/PRD/PRD_CREATION_RULES.md` (lines 797-873)
- Update section 20 "Feature ID Naming Standard" to align with simple numeric
- Remove compound `FR-NNN-NN` requirement

**File 2**: `ai_dev_flow/BRD/BRD_CREATION_RULES.md` (~line 1338)
- Add NFR categorical prefix rules
- Add AI keyword detection guidance

**File 3**: `ai_dev_flow/EARS/EARS_CREATION_RULES.md`
- Ensure NFR examples use categorical format
- Add note about inheriting NFR IDs from BRD

#### Phase 4: Update TEMPLATES (Examples)

**File 1**: `ai_dev_flow/BRD/BRD-TEMPLATE.md` (lines 655-748)
- Update NFR-001 through NFR-046 to categorical format
- Group by category in section 5

**File 2**: `ai_dev_flow/PRD/PRD-TEMPLATE.md` (lines 369-392)
- Update feature ID examples to simple numeric

**File 3**: `ai_dev_flow/EARS/EARS-TEMPLATE.md` (lines 142-155)
- Verify NFR examples use consistent categorical format

#### Phase 5: Update Reference Docs

**File 1**: `ai_dev_flow/TRACEABILITY.md` (lines 463-491, 550-578)
- Update cross-reference examples
- Add NFR categorical prefix reference

**File 2**: `ai_dev_flow/COMPLETE_TAGGING_EXAMPLE.md`
- Ensure all NFR examples use categorical format
- Verify cross-references consistent

**File 3**: `ai_dev_flow/README.md` (line 778)
- Update Layer 6 SYS description for NFR format

#### Phase 6: Cleanup and Verification
- Run validation scripts
- Update `FEATURE_ID_AUDIT_REPORT.md` with resolution status
- Verify no conflicting patterns between files

### Verification

After implementation, verify:
- [ ] All NFRs in templates use `NFR-{CATEGORY}-NNN` format
- [ ] ID_NAMING_STANDARDS has complete NFR section
- [ ] PRD_SCHEMA no longer requires compound FR format
- [ ] Cross-reference examples consistent in TRACEABILITY.md
- [ ] README Layer 6 description updated
- [ ] No conflicting patterns between SCHEMA files

### Expected Outcomes
- Unified feature ID format across all 16 layers
- Automated NFR categorization via AI keyword matching
- Clear cross-reference format: `@type: DOC-NNN:NNN` or `@type: DOC-NNN:NFR-CAT-NNN`
- No validation errors from schema conflicts

## References

### Related Files
- `/opt/data/docs_flow_framework/ai_dev_flow/ID_NAMING_STANDARDS.md` - Authoritative naming standard
- `/opt/data/docs_flow_framework/ai_dev_flow/TRACEABILITY.md` - Cross-layer traceability guide
- `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD_SCHEMA.yaml` - PRD validation schema
- `/opt/data/docs_flow_framework/ai_dev_flow/SYS/SYS_SCHEMA.yaml` - SYS validation schema

### Documentation
- Gap analysis: `/opt/data/docs_flow_framework/work_plans/feature-level-traceability-gap-analysis_20251201.md`
- Audit report: `/opt/data/docs_flow_framework/FEATURE_ID_AUDIT_REPORT.md`

### Estimated Changes

| File | Lines Changed | Type |
|------|---------------|------|
| ID_NAMING_STANDARDS.md | +60 | New section |
| PRD_SCHEMA.yaml | ~10 | Pattern update |
| SYS_SCHEMA.yaml | ~20 | Category prefix update |
| PRD_CREATION_RULES.md | ~30 | Section rewrite |
| BRD_CREATION_RULES.md | +40 | New section |
| BRD-TEMPLATE.md | ~50 | NFR reorganization |
| TRACEABILITY.md | ~20 | Example updates |
| Others | ~30 | Minor updates |

**Total: ~260 lines across 12 files**
