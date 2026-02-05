---
id: CHG-XX
title: Title of Change
tags:
  - change-document
  - minor-change
  - shared-architecture
custom_fields:
  document_type: change-record
  artifact_type: CHG
  change_level: L2
  change_source: null
  development_status: proposed
status: Proposed
date: YYYY-MM-DD
author: [Author Name]
affected_layers: []
---

# CHG-XX: [Title of Change]

> **Change Level**: L2 (Minor) - Lightweight CHG process
> **Change Source**: [Upstream | Midstream | Downstream | External | Feedback]
> **Entry Gate**: [GATE-01 | GATE-05 | GATE-09 | GATE-12]

### Gate Status

| Gate | Applicable | Status |
|------|------------|--------|
| GATE-01 | [ ] Yes / [ ] No | [ ] Passed / [ ] N/A |
| GATE-05 | [ ] Yes / [ ] No | [ ] Passed / [ ] N/A |
| GATE-09 | [ ] Yes / [ ] No | [ ] Passed / [ ] N/A |
| GATE-12 | [ ] Yes / [ ] No | [ ] Passed / [ ] N/A |

---

## 1. Change Summary

### 1.1 Description

[Brief description of what is being changed and why - 2-3 sentences]

### 1.2 Classification Confirmation

| Criterion | Value | L2 Requirement |
|-----------|-------|----------------|
| Backward Compatible | Yes/No | Must be Yes |
| ADR Changes Required | Yes/No | Must be No |
| Layers Affected | [count] | Should be 2-5 |
| Breaking Changes | Yes/No | Must be No |

**Confirmed L2**: [ ] Yes, this change qualifies as L2 Minor

### 1.3 Change Source

| Source | Selected | Details |
|--------|----------|---------|
| Upstream (L1-L4) | ☐ | |
| Midstream (L5-L11) | ☐ | |
| Downstream (L12-L14) | ☐ | |
| External | ☐ | |
| Feedback | ☐ | |

## 2. Impact Analysis

### 2.1 Affected Layers

| Layer | Artifact | Impact | Action |
|-------|----------|--------|--------|
| [N] | [ID] | [Description] | Update/New/None |

### 2.2 Unchanged Components

[List what is explicitly NOT changing to prevent scope creep]

- Component A - No changes
- Component B - No changes

## 3. Implementation

### 3.1 Changes Made

| # | Artifact | Before | After | Status |
|---|----------|--------|-------|--------|
| 1 | | | | ☐ Pending |
| 2 | | | | ☐ Pending |
| 3 | | | | ☐ Pending |

### 3.2 TSPEC Updates

> Required if SPEC (L9) or lower layers are affected

| Test Spec | Update Required | Status |
|-----------|-----------------|--------|
| UTEST | Yes/No | ☐ |
| ITEST | Yes/No | ☐ |
| STEST | Yes/No | ☐ |
| FTEST | Yes/No | ☐ |

## 4. Validation

### 4.1 Tests

- [ ] Affected unit tests pass
- [ ] Affected integration tests pass
- [ ] TSPEC validation passes (if applicable)
- [ ] No regression in existing functionality

### 4.2 Traceability

- [ ] Cross-references updated
- [ ] No broken links
- [ ] Traceability matrix updated

## 5. Completion

### 5.1 Checklist

- [ ] All changes documented in Section 3
- [ ] Tests pass (Section 4.1)
- [ ] Traceability verified (Section 4.2)
- [ ] Version numbers updated
- [ ] Status updated to Completed

### 5.2 Sign-off

| Role | Name | Date |
|------|------|------|
| Author | | |
| Reviewer | | |

---

**Status**: [Proposed → In Progress → Completed]

**Completion Date**: [YYYY-MM-DD when completed]
