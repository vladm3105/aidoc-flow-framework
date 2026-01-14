---
title: "Quality Gates Integration with 16-Layer Traceability"
tags:
  - framework-guide
  - shared-architecture
custom_fields:
  document_type: guide
  priority: shared
  development_status: active
---

# Quality Gates Integration with 16-Layer Traceability

**Version**: 1.0
**Date**: 2025-11-19
**Status**: Active
**Framework**: AI Dev Flow SDD (100% Compliant with TRACEABILITY.md)
**Purpose**: Quality gate system aligned with 16-layer architecture and cumulative tagging hierarchy

---

## Table of Contents

1. [Quality Gate Architecture](#1-quality-gate-architecture)
2. [16-Layer Quality Gates Matrix](#2-16-layer-quality-gates-matrix)
3. [Validation Integration](#3-validation-integration)
4. [Pre-Commit Implementation](#4-pre-commit-implementation)
5. [Quality Gate Commands](#5-quality-gate-commands)

---

## 1. Quality Gate Architecture

Quality gates ensure that artifacts meet maturity thresholds before progressing to the next layer in the 16-layer SDD workflow (Layers 0-15, per TRACEABILITY.md §1.2.1).

### Traceability Rules (REQUIRED vs OPTIONAL)

| Document Type | Upstream Traceability | Downstream Traceability |
|---------------|----------------------|------------------------|
| **BRD** | OPTIONAL (to other BRDs) | OPTIONAL |
| **All Other Documents** | REQUIRED | OPTIONAL |

**Key Rules**:
- **Upstream REQUIRED** (except BRD): Document MUST reference its upstream sources
- **Downstream OPTIONAL**: Only link to documents that already exist
- **No-TBD Rule**: NEVER use placeholder IDs (TBD, XXX, NN) - leave empty or omit section

### Quality Gate Definitions

| **Gate Type** | **Trigger** | **Criteria** | **Enforcement** | **Recovery** |
|---------------|-------------|--------------|-----------------|--------------|
| **Ready Score Gate** | Document creation/modification | `[NEXT_LAYER]-ready score ≥90%` | Template validation | Improve document completeness |
| **Cumulative Tag Gate** | Pre-commit | All upstream tags present (TRACEABILITY.md §4.3) | Script validation | Add missing traceability tags |
| **Layer Sequence Gate** | Workflow progression | Follows documented sequence (TRACEABILITY.md §1.3) | Script validation | Complete previous layers first |

### Ready Score Implementation

Each artifact includes a readiness assessment field:

```yaml
# SPEC-TEMPLATE.yaml (Layer 10)
metadata:
  task_ready_score: "✅ 95% (Target: ≥90%)"

# Document Control (MarkDown artifacts)
| SPEC-Ready Score | ✅ 92% (Target: ≥90%) |
| IMPL-Ready Score | ✅ 95% (Target: ≥90%) |
```

---

## 2. 16-Layer Quality Gates Matrix

Aligned with the 16-Layer Architecture (TRACEABILITY.md §1.2.1):

| **Layer** | **Artifact Type** | **Ready Score Field** | **Validation Command** | **Gates Upstream Tags** |
|-----------|-------------------|----------------------|------------------------|------------------------|
| **0** | Strategy | N/A | N/A | None |
| **1** | BRD | `EARS-Ready Score` | `./scripts/validate_brd_template.sh` | None |
| **2** | PRD | `BDD-Ready Score` | `python scripts/validate_prd.py` | `@brd` |
| **3** | EARS | `ADR-Ready Score` | `python scripts/validate_ears.py` | `@brd @prd` |
| **4** | BDD | `SYS-Ready Score` | `python scripts/validate_bdd.py` | `@brd @prd @ears` |
| **5** | ADR | `REQ-Ready Score` | `python scripts/validate_adr.py` | `@brd→@bdd` |
| **6** | SYS | `SPEC-Ready Score` | `python scripts/validate_sys.py` | `@brd→@adr` |
| **7** | REQ | `IMPL-Ready Score` | `./scripts/validate_req_template.sh` | `@brd→@sys` |
| **8** | IMPL | N/A (Project Management) | `./scripts/validate_impl.sh` | `@brd→@req` |
| **9** | CTR | N/A (Interface Contracts) | `./scripts/validate_ctr.sh` | `@brd→@req @impl` |
| **10** | SPEC | `TASKS-Ready Score` | `python scripts/validate_spec.py` | `@brd→@req +optional` |
| **11** | TASKS | `IPLAN-Ready Score` | `./scripts/validate_tasks.sh` | `@brd→@spec` |
| **11 (optional)** | ICON | N/A (Implementation Contracts) | `./scripts/validate_icon.sh` | `@brd→@spec (+ optional @icon)` |
| **12** | IPLAN | N/A (Implementation Plans) | `./scripts/validate_iplan.sh` | `@brd→@tasks` |
| **13** | Code | N/A | TBD | `@brd→@iplan` |
| **14** | Tests | N/A | TBD | `@brd→@code` |
| **15** | Validation | N/A | Deployment verification | All upstream tags |

### Layer Transition Quality Gates

| **From→To** | **Pre-Conditions** | **Quality Gate** | **Success Criteria** |
|-------------|-------------------|------------------|---------------------|
| **L1→L2** | Business analysis complete | EARS-ready score ≥90% | Functional requirements documentable as EARS |
| **L2→L3** | Product features defined | BDD-ready score ≥90% | Can translate to WHEN-THE-SHALL-WITHIN statements |
| **L3→L4** | Requirements structured | ADR-ready score ≥90% | WHEN-THE-SHALL validation passes, behavioral scenarios identifiable |
| **L4→L5** | Behavioral tests defined | SYS-ready score ≥90% | Architecture decisions can be evaluated against test requirements |
| **L5→L6** | Architecture decisions made | REQ-ready score ≥90% | System specifications can be decomposed into atomic requirements |
| **L6→L7** | System requirements specified | SPEC-ready score ≥90% | Atomic requirements contain all information needed for SPEC generation |
| **L7→L8** | Requirements atomicized | IMPL-ready score ≥90% | Technical conclusion reached, ready for project management |
| **L8→L10** | Project plans approved | TASKS-ready score ≥90% | Technical specifications machine-readable and complete |
| **L10→L11** | Specs created | IPLAN-ready score ≥90% | Code generation plan structured and AI-ready |
| **L11→L12** | Tasks planned | Implementation plan complete | Session execution plans with bash commands validated |

---

## 3. Validation Integration

### MVP Validator Profile

- Validators support a relaxed MVP profile via document frontmatter: set `custom_fields.template_profile: mvp` in MVP templates to treat certain non-critical checks as warnings while drafting. Full templates use the default strict profile.

### Pre-Commit Hook Integration

```bash
#!/bin/bash
# .git/hooks/pre-commit

validate_quality_gates() {
    local changed_files=$1

    for file in $changed_files; do
        case "$file" in
            01_BRD/*.md) ./scripts/validate_brd_template.sh "$file" ;;
            02_PRD/*.md) python scripts/validate_prd.py "$file" ;;
            03_EARS/*.md) python scripts/validate_ears.py --path "$file" ;;
            04_BDD/BDD-*/BDD-*.feature) python scripts/validate_bdd.py "$file" ;;
            05_ADR/*.md) python scripts/validate_adr.py "$file" ;;
            06_SYS/*.md) python scripts/validate_sys.py "$file" ;;
            07_REQ/**/*.md|07_REQ/*.md) ./scripts/validate_req_template.sh "$file" ;;
            10_SPEC/*.yaml|10_SPEC/**/*.yaml) python scripts/validate_spec.py "$file" ;;
            11_TASKS/*.md) ./scripts/validate_tasks.sh "$file" ;;
            ICON/*.md) ./scripts/validate_icon.sh "$file" ;;
            12_IPLAN/*.md) ./scripts/validate_iplan.sh "$file" ;;
        esac

        # Check cumulative tagging (TRACEABILITY.md §4)
        validate_cumulative_tags "$file" &&
        validate_upstream_chain "$file"

        if [ $? -ne 0 ]; then
            echo "❌ Quality gate failed for $file"
            exit 1
        fi
    done

    echo "✅ All quality gates passed"
}
```

### Ready Score Validation Functions

```bash
validate_ready_score() {
    local file="$1"
    local score_type="$2"
    local min_threshold="$3"

    # Extract ready score from document
    score=$(extract_ready_score "$file" "$score_type")

    if [ -z "$score" ]; then
        echo "❌ Missing $score_type in $file"
        return 1
    fi

    if [ "$score" -lt "$min_threshold" ]; then
        echo "❌ $score_type too low: $score% (minimum: ${min_threshold}%)"
        return 1
    fi

    echo "✅ $score_type valid: $score% ≥ ${min_threshold}%"
    return 0
}

validate_cumulative_tags() {
    local file="$1"

    # Extract required tags for this layer (TRACEABILITY.md §4.3)
    required_tags=$(get_required_layer_tags "$file")

    # Check tags are present and valid
    for tag in $required_tags; do
        if ! grep -q "^@$tag:" "$file"; then
            echo "❌ Missing tag: @$tag"
            return 1
        fi
    done

    echo "✅ Cumulative tagging valid"
    return 0
}
```

---

## 4. Pre-Commit Implementation

### Git Hook Setup

**Step 1: Create pre-commit hook**
```bash
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/sh

# AI Dev Flow Quality Gates Integration
# Validates against 16-Layer Architecture (TRACEABILITY.md)

echo "🔍 Running AI Dev Flow quality gate validation..."

# Get changed artifact files
changed_artifacts=$(git diff --cached --name-only | grep '^docs/')

if [ -n "$changed_artifacts" ]; then
    # Run validation scripts
    for artifact in $changed_artifacts; do
        echo "Validating: $artifact"
        if ! ./scripts/validate_quality_gates.sh "$artifact"; then
            echo "❌ Quality gate failed for $artifact"
            echo "💡 Run: ./scripts/fix_quality_gate.sh '$artifact'"
            exit 1
        fi
    done
fi

echo "✅ All quality gates passed!"
EOF

chmod +x .git/hooks/pre-commit
```

**Step 2: Main quality gates validation script**
```bash
cat > scripts/validate_quality_gates.sh << 'EOF'
#!/bin/bash

validate_quality_gates() {
    local file="$1"

    case "$file" in
        docs/01_BRD/*.md) validate_score "$file" "EARS-Ready Score" ;;
        docs/02_PRD/*.md) validate_score "$file" "BDD-Ready Score" ;;
        docs/03_EARS/*.md) validate_score "$file" "ADR-Ready Score" ;;
        docs/04_BDD/BDD-*/BDD-*.feature) validate_score "$file" "SYS-Ready Score" ;;
        docs/05_ADR/*.md) validate_score "$file" "REQ-Ready Score" ;;
        docs/06_SYS/*.md) validate_score "$file" "SPEC-Ready Score" ;;
        docs/07_REQ/*.md) validate_score "$file" "IMPL-Ready Score" ;;
        docs/10_SPEC/*.yaml) validate_meta_score "$file" "task_ready_score" ;;
        docs/11_TASKS/*.md) validate_score "$file" "IPLAN-Ready Score" ;;
    esac

    validate_cumulative_tags "$file"
}

validate_score() {
    local file="$1"
    local score_field="$2"

    score=$(grep "| $score_field" "$file" | sed 's/.*✅ \([0-9]*\)%.*/\1/')

    if [ -z "$score" ] || [ "$score" -lt 90 ]; then
        echo "❌ $score_field: $score% (requires ≥90%)"
        return 1
    fi

    echo "✅ $score_field: $score%"
    return 0
}

validate_meta_score() {
    local file="$1"
    local meta_field="$2"

    score=$(grep "task_ready_score:" "$file" | sed 's/.*✅ \([0-9]*\)%.*/\1/')

    if [ -z "$score" ] || [ "$score" -lt 90 ]; then
        echo "❌ $meta_field: $score% (requires ≥90%)"
        return 1
    fi

    echo "✅ $meta_field: $score%"
    return 0
}

validate_cumulative_tags() {
    local file="$1"

    # Check required tags based on file path
    case "$file" in
        docs/07_REQ/*.md) required_tags=("brd" "prd" "ears" "bdd" "adr" "sys") ;;
        docs/10_SPEC/*.yaml) required_tags=("brd" "prd" "ears" "bdd" "adr" "sys" "req") ;;
        docs/11_TASKS/*.md) required_tags=("brd" "prd" "ears" "bdd" "adr" "sys" "req" "spec") ;;
    esac

    for tag in "${required_tags[@]}"; do
        if ! grep -q "^@$tag:" "$file"; then
            echo "❌ Missing cumulative tag: @$tag"
            return 1
        fi
    done

    echo "✅ Cumulative tagging valid"
    return 0
}

# Execute validation
validate_quality_gates "$1"
EOF

chmod +x scripts/validate_quality_gates.sh
```

---

## 5. Quality Gate Commands

### Daily Workflow Commands

**Single File Validation:**
```bash
# Validate specific artifact
./scripts/validate_quality_gates.sh docs/06_SYS/SYS-01.md

# Output: ✅ SPEC-Ready Score: 95% ≥90%
# Output: ✅ Cumulative tagging valid
# Output: ✅ Quality gates passed for docs/06_SYS/SYS-01.md
```

**Batch Validation:**
```bash
# Validate all artifacts in directory  
find docs/ -type f \( -name "*.md" -o -name "*.yaml" \) -exec ./scripts/validate_quality_gates.sh {} \;

# Validate only changed files
git diff --name-only | grep '^docs/' | xargs ./scripts/validate_quality_gates.sh
```

**Quality Gate Status Report:**
```bash
# Generate quality dashboard
./scripts/generate_quality_report.py > docs/QUALITY_DASHBOARD.md

# Sample output in markdown
# # Quality Dashboard - 2025-11-19
#
# ## Layer Readiness Summary
# - BRD Layer: 15/15 (100%) ready for EARS
# - PRD Layer: 12/12 (100%) ready for BDD  
# - EARS Layer: 11/18 (61%) need ADR-ready improvements
# - BDD Layer: 20/20 (100%) ready for SYS
#
# ## Quality Trends
# [Chart showing improvement over time]
```

### Recovery Commands

**Fix Missing Ready Score:**
```bash
# Add ready score to document
./scripts/fix_quality_gate.sh docs/06_SYS/SYS-01.md "add-score"
# Output: Added SYS-Ready Score field to Document Control
```

**Auto-generate Cumulative Tags:**
```bash
# Generate missing tags
./scripts/fix_quality_gate.sh docs/06_SYS/SYS-01.md "add-tags"
# Output: Added @brd @prd @ears @bdd @adr tags to traceability section
```

**Quality Improvement Suggestions:**
```bash
# Get specific improvement recommendations
./scripts/suggest_quality_improvements.sh docs/07_REQ/REQ-01.md
# Output: 
# 💡 IMPROVEMENT: Add interface schemas (section 3)
# 💡 IMPROVEMENT: Add error handling examples (section 5)
# 💡 IMPROVEMENT: IMPROVEMENT Connect 2 upstream sources to reach 90%
```

---

## Integration with TRACEABILITY.md

### Complete Alignment

This quality gate system is **100% aligned** with TRACEABILITY.md requirements:

- **Layer Numbers**: Uses 16-layer formal numbering (0-15)
- **Cumulative Tagging**: Enforces cumulative inheritance rules (§4.3)
- **Diagram Conventions**: Follows L1-L11 visual groupings with formal layer references
- **Tag Format**: Uses `@artifact-type: TYPE.NN.TT.SS (Unified Feature ID)` format (§4.1)

### Success Metrics

Quality gates measure framework effectiveness:

- **Maturity Rate**: Percentage of artifacts ≥90% ready scores
- **Deployability**: Artifacts passing all quality gates
- **Traceability Completeness**: 100% bidirectional linking
- **Development Speed**: Faster reviews with standardized templates

---

## Conclusion

This quality gate system provides **smooth transitions** between SDD workflow layers by:

1. **Enforcing readiness scores** before progression
2. **Validating cumulative tagging** against TRACEABILITY.md requirements
3. **Pre-commit blocking** prevents immature artifacts
4. **Automated recovery** provides immediate improvement guidance

**Result**: Zero-defect progression through the 16-layer SDD architecture with complete traceability coverage.

---

**Document End**

**Version**: 1.0 - Aligned with TRACEABILITY.md §1-4
**Updated**: 2025-11-19
**Next Review**: 2025-12-19
