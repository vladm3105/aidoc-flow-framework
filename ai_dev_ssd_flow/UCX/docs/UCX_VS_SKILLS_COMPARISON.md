# UCX vs Claude Skills Feature Comparison

**Document ID**: UCX-COMPARISON-001
**Date**: 2026-03-09
**Status**: Feature Gap Analysis

---

## Executive Summary

This document compares features between the UCX (Unified Context) Framework and the Claude Skills system (e.g., `doc-brd-autopilot`). The comparison identifies feature gaps that need to be addressed for UCX to achieve full parity.

---

## Feature Comparison Matrix

| Feature | Claude Skills | UCX | Gap Status |
|---------|--------------|-----|------------|
| **Document Creation** | `doc-brd`, `doc-prd`, etc. | `run_ucc.sh` | PARITY |
| **Document Review** | `doc-brd-audit` | `run_ucr.sh` | PARITY |
| **Document Remediation** | `doc-brd-fixer` | `run_ucrem.sh` | PARITY |
| **Multi-Persona Authoring** | Per skill | Skill injection | PARITY |
| **Validation Integration** | `doc-*-validator` | `validators/` | PARITY |
| **Template Loading** | From skill | `--template` option | PARITY |
| **Upstream Artifact Support** | `--upstream` | `--from-upstream` | PARITY |
| **Reference Document Loading** | `--ref` | `--from-ref` | PARITY |
| **Drift Monitoring** | `.drift_cache.json` + SHA-256 | **MISSING** | **GAP** |
| **Smart Document Detection** | Auto-detect action | **MISSING** | **GAP** |
| **Full Autopilot Cycle** | UCC→UCR→UCRem (max 3) | **MISSING** | **GAP** |
| **IPLAN Input Support** | `--iplan` option | **MISSING** | **GAP** |
| **Multi-Document Batch** | Chunked by 3 | **MISSING** | **GAP** |
| **Confidence Gate** | `manual-required` check | Partial | **MINOR GAP** |
| **PRD-Ready Scoring** | Score >= 90% check | **MISSING** | **GAP** |

---

## Detailed Gap Analysis

### 1. Drift Monitoring (CRITICAL GAP)

**Claude Skills Implementation**:
- `upstream_mode` field in frontmatter (`"ref"` or `"none"`)
- `.drift_cache.json` file tracks:
  - Upstream document SHA-256 hashes
  - Review history
  - Drift detection status
- Hash computation via `sha256sum`
- Automatic drift detection on review

**UCX Current State**:
- No drift tracking mechanism
- No hash computation
- No upstream change detection

**Required Implementation**:
```bash
# In run_ucr.sh - Add drift cache generation
DRIFT_CACHE="$DOC_DIR/.drift_cache.json"
if [[ -n "$UPSTREAM_REF" ]]; then
    HASH=$(sha256sum "$UPSTREAM_REF" | cut -d' ' -f1)
    # Write to .drift_cache.json
fi
```

---

### 2. Smart Document Detection (CRITICAL GAP)

**Claude Skills Implementation**:
- If document exists → Review & Fix mode
- If document missing → Generate mode
- Reference docs → Generate mode
- Special handling for different input types

**UCX Current State**:
- User must explicitly choose `run_ucc.sh` or `run_ucr.sh`
- No automatic action selection

**Required Implementation**:
```bash
# In run_ucx_autopilot.sh
if [[ -f "$DOC_PATH" ]]; then
    # Document exists: Review & Fix
    run_ucr.sh "$DOC_TYPE" "$DOC_PATH"
else
    # Document missing: Generate
    run_ucc.sh "$DOC_TYPE" "$DOC_PATH" --from-ref "$REF_PATH"
fi
```

---

### 3. Full Autopilot Cycle (CRITICAL GAP)

**Claude Skills Implementation**:
- Phase 1: Input detection
- Phase 2: Source analysis
- Phase 3: Document generation (UCC)
- Phase 4: Validation + Review (UCR)
- Phase 5: Fix cycle with max 3 iterations
- Confidence gate: No `manual-required` fixes unresolved
- PRD-Ready score >= 90%

**UCX Current State**:
- Each phase runs independently
- No automatic iteration
- No score-based exit condition

**Required Implementation**:
- Create `run_ucx_autopilot.sh` that orchestrates all phases
- Add iteration loop with max 3 cycles
- Add PRD-Ready score extraction and check

---

### 4. IPLAN Input Support (MEDIUM GAP)

**Claude Skills Implementation**:
- `--iplan <path|IPLAN-NNN>` option
- IPLAN resolution order:
  1. Direct file path
  2. `work_plans/IPLAN-NNN*.md`
  3. `governance/plans/IPLAN-NNN*.md`
- ID transformation (FR-XXX → BRD.NN.TT.SS)

**UCX Current State**:
- No IPLAN input support

**Required Implementation**:
- Add `--from-iplan` option to `run_ucc.sh`
- Add IPLAN resolution logic
- Add ID transformation

---

### 5. Multi-Document Batch Processing (MEDIUM GAP)

**Claude Skills Implementation**:
- Process multiple documents in chunks of 3
- Parallel execution support

**UCX Current State**:
- Single document processing only

**Required Implementation**:
- Add batch mode to autopilot
- Implement chunking logic

---

## Implementation Priority

| Priority | Feature | Complexity | Impact |
|----------|---------|------------|--------|
| P0 | Smart Document Detection | Low | High |
| P0 | Full Autopilot Cycle | Medium | High |
| P1 | Drift Monitoring | Medium | Medium |
| P2 | IPLAN Input Support | Medium | Medium |
| P2 | Multi-Document Batch | Low | Medium |
| P3 | PRD-Ready Scoring | Low | Low |

---

## Recommendation

Create `run_ucx_autopilot.sh` that implements:
1. Smart document detection (auto-select create vs review)
2. Full UCC → UCR → UCRem cycle with 3 max iterations
3. Drift cache management
4. Score-based exit condition (PRD-Ready >= 90%)
5. Multi-document batch support

This will bring UCX to full feature parity with Claude Skills while maintaining the simpler shell-based architecture.
