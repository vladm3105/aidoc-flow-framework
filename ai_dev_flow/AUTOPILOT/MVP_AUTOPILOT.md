---
title: "MVP Autopilot: Core Guide (v6.0 - TSPEC, TDD & CHG Integration)"
tags:
  - framework-core
  - mvp-workflow
  - automation
  - tspec
  - tdd
  - change-management
custom_fields:
  document_type: guide
  artifact_type: DOCS
  layer: 0
  priority: primary
  development_status: active
  version: "6.0"
  last_updated: "2026-02-06"
---

# MVP Autopilot: Core Guide (v6.0)

This document is the authoritative reference for MVP Autopilot in the AI Dev Flow framework. It explains what autopilot does, how to use it, and provides practical guidance for both local development and GitHub Actions CI/CD.

**v6.0 Enhancements**:
- **TSPEC Integration**: Layer 10 Test Specifications (UTEST, ITEST, STEST, FTEST)
- **TDD Workflow**: Test-Driven Development with test-first validation
- **CHG Integration**: 4-Gate Change Management for existing artifacts

## Quick Start

**Local Development**:
```bash
# Install dependencies
pip install -r ai_dev_flow/AUTOPILOT/scripts/requirements.txt

# Run autopilot with defaults
python3 ai_dev_flow/AUTOPILOT/scripts/mvp_autopilot.py \
  --root ai_dev_flow \
  --intent "My MVP" \
  --slug my_mvp \
  --auto-fix \
  --report markdown
```

**GitHub Actions**:
```bash
# Via Makefile (recommended)
make docs

# Or via GitHub UI
# Go to Actions tab → Select "MVP Autopilot - Full Pipeline" → Click "Run workflow"
```

---

## What It Does

### Core Capabilities

1. **Single-Command Scaffolding**: Generates all MVP artifacts from BRD through TSPEC to TASKS (L1-L11)
2. **Template-Based Generation**: Uses repo templates with smart placeholder substitution
3. **Per-Layer Validation**: Runs quality gate validators for each generated document
4. **Auto-Fix Strategies**: Fixes frontmatter, titles, required sections, and traceability tags
5. **Traceability Tagging**: Automatic cumulative tagging across all 11 documentation layers
6. **Flexible Execution**: Supports multiple execution modes and entry/exit points
7. **TSPEC Generation**: Creates test specifications (Unit, Integration, Smoke, Functional) from upstream artifacts
8. **TDD Workflow**: Test-first development with failing test validation before code generation
9. **Change Management**: 4-Gate change validation system for modifying existing artifacts

### What It Does NOT Do

- Does NOT make network calls to LLMs
- Does NOT execute arbitrary system commands
- Does NOT write outside the project directory
- Does NOT execute TASKS bash commands (content-only)

---

## Architecture Overview

### Directory Structure

```
ai_dev_flow/AUTOPILOT/
├── MVP_AUTOPILOT.md              # This guide
├── MVP_GITHUB_CICD_INTEGRATION_PLAN.md
├── MVP_PIPELINE_END_TO_END_USER_GUIDE.md
├── scripts/
│   ├── mvp_autopilot.py              # Main orchestration script
│   ├── validate_metadata.py          # Metadata validator
│   ├── validate_quality_gates.py     # Quality gate checker
│   ├── vertex_code_generator.py      # Optional code generator
│   ├── analyze_test_requirements.py  # TDD: Test analysis (Phase 2)
│   ├── generate_spec_tdd.py          # TDD: Test-aware SPEC generation
│   ├── update_test_traceability.py   # TDD: PENDING tag updater
│   ├── validate_tdd_stage.py         # TDD: Red/Green validation
│   ├── generate_integration_tests.py # TDD: Integration test generator
│   ├── generate_smoke_tests.py       # TDD: Smoke test generator
│   └── requirements.txt              # Python dependencies
├── config/
│   ├── default.yaml                  # Default configuration
│   ├── tdd.yaml                      # TDD mode configuration
│   ├── quality_gates.yaml            # Quality gate settings
│   └── layers.yaml                   # Layer-specific configs
└── tests/                            # Test suite
    ├── test_config_parsing.py
    ├── test_prechecks.py
    ├── test_cli_parsing.py
    └── integration/
        └── test_full_pipeline.py
```

### Execution Flow

```
┌─────────────────────────────────────────┐
│  Configuration Loading                  │
│  (Load YAML configs)                    │
└─────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Pre-Checks                             │
│  (Validate paths, dependencies)         │
└─────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Documentation Generation (L1-L9)       │
│  BRD → PRD → EARS → BDD → ADR →        │
│  SYS → REQ → CTR → SPEC                 │
└─────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  TSPEC Generation (L10)                 │
│  UTEST, ITEST, STEST, FTEST             │
└─────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  TDD Validation (if --tdd-mode)         │
│  Generate tests, validate fail state    │
└─────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  TASKS Generation (L11)                 │
│  (Implementation task breakdown)        │
└─────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Validation                             │
│  (Run quality gate scripts)             │
└─────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Post-Checks                            │
│  (Verify outputs, link integrity)       │
└─────────────────────────────────────────┘
```

---

## Command Reference

### Essential Flags

| Flag | Short | Required | Description |
|-------|--------|----------|-------------|
| `--root` | `-r` | No | Project root directory (default: `.`) |
| `--intent` | `-i` | No | Short description for project name (e.g., "A trading bot") |
| `--slug` | `-s` | No | Lowercase underscore slug for filenames (e.g., `trading_bot`) |
| `--nn` | `-n` | No | Numeric ID (default: `01`) |
| `--from-layer` | `-f` | No | Start from specific layer (e.g., `PRD`) |
| `--up-to` | `-u` | No | Last layer to generate (e.g., `TASKS`) |
| `--auto-fix` | `-a` | No | Enable auto-fix strategies |
| `--no-validate` | `-N` | No | Skip all validators, generate only |
| `--strict` | `-S` | No | Treat warnings as errors |
| `--profile` | `-P` | No | Load configuration profile (default: `mvp`) |
| `--config` | `-c` | No | Custom configuration file |
| `--report` | `-R` | No | Report format: `none\|markdown\|json\|text` |

### TDD & CHG Flags (v6.0)

| Flag | Short | Required | Description |
|-------|--------|----------|-------------|
| `--tdd-mode` | `-T` | No | Enable TDD workflow with test-first validation |
| `--chg-mode` | `-C` | No | Enable Change Management workflow |
| `--chg-level` | | No | Change level: `L1`, `L2`, or `L3` |
| `--chg-source` | | No | Change source: `upstream`, `midstream`, `downstream`, `external`, `feedback` |
| `--skip-tspec` | | No | Skip TSPEC generation (legacy mode) |
| `--validate-gates` | | No | Run CHG gate validation only |

### Execution Modes

| Mode | Description | Use Case |
|-------|-------------|----------|
| **generate** | Default mode - Generate all layers from BRD to TASKS | Standard workflow |
| **validate** | Run validators on existing documents | Quality assurance |
| **resume** | Continue existing project, generate missing layers | Incremental updates |
| **plan** | Generate execution plan without making changes | Preview mode |
| **tdd** | TDD mode - Generate tests before code, validate fail/pass states | Test-first development |
| **chg** | CHG mode - Change management with gate validation | Modifying existing artifacts |

### Configuration Profiles

| Profile | Auto-Fix | Strict Mode | Quality Threshold |
|---------|-----------|--------------|-------------------|
| `mvp` | Enabled | Disabled | 90% auto-approve |
| `strict` | Enabled | Enabled | 95% threshold |

---

## Layer-by-Layer Behavior

### BRD (Layer 1)
**Template**: `01_BRD/BRD-MVP-TEMPLATE.md`

**Generation**:
- Fixes: frontmatter (tags, custom_fields), H1 title, Document Control stub
- MVP-aware validation: Uses per-file Python validator when available

**Validation**:
- Script: `01_BRD/scripts/validate_brd_quality_score.sh`
- Minimum Score: 85% (non-strict), 95% (strict)

### PRD (Layer 2)
**Template**: `02_PRD/PRD-MVP-TEMPLATE.md`

**Generation**:
- Fixes: frontmatter, H1, Document Control with `@brd: BRD.NN.01.01`, sections 1-3
- Auto-populates traceability tags: `@brd`, `@prd`

**Validation**:
- Script: `02_PRD/scripts/validate_prd_quality_score.sh`
- Minimum Score: 90% (non-strict), 95% (strict)

### EARS (Layer 3)
**Template**: `03_EARS/EARS-MVP-TEMPLATE.md`

**Generation**:
- Fixes: frontmatter, H1, `## Document Control`, `## Purpose`, `## Traceability`
- Converts PRD requirements to EARS format
- Auto-populates tags: `@brd`, `@prd`, `@ears`

**Validation**:
- Script: `03_EARS/scripts/validate_ears_quality_score.sh`
- Minimum Score: 90%

### BDD (Layer 4)
**Template**: `04_BDD/BDD-MVP-TEMPLATE.feature`

**Generation**:
- Fixes: header cumulative tags (`@brd @prd @ears`)
- Feature line with proper format
- One GWT scenario minimum

**Validation**:
- Script: `04_BDD/scripts/validate_bdd_quality_score.sh`
- Minimum Score: 90%

### ADR (Layer 5)
**Template**: `05_ADR/ADR-MVP-TEMPLATE.md`

**Generation**:
- Creates from template with required sections + subsections
- Context: BRD, PRD, EARS, BDD

**Validation**:
- Script: `05_ADR/scripts/validate_adr_quality_score.sh`
- Minimum Score: 90%

### SYS (Layer 6)
**Template**: `06_SYS/SYS-MVP-TEMPLATE.md`

**Generation**:
- Fixes: frontmatter, H1
- Inserts Sections 1-15
- Auto-populates traceability: `@brd`, `@prd`, `@ears`, `@bdd`, `@adr`

**Validation**:
- Script: `06_SYS/scripts/validate_sys_quality_score.sh`
- Minimum Score: 90%

### REQ (Layer 7)
**Template**: `07_REQ/REQ-MVP-TEMPLATE.md`

**Generation**:
- Creates 12 atomic requirement files
- Document Control: SemVer, ISO dates, P-level, SPEC-Ready Score
- Upstream chain, cumulative tags

**Validation**:
- Script: `07_REQ/scripts/validate_req_quality_score.sh`
- Minimum Score: 90%

### CTR (Layer 8)
**Template**: `08_CTR/CTR-MVP-TEMPLATE.yaml`

**Generation**:
- Dual-file format: Human-readable `.md` + machine-readable `.yaml`
- OpenAPI 3.x specification
- Contract compliance checking

**Validation**:
- Script: `08_CTR/scripts/validate_ctr_quality_score.sh`
- Minimum Score: 90%

### SPEC (Layer 9)
**Template**: `09_SPEC/SPEC-MVP-TEMPLATE.yaml`

**Generation**:
- YAML format with required top-level keys
- Traceability: `traceability.cumulative_tags`, `upstream_sources`
- Interfaces, performance, security, observability, verification stubs

**Validation**:
- Script: `09_SPEC/scripts/validate_spec_quality_score.sh`
- Minimum Score: 92% (non-strict), 95% (strict)

### TSPEC (Layer 10) - Test Specifications
**Directory**: `10_TSPEC/`

TSPEC formalizes test specifications between SPEC (L9) and TASKS (L11) to enable Test-Driven Development (TDD) workflow.

**Test Type Specifications**:

| Type | Directory | Sources | Purpose | Min Score |
|------|-----------|---------|---------|-----------|
| UTEST | `10_TSPEC/UTEST/` | REQ (L7), SPEC (L9) | Unit test specifications | 90% |
| ITEST | `10_TSPEC/ITEST/` | CTR (L8), SYS (L6), SPEC (L9) | Integration test specifications | 85% |
| STEST | `10_TSPEC/STEST/` | EARS (L3), BDD (L4), REQ (L7) | Smoke test specifications | 100% |
| FTEST | `10_TSPEC/FTEST/` | SYS (L6) | Functional test specifications | 85% |

**Generation** (per test type):
- Template-based generation from upstream artifacts
- I/O tables with input/expected output specifications
- Pseudocode for test implementation
- Traceability tags: `@brd` through `@spec`

**Validation**:
- Script: `10_TSPEC/scripts/validate_tspec_quality_score.sh`
- Per-type validators: `validate_utest.py`, `validate_itest.py`, `validate_stest.py`, `validate_ftest.py`

**TDD Integration**:
- When `--tdd-mode` enabled, generates test files with `@code: PENDING` tags
- Validates tests fail before code generation (Red state)
- Updates tags after code generation passes tests (Green state)

**Element ID Format**: `TSPEC.NN.TT.SS`
- `NN`: Document number (01-99)
- `TT`: Test type code (40=UTEST, 41=ITEST, 42=STEST, 43=FTEST)
- `SS`: Sequential test case (01-99)

### TASKS (Layer 11)
**Template**: `11_TASKS/TASKS-MVP-TEMPLATE.md`

**Generation**:
- Generated from template
- Includes execution commands in Section 4
- 9 cumulative tags: `@brd` through `@tspec`
- References TSPEC test specifications

**Validation**:
- Script: `11_TASKS/scripts/validate_tasks_quality_score.sh`
- Minimum Score: 90%

---

## Validation Semantics

### Default Mode (Non-Strict)
- A layer passes if validator exits 0 or 1 (warnings allowed)
- Auto-fix loop: Apply targeted fixes → revalidate
- If still failing: Halt and report errors for manual resolution
- Halt on persistent errors

### Strict Mode
- A layer passes only if exit code is 0 (warnings fail the layer)
- Use for production releases or critical quality gates

### Auto-Fix Loop
```python
max_attempts = 3  # Configurable in default.yaml

for attempt in range(1, max_attempts + 1):
    apply_fixes()
    run_validator()
    if passes:
        break
    else:
        continue  # Next attempt

if attempt == max_attempts:
    halt_and_report_error()
```

---

## Traceability Rules

### Cumulative Tagging Hierarchy

Every artifact includes tags from ALL upstream layers:

| Layer | Required Tags | Format |
|-------|---------------|--------|
| **BRD** (L1) | None | No upstream tags |
| **PRD** (L2) | `@brd` | `@brd: BRD.01.01.01` |
| **EARS** (L3) | `@brd`, `@prd` | `@brd: BRD.01.01.01`, `@prd: PRD.01.01.01` |
| **BDD** (L4) | `@brd`, `@prd`, `@ears` | All upstream tags |
| **ADR** (L5) | `@brd`, `@prd`, `@ears`, `@bdd` | All upstream tags |
| **SYS** (L6) | `@brd`, `@prd`, `@ears`, `@bdd`, `@adr` | All upstream tags |
| **REQ** (L7) | `@brd` through `@sys` | All upstream tags |
| **CTR** (L8) | `@brd` through `@req` | All upstream tags |
| **SPEC** (L9) | `@brd` through `@ctr` | All upstream tags |
| **TSPEC** (L10) | `@brd` through `@spec` | All upstream tags + `@tspec` |
| **TASKS** (L11) | `@brd` through `@tspec` | All upstream tags |

### TSPEC-Specific Tags

| Test Type | Required Upstream Tags | Additional Tags |
|-----------|------------------------|-----------------|
| UTEST | `@req`, `@spec` | `@threshold` (optional) |
| ITEST | `@ctr`, `@sys`, `@spec` | `@sequence` (optional) |
| STEST | `@ears`, `@bdd`, `@req` | `@timeout`, `@rollback` |
| FTEST | `@sys` | `@threshold` (required) |

### Dotted vs Hyphenated IDs

Auto-pilot converts hyphenated IDs to dotted forms where required:

| Original | Converted | Where Used |
|---------|----------|------------|
| `BRD-01` | `BRD.01` | SYS, REQ, SPEC, TSPEC, TASKS references |
| `PRD-01` | `PRD.01.01` | EARS, BDD, ADR, SYS, REQ, SPEC, TSPEC, TASKS |
| `REQ-15` | `REQ.15.01.01` | SPEC, TSPEC, TASKS references |
| `TSPEC-01` | `TSPEC.01.40.01` | TASKS, Code references |

---

## Reporting

### Report Formats

**Markdown** (`--report markdown`):
```markdown
# MVP Autopilot Report
**Intent**: ${INTENT}
**Slug**: ${SLUG}
**Status**: PASS | FAIL
**Configuration**: Profile: ${PROFILE}, Strict: ${STRICT}, TDD: ${TDD_MODE}
**Layers Summary**:
| Layer | Status | Score | Notes |
|-------|--------|-------|-------|
| BRD | PASS | 92% | ✅ |
| PRD | PASS | 91% | ✅ |
| EARS | PASS | 90% | ✅ |
| BDD | PASS | 94% | ✅ |
| ADR | PASS | 88% | ⚠️ Manual review |
| SYS | PASS | 91% | ✅ |
| REQ | PASS | 90% | ✅ |
| CTR | PASS | 95% | ✅ |
| SPEC | PASS | 95% | ✅ |
| TSPEC | PASS | 91% | ✅ (UTEST:90%, ITEST:92%, STEST:100%, FTEST:88%) |
| TASKS | PASS | 92% | ✅ |

**TDD Summary** (when --tdd-mode enabled):
| Phase | Status | Details |
|-------|--------|---------|
| Test Generation | ✅ | 24 test cases generated |
| Red State | ✅ | All tests fail (expected) |
| Green State | ✅ | All tests pass |
| Tag Update | ✅ | 24 @code: PENDING → paths |
```

**JSON** (`--report json`):
```json
{
  "intent": "${INTENT}",
  "slug": "${SLUG}",
  "profile": "${PROFILE}",
  "timestamp": "2026-01-19T12:00:00Z",
  "status": "PASS|FAIL",
  "layers": [
    {
      "id": "BRD",
      "status": "PASS|FAIL",
      "score": 92,
      "file": "01_BRD/BRD-01_${SLUG}.md"
    }
  ]
}
```

**Text** (`--report text`):
```
BRD: PASS (92%)
PRD: PASS (91%)
EARS: PASS (90%)
```

### Output Directory

- Default: `work_plans/`
- Contains: `mvp_autopilot_report_*.md`, `mvp_autopilot_report_*.json`

---

## CI Integration

### GitHub Actions Setup

**Prerequisites**:
1. Copy workflow files to `.github/workflows/`
2. Configure repository secrets if needed (e.g., `GCP_PROJECT_ID`)
3. Ensure workflow is enabled

**Workflow Files**:
- `mvp-docs-generation.yml` - Documentation pipeline (L1-L10)
- `quality-checks.yml` - Validation (L1-L10)
- `code-generation.yml` - L11 code generation (optional)
- `full-mvp-pipeline.yml` - Orchestrated L1-L13 pipeline

**Triggering**:
- **Manual**: GitHub Actions UI
- **Automatic**: On push to `main` or `develop` branches

### Quality Gates

Auto-approval threshold: 90%
- Score ≥ 90%: Auto-approve PR
- Score < 90%: Require manual review

### Local Development Workflow

```bash
# Install dependencies
pip install -r ai_dev_flow/AUTOPILOT/scripts/requirements.txt

# Run with auto-fix (recommended for speed)
python3 ai_dev_flow/AUTOPILOT/scripts/mvp_autopilot.py \
  --root ai_dev_flow \
  --intent "My MVP" \
  --slug my_mvp \
  --auto-fix

# Validate existing docs
python3 ai_dev_flow/scripts/validate_all.py \
  ai_dev_flow \
  --all \
  --report markdown
```

---

## Troubleshooting

### Common Issues

**Issue**: Autopilot halts at a layer
**Solution**: Re-run with `--auto-fix` to allow fixes

**Issue**: Link integrity warnings at end
**Solution**: Fill in real links and re-run `validate_links.py`

**Issue**: Quality score below threshold
**Solution**: Review document, improve content, re-run with `--auto-fix`

**Issue**: Auto-fixers brittle with template changes
**Solution**: Update fixer patterns in `mvp_autopilot.py` after major template refactors

### Resume vs Fork

**Resume In-Place**:
- Discovers existing artifacts
- Validates and fixes them
- Generates only missing layers/files
- Preserves IDs and links
- Use for teams picking up partial work

**Fork-As-New**:
- Copies existing project as base
- New identifiers (e.g., BRD-02 → BRD-01)
- Updates traceability across all files
- Use when project needs clean restart

---

## Best Practices

### Development Workflow

1. **Start with speed**: Run non-strict with auto-fix for quick baseline
2. **Iterate quickly**: Replace stubs with real material between runs
3. **Tighten gradually**: Turn on `--strict` when content stabilizes
4. **Validate frequently**: Run `validate_all.py` to catch issues early

### Local Development

1. **Use Makefile**: Standardized commands for common operations
2. **Watch mode**: Auto-reload on file changes (see Makefile target)
3. **Test changes**: Run `pytest AUTOPILOT/tests/` after modifications
4. **Commit frequently**: Small, focused commits for easier debugging

### CI/CD

1. **Automate validation**: Run quality gates on every PR
2. **Require approval**: Manual review for scores < 90%
3. **Parallel execution**: Run independent checks in parallel
4. **Artifact storage**: Upload reports as workflow artifacts

---

## Configuration System

### Configuration Files

**Default Configuration** (`config/default.yaml`):
- Auto-fix: Enabled
- MVP validators: Enabled
- Parallel execution: Disabled
- Timeout per layer: 300 seconds
- Quality threshold: 90% (auto-approve)

**Quality Gates Configuration** (`config/quality_gates.yaml`):
- Auto-approve threshold: 90%
- Strict mode threshold: 95%
- Enable auto-approval: Enabled

**Layer-Specific Configuration** (`config/layers/*.yaml`):
- Template overrides
- Validator selections
- Custom timeouts
- Layer-specific auto-fix rules

### Profiles

**Profile: `mvp`** (Default):
- Entry: L1_BRD
- Exit: L11_TASKS
- Auto-fix: Enabled
- Strict: Disabled

**Profile: `strict`** (Production):
- Entry: L1_BRD
- Exit: L11_TASKS
- Auto-fix: Enabled
- Strict: Enabled

**Profile: `tdd`** (Test-Driven Development):
- Entry: L1_BRD
- Exit: L11_TASKS + Tests
- TDD Mode: Enabled
- Auto-fix: Enabled
- Test Validation: Red→Green required

---

## TDD Workflow (v6.0)

Test-Driven Development integration enables test-first workflow where tests are generated and validated before code implementation.

### TDD Mode Activation

```bash
python3 ai_dev_flow/AUTOPILOT/scripts/mvp_autopilot.py \
  --root ai_dev_flow \
  --intent "My MVP" \
  --slug my_mvp \
  --tdd-mode \
  --auto-fix \
  --report markdown
```

### TDD Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     TDD WORKFLOW                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Generate Documentation (L1-L9)                              │
│         ↓                                                       │
│  2. Generate TSPEC (L10)                                        │
│     - UTEST from REQ + SPEC                                     │
│     - ITEST from CTR + SYS + SPEC                               │
│     - STEST from EARS + BDD + REQ                               │
│     - FTEST from SYS                                            │
│         ↓                                                       │
│  3. Generate Test Files                                         │
│     - Create tests/unit/, tests/integration/, etc.              │
│     - Tag with @code: PENDING                                   │
│         ↓                                                       │
│  4. Validate RED State                                          │
│     - Run pytest, expect failures                               │
│     - Exit code != 0 required                                   │
│         ↓                                                       │
│  5. Generate TASKS (L11)                                        │
│         ↓                                                       │
│  6. Generate Code (if --up-to CODE)                             │
│         ↓                                                       │
│  7. Validate GREEN State                                        │
│     - Run pytest, expect passes                                 │
│     - Exit code == 0 required                                   │
│         ↓                                                       │
│  8. Update Traceability Tags                                    │
│     - @code: PENDING → @code: src/actual/path.py                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### TDD Configuration

Add to `config/default.yaml`:

```yaml
tdd:
  enabled: false              # Enable via --tdd-mode flag
  generate_tests: true        # Generate test files from TSPEC
  validate_failing: true      # Validate tests fail before code
  validate_passing: true      # Validate tests pass after code
  update_tags: true           # Update PENDING tags to actual paths
  test_framework: pytest
  coverage_threshold: 90
  test_output_dirs:
    unit: tests/unit/
    integration: tests/integration/
    smoke: tests/smoke/
    functional: tests/functional/
```

### TDD Traceability Tags

**Before Code Generation**:
```python
"""
Unit tests for REQ-001
@brd: BRD.01.01.01
@req: REQ-01.01.01
@spec: SPEC-01.yaml
@tspec: TSPEC.01.40.01
@code: PENDING
"""
```

**After Code Generation**:
```python
"""
Unit tests for REQ-001
@brd: BRD.01.01.01
@req: REQ-01.01.01
@spec: SPEC-01.yaml
@tspec: TSPEC.01.40.01
@code: src/services/validation_service.py
"""
```

### TDD Quality Gates

| Phase | Requirement | Exit Code |
|-------|-------------|-----------|
| Red State | All tests fail | != 0 |
| Green State | All tests pass | == 0 |
| Coverage | ≥90% line coverage | Check threshold |

### TDD Scripts Reference (v6.0)

The following scripts support the TDD workflow:

#### Test Analysis Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `analyze_test_requirements.py` | Parse test files, extract traceability tags and method signatures | `--test-dir tests/unit/ --output tmp/test_requirements.json` |
| `generate_spec_tdd.py` | Generate SPEC YAML from test requirements | `--test-requirements tmp/test_requirements.json --output tmp/generated_specs/` |
| `update_test_traceability.py` | Update PENDING tags with actual file paths | `--test-dir tests/unit/ --spec-dir ai_dev_flow/09_SPEC/` |
| `validate_tdd_stage.py` | Validate Red/Green state | `--stage red --test-dir tests/unit/` |

#### Test Generation Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `generate_integration_tests.py` | Generate integration tests from CTR/SYS/SPEC | `--spec-dir ai_dev_flow/09_SPEC/ --output tests/integration/` |
| `generate_smoke_tests.py` | Generate smoke tests from EARS/BDD/REQ | `--bdd-dir ai_dev_flow/04_BDD/ --output tests/smoke/` |

#### TDD Workflow Commands

```bash
# Step 1: Analyze existing tests
python ai_dev_flow/AUTOPILOT/scripts/analyze_test_requirements.py \
  --test-dir tests/unit/ \
  --output tmp/test_requirements.json \
  --verbose

# Step 2: Generate test-aware SPEC
python ai_dev_flow/AUTOPILOT/scripts/generate_spec_tdd.py \
  --test-requirements tmp/test_requirements.json \
  --output ai_dev_flow/09_SPEC/ \
  --verbose

# Step 3: Validate Red State (before implementation)
python ai_dev_flow/AUTOPILOT/scripts/validate_tdd_stage.py \
  --stage red \
  --test-dir tests/unit/

# Step 4: [Implement code based on SPEC]

# Step 5: Validate Green State (after implementation)
python ai_dev_flow/AUTOPILOT/scripts/validate_tdd_stage.py \
  --stage green \
  --test-dir tests/unit/ \
  --code-dir src/ \
  --coverage 90

# Step 6: Update traceability tags
python ai_dev_flow/AUTOPILOT/scripts/update_test_traceability.py \
  --test-dir tests/unit/ \
  --spec-dir ai_dev_flow/09_SPEC/ \
  --tasks-dir ai_dev_flow/11_TASKS/ \
  --code-dir src/

# Step 7: Generate integration tests
python ai_dev_flow/AUTOPILOT/scripts/generate_integration_tests.py \
  --spec-dir ai_dev_flow/09_SPEC/ \
  --ctr-dir ai_dev_flow/08_CTR/ \
  --output tests/integration/

# Step 8: Generate smoke tests
python ai_dev_flow/AUTOPILOT/scripts/generate_smoke_tests.py \
  --bdd-dir ai_dev_flow/04_BDD/ \
  --ears-dir ai_dev_flow/03_EARS/ \
  --output tests/smoke/
```

---

## Change Management (CHG) Integration (v6.0)

CHG integration enables formal change management with the 4-Gate validation system when modifying existing artifacts.

### CHG Mode Activation

```bash
# For L2 Minor changes
python3 ai_dev_flow/AUTOPILOT/scripts/mvp_autopilot.py \
  --root ai_dev_flow \
  --chg-mode \
  --chg-level L2 \
  --chg-source midstream \
  --auto-fix \
  --report markdown

# For L3 Major changes
python3 ai_dev_flow/AUTOPILOT/scripts/mvp_autopilot.py \
  --root ai_dev_flow \
  --chg-mode \
  --chg-level L3 \
  --chg-source upstream \
  --auto-fix \
  --report markdown
```

### 4-Gate System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    4-GATE CHANGE MANAGEMENT                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  GATE-01 (L1-L4)     GATE-05 (L5-L8)                           │
│  Business Layer      Architecture Layer                        │
│  BRD, PRD, EARS,     ADR, SYS, REQ, CTR                        │
│  BDD                                                            │
│       │                   │                                     │
│       └─────────┬─────────┘                                     │
│                 ↓                                               │
│           GATE-09 (L9-L11)                                      │
│           Design/Test Layer                                     │
│           SPEC, TSPEC, TASKS                                    │
│                 ↓                                               │
│           GATE-12 (L12-L14)                                     │
│           Implementation Layer                                  │
│           Code, Tests, Deploy                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Change Level Determination

| Level | Criteria | Process |
|-------|----------|---------|
| **L1 Patch** | Bug fix, typo, no behavior change | Edit in place, version bump |
| **L2 Minor** | Feature add, enhancement, non-breaking | CHG-MVP template, partial regeneration |
| **L3 Major** | Architecture change, breaking change | CHG template, archive old, full cascade |

### Change Source Routing

| Source | Entry Gate | Cascade Path |
|--------|------------|--------------|
| Upstream (L1-L4) | GATE-01 | 01 → 05 → 09 → 12 |
| Midstream (L5-L11) | GATE-05 | 05 → 09 → 12 |
| Downstream (L12-L14) | GATE-12 | 12 only |
| External | GATE-05 | 05 → 09 → 12 |
| Feedback | GATE-12 | 12 (or bubble up) |

### CHG Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     CHG WORKFLOW                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Analyze Change Request                                      │
│     - Identify affected layers                                  │
│     - Determine change level (L1/L2/L3)                         │
│     - Determine entry gate                                      │
│         ↓                                                       │
│  2. Create CHG Document                                         │
│     - Use CHG-MVP-TEMPLATE (L2) or CHG-TEMPLATE (L3)            │
│     - Populate impact analysis                                  │
│         ↓                                                       │
│  3. Validate Gates                                              │
│     - Run gate validation scripts                               │
│     - Collect approvals                                         │
│         ↓                                                       │
│  4. Archive Obsolete (L3 only)                                  │
│     - Move old artifacts to archive/                            │
│     - Add deprecation notices                                   │
│         ↓                                                       │
│  5. Process Affected Layers                                     │
│     - Regenerate downstream artifacts                           │
│     - Update TSPEC if L9+ affected                              │
│         ↓                                                       │
│  6. Repair Traceability                                         │
│     - Update cross-references                                   │
│     - Verify no broken links                                    │
│         ↓                                                       │
│  7. Complete CHG Document                                       │
│     - Update status to Completed                                │
│     - Document lessons learned                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### CHG Configuration

Add to `config/default.yaml`:

```yaml
change_management:
  enabled: false              # Enable via --chg-mode flag
  auto_classify: true         # Auto-determine L1/L2/L3
  create_chg_doc: true        # Auto-create CHG document
  validate_gates: true        # Run gate validation scripts
  archive_obsolete: true      # Archive replaced artifacts (L3)
  chg_directory: "docs/CHG"
  templates:
    l2: "CHG/CHG-MVP-TEMPLATE.md"
    l3: "CHG/CHG-TEMPLATE.md"
  gates:
    gate01: "CHG/scripts/validate_gate01.sh"
    gate05: "CHG/scripts/validate_gate05.sh"
    gate09: "CHG/scripts/validate_gate09.sh"
    gate12: "CHG/scripts/validate_gate12.sh"
```

### CHG Validation Commands

```bash
# Validate CHG routing
python CHG/scripts/validate_chg_routing.py docs/CHG/CHG-XX/CHG-XX.md

# Validate specific gates
./CHG/scripts/validate_gate01.sh docs/CHG/CHG-XX.md
./CHG/scripts/validate_gate05.sh docs/CHG/CHG-XX.md
./CHG/scripts/validate_gate09.sh docs/CHG/CHG-XX.md
./CHG/scripts/validate_gate12.sh docs/CHG/CHG-XX.md

# Validate all applicable gates
./CHG/scripts/validate_all_gates.sh docs/CHG/CHG-XX.md
```

### TSPEC in Change Management

Changes affecting L9 (SPEC) or lower MUST include TSPEC updates:

```
Change → SPEC update → TSPEC update → TASKS update → Code → Tests
                           │
                           └── Test specifications MUST be
                               updated BEFORE code changes
```

---

## Safety & Security

### File Operations
- Writes only inside `--root` directory
- No execution of arbitrary commands
- TASKS documents: Bash commands in content-only mode
- No network calls to external LLMs

### Validation Scripts
- Invoked via subprocess with `shell=True`
- Output capture for reporting
- Error handling with return codes

### Secrets Management

**GitHub Actions**:
- Use repository secrets (e.g., `GCP_PROJECT_ID`)
- Never log or print secrets
- Validate secret configuration in workflows

**Local Development**:
- Never commit secrets
- Use environment variables for sensitive data
- Use `.env` files with appropriate permissions

---

## Advanced Features

### Resume Operation

Resume from last completed layer:
```bash
python3 ai_dev_flow/AUTOPILOT/scripts/mvp_autopilot.py \
  --root ai_dev_flow \
  --resume \
  --auto-fix \
  --report markdown
```

### Plan-Only Mode

Generate execution plan without making changes:
```bash
python3 ai_dev_flow/AUTOPILOT/scripts/mvp_autopilot.py \
  --root ai_dev_flow \
  --plan-only \
  --report markdown
```

### Parallel Execution (Experimental)

Execute layers in parallel when possible:
```bash
python3 ai_dev_flow/AUTOPILOT/scripts/mvp_autopilot.py \
  --root ai_dev_flow \
  --profile parallel \
  --auto-fix
```

---

## Extensibility

### Custom Validators

Add custom validation logic via configuration:
```yaml
# config/custom_validators.yaml
custom_validators:
  - name: business_logic_check
    script: scripts/validate_business_logic.py
    layers: [BRD, PRD, SYS]
    min_score: 95
```

### Custom Code Generators

Support for multiple AI providers via pluggable architecture:
- Vertex AI (GCP)
- OpenAI (via API)
- Anthropic Claude
- Local mock generator for testing

---

## Related Documentation

**Framework Guides**:
- `ai_dev_flow/MVP_WORKFLOW_GUIDE.md` - Workflow patterns
- `ai_dev_flow/MVP_AUTOMATION_DESIGN.md` - Architecture design
- `ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` - SDD methodology
- `ai_dev_flow/TRACEABILITY.md` - Traceability standards

**TSPEC & TDD** (v6.0):
- `ai_dev_flow/10_TSPEC/README.md` - TSPEC layer overview
- `ai_dev_flow/10_TSPEC/TSPEC-00_index.md` - Test specification index
- `ai_dev_flow/TESTING_STRATEGY_TDD.md` - TDD integration guide

**Change Management** (v6.0):
- `ai_dev_flow/CHG/CHANGE_MANAGEMENT_GUIDE.md` - 4-Gate system
- `ai_dev_flow/CHG/CHANGE_CLASSIFICATION_GUIDE.md` - L1/L2/L3 decision
- `ai_dev_flow/CHG/CHG-MVP-TEMPLATE.md` - L2 change template
- `ai_dev_flow/CHG/CHG-TEMPLATE.md` - L3 change template

**Validation**:
- `ai_dev_flow/VALIDATION_STANDARDS.md` - Validation rules
- Layer-specific validation rules: `ai_dev_flow/{LAYER}/*_VALIDATION_RULES.md`

**Scripts**:
- `ai_dev_flow/scripts/README.md` - Script registry
- `ai_dev_flow/10_TSPEC/scripts/README.md` - TSPEC validation scripts
- `ai_dev_flow/CHG/scripts/` - CHG gate validation scripts

---

## Version History

**v6.0** (2026-02-06):
- Added TSPEC layer (L10) integration with 4 test types
- Added TDD workflow mode (`--tdd-mode`) with Red→Green validation
- Added CHG integration (`--chg-mode`) with 4-Gate system
- Fixed layer numbering: TSPEC=L10, TASKS=L11
- Added new CLI flags for TDD and CHG modes
- Updated traceability hierarchy to include TSPEC
- Added TDD configuration section
- Added CHG configuration section
- Enhanced reporting with TDD summary

**v5.0** (2026-01-19):
- Simplified configuration system (modular YAML configs)
- Added Makefile for common operations
- Implemented actual GitHub Actions workflows
- Converted quality gates to Python validator
- Added Docker support
- Created test suite structure
- Improved local development workflow
- Simplified CLI with better defaults
- Decoupled code generation (plugin architecture)

**v4.0** (2026-01-18):
- Original comprehensive autopilot guide
- Single monolithic YAML configuration
- Documentation-only GitHub integration plan

---

## Summary

The MVP Autopilot provides:
- **90%+ automation** of the 11-layer SDD documentation workflow (L1-L11)
- **TSPEC integration** for formal test specifications (Unit, Integration, Smoke, Functional)
- **TDD workflow** with test-first development and Red→Green validation
- **CHG integration** with 4-Gate change management system
- **Quality enforcement** via automated validation gates
- **Flexible execution** for local development and CI/CD
- **Comprehensive documentation** for all features
- **Extensible architecture** for custom validators and generators
- **Production-ready** GitHub Actions integration

**Key Principles**:
- Simplicity over complexity
- Convention over configuration
- Test-first development (TDD)
- Formal change management (CHG)
- Standard operations via Makefile
- Modular configuration files
- Comprehensive testing
- Clear documentation
