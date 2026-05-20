# doc-req - Quick Reference

**Skill ID:** doc-req
**Layer:** 7 (Atomic Requirements)
**Purpose:** Create atomic, implementation-ready requirements using REQ MVP format

## Quick Start

```bash
# Invoke skill
skill: "doc-req"

# Common requests
- "Create atomic requirements from SYS-001"
- "Decompose system requirements for validation service"
- "Generate Layer 7 requirements with SPEC-ready score"
```

## What This Skill Does

1. Decompose SYS into atomic requirements
2. Apply REQ MVP format (11 required sections)
3. Calculate SPEC-readiness score (≥90% required)
4. Define interface specifications and data schemas
5. Document error handling and configuration

## Output Location

```
docs/07_REQ/REQ-NN_{slug}/REQ-NN_{slug}.md
```

## REQ MVP Format (11 Sections)

| # | Section | Purpose |
|---|---------|---------|
| 1 | Document Control | Metadata, SPEC-Ready Score |
| 2 | Requirement Description | Atomic requirement + context + scenario |
| 3 | Functional Specification | Core capabilities + business rules + I/O |
| 4 | Interface Definition | API contract + schemas/DTOs |
| 5 | Error Handling | Exception catalog + recovery strategies |
| 6 | Quality Attributes | Performance/security/reliability targets |
| 7 | Configuration | Parameters, feature flags, validation |
| 8 | Testing Requirements | Unit, Integration, BDD scenarios |
| 9 | Acceptance Criteria | ≥3 measurable criteria (MVP) |
| 10 | Traceability | Upstream chain, downstream artifacts, tags |
| 11 | Implementation Notes | Technical approach, code locations, dependencies |

## SPEC-Ready Score

```markdown
**Current Score**: 10/11 sections = 91% ✓
**Quality Gate**: ≥90% (10/11 sections minimum)
```

## Upstream/Downstream

```
BRD, PRD, EARS, BDD, ADR, SYS → REQ → CTR, SPEC, TASKS
```

## Quick Validation

- [ ] All 11 required sections completed
- [ ] SPEC-Ready Score ≥90%
- [ ] Nested folder structure (REQ-NN_{slug}/)
- [ ] Interface specifications detailed (Section 4)
- [ ] Data schemas with validation rules (Section 4)
- [ ] Atomic (single responsibility per REQ)
- [ ] Cumulative tags: @brd through @sys (6 tags)

## Template Location

```
framework/07_REQ/REQ-MVP-TEMPLATE.md
```

## Related Skills

- `doc-sys` - System requirements (upstream)
- `doc-ctr` - Data contracts (downstream, optional)
- `doc-spec` - Technical specifications (downstream)
