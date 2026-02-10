---
title: "Change Classification Guide"
tags:
  - framework-guide
  - change-management
  - decision-guide
  - shared-architecture
custom_fields:
  document_type: guide
  artifact_type: CHG
  priority: shared
  development_status: active
  version: "1.0"
  last_updated: "2026-02-05T00:00:00"
---

# Change Classification Guide

This guide provides detailed criteria for classifying changes into L1 (Patch), L2 (Minor), or L3 (Major) levels.

## 1. Classification Overview

```
┌────────────────────────────────────────────────────────────────────────────┐
│                      CHANGE CLASSIFICATION SPECTRUM                        │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│   L1 PATCH              L2 MINOR                L3 MAJOR                  │
│   ──────────            ──────────              ──────────                │
│                                                                            │
│   ▪ Bug fixes           ▪ New features          ▪ Architecture pivots     │
│   ▪ Typos               ▪ Enhancements          ▪ Breaking changes        │
│   ▪ Clarifications      ▪ Extensions            ▪ Mass deprecation        │
│   ▪ Minor refactoring   ▪ Non-breaking adds     ▪ Technology switches     │
│                                                                            │
│   Process: None         Process: Lightweight    Process: Full CHG         │
│   Template: None        Template: MVP           Template: Full            │
│   Archive: No           Archive: Optional       Archive: Required         │
│                                                                            │
│   ◄─────────────── Increasing Impact & Overhead ──────────────────►       │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

## 2. Decision Flowchart

Use this flowchart to determine the appropriate change level:

```
                         ┌─────────────────────────┐
                         │    Change Requested     │
                         └───────────┬─────────────┘
                                     │
                                     ▼
                         ┌─────────────────────────┐
                         │  Does it break backward │
                         │  compatibility?         │
                         └───────────┬─────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │ NO                              │ YES
                    ▼                                 ▼
          ┌─────────────────────┐          ┌─────────────────────┐
          │ Does it require     │          │      L3 MAJOR       │
          │ ADR changes?        │          │   (Full CHG)        │
          └─────────┬───────────┘          └─────────────────────┘
                    │
       ┌────────────┴────────────┐
       │ NO                      │ YES
       ▼                         ▼
┌─────────────────────┐  ┌─────────────────────┐
│ Does it affect more │  │      L3 MAJOR       │
│ than 3 layers?      │  │   (Full CHG)        │
└─────────┬───────────┘  └─────────────────────┘
          │
     ┌────┴────┐
     │ NO      │ YES
     ▼         ▼
┌──────────┐  ┌─────────────────────┐
│ Is it a  │  │      L2 MINOR       │
│ bug fix? │  │  (Lightweight CHG)  │
└────┬─────┘  └─────────────────────┘
     │
┌────┴────┐
│ YES     │ NO
▼         ▼
┌──────────┐  ┌─────────────────────┐
│ L1 PATCH │  │      L2 MINOR       │
│ (No CHG) │  │  (Lightweight CHG)  │
└──────────┘  └─────────────────────┘
```

## 3. L1 Patch - Detailed Criteria

### 3.1 Definition

L1 Patch is for **minimal changes that fix issues without modifying behavior or contracts**.

### 3.2 Qualifying Criteria

A change qualifies as L1 if ALL of the following are true:

| # | Criterion | Must Be |
|---|-----------|---------|
| 1 | Backward compatible | ✅ Yes |
| 2 | Affects ADR/architecture | ❌ No |
| 3 | Changes API contracts | ❌ No |
| 4 | Affects more than 1 layer | ❌ No |
| 5 | Requires stakeholder approval | ❌ No |
| 6 | Deprecates existing artifacts | ❌ No |

### 3.3 Examples

| Change | Classification | Reason |
|--------|----------------|--------|
| Fix typo in BRD description | ✅ L1 | No functional change |
| Correct calculation bug in code | ✅ L1 | Code-only fix, behavior as designed |
| Update outdated comment | ✅ L1 | Documentation only |
| Fix failing unit test (test was wrong) | ✅ L1 | Test correction, not behavior change |
| Refactor method for readability | ✅ L1 | No behavioral change |
| Security patch for dependency | ✅ L1* | *Unless API changes |

### 3.4 Process

```bash
# L1 Patch Process
1. Edit artifact directly
2. Increment patch version (1.0.0 → 1.0.1)
3. Run relevant tests
4. Commit with "fix: [description]"
```

**No CHG document required.**

## 4. L2 Minor - Detailed Criteria

### 4.1 Definition

L2 Minor is for **feature additions, enhancements, and non-breaking changes that affect multiple layers**.

### 4.2 Qualifying Criteria

A change qualifies as L2 if ALL of the following are true:

| # | Criterion | Must Be |
|---|-----------|---------|
| 1 | Backward compatible | ✅ Yes |
| 2 | Affects ADR/architecture | ❌ No |
| 3 | Changes API contracts | ✅ Can add (not break) |
| 4 | Affects 2-5 layers | ✅ Yes |
| 5 | Requires regeneration | ✅ Partial |
| 6 | Deprecates artifacts | ⚪ Optional |

### 4.3 Examples

| Change | Classification | Reason |
|--------|----------------|--------|
| Add new optional field to API | ✅ L2 | Non-breaking addition |
| New feature with 4 layers affected | ✅ L2 | Multi-layer but compatible |
| Enhance existing capability | ✅ L2 | Extension, not breaking |
| Add new test type (e.g., PTEST) | ✅ L2 | New capability |
| Update dependency (minor version) | ✅ L2 | May affect multiple layers |
| Performance optimization in SPEC | ✅ L2 | Design change, compatible |

### 4.4 Process

```bash
# L2 Minor Process
1. Create CHG directory: docs/CHG/CHG-XX_{slug}/
2. Create CHG document using CHG-MVP-TEMPLATE.md
3. Update affected artifacts (version or new)
4. Update TSPEC if L9+ affected
5. Repair traceability links
6. Run tests and validate
7. Set CHG status to Completed
```

**Use `CHG-MVP-TEMPLATE.md`**

## 5. L3 Major - Detailed Criteria

### 5.1 Definition

L3 Major is for **breaking changes, architectural pivots, and mass deprecations**.

### 5.2 Qualifying Criteria

A change qualifies as L3 if ANY of the following are true:

| # | Criterion | If True → L3 |
|---|-----------|--------------|
| 1 | Breaks backward compatibility | ✅ L3 |
| 2 | Requires ADR changes | ✅ L3 |
| 3 | Changes fundamental architecture | ✅ L3 |
| 4 | Deprecates multiple artifacts | ✅ L3 |
| 5 | Affects >5 layers significantly | ✅ L3 |
| 6 | Technology stack change | ✅ L3 |
| 7 | Requires stakeholder sign-off | ✅ L3 |

### 5.3 Examples

| Change | Classification | Reason |
|--------|----------------|--------|
| Switch from REST to GraphQL | ✅ L3 | Architecture change |
| Database migration (PostgreSQL→MongoDB) | ✅ L3 | Technology stack |
| Monolith to microservices | ✅ L3 | Fundamental architecture |
| Remove deprecated feature | ✅ L3 | Mass deprecation |
| Breaking API change (v1→v2) | ✅ L3 | Backward incompatible |
| Regulatory compliance overhaul | ✅ L3 | Multiple layers, policy change |
| Security incident requiring redesign | ✅ L3 | Architecture response |

### 5.4 Process

```bash
# L3 Major Process (6 Steps)
1. INITIALIZE
   - Create CHG directory with archive/
   - Create CHG document (CHG-TEMPLATE.md)
   - Create implementation_plan.md

2. ARCHIVE & DEPRECATE
   - Move old artifacts to archive/
   - Add deprecation notices

3. SUPERSEDE
   - Create new artifacts in standard locations
   - Set "Supersedes" metadata

4. REPAIR TRACEABILITY
   - Update all references
   - Verify no orphans

5. EXECUTE
   - Implement new TASKS
   - Run TSPEC tests
   - Validate all layers

6. CLOSE
   - Update status to Completed
   - Document lessons learned
```

**Use `CHG-TEMPLATE.md`**

## 6. Edge Cases & Escalation

### 6.1 When Unsure

If you're unsure about classification:

1. **Default to the higher level** (L1→L2 or L2→L3)
2. **Consult the impact matrix** - count affected layers
3. **Ask**: "Will this break anything for existing users?"
4. **Ask**: "Does this change HOW the system works (architecture)?"

### 6.2 Escalation Triggers

| Situation | Escalate To |
|-----------|-------------|
| L1 affects more layers than expected | → L2 |
| L2 requires ADR change | → L3 |
| L2 breaks backward compatibility | → L3 |
| Security vulnerability critical | → L3 (fast-track) |
| Regulatory deadline | → L3 (with timeline) |

### 6.3 Fast-Track L3

For critical situations (security, compliance), L3 can be fast-tracked:

1. Create minimal CHG document
2. Execute with expedited approval
3. Complete full documentation post-implementation
4. Flag as "Fast-Track" in status

## 7. Classification by Change Source

### 7.1 Source × Level Matrix

| Change Source | L1 Typical | L2 Typical | L3 Typical |
|---------------|------------|------------|------------|
| **Upstream** | Typo in BRD | New feature request | Strategic pivot |
| **Midstream** | Spec clarification | Design enhancement | Architecture change |
| **Downstream** | Code bug fix | Test improvement | Fundamental impl. change |
| **External** | Security patch | Dep. minor update | Platform migration |
| **Feedback** | Quick hotfix | UX improvement | Major redesign |

### 7.2 Source-Specific Guidance

See detailed guides in `sources/` directory:
- `UPSTREAM_CHANGE_GUIDE.md`
- `MIDSTREAM_CHANGE_GUIDE.md`
- `DOWNSTREAM_CHANGE_GUIDE.md`
- `EXTERNAL_CHANGE_GUIDE.md`
- `FEEDBACK_CHANGE_GUIDE.md`

## 8. Classification Checklist

Use this checklist to confirm your classification:

### 8.1 L1 Patch Checklist

- [ ] Change is a bug fix, typo, or clarification
- [ ] No functional behavior change
- [ ] No API/contract changes
- [ ] Only 1 layer affected
- [ ] No stakeholder approval needed
- [ ] No deprecation required

**If all checked → L1 is correct**

### 8.2 L2 Minor Checklist

- [ ] Change is backward compatible
- [ ] No architecture (ADR) changes
- [ ] 2-5 layers affected
- [ ] Partial regeneration needed
- [ ] May add (not break) contracts
- [ ] Optional deprecation only

**If all checked → L2 is correct**

### 8.3 L3 Major Checklist

- [ ] Change breaks compatibility OR
- [ ] Architecture (ADR) change required OR
- [ ] Technology stack change OR
- [ ] >5 layers significantly affected OR
- [ ] Mass deprecation required OR
- [ ] Stakeholder sign-off required

**If any checked → L3 is required**

## 9. Quick Reference Card

```
┌────────────────────────────────────────────────────────────────┐
│              CHANGE CLASSIFICATION QUICK REFERENCE             │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  L1 PATCH                                                      │
│  ─────────                                                     │
│  ✓ Bug fix, typo, clarification                               │
│  ✓ Single layer only                                          │
│  ✓ No CHG document needed                                     │
│  ✓ Version: 1.0.0 → 1.0.1                                     │
│                                                                │
│  L2 MINOR                                                      │
│  ─────────                                                     │
│  ✓ New feature, enhancement                                   │
│  ✓ 2-5 layers affected                                        │
│  ✓ Use CHG-MVP-TEMPLATE.md                                    │
│  ✓ Version: 1.0.0 → 1.1.0                                     │
│                                                                │
│  L3 MAJOR                                                      │
│  ─────────                                                     │
│  ✓ Breaking change, pivot                                     │
│  ✓ >5 layers or architecture change                           │
│  ✓ Use CHG-TEMPLATE.md + archive/                             │
│  ✓ Version: 1.0.0 → 2.0.0                                     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

**Related Documents**:
- [CHANGE_MANAGEMENT_GUIDE.md](./CHANGE_MANAGEMENT_GUIDE.md)
- [CHG-TEMPLATE.md](./CHG-TEMPLATE.md)
- [CHG-MVP-TEMPLATE.md](./CHG-MVP-TEMPLATE.md)
