---
title: "MVP Autopilot: Core Guide (v5.0 - Simplified & Production-Ready)"
tags:
  - framework-core
  - mvp-workflow
  - automation
custom_fields:
  document_type: guide
  artifact_type: DOCS
  layer: 0
  priority: primary
  development_status: active
---

# MVP Autopilot: Core Guide (v5.0)

This document is the authoritative reference for MVP Autopilot in the AI Dev Flow framework. It explains what autopilot does, how to use it, and provides practical guidance for both local development and GitHub Actions CI/CD.

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

1. **Single-Command Scaffolding**: Generates all MVP artifacts from BRD to TASKS
2. **Template-Based Generation**: Uses repo templates with smart placeholder substitution
3. **Per-Layer Validation**: Runs quality gate validators for each generated document
4. **Auto-Fix Strategies**: Fixes frontmatter, titles, required sections, and traceability tags
5. **Traceability Tagging**: Automatic cumulative tagging across all 15 layers
6. **Flexible Execution**: Supports multiple execution modes and entry/exit points

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
│   ├── mvp_autopilot.py         # Main orchestration script
│   ├── validate_metadata.py        # Metadata validator
│   ├── validate_quality_gates.py   # Quality gate checker (Python)
│   ├── vertex_code_generator.py    # Optional code generator
│   └── requirements.txt            # Python dependencies
├── config/
│   ├── default.yaml                # Default configuration
│   ├── quality_gates.yaml           # Quality gate settings
│   └── layers.yaml                # Layer-specific configs
└── tests/                             # Test suite
    ├── test_config_parsing.py
    ├── test_prechecks.py
    ├── test_cli_parsing.py
    └── integration/
        └── test_full_pipeline.py
```

### Execution Flow

```
┌─────────────────────────────────────────┐
│  Configuration Loading              │
│  (Load YAML configs)               │
└─────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Pre-Checks                       │
│  (Validate paths, dependencies)       │
└─────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Document Generation                │
│  (Use templates, auto-populate tags)  │
└─────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Validation                       │
│  (Run quality gate scripts)         │
└─────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Post-Checks                      │
│  (Verify outputs, link integrity)     │
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

### Execution Modes

| Mode | Description | Use Case |
|-------|-------------|----------|
| **generate** | Default mode - Generate all layers from BRD to TASKS | Standard workflow |
| **validate** | Run validators on existing documents | Quality assurance |
| **resume** | Continue existing project, generate missing layers | Incremental updates |
| **plan** | Generate execution plan without making changes | Preview mode |

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

### TASKS (Layer 10)
**Template**: `11_TASKS/TASKS-MVP-TEMPLATE.md`

**Generation**:
- Generated from template
- Includes execution commands in Section 4
- 8 cumulative tags: `@brd` through `@spec`

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
| **PRD** (L2) | `@brd` | `@brd: BRD-01` |
| **EARS** (L3) | `@brd`, `@prd` | `@brd: BRD-01`, `@prd: PRD-01` |
| **BDD** (L4) | `@brd`, `@prd`, `@ears` | `@brd: BRD-01`, `@prd: PRD-01`, `@ears: EARS-01` |
| **ADR** (L5) | `@brd`, `@prd`, `@ears`, `@bdd` | All upstream tags |
| **SYS** (L6) | `@brd`, `@prd`, `@ears`, `@bdd`, `@adr` | All upstream tags |
| **REQ** (L7) | `@brd` through `@sys` | All upstream tags |
| **CTR** (L8) | `@brd` through `@req` | All upstream tags |
| **SPEC** (L9) | `@brd` through `@ctr` | All upstream tags |
| **TASKS** (L10) | `@brd` through `@spec` | All upstream tags |

### Dotted vs Hyphenated IDs

Auto-pilot converts hyphenated IDs to dotted forms where required:

| Original | Converted | Where Used |
|---------|----------|------------|
| `BRD-01` | `BRD.01` | SYS, REQ, SPEC, TASKS references |
| `PRD-01` | `PRD.01.01` | EARS, BDD, ADR, SYS, REQ, SPEC, TASKS |
| `REQ-15` | `REQ.15.01.01` | SPEC, TASKS references |

---

## Reporting

### Report Formats

**Markdown** (`--report markdown`):
```markdown
# MVP Autopilot Report
**Intent**: ${INTENT}
**Slug**: ${SLUG}
**Status**: PASS | FAIL
**Configuration**: Profile: ${PROFILE}, Strict: ${STRICT}
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
| TASKS | PASS | 92% | ✅ |
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

**Validation**:
- `ai_dev_flow/VALIDATION_STANDARDS.md` - Validation rules
- Layer-specific validation rules: `ai_dev_flow/{LAYER}/*_VALIDATION_RULES.md`

**Scripts**:
- `ai_dev_flow/scripts/README.md` - Script registry

---

## Version History

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
- **90%+ automation** of the 15-layer SDD workflow (L1-L10)
- **Quality enforcement** via automated validation gates
- **Flexible execution** for local development and CI/CD
- **Comprehensive documentation** for all features
- **Extensible architecture** for custom validators and generators
- **Production-ready** GitHub Actions integration

**Key Principles**:
- Simplicity over complexity
- Convention over configuration
- Standard operations via Makefile
- Modular configuration files
- Comprehensive testing
- Clear documentation
