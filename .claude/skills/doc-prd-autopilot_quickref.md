# doc-prd-autopilot Quick Reference

Automated PRD generation pipeline from BRD documents.

## Usage

```bash
# Single BRD
/doc-prd-autopilot BRD-01

# Multiple BRDs
/doc-prd-autopilot BRD-01,BRD-02,BRD-03

# All BRDs (automatic mode)
/doc-prd-autopilot all --auto

# Preview only (no changes)
/doc-prd-autopilot all --dry-run

# Resume after failure
/doc-prd-autopilot resume
```

## 7-Step Workflow

| Step | Action | Output |
|------|--------|--------|
| 1 | Input BRD List | List of BRDs to process |
| 2 | Dependency Analysis | Execution order + parallel groups |
| 3 | PRD-Ready Validation | Score >= 90% (auto-fix available) |
| 4 | PRD Generation | docs/02_PRD/PRD-NN_{slug}/ |
| 5 | EARS-Ready Validation | Score >= 90% (auto-fix available) |
| 6 | Next BRD | Continue sequential processing |
| 7 | Parallel Execution | Independent BRDs processed in parallel |

## Key Options

| Option | Description |
|--------|-------------|
| `--auto` | No confirmation, auto-fix enabled |
| `--dry-run` | Preview execution plan only |
| `--max-parallel N` | Max parallel generations (default: 3) |
| `--min-prd-ready N` | Minimum PRD-Ready score (default: 90) |
| `--continue-on-error` | Don't stop on single BRD failure |

## Scoring Thresholds

| Score | Minimum | Category |
|-------|---------|----------|
| PRD-Ready | 90% | BRD completeness before PRD generation |
| EARS-Ready | 90% | PRD completeness after generation |

## Output Structure

**Monolithic** (<25KB):
```
docs/02_PRD/PRD-01_f1_iam.md
```

**Sectioned** (>=25KB):
```
docs/02_PRD/PRD-01_f1_iam/
├── PRD-01.0_index.md
├── PRD-01.1_document_control.md
...
└── PRD-01.21_qa_strategy.md
```

## Related Skills

- `doc-brd` - Create BRDs (upstream)
- `doc-prd` - Manual PRD creation
- `doc-ears` - Create EARS (downstream)

## Full Documentation

See: `.claude/skills/doc-prd-autopilot/SKILL.md`
