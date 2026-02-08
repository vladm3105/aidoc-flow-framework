# REQ Validation & Cross-Link Scripts

Collection of tools for validating REQ documents and generating cross-links.

**All scripts are called by the master orchestrator** (`validate_all.sh`). Run it for unified validation across all checks.

**For detailed architectural guidance**, see [../REQ_VALIDATION_STRATEGY.md](../REQ_VALIDATION_STRATEGY.md) (REQ-specific) or [../../VALIDATION_STRATEGY_GUIDE.md](../../VALIDATION_STRATEGY_GUIDE.md) (framework-wide).

**Related Documentation:**
- [../REQ_VALIDATION_COMMANDS.md](../REQ_VALIDATION_COMMANDS.md) - REQ validation CLI commands
- [../../VALIDATION_COMMANDS.md](../../VALIDATION_COMMANDS.md) - Framework-wide CLI reference
- [../../VALIDATION_STRATEGY_GUIDE.md](../../VALIDATION_STRATEGY_GUIDE.md) - Architecture, gates, patterns
- [../REQ_AI_VALIDATION_DECISION_GUIDE.md](../REQ_AI_VALIDATION_DECISION_GUIDE.md) - REQ decision patterns
- [../../AI_VALIDATION_DECISION_GUIDE.md](../../AI_VALIDATION_DECISION_GUIDE.md) - Framework decision guide

---

## Quick Start

### Installation

```bash
# Ensure scripts are executable
chmod +x validate_all.sh
chmod +x validate_req_quality_score.sh
chmod +x validate_req_template.sh
chmod +x *.py

# Optional: Add to your PATH for global access
export PATH="$PATH:$(pwd)"
```

### Basic Usage

**Validate a single file:**
```bash
bash validate_all.sh --file docs/07_REQ/REQ-06_f6_infrastructure/REQ-06.01_cloud_run_deployment.md
```

**Validate an entire folder:**
```bash
bash validate_all.sh --directory docs/07_REQ/REQ-06_f6_infrastructure
```

**Validate with higher threshold (95% instead of default 90%):**
```bash
bash validate_all.sh --directory docs/07_REQ/REQ-06_f6_infrastructure --min-score 95
```

**Skip specific validators (quick check):**
```bash
bash validate_all.sh --directory . --skip-quality --skip-template
```

---

## Tool Overview

### 1. validate_all.sh (Master Orchestrator)

Entry point for all validation workflows.

**Modes:**
- **File Mode**: Validates single REQ file (SPEC-ready, Template, IDs)
- **Directory Mode**: Validates folder (Quality Gates, SPEC-ready, IDs)

**Common Options:**
- `--file <path>` - Single file validation
- `--directory <path>` - Directory validation
- `--min-score 85` - Custom SPEC-ready threshold (default: 90%)
- `--skip-quality` - Bypass quality gate checks
- `--skip-spec` - Bypass SPEC-readiness scoring
- `--skip-template` - Bypass template validation
- `--skip-ids` - Bypass ID format checks

### 2. validate_req_quality_score.sh (Quality Gates)

Validates 14 quality gates across a directory (corpus-level).

**Key Gates:**
- Placeholder text detection (TBD, TODO, FIXME)
- ID uniqueness
- Traceability tags (@brd, @prd, @ears)
- Template format
- Diagram syntax validation

```bash
bash validate_req_quality_score.sh docs/07_REQ/REQ-06_f6_infrastructure
```

### 3. validate_req_spec_readiness.py (Readiness Scoring)

Scores REQ files on readiness for SPEC generation (0-100%).

**Factors:** Protocol definitions, Pydantic models, exceptions, YAML configs, element completeness.

```bash
# Score single file
python3 validate_req_spec_readiness.py --req-file docs/07_REQ/REQ-08.01_agent_registry.md

# Score directory
python3 validate_req_spec_readiness.py --directory docs/07_REQ/REQ-08_trading_intelligence --min-score 85
```

### 4. validate_req_template.sh (Template Compliance)

Validates that REQ files follow the 11-section MVP template.

```bash
bash validate_req_template.sh docs/07_REQ/REQ-06.01_cloud_run_deployment.md
```

**Note:** File-level only.

### 5. validate_requirement_ids.py (ID Validation)

Validates REQ ID format (REQ-NN.MM), no duplicates, hierarchical organization.

```bash
# Single file
python3 validate_requirement_ids.py --req-file docs/07_REQ/REQ-08.01_agent_registry.md

# Directory
python3 validate_requirement_ids.py --directory docs/07_REQ/REQ-08_trading_intelligence
```

### 6. add_crosslinks_req.py (Cross-Link Generator)

Pre-validation step that auto-generates cross-links (@depends, @discoverability).

```bash
python3 add_crosslinks_req.py --req-num 8

# Then validate
bash validate_all.sh --directory docs/07_REQ/REQ-08_trading_intelligence
```

---

## Troubleshooting

### "No such file or directory: validate_all.sh"

Ensure you're in the scripts directory and the file exists:

```bash
ls -la validate_all.sh    # Check if file exists
chmod +x validate_all.sh  # Make executable
bash validate_all.sh --help  # Test
```

### "Python: command not found"

Use `python3` instead of `python`:

```bash
python3 validate_req_spec_readiness.py --file <path>
```

### Script fails with permission denied

Make scripts executable:

```bash
chmod +x *.sh *.py
```

### Validation passes locally but fails in CI

Ensure the working directory path is correct:

```bash
# Use absolute paths in CI environments
bash $(pwd)/validate_all.sh --directory /absolute/path/to/REQ
```

---

## More Information

For usage patterns, gate details, assessment, and integration architecture, see [VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md).

For CLI command reference, see [VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md).

For decision-making framework, see [AI_VALIDATION_DECISION_GUIDE.md](../AI_VALIDATION_DECISION_GUIDE.md).
