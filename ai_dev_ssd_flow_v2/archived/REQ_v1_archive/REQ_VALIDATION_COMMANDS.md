---
title: "REQ Validation Commands (Quick Reference)"
tags:
  - validation
  - cli
  - req
custom_fields:
  document_type: reference-guide
  artifact_type: REQ
  priority: high
  version: "1.0"
  scope: req-validation
---

# REQ Validation Commands

**Purpose:** Quick reference for REQ-specific validation commands.

**Full Documentation:** See [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md) for complete framework-wide CLI reference covering all document types.

**Strategy & Gates:** See [REQ_VALIDATION_STRATEGY.md](./REQ_VALIDATION_STRATEGY.md) for architecture and gate details.

---

## Master Orchestrator

```bash
# Single file
bash scripts/validate_all.sh --file <file.md>

# Directory  
bash scripts/validate_all.sh --directory <folder>

# Custom SPEC-ready threshold
bash scripts/validate_all.sh --directory <folder> --min-score 95

# Skip validators
bash scripts/validate_all.sh --directory <folder> --skip-quality --skip-spec
```

---

## Individual Validators

### Quality Gate Validator (14 gates, directory-level)
```bash
bash scripts/validate_req_quality_score.sh <directory>
```

### SPEC-Readiness Scorer (0-100% scoring)
```bash
python3 scripts/validate_req_spec_readiness.py --req-file <file>
python3 scripts/validate_req_spec_readiness.py --directory <folder> --min-score 90
```

### Template Compliance (11 sections, file-level)
```bash
bash scripts/validate_req_template.sh <file.md>
```

### ID Format Validator (REQ-NN.MM)
```bash
python3 scripts/validate_requirement_ids.py --req-file <file>
python3 scripts/validate_requirement_ids.py --directory <folder>
```

### Cross-Link Generator (pre-validation helper)
```bash
python3 scripts/add_crosslinks_req.py --req-num 8
python3 scripts/add_crosslinks_req.py --folder <path>
```

---

## Workflows

### Development
```bash
# 1. Create/edit REQ
nano docs/07_REQ/REQ-08_trading_intelligence/REQ-08.01_agent_registry.md

# 2. Add cross-links
python3 scripts/add_crosslinks_req.py --req-num 8

# 3. Validate single file
bash scripts/validate_all.sh --file docs/07_REQ/REQ-08_trading_intelligence/REQ-08.01_agent_registry.md

# 4. Fix issues, repeat 3
```

### Release
```bash
# 1. Validate entire folder
bash scripts/validate_all.sh --directory docs/07_REQ/REQ-08_trading_intelligence

# 2. Address failures (especially ERROR gates)
# 3. Generate SPEC from validated REQ
```

### CI/CD
```bash
#!/bin/bash
for req_file in $(git diff --name-only | grep 'REQ-.*\.md'); do
  bash scripts/validate_all.sh --file "$req_file" || exit 1
done
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Permission denied | `chmod +x scripts/*.sh scripts/*.py` |
| Python not found | Use `python3` explicitly |
| File not found | Use absolute paths in CI environments |

---

## More Information

- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md) - Framework-wide CLI reference
- [REQ_VALIDATION_STRATEGY.md](./REQ_VALIDATION_STRATEGY.md) - REQ gates and architecture
- [REQ_AI_VALIDATION_DECISION_GUIDE.md](./REQ_AI_VALIDATION_DECISION_GUIDE.md) - REQ decision patterns
- [scripts/README.md](./scripts/README.md) - Tool quick start
