# Implementation Plan - Fix Framework Format Issues

**Created**: 2025-12-10 17:35:59 EST
**Completed**: 2025-12-10 EST
**Status**: ✅ Completed
**Reference Report**: `/opt/data/docs_flow_framework/tmp/FRAMEWORK_FORMAT_REVIEW_REPORT_20251210.md`

## Objective

Fix all formatting issues identified in the framework document review across 10 files, including promotional language, tag format standardization, QA terminology migration, and TBD placeholder replacements.

## Context

A comprehensive review of the docs_flow_framework identified several categories of formatting issues:
- Recent commits (4fde14d, 046187a, bb9d144) addressed many issues
- Remaining items are focused on language consistency, tag format, and script updates
- NFR (Non-Functional Requirements) → QA (Quality Attributes) terminology migration in progress

## Task List

### Completed

- [x] Fix promotional language in CTR/README.md (lines 156, 164)
- [x] Fix promotional language in ADR/README.md (lines 394, 883)
- [x] Fix promotional language in PRD/PRD-TEMPLATE.md (line 491)
- [x] Update tag format in PRD_CREATION_RULES.md
- [x] Update tag format in PRD_VALIDATION_RULES.md
- [x] Update validate_req_spec_readiness.py for QA terminology
- [x] Update validate_brd_template.sh for QA terminology
- [x] Update validate_req_template.sh for QA terminology
- [x] Replace TBD in TRACEABILITY_MATRIX_SPEC_EXAMPLE.md
- [x] Replace TBD/REQ-XXX in BDD-000_index.md

### Additional Fixes (discovered during verification)

- [x] Fix promotional language in REQ/README.md (line 429): "Easy to track" → "Enables tracking"
- [x] Fix promotional language in REQ/REQ-TEMPLATE.md (line 967): "Easy to mock" → "Enables mocking"

## Implementation Guide

### HIGH Priority: Promotional Language (3 files)

#### 1. CTR/README.md
**Path**: `/opt/data/docs_flow_framework/ai_dev_flow/CTR/README.md`
| Line | Current | Replace With |
|------|---------|--------------|
| 156 | "Easy to manage 50+ contracts" | "Supports management of 50+ contracts" |
| 164 | "Easy to trace CTR → SPEC" | "Enables tracing CTR → SPEC" |

#### 2. ADR/README.md
**Path**: `/opt/data/docs_flow_framework/ai_dev_flow/ADR/README.md`
| Line | Current | Replace With |
|------|---------|--------------|
| 394 | "Easy to scan" | "Structure enables navigation" |
| 883 | "easy for LLMs/AI agents" | "structured for LLMs/AI agents" |

#### 3. PRD/PRD-TEMPLATE.md
**Path**: `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD-TEMPLATE.md`
| Line | Current | Replace With |
|------|---------|--------------|
| 491 | "optimal user experience" | "consistent user experience" |

### MEDIUM Priority: Tag Format Standardization (2 files)

#### 4. PRD/PRD_CREATION_RULES.md
**Path**: `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD_CREATION_RULES.md`
| Line | Current | Replace With |
|------|---------|--------------|
| 84 | `@brd: BRD-XXX` | `@brd: BRD.NNN.NNN` |
| 112 | `@brd: BRD-NNN` | `@brd: BRD.NNN.NNN` |

#### 5. PRD/PRD_VALIDATION_RULES.md
**Path**: `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD_VALIDATION_RULES.md`
| Line | Current | Replace With |
|------|---------|--------------|
| 112 | `@brd: BRD-XXX` | `@brd: BRD.NNN.NNN` |

### MEDIUM Priority: QA Terminology (3 scripts)

#### 6. scripts/validate_req_spec_readiness.py
**Path**: `/opt/data/docs_flow_framework/ai_dev_flow/scripts/validate_req_spec_readiness.py`
| Line | Current | Replace With |
|------|---------|--------------|
| 11 | "Non-functional requirements" | "Quality attributes" |
| 47 | `r"##\s*7\.\s*Non-Functional\s+Requirements"` | `r"##\s*7\.\s*Quality\s+Attributes"` |
| 180 | docstring "Non-Functional Requirements" | "Quality Attributes" |
| 183 | error message "Non-Functional Requirements" | "Quality Attributes" |

#### 7. scripts/validate_brd_template.sh
**Path**: `/opt/data/docs_flow_framework/ai_dev_flow/scripts/validate_brd_template.sh`
| Line | Current | Replace With |
|------|---------|--------------|
| 47 | `"## 7. Non-Functional Requirements"` | `"## 7. Quality Attributes"` |

#### 8. scripts/validate_req_template.sh
**Path**: `/opt/data/docs_flow_framework/ai_dev_flow/scripts/validate_req_template.sh`
| Line | Current | Replace With |
|------|---------|--------------|
| 47 | `"## 7. Non-Functional Requirements"` | `"## 7. Quality Attributes"` |

### LOW Priority: TBD Replacements (2 files)

#### 9. SPEC/examples/TRACEABILITY_MATRIX_SPEC_EXAMPLE.md
**Path**: `/opt/data/docs_flow_framework/ai_dev_flow/SPEC/examples/TRACEABILITY_MATRIX_SPEC_EXAMPLE.md`
| Line | Current | Replace With |
|------|---------|--------------|
| 171 | `TBD` (Performance verification) | `Pending performance baseline` |
| 172 | `TBD` (Observability verification) | `Metrics dashboard review` |

#### 10. BDD/BDD-000_index.md
**Path**: `/opt/data/docs_flow_framework/ai_dev_flow/BDD/BDD-000_index.md`
| Lines | Current | Replace With |
|-------|---------|--------------|
| 106, 116, 126, 146, 156 | `REQ-XXX` | Context-appropriate REQ IDs or "REQ.NNN.NNN" format |
| 249-252 | `[TBD]` | `[Pending]` (4 metrics rows) |

### Execution Order

1. HIGH: Fix promotional language (3 files, 5 edits)
2. MEDIUM: Update tag format (2 files, 3 edits)
3. MEDIUM: Update QA terminology (3 scripts, ~8 edits)
4. LOW: Replace TBD values (2 files, ~10 edits)

**Total**: 10 files, ~26 edits (+ 2 additional fixes discovered during verification = 12 files, ~28 edits)

### Verification

After fixes:
```bash
# Check for remaining promotional language
grep -rn "Easy to" ai_dev_flow/ --include="*.md" | grep -v EARS

# Check for optimal outside technical metrics
grep -rn "optimal" ai_dev_flow/ --include="*.md"

# Check for old tag format
grep -rn "BRD-XXX\|PRD-XXX" ai_dev_flow/ --include="*.md"

# Check for NFR in scripts
grep -rn "Non-Functional Requirements" ai_dev_flow/scripts/

# Check for TBD in example files
grep -n "\[TBD\]" ai_dev_flow/SPEC/examples/*.md ai_dev_flow/BDD/BDD-000_index.md
```

## Verification Results

All verification checks passed:
- ✅ "Easy to" promotional language removed from target files (EARS excluded as expected)
- ✅ "optimal" remaining uses are valid technical contexts
- ✅ Tag format standardized to `BRD.NNN.NNN` pattern
- ✅ QA terminology updated in all 3 validation scripts
- ✅ All `[TBD]` placeholders replaced with meaningful values

## References

- Review report: `/opt/data/docs_flow_framework/tmp/FRAMEWORK_FORMAT_REVIEW_REPORT_20251210.md`
- Plan file: `/home/ya/.claude/plans/dreamy-tinkering-peach.md`
- Related commits: 4fde14d, 046187a, bb9d144, 77b67f6, f4531c6
