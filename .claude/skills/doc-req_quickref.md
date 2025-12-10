# doc-req - Quick Reference

**Skill ID:** doc-req
**Layer:** 7 (Atomic Requirements)
**Purpose:** Create atomic, implementation-ready requirements using REQ v3.0 format

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
2. Apply REQ v3.0 format (12 required sections)
3. Calculate SPEC-readiness score (≥90% required)
4. Define interface specifications and data schemas
5. Document error handling and configuration

## Output Location

```
docs/REQ/REQ-{domain}-{subdomain}-NNN_{slug}.md
```

## REQ v3.0 Format (12 Sections)

1. Requirement Overview
2. Acceptance Criteria
3. **Interface Specifications** (NEW)
4. **Data Schemas** (NEW)
5. **Error Handling Specifications** (NEW)
6. **Configuration Specifications** (NEW)
7. **Quality Attributes** (NEW)
8. Dependencies
9. Implementation Guidance
10. Testing Strategy
11. Verification Methods
12. Traceability

## SPEC-Ready Score

```markdown
**Current Score**: 11/12 sections = 91.7% ✓
**Quality Gate**: ≥90% (11/12 sections minimum)
```

## Upstream/Downstream

```
BRD, PRD, EARS, BDD, ADR, SYS → REQ → IMPL, CTR, SPEC
```

## Quick Validation

- [ ] All 12 required sections completed
- [ ] SPEC-Ready Score ≥90%
- [ ] Domain/subdomain organization in ID
- [ ] Interface specifications detailed (Section 3)
- [ ] Data schemas with validation rules (Section 4)
- [ ] Atomic (single responsibility per REQ)
- [ ] Cumulative tags: @brd through @sys (6 tags)

## Template Location

```
ai_dev_flow/REQ/REQ-TEMPLATE.md
```

## Related Skills

- `doc-sys` - System requirements (upstream)
- `doc-impl` - Implementation approach (downstream, optional)
- `doc-spec` - Technical specifications (downstream)
