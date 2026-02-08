---
title: "REQ Validation Strategy (Quick Reference)"
tags:
  - validation
  - req
  - quick-reference
custom_fields:
  document_type: quick-reference
  artifact_type: REQ
  priority: high
  version: "1.0"
  scope: req-validation
---

# REQ Validation Strategy (Quick Reference)

**Purpose:** Quick reference for REQ validation architecture, gates, and patterns.

**Full Documentation:** See [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) for framework-wide architecture and patterns applicable to all document types.

**CLI Reference:** See [REQ_VALIDATION_COMMANDS.md](./REQ_VALIDATION_COMMANDS.md) for all command syntax.

**Decision Guide:** See [REQ_AI_VALIDATION_DECISION_GUIDE.md](./REQ_AI_VALIDATION_DECISION_GUIDE.md) for REQ-specific decision patterns.

---

## REQ Validation Architecture

### Master Orchestrator

```
validate_all.sh (Master Orchestrator)
├── File Mode:
│   ├─ validate_req_spec_readiness.py --req-file <file>
│   ├─ validate_req_template.sh <file>
│   └─ validate_requirement_ids.py --req-file <file>
│
└── Directory Mode:
    ├─ validate_req_quality_score.sh <directory>
    ├─ validate_req_spec_readiness.py --directory <directory>
    └─ validate_requirement_ids.py --directory <directory>
```

---

## 14 REQ Quality Gates

| Gate | Type | Name | Brief |
|------|------|------|-------|
| 01 | ERROR | Placeholder Detection | Remove TBD, TODO, FIXME |
| 02 | ERROR | Premature References | No forward references |
| 03 | WARNING | Count Consistency | Section counts match |
| 04 | ERROR | Index Sync | REQ index up-to-date |
| 05 | INFO | Cross-Linking | @depends/@discoverability tags |
| 06 | ERROR | Diagram Validation | Mermaid syntax valid |
| 07 | WARNING | Glossary Consistency | SHALL vs MUST usage |
| 08 | ERROR | ID Uniqueness | No duplicate element IDs |
| 09 | WARNING | Priority Distribution | Priority levels valid |
| 10 | WARNING | File Size Compliance | Token limits respected |
| 11 | ERROR | Traceability Tags | @brd, @prd, @ears present |
| 22 | WARNING | Upstream TBD Refs | Resolve dependencies |

**Plus:** Template (11 sections), SPEC-readiness (0-100%), ID format validation.

---

## Quick Usage

```bash
# Single file
bash scripts/validate_all.sh --file path/to/file.md

# Directory
bash scripts/validate_all.sh --directory path/to/folder

# Strict scoring (95% instead of 90%)
bash scripts/validate_all.sh --directory path/to/folder --min-score 95

# Quick check (skip quality gates)
bash scripts/validate_all.sh --directory path/to/folder --skip-quality
```

---

## Validator Activity

| Validator | Mode | Called | Purpose |
|-----------|------|--------|---------|
| validate_all.sh | Both | User → CLI | Master orchestrator |
| validate_req_quality_score.sh | Directory | validate_all.sh | 14 quality gates |
| validate_req_spec_readiness.py | Both | validate_all.sh | Readiness 0-100% |
| validate_req_template.sh | File | validate_all.sh | 11-section MVP |
| validate_requirement_ids.py | Both | validate_all.sh | ID format (REQ-NN.MM) |
| add_crosslinks_req.py | Generator | User → pre-validation | @depends/@discoverability |

**All tools actively integrated. No dead code.**

---

## More Information

**Framework-Level Docs:**
- [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) - Complete architecture and gates
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md) - CLI reference for all document types
- [../AI_VALIDATION_DECISION_GUIDE.md](../AI_VALIDATION_DECISION_GUIDE.md) - Decision framework

**REQ-Specific Docs:**
- [REQ_VALIDATION_COMMANDS.md](./REQ_VALIDATION_COMMANDS.md) - REQ CLI commands
- [REQ_AI_VALIDATION_DECISION_GUIDE.md](./REQ_AI_VALIDATION_DECISION_GUIDE.md) - REQ decision patterns
- [scripts/README.md](./scripts/README.md) - Tool quick start
