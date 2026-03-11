# UCX Framework Quick Start Guide

## Overview

UCX (Unified Context Framework) provides AI-powered document lifecycle management with three phases:
- **UCC** (Creation): Generate new documents from templates
- **UCR** (Review): Multi-persona AI review with domain expertise
- **UCRem** (Remediation): Apply fixes based on review findings

## Prerequisites

```bash
# Activate UCX virtual environment
source /opt/data/docs_flow_framework/.venv/bin/activate

# Verify installation
ucx --version
# Expected: ucx, version 1.9.3+
```

## Basic Commands

### Validate a BRD Document

```bash
# Full validation (Tier 1 + Tier 2) - console output
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/

# Pre-commit validation (Tier 1 only, fast)
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/ --tier1-only

# Strict mode (warnings treated as errors)
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/ --strict

# JSON output for CI/CD
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/ --format json

# Write SDD-compliant validation report to document directory (auto-versioned)
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/ -o docs/01_BRD/BRD-01_platform_architecture/
# → Creates: BRD-01.V_validation_report_v001.md

# Write validation report to specific file
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/ -o tmp/BRD-01_validation.md

# JSON report to file
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/ --format json -o report.json

# Auto-fix structural issues (v1.9.6+)
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/ --fix

# Auto-fix and generate report
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/ --fix --report

# Auto-fix, generate report, and cleanup old reports (recommended)
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/ --fix --report --clean-reports

# Clean up old validation reports, keep only latest (v1.9.5+)
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/ --clean-reports

# Keep 3 most recent validation reports
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/ --clean-reports --keep-versions 3
```

**Validation Report Structure (when using `-o`):**
```
## 0. Document Control (YAML frontmatter + table)
## 1. Executive Summary
## 2. Validation Score Breakdown
## 3. Tier 1 Findings (Core Checks)
## 4. Tier 2 Findings (Advisory Checks)
## 5. Checks Performed
## 6. Recommended Next Steps
```

### Review a BRD Document

```bash
cd /path/to/project
ucx --project-dir . review brd docs/01_BRD/BRD-01_platform_architecture/
```

### Review a PRD Document

```bash
ucx --project-dir . review prd docs/02_PRD/PRD-01_user_onboarding/
```

### Create a New BRD

```bash
ucx --project-dir . create brd --output docs/01_BRD/BRD-XX_new_feature/
```

### Apply Remediation

```bash
ucx --project-dir . remediate brd docs/01_BRD/BRD-01_platform_architecture/
```

## Command Options

| Option | Description |
|--------|-------------|
| `--project-dir PATH` | Project root for loading project-specific prompts and skills |
| `--model MODEL` | AI model: `opus` (default), `sonnet`, `haiku` |
| `--multi-turn` | Force multi-turn persona review mode |
| `--skip-validation` | Skip schema validation (for drafts) |
| `-W` | Enable web search for fact-checking |

## Review Process Architecture

### Phase 1: Unified Validation (Non-AI)

Before AI review, UCX runs UnifiedBRDValidator with tiered checks:

**Tier 1 (Core, blocking)** - Must pass before proceeding:

| Check | Description | Error Codes |
|-------|-------------|-------------|
| Element codes | `BRD.NN.TT.SS` format, uniqueness | `GATE-E008`, `BRD-E001` |
| Structure | Required sections, H1 headings, file naming | `BRD-E006`, `BRD-E002` |
| Metadata | YAML frontmatter, `custom_fields`, tags | `BRD-E002`, `BRD-E003` |
| Quality gates | Placeholders, downstream refs, file size | `GATE-E001`, `GATE-E002`, `GATE-E010` |

**Tier 2 (Advisory, non-blocking)** - Recommendations for quality:

| Check | Description | Warning Codes |
|-------|-------------|---------------|
| Links | Markdown link validation | `LINK-W*` |
| Forward references | SDD layer compliance | `FWDREF-W*` |
| Diagrams | Mermaid/SVG vs prose consistency | `DIAG-W001` |
| Quality gates | Glossary, counts, cost format | `GATE-W003`, `GATE-W007`, `GATE-W009` |

**Exit Codes:**

| Code | Meaning | `--tier1-only` | `--strict` |
|------|---------|----------------|------------|
| `0` | All passed | ✅ | ✅ |
| `1` | Tier 2 warnings only | N/A (skipped) | ❌ Fails |
| `2` | Tier 1 errors | ❌ Fails | ❌ Fails |

> **Note**: Exit code 2 indicates validation completed successfully but found blocking errors - this is expected behavior, not a command failure. The validation report is still generated. These exit codes enable CI/CD integration where pipelines can distinguish between warnings (1) and errors (2).

Use `ucx validate brd <path>` for standalone validation or `ucx review brd <path>` for full AI review pipeline.

### Phase 2: AI Multi-Persona Review

UCX loads the project-specific review prompt and executes 11 persona reviews sequentially.

#### BRD Review Personas (11)

| # | Persona | Domain Focus |
|---|---------|--------------|
| 1 | Architect | System design, scalability, CAP theorem |
| 2 | Auditor | Compliance, regulatory, security |
| 3 | Tech Lead | Core technology, implementation |
| 4 | Integration Lead | External APIs, partner dependencies |
| 5 | Devil's Advocate | Edge cases, failure modes |
| 6 | Operator | DevOps, SRE, monitoring |
| 7 | Strategist | Business economics, ROI |
| 8 | Product Owner | Feature scope, MVP boundaries |
| 9 | Business Analyst | Requirements quality, traceability |
| 10 | Fact Checker | Cross-validation, false positive detection |
| 11 | Chairperson | Consensus synthesis, final scoring |

#### PRD Review Personas (11)

| # | Persona | Domain Focus |
|---|---------|--------------|
| 1 | Architect | Technical feasibility |
| 2 | Auditor | Compliance alignment |
| 3 | Tech Lead | Implementation complexity |
| 4 | Integration Lead | API dependencies |
| 5 | Devil's Advocate | Requirement gaps |
| 6 | UX Strategist | User journeys, accessibility |
| 7 | QA Lead | Testability, BDD scenarios |
| 8 | Product Owner | Scope validation |
| 9 | Business Analyst | Requirement completeness |
| 10 | Fact Checker | Cross-reference validation |
| 11 | Chairperson | Final recommendation |

### Phase 3: Report Generation

Review report written to document directory:
```
{document_dir}/{DOC_ID}.UCR_review_report_v00X.md
```

## Review Mode Selection

| Document Size | Mode | Behavior |
|---------------|------|----------|
| < 100K chars | Single-turn | All personas in one API request |
| >= 100K chars | Multi-turn | 11 sequential API calls with memory |

Force multi-turn for thorough reviews:
```bash
ucx --project-dir . review brd docs/01_BRD/BRD-01/ --multi-turn
```

## Project-Specific Configuration

### Directory Structure

```
project/
├── docs/
│   └── UCX/
│       ├── skills/                    # Project-specific persona skills
│       │   ├── architect.md
│       │   ├── auditor.md
│       │   ├── tech_lead.md
│       │   └── ...
│       ├── review/                    # Review prompts (required)
│       │   ├── UCR_PROMPT_BRD_PROJECT.md
│       │   └── UCR_PROMPT_PRD_PROJECT.md
│       ├── creation/                  # Creation prompts
│       │   └── UCC_PROMPT_BRD_PROJECT.md
│       └── remediation/               # Remediation prompts
│           └── UCRem_PROMPT_BRD_PROJECT.md
```

### Loading Priority

**Skills** (with fallback):
1. Project skills: `{project_dir}/docs/UCX/skills/{persona}.md`
2. Framework skills: `/opt/data/docs_flow_framework/UCX/skills/{persona}.md`

**Prompts** (project-specific only, no fallback):
- `{project_dir}/docs/UCX/review/UCR_PROMPT_{TYPE}_PROJECT.md`

### Skill Injection

During review, UCX injects skill content into persona prompts:

```
=== YOUR DOMAIN KNOWLEDGE ===
[Contents of {persona}.md skill file]
=== END DOMAIN KNOWLEDGE ===
```

## Debug and Troubleshooting

### Enable Debug Logging

```bash
UCX_LOG_LEVEL=DEBUG ucx --project-dir . review brd docs/01_BRD/BRD-01/
```

### Verify Skill Loading

Look for log entries:
```
Loaded project-specific skill: architect from .../docs/UCX/skills
Loaded project-specific skill: auditor from .../docs/UCX/skills
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "No prompt found" | Missing project prompt | Create `UCR_PROMPT_{TYPE}_PROJECT.md` |
| "Skill not loaded" | Missing skill file | Create skill or rely on framework fallback |
| "Validation failed" | Schema errors | Fix YAML frontmatter, element IDs |
| "API timeout" | Large document | Use `--multi-turn` mode |

## Example: BeeLocal Project

```bash
# Activate environment
source /opt/data/docs_flow_framework/.venv/bin/activate

# Navigate to project
cd /opt/data/b-local/b-local-docs

# Review BRD-01 with project-specific skills
ucx --project-dir . review brd docs/01_BRD/BRD-01_platform_architecture/

# Review with web search for regulatory fact-checking
ucx --project-dir . -W review brd docs/01_BRD/BRD-03_security_compliance/

# Review PRD with Sonnet model (faster)
ucx --project-dir . --model sonnet review prd docs/02_PRD/PRD-01/
```

## Version History

| Version | Changes |
|---------|---------|
| 1.9.7 | Extended `--fix` for Tier 2 count mismatches: GATE-W003 (stated vs actual), DIAG-W001 (diagram nodes) |
| 1.9.6 | Auto-fix structural issues (`--fix`), auto-report (`--report`), combined workflow (`--fix --report --clean-reports`) |
| 1.9.5 | Validation report cleanup (`--clean-reports`, `--keep-versions`) |
| 1.9.4 | QA subcategory codes 91-99, section mappings for 3/4, tag pattern updates |
| 1.9.3 | SDD-compliant validation reports with YAML frontmatter, auto-versioning, report naming `{DOC-ID}.V_validation_report_v{NNN}.md` |
| 1.9.2 | Unified validator registry integration - `ucx review` uses UnifiedBRDValidator |
| 1.9.1 | Tier 2 advisory validators (links, references, diagrams) |
| 1.9.0 | Unified BRD Validation with tiered checks and quality gates |
| 1.8.0 | Project-specific skills support with fallback |
| 1.7.0 | Multi-turn persona review mode |
| 1.6.0 | Web search integration |
| 1.5.0 | Schema validation phase |

## Related Documentation

- [UCX README](/opt/data/docs_flow_framework/UCX/README.md)
- [Skills Reference](/opt/data/docs_flow_framework/UCX/skills/README.md)
- [API Reference](/opt/data/docs_flow_framework/UCX/docs/API.md)
