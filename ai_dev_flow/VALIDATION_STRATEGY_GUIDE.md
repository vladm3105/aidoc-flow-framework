---
title: "Validation Strategy & Architecture Guide (Framework-Wide)"
tags:
  - validation-strategy
  - architecture
  - integration
  - framework-guide
custom_fields:
  document_type: architecture-guide
  artifact_type: validation-framework
  priority: high
  version: "1.0"
  scope: all-document-types
---

# Validation Strategy & Architecture Guide

**Purpose:** Complete reference for validation architecture across all SDD document types (BRD, PRD, EARS, BDD, ADR, SYS, REQ, CTR, SPEC, TASKS).

**Audience:** Framework architects, DevOps, validator maintainers, advanced users.

**Quick Navigation:**
- [REQ Validation Architecture](#req-validation-architecture)
- [Validation Gate Coverage](#validation-gate-coverage)
- [Usage Patterns](#usage-patterns)
- [Assessment & Quality](#assessment--quality)

**Related Documents:**
- [VALIDATION_COMMANDS.md](./VALIDATION_COMMANDS.md) - CLI reference
- [AI_VALIDATION_DECISION_GUIDE.md](./AI_VALIDATION_DECISION_GUIDE.md) - Decision framework
- [VALIDATION_DECISION_FRAMEWORK.md](./VALIDATION_DECISION_FRAMEWORK.md) - Universal rules

**Last Updated:** 2026-01-24

---

## REQ Validation Architecture

The REQ validation system follows a **layered orchestrator pattern** for reliability and consistency.

### Master Orchestrator: validate_all.sh

`validate_all.sh` is the single entry point that delegates to specialized validators:

```
validate_all.sh (Master Orchestrator)
├── File Mode:
│   ├─ validate_req_spec_readiness.py --req-file <file>
│   ├─ validate_req_template.sh <file>
│   └─ validate_requirement_ids.py --req-file <file>
│   Output: 3 validators run
│
└── Directory Mode:
    ├─ validate_req_quality_score.sh <directory>
    ├─ validate_req_spec_readiness.py --directory <directory>
    └─ validate_requirement_ids.py --directory <directory>
    Output: 3 validators run (quality gates for corpus-level)
```

### Design Principles

- **Unified Entry Point**: Single `validate_all.sh` command for all workflows
- **Consistent Output**: Color-coded results across all validators
- **Selective Execution**: Skip specific validators with CLI flags
- **Flexible Thresholds**: Customizable SPEC-ready threshold (default 90%)
- **Mode-Aware Routing**: Different validators run based on file vs directory mode
- **Separation of Concerns**: Each validator handles one validation aspect

### Orchestration Flow

**File Mode Workflow:**
1. User: `bash validate_all.sh --file <file.md>`
2. Master script runs: SPEC-readiness → Template compliance → IDs validation
3. Output: 3 validation reports + summary

**Directory Mode Workflow:**
1. User: `bash validate_all.sh --directory <folder>`
2. Master script runs: Quality gates → SPEC-readiness → IDs validation
3. Output: 3 validation reports + comprehensive summary with corpus statistics

---

## Validation Gate Coverage

### REQ Validation: 14 Active Gates

**Total Gates**: 14 gates + 1 informational = Complete quality assurance

#### ERROR Gates (Must Pass - 7 gates):

| Gate | Name | Validates |
|------|------|-----------|
| 01 | Placeholder Text Detection | TBD, TODO, FIXME removal |
| 02 | Premature Downstream References | No forward references to incomplete REQs |
| 04 | Index Synchronization | REQ index is up-to-date |
| 06 | Mermaid Diagram Validation | Diagram syntax correctness |
| 08 | Element ID Uniqueness | No duplicate element IDs |
| 11 | Cumulative Traceability | @brd, @prd, @ears tags present |
| 12 | 11-Section MVP Format | Template structure compliance |

#### WARNING Gates (Should Fix - 5 gates):

| Gate | Name | Validates |
|------|------|-----------|
| 03 | Internal Count Consistency | Section counts match declared values |
| 07 | Glossary Consistency | SHALL vs MUST usage consistency |
| 09 | Priority Distribution | Priority levels within acceptable range |
| 10 | File Size & Token Compliance | Document readability and token limits |
| 22 | Upstream TBD References | Unresolved upstream dependencies |

#### INFO Gates (Tracking - 1 gate):

| Gate | Name | Validates |
|------|------|-----------|
| 05 | Inter-REQ Cross-Linking | @depends/@discoverability tags presence |

### Additional Validation Systems

- **SPEC-Ready Scoring** (0-100%): Readiness for SPEC generation
  - Protocol/ABC definitions presence
  - Pydantic models count
  - Exception classes count
  - YAML config presence
  - Element completeness

- **Template Compliance** (11 sections): MVP structure validation
  - Section presence and order
  - Metadata completeness
  - Template version matching

- **ID Format Validation**: REQ-NN.MM format and naming
  - No duplicates
  - Hierarchical organization
  - Pattern consistency

---

## Validation Gate Severity & Recovery

### ERROR Gates (Must Fix)

If ERROR gates fail, the document is **not ready for downstream processing**.

**Fix required before:**
- Committing to main branch
- SPEC generation
- Release

**Common Fixes by Gate:**
- **GATE-01**: Remove TBD, TODO, FIXME placeholders
- **GATE-02**: Remove forward references to incomplete REQs
- **GATE-04**: Update index to reflect new/modified REQs
- **GATE-06**: Close unclosed Mermaid code blocks
- **GATE-08**: Ensure all element IDs are unique
- **GATE-11**: Add missing @brd/@prd/@ears tags
- **GATE-12**: Ensure all 11 sections present

### WARNING Gates (Should Fix)

WARNING gates indicate quality issues. Fixing recommended before:
- Feature freeze
- Release candidates
- Customer delivery

**Common Fixes by Gate:**
- **GATE-03**: Update section counts if content changes
- **GATE-07**: Use consistent SHALL vs MUST terminology
- **GATE-09**: Adjust priority levels for balance
- **GATE-10**: Trim excessive content or split files
- **GATE-22**: Resolve upstream dependencies

### INFO Gates (Informational)

**GATE-05** (cross-linking) is informational:
- ✅ Files with cross-links = framework-compliant
- ⚪ Files without cross-links = acceptable (standalone domains)
- 🔄 Recommended for platform features (infrastructure, security, ops)

---

## Usage Patterns

### Pattern 1: Single File Validation (Development)

**Scenario:** Validate a newly created or edited REQ file during development

```bash
bash validate_all.sh --file docs/07_REQ/REQ-06.01_cloud_run_deployment.md
```

**When to Use**: Before committing a single requirement, during iterative development.

**Validators Run**: 3 (SPEC-ready, Template, IDs)

**Expected Output:**
```
✓ SPEC-Readiness Validator   (scores 0-100%)
✓ Template Compliance        (checks 11 sections)
✓ Requirement IDs Validator  (validates REQ-NN.MM format)
✓ All validation checks passed!
```

---

### Pattern 2: Directory Validation (Quality Assurance)

**Scenario:** Validate an entire REQ folder before SPEC generation or release

```bash
bash validate_all.sh --directory docs/07_REQ/REQ-06_f6_infrastructure
```

**When to Use**: Quality assurance before feature completion, release cycles.

**Validators Run**: 3 (Quality gates, SPEC-ready, IDs)

**Scope**: All REQ files in directory (corpus-level checks via quality gates)

**Expected Output:**
```
✓ Quality Gate Validator     (14 gates across 40 files)
✓ SPEC-Readiness Validator  (scores each file 0-100%)
✓ Requirement IDs Validator  (validates all IDs)
✓ All validation checks passed!
```

---

### Pattern 3: Selective Validation (Quick Feedback)

**Scenario:** Skip certain validators for fast feedback during development

```bash
bash validate_all.sh --directory . --skip-quality --skip-template
```

**When to Use**: Quick validation during development, when you know quality gates are passing.

**Available Skip Options**:
- `--skip-quality`: Bypass all 14 quality gates
- `--skip-spec`: Bypass SPEC-readiness scoring
- `--skip-template`: Bypass template compliance (file mode only)
- `--skip-ids`: Bypass ID format validation

**Use Case:** Developers want rapid feedback on ID and readiness; skip quality gates that run slower.

---

### Pattern 4: Custom Threshold (Flexible Standards)

**Scenario:** Require stricter (or more lenient) SPEC-ready threshold

```bash
# Stricter for final review
bash validate_all.sh --directory docs/07_REQ/REQ-06 --min-score 95

# Lenient for draft review
bash validate_all.sh --directory docs/07_REQ/REQ-06 --min-score 75
```

**When to Use**: Final review (stricter 95%), draft review (more lenient 75%).

**Default**: 90%

---

## Assessment & Quality

### ✅ What's Working

- **Master orchestrator** (`validate_all.sh`) properly delegates to all validators
- **All 5 validators actively used** - no dead code
- **Clear separation of concerns**:
  - Quality gates (corpus-level, directory-only)
  - SPEC-readiness scoring (both file & directory)
  - Template compliance (file-level)
  - ID format validation (both levels)
  - Cross-link generation (pre-validation helper)
- **Flexible CLI** with skip options and custom thresholds
- **Color-coded output** for clarity
- **Complementary checking** - each validator addresses different quality aspects

### ✨ Strengths

- Consistent CLI patterns: `--file`, `--directory`, `--min-score`
- Sensible defaults: 90% SPEC-ready threshold
- Idempotent tools (safe to run multiple times)
- Comprehensive gate coverage (14+ validation checks)
- Pre-validation support (`add_crosslinks_req.py`)
- Documented with examples for all use cases
- Clean separation between infrastructure and decision-making
- Framework extensible to other document types (BRD, SPEC, etc.)

### 🔧 Optional Future Enhancements

- Config file for threshold tuning (YAML-based `.validation.yaml`)
- CSV/JSON export for tracking trends and metrics
- GitHub Actions CI/CD integration templates
- Performance timing per validator (SLA monitoring)
- Composite pass/fail metrics across validators
- Batch processing with progress reporting
- Failure recovery and retry mechanisms
- Parallel validator execution for large directories
- Custom gate plugins for domain-specific rules

---

## Validator Activity Summary (REQ)

| Validator | Called By | Modes | Usage | Purpose |
|-----------|-----------|-------|-------|---------|
| validate_all.sh | User (CLI) | Both | 100% | Master orchestrator entry point |
| validate_req_quality_score.sh | validate_all.sh | Directory | 100% | Corpus-level quality checks (14 gates) |
| validate_req_spec_readiness.py | validate_all.sh | Both | 100% | Readiness scoring (0-100%) |
| validate_req_template.sh | validate_all.sh | File | 100% | Structure validation (11 sections) |
| validate_requirement_ids.py | validate_all.sh | Both | 100% | Format & naming validation |
| add_crosslinks_req.py | User (pre-validation) | Generator | 100% | Pre-validation cross-link population |

**Conclusion:** All tools are actively integrated. No unused scripts. Clean architecture with proper delegation.

---

## Recommended Workflows

### Development Workflow

```bash
# 1. Create/edit REQ document
nano docs/07_REQ/REQ-08_trading_intelligence/REQ-08.01_agent_registry.md

# 2. Add cross-links (pre-validation)
python3 scripts/add_crosslinks_req.py --req-num 8

# 3. Validate single file
bash scripts/validate_all.sh --file docs/07_REQ/REQ-08_trading_intelligence/REQ-08.01_agent_registry.md

# 4. Fix any issues and repeat 3
```

### Release Workflow

```bash
# 1. Validate entire REQ folder
bash scripts/validate_all.sh --directory docs/07_REQ/REQ-08_trading_intelligence

# 2. Address any failures (especially ERROR gates)
# (repeat validation until all gates pass)

# 3. Generate SPEC from validated REQ
# (downstream process)
```

### CI/CD Integration (Example)

```bash
#!/bin/bash
# Pre-commit validation

for req_file in $(git diff --name-only | grep 'REQ-.*\.md'); do
  bash scripts/validate_all.sh --file "$req_file" || exit 1
done

echo "✓ All REQ files passed validation"
```

---

## Framework-Level Application

This architecture is designed to be **portable across all document types**:

- **BRD Validation**: Similar orchestrator, different gates (BRD-specific business rules)
- **PRD Validation**: Feature completeness gates, API contract validation
- **SPEC Validation**: Code generation readiness, schema compliance
- **TASKS Validation**: Dependency tracking, closure criteria

Each document type has its own `scripts/validate_all.sh` that delegates to type-specific validators.

---

## File Locations (REQ-Specific)

```
ai_dev_flow/07_REQ/
├── scripts/
│   ├── add_crosslinks_req.py          # Cross-link generator
│   ├── validate_all.sh                # Master orchestrator
│   ├── validate_req_quality_score.sh  # Quality gate validator
│   ├── validate_req_spec_readiness.py # SPEC-readiness scorer
│   ├── validate_req_template.sh       # Template compliance
│   ├── validate_requirement_ids.py    # ID format validator
│   └── README.md                      # Quick start guide
│
├── VALIDATION_COMMANDS.md             # CLI reference (in 07_REQ/)
├── VALIDATION_STRATEGY_GUIDE.md       # ← You are here (in 07_REQ/)
├── AI_VALIDATION_DECISION_GUIDE.md    # Decision framework (in 07_REQ/)
├── REQ-MVP-TEMPLATE.md                # Document template
└── ...other files
```

**Framework-Level Versions:**
- `ai_dev_flow/VALIDATION_COMMANDS.md` - Framework-wide CLI reference
- `ai_dev_flow/VALIDATION_STRATEGY_GUIDE.md` - Framework-wide architecture
- `ai_dev_flow/AI_VALIDATION_DECISION_GUIDE.md` - Framework-wide decision framework

---

**Last Updated:** 2026-01-24  
**Status:** Architecture documentation for validation framework  
**Scope:** REQ validation (with framework-wide applicability)  
**Audience:** Framework architects, validator maintainers, advanced users
