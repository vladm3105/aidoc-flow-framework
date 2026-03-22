# UCX Framework: How to Use

This guide covers practical usage of the UCX (Unified Context) Framework.

---

## Prerequisites

- Python 3.10+
- UCX package installed in venv
- Project structure with `docs/` directory
- For CLI mode: Claude CLI, Codex CLI, Gemini CLI, or Ollama installed
- For API mode: Provider API keys

### Installation

```bash
# Activate the shared venv
source /opt/data/docs_flow_framework/.venv/bin/activate

# Verify UCX is installed
ucx --version
```

---

## Two Modes of Operation

UCX supports two modes for AI interaction:

| Mode | Client | When to Use |
|------|--------|-------------|
| **CLI** (default) | `CLIClient` | Use existing CLI tools (Claude CLI, Codex CLI, Gemini CLI) |
| **API** | `LiteLLMClient` | Direct API calls when CLI isn't available |

### CLI Mode (Default)

Uses shell commands to invoke AI CLI tools. No API keys required - uses your existing CLI authentication.

```bash
# Claude CLI (default)
ucx review brd docs/01_BRD/BRD-01/

# Specify CLI tool
ucx --mode cli --cli-tool claude review brd docs/01_BRD/BRD-01/
ucx --mode cli --cli-tool codex --model gpt-5-codex review brd docs/01_BRD/BRD-01/
ucx --mode cli --cli-tool gemini review brd docs/01_BRD/BRD-01/
ucx --mode cli --cli-tool ollama review brd docs/01_BRD/BRD-01/
```

### API Mode

Direct HTTP API calls via LiteLLM. Requires provider API keys.

```bash
# Set API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Use API mode
ucx --mode api --model opus review brd docs/01_BRD/BRD-01/
```

### Validate a PRD Document

```bash
# Full validation (Tier 1 + Tier 2) - Source protected
ucx validate prd docs/02_PRD/PRD-01_user_onboarding/

# Tier 1 only (fast, pre-commit mode) - Source protected
ucx validate prd docs/02_PRD/PRD-01_user_onboarding/ --tier1-only

# Validate without fix analysis
ucx validate prd docs/02_PRD/PRD-01_user_onboarding/ --no-fix

# JSON output
ucx validate prd docs/02_PRD/PRD-01_user_onboarding/ --format json
```

**Source Protection (v1.21.6+)**:
As of v1.21.6, validation uses **source protection**: the utility analyzes what could be fixed, documents recommendations in the validation report, but **never modifies the source PRD/BRD file**. This makes validation a safe, read-only operation that produces only report artifacts.

Example output:
```
Auto-fixing 3 structural issue(s)...
  ✓ GATE-E001: Missing custom_fields.document_type
  ◐ GATE-E002: Missing required tags
    LLM Task: Cross-verify tag alignment with PRD scope
  ⚠ Restored source files (validation report-only):
    → PRD-01_platform_architecture.md
  Source documents unchanged. Fix recommendations documented in validation report only.
```

Use `ucx remediate` to apply actual fixes to the source PRD/BRD if desired.

**Planned PRD Flow (v1.22.0 / PLAN-012)**:
The current command set stops at report-only validation. The planned PRD derived-artifact flow adds:
- `ucx validate-fix prd ...` to create a `_validation` copy from the source PRD plus `PRD-01_validation_report.md`
- `ucx remediate-apply prd ...` to create a `_remediated` copy from the `_validation` PRD plus remediation report

Those commands are not part of the current v1.21.6 runtime.


### Review a PRD Document

```bash
# Multi-persona AI review (10 personas)
ucx review prd docs/02_PRD/PRD-01_user_onboarding/

# One-turn unified review (faster)
ucx review prd docs/02_PRD/PRD-01_user_onboarding/ --one-turn

# With project-specific prompts
ucx -p docs/UCX/ review prd docs/02_PRD/PRD-01_user_onboarding/
```

### Create a New PRD

```bash
# Create PRD from upstream BRD (plain ID — UCX auto-slugs and creates folder)
ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01_platform_architecture
# writes: docs/02_PRD/PRD-01_platform_architecture/PRD-01_platform_architecture.md

# Create with full canonical path (v1.21.1+) — writes directly, no extra nesting
ucx create prd docs/02_PRD/PRD-01_platform_architecture/PRD-01_platform_architecture.md \
    --from-upstream docs/01_BRD/BRD-01_platform_architecture

# v1.21.2+: output guardrails normalize required metadata and target PRD identity
# (frontmatter fields + H1 + Document ID row + PRD.NN element prefix alignment)

# v1.21.3+: prompt history for canonical PRD paths is saved directly in
# docs/02_PRD/<slug>/.ucx_create_session/

# Create with validation
ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01_platform_architecture --validate

# Create with strict validation (fail on any issue)
ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01_platform_architecture --strict

# Prompt history location (v1.21.0+)
ls docs/02_PRD/PRD-01_platform_architecture/.ucx_create_session/

# Optional: include raw PRD LLM responses as Appendix D (disabled by default)
UCX_PRD_LLM_AUDIT_COPY=true \
    ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01_platform_architecture

# Retry with alternate backend/model if quota or rate limit is hit
ucx --cli-tool codex create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01_platform_architecture
ucx --cli-tool gemini --model gemini-2.5-pro create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01_platform_architecture
```

PRD environment toggles:

- `UCX_UPSTREAM_SECTION_CHARS` and `UCX_UPSTREAM_TOTAL_CHARS`: optional upstream clipping controls (default: unlimited)
- `UCX_PRD_LLM_AUDIT_COPY`: set to `true` to append Appendix D with raw LLM attempts; unset/false keeps it disabled

### Project-Specific Prompts & Skills

For best quality, create project-specific prompts AND skills with domain expertise:

```bash
# Use project prompts (recommended)
ucx -p docs/UCX/ review brd docs/01_BRD/BRD-01/

# With model selection
ucx -p docs/UCX/ --model sonnet review brd docs/01_BRD/BRD-01/

# Review PRD with project context
ucx -p docs/UCX/ review prd docs/02_PRD/PRD-01/
```

**Create project directories**:
```bash
# Create prompt directory
mkdir -p docs/UCX/review
cp /opt/data/docs_flow_framework/UCX/ucx/prompts/templates/ucr/UCR_PROMPT_BRD.md \
   docs/UCX/review/UCR_PROMPT_BRD_PROJECT.md

# Create skills directory (v1.8.0+)
mkdir -p docs/UCX/skills
cp /opt/data/docs_flow_framework/UCX/skills/auditor.md \
   docs/UCX/skills/auditor.md
# Then customize for your domain
```

**Prompt naming convention**:
| Pattern | Description |
|---------|-------------|
| `UCR_PROMPT_BRD_PROJECT.md` | Project-specific BRD review (required) |
| `UCR_PROMPT_BRD.md` | Fallback (not recommended) |

**Skill loading (v1.8.0+)**:
| Priority | Location | Behavior |
|----------|----------|----------|
| 1 | `{project}/docs/UCX/skills/` | Project-tuned skills (preferred) |
| 2 | `/UCX/skills/` | Framework defaults (fallback) |

**Key difference**:
- **UCR review prompts**: Project-specific preferred (framework fallback if project prompt is absent)
- **UCC create prompts (v1.21.2+)**: Framework contracts + project overrides are merged
- **UCC prompt session path (v1.21.3+)**: Canonical PRD paths save `.ucx_create_session/` beside the file, not in a nested slug folder
- **Skills**: Project first, framework fallback if not found

**Recommended personas for fintech/compliance**:
1-9: Standard personas (Architect, Auditor, Tech Lead, etc.)
10: **Fact Checker** - Cross-verifies all P0/P1 findings
11: **Chairperson** - Synthesizes verdicts, calculates PRD-Ready score

**Verify skill loading**:
```bash
UCX_LOG_LEVEL=DEBUG ucx review brd docs/01_BRD/BRD-01/
# Look for: "Loaded project-specific skill: auditor from .../docs/UCX/skills"
```

---

## Phase 1: UCC (Creation)

### CLI Usage

```bash
# Create a BRD from reference documents (CLI mode - default)
ucx create brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/

# Create with API mode
ucx --mode api create brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/

# Create a PRD from upstream BRD (auto-slugged output filename)
ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01_platform_architecture
# writes: docs/02_PRD/PRD-01_platform_architecture/PRD-01_platform_architecture.md

# Or supply the full canonical path — UCX writes directly without extra nesting (v1.21.1+)
ucx create prd docs/02_PRD/PRD-01_platform_architecture/PRD-01_platform_architecture.md \
    --from-upstream docs/01_BRD/BRD-01_platform_architecture

# Use specific template
ucx create brd docs/01_BRD/BRD-01 --template BRD-MVP-TEMPLATE.md

# Multi-file output (index + sections)
ucx create brd docs/01_BRD/BRD-01_platform --multi-file
```

### Python API

```python
from ucx import UCCPhase, UCXConfig
from pathlib import Path

# CLI mode (default)
config = UCXConfig(ai_mode="cli", cli_tool="claude")
ucc = UCCPhase(config)

doc = ucc.create(
    doc_type="brd",
    output_path=Path("docs/01_BRD/BRD-01"),
    from_ref=Path("docs/00_REF/"),
)
```

### Options

| CLI Option | Python Parameter | Description |
|------------|------------------|-------------|
| `--mode cli/api` | `ai_mode=` | AI client mode |
| `--cli-tool claude` | `cli_tool=` | CLI tool for cli mode |
| `--model opus` | `model=` | Model for API mode |
| `--from-ref <dir>` | `from_ref=` | Load reference documents |
| `--from-upstream <path>` | `from_upstream=` | Load upstream artifact |
| `--template <file>` | `template=` | Use specific template |
| `--multi-file` | `multi_file=True` | Multi-file output |

---

## Phase 2: UCR (Review)

### CLI Usage

```bash
# Review a document folder (CLI mode - default)
ucx review brd docs/01_BRD/BRD-01_platform/

# Persona prompts mode (recommended for large documents)
ucx review brd docs/01_BRD/BRD-01/ --persona

# Persona prompts with fresh start (clear previous session)
ucx review brd docs/01_BRD/BRD-01/ --persona --no-resume

# Persona prompts with custom session TTL
ucx review brd docs/01_BRD/BRD-01/ -p --session-ttl 48

# Review with specific CLI tool
ucx --mode cli --cli-tool claude review brd docs/01_BRD/BRD-01/

# Review with API mode
ucx --mode api --model opus review brd docs/01_BRD/BRD-01/

# Review a single file
ucx review prd docs/02_PRD/PRD-01.md

# Validate structure only (no AI review)
ucx validate brd docs/01_BRD/BRD-01.md
```

### Persona Prompts Mode

For large documents (>50K tokens), use `--persona` to break the review into per-persona calls:

| Option | Behavior |
|--------|----------|
| `--persona` / `-p` | Use persona prompts mode (resumes from previous session if valid) |
| `--unified` / `-u` | Force unified prompt mode (skip auto-detect for large docs) |
| `--no-resume` | Clear memory and start fresh |
| `--session-ttl N` | Expire sessions older than N hours (default: 24) |
| `--clean-memory` | Remove `.ucx_review_session/` and exit (no review) |
| `--clean-reports` | Remove old review reports, keep only latest |
| `--clean-all` | Clean both session memory and old reports |

**Benefits:**
- **No timeouts** - Each persona call is ~45K tokens instead of 200K+
- **Resume** - Automatically skip completed personas if interrupted
- **Debug** - Inspect prompts/responses in `.ucx_review_session/`
- **Quality** - Each persona generates detailed output (8-10K chars)

**Cleanup options:**
```bash
# Remove session memory for a document
ucx review brd docs/01_BRD/BRD-01/ --clean-memory

# Remove old review reports, keep only latest
ucx review brd docs/01_BRD/BRD-01/ --clean-reports

# Clean both memory and old reports
ucx review brd docs/01_BRD/BRD-01/ --clean-all
```

### Python API

```python
from ucx import UCRPhase, UCXConfig
from pathlib import Path

# CLI mode
config = UCXConfig(ai_mode="cli", cli_tool="claude", cli_timeout=600)
ucr = UCRPhase(config)

# Standard review (single call)
result = ucr.review(
    doc_type="brd",
    doc_path=Path("docs/01_BRD/BRD-01.md"),
)

# Multi-turn review (recommended for large docs)
result = ucr.review_multi_turn(
    doc_type="brd",
    doc_path=Path("docs/01_BRD/BRD-01/"),
    resume=True,           # Skip completed personas (default)
    session_ttl_hours=24,  # Expire old sessions (default: 24)
)

print(f"Score: {result.score}")
print(f"Findings: {len(result.findings)}")
```

### Review Flow

1. **Validation Phase**: Automated schema/structure checks
2. **Content Review Phase**: Multi-persona analysis via AI
3. **Output**: Unified report with P0/P1/P2 findings

### Understanding Findings

| Priority | Meaning | Action |
|----------|---------|--------|
| **P0** | Critical - blocking | Must fix before approval |
| **P1** | High - should fix | Fix before release |
| **P2** | Medium - consider | Optional improvement |

**Finding ID lifecycle (review reports):**
- Persona outputs should emit extraction IDs as `{PREFIX}-P{PRIORITY}-{NNN}`.
- Assembled reports canonicalize findings into hash IDs as `P{0|1|2}-{hex}`.
- Canonical IDs are used for deduplication and weighted scoring; persona IDs remain available for traceability.

---

## Phase 3: UCRem (Remediation)

### Pre-Screening (v1.10.0+)

Before remediation, UCX automatically analyzes the review report to determine which fixer personas are needed:

```bash
# Pre-screen a review report (standalone command)
ucx prescreen BRD-01.UCR_review_report_v003.md --verbose

# Output:
# ┌─────────────────────────┬──────────────────────────────────────┐
# │ Metric                  │ Value                                │
# ├─────────────────────────┼──────────────────────────────────────┤
# │ Total findings          │ 103                                  │
# │ Actionable (P0/P1 open) │ 17                                   │
# │ Domain fixers needed    │ qa_lead                              │
# │ Mandatory fixers        │ chaos_engineer, chairperson         │
# │ Excluded fixers         │ architect, auditor, integration_lead │
# └─────────────────────────┴──────────────────────────────────────┘
# → Remediation will load 3 fixers (saved 3 from loading)

# Save screening results to JSON
ucx prescreen BRD-01.UCR_review_report_v003.md -o screening.json
```

### CLI Usage

```bash
# Auto-detect latest review report (recommended - v1.16.0+)
ucx remediate docs/01_BRD/BRD-01/

# PRD remediation (same command contract)
ucx remediate docs/02_PRD/PRD-01/

# Apply auto-safe fixes automatically
ucx remediate docs/01_BRD/BRD-01/ --apply-auto-safe

# PRD remediation with auto-safe fixes
ucx remediate docs/02_PRD/PRD-01/ --apply-auto-safe

# Use specific report (override auto-detection)
ucx remediate docs/01_BRD/BRD-01/ -r BRD-01.UCR_review_report_v001.md

# PRD remediation using a specific review report
ucx remediate docs/02_PRD/PRD-01/ -r docs/02_PRD/PRD-01/PRD-01.UCX_review_report_v001.md
```

**Auto-detection** finds the latest `*.UCX_review_report_v*.md` by version number:
- `BRD-01.UCX_review_report_v003.md` selected over `v001.md` or `v002.md`
- Falls back to modification time if versions match
 - PRD review reports in the same folder are discovered using the same latest-version strategy

**Remediation output (single canonical report):**
- Each run writes `{DOC-ID}.UCX_remediation_report_v{NNN}.md` in the document directory.
- The remediation report is the canonical artifact for both summary and detailed fix blocks.
- `--apply-auto-safe` applies fixes parsed from the canonical UCX remediation report.
- Remediation generation is source-protected by default: unexpected edits to source documentation files are restored automatically.

### Python API

```python
from ucx import UCRemPhase, UCXConfig
from pathlib import Path

config = UCXConfig(ai_mode="cli", cli_tool="claude")
ucrem = UCRemPhase(config)

# Auto-detect latest review report (v1.16.0+)
fixes, report_path = ucrem.generate_fixes(
    doc_path=Path("docs/01_BRD/BRD-01/"),
)
print(f"Used report: {ucrem.last_review_report}")

# Or specify explicit report
fixes, report_path = ucrem.generate_fixes(
    doc_path=Path("docs/01_BRD/BRD-01/"),
    review_report=Path("docs/01_BRD/BRD-01.UCR_review_report_v003.md"),
)

# Check pre-screening results
print(f"Domain fixers loaded: {ucrem.last_screening.domain_fixers_needed}")
print(f"Excluded fixers: {ucrem.last_screening.excluded_fixers}")
print(f"Token savings: {len(ucrem.last_screening.excluded_fixers)} personas excluded")

for fix in fixes:
    print(f"{fix.fix_id}: {fix.confidence} - {fix.target_section}")
```

### Adaptive Fixer Loading

| Category | Personas | Loading Rule |
|----------|----------|--------------|
| **Domain Fixers** | architect, auditor, qa_lead, integration_lead | Only loaded if they have findings |
| **Mandatory** | chaos_engineer, chairperson | Always loaded |

**Benefits:**
- **Token savings**: 30-60% reduction in prompt size
- **Focused AI attention**: Only relevant domains analyzed
- **Quality synthesis**: Chairperson provides de-duplication and final conclusion

### Fix Confidence Levels

| Level | Description | Action |
|-------|-------------|--------|
| `auto-safe` | Deterministic fix | Apply automatically |
| `auto-assisted` | Template with [TODO] | Apply, complete placeholders |
| `manual-required` | Needs human decision | Create task, don't auto-apply |

---

## Full Workflow (Autopilot)

### CLI Usage

```bash
# Run full autopilot cycle (CLI mode - default)
ucx autopilot brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/

# With API mode
ucx --mode api autopilot brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/

# With iteration limits
ucx autopilot brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/ --max-iterations 3
```

### Python API

```python
from ucx import UCXAutopilot, UCXConfig
from pathlib import Path

config = UCXConfig(
    ai_mode="cli",           # or "api"
    cli_tool="claude",       # for cli mode
    max_iterations=3,
    min_score=90,
)
pilot = UCXAutopilot(config)

result = pilot.run(
    doc_type="brd",
    target=Path("docs/01_BRD/BRD-01"),
    from_ref=Path("docs/00_REF/"),
)

if result.is_success:
    print(f"Success! Score: {result.score}")
else:
    print(f"Needs manual review. Score: {result.score}")
```

---

## AI Availability Probe (v1.21.4+)

The `ucx ai probe` command runs the AI preflight checks without executing a full create/review/remediate cycle. Use it to diagnose AI backend availability, model responsiveness, and date/time validation.

### Basic Usage

```bash
# Quick availability check (3-phase preflight)
ucx ai probe

# Full-output probe with detailed diagnostics
ucx ai probe --full-output

# Specify CLI tool and model
ucx ai probe --cli-tool claude --model opus
ucx ai probe --cli-tool codex --model gpt-5-codex
ucx ai probe --cli-tool gemini
```

### What It Checks

The probe runs a **3-phase availability check**:

| Phase | Check | Result |
|-------|-------|--------|
| **1. Budget/Rate-Limit** | Send minimal prompt; detect quota/rate-limit signals | `"ok"` \| `"quota_exceeded"` \| `"no_response"` |
| **2. Capability** (if Phase 1 fails) | Run tool version/list command (no LLM call) | Determines if binary/daemon is installed |
| **3. Epoch Date Validation** | Ask LLM for UTC date; validate against today's UTC | Confirms coherent responses |

**Phase 3 Robustness (v1.21.5+)**:
- **Two-stage validation**: Primary epoch extraction + ISO date fallback
- **Formatting drift tolerance**: Accepts correct ISO date (YYYY-MM-DD) even if epoch token is malformed
- **Preference logic**: If expected UTC date found in response ISO matches, uses it; otherwise uses first valid ISO date
- **Safety**: Only accepts dates that parse as valid `YYYY-MM-DD` from the response text itself

This handles common LLM formatting errors where the prose includes the correct date but the timestamp is inconsistent (e.g., Claude responses with "2026-03-21" in text but epoch `1774252800` = 2026-03-23 UTC).

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All 3 phases passed; LLM is available and coherent |
| `1` | Phase 1 failed (quota/rate-limit) or Phase 2 failed (tool not installed) |
| `2` | Phase 3 failed (date validation mismatch) |

### Usage in Scripts

```bash
# Health check in CI/CD
ucx ai probe
if [ $? -eq 0 ]; then
    echo "LLM ready; starting review"
    ucx review brd docs/01_BRD/BRD-01/
else
    echo "LLM unavailable; skipping AI operations"
    exit 1
fi

# Diagnosis with full output
ucx ai probe --full-output > probe_report.txt
cat probe_report.txt
```

### Troubleshooting with `--full-output`

```bash
# Get detailed phase-by-phase diagnostics
ucx ai probe --cli-tool claude --full-output

# Example output:
# Phase 1 (Budget Check): ok
# Phase 2 (Capability Check): [skipped - Phase 1 passed]
# Phase 3 (Epoch Date Validation):
#   Expected UTC date: 2026-03-21
#   Response: **2026-03-21 in UTC epoch**: `1774252800` (inconsistent epoch = 2026-03-23)
#   ISO fallback applied: 2026-03-21 found in response text
#   Result: PASS (epoch mismatch accepted via ISO fallback)
```

---

## AI Client Direct Usage

For custom workflows, use the AI clients directly:

```python
from ucx.ai import get_client, CLIClient, LiteLLMClient

# Factory function (recommended)
client = get_client(mode="cli", cli_tool="claude", timeout=600)

# Or direct instantiation
cli_client = CLIClient(cli_tool="claude", timeout=600)
api_client = LiteLLMClient(model="opus")

# Generate response
response = client.generate(
    prompt="Analyze this requirement for completeness...",
    system_prompt="You are a requirements analyst.",
)

# With file context (CLI mode)
response = cli_client.generate_with_context(
    prompt="Review these files for consistency",
    context_files=[Path("file1.md"), Path("file2.md")],
)
```

### Check Available CLI Tools

```python
from ucx.ai import CLIClient

# Check if a tool is available
if CLIClient.is_available("claude"):
    print("Claude CLI is installed")

# List all available tools
available = CLIClient.available_tools()
print(f"Available: {available}")
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `UCX_AI_MODE` | `cli` | AI mode: `cli` or `api` |
| `UCX_CLI_TOOL` | `claude` | CLI tool for cli mode |
| `UCX_CLI_TIMEOUT` | `300` | CLI timeout in seconds |
| `UCX_MODEL` | `opus` | Model for API mode |
| `UCX_API_BASE` | - | Custom API base URL |
| `UCX_MAX_ITER` | `3` | Max review/fix cycles |
| `UCX_MIN_SCORE` | `90` | Minimum passing score |

### API Mode: Provider Keys

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export OPENROUTER_API_KEY="sk-or-..."
```

---

## Troubleshooting

### "ucx: command not found"

Activate the venv:
```bash
source /opt/data/docs_flow_framework/.venv/bin/activate
```

### "CLI tool not found: claude"

Install the CLI tool:
```bash
# Claude CLI
npm install -g @anthropic/claude-code

# Gemini CLI
pip install google-generativeai

# Ollama
# See https://ollama.ai/download
```

### "CLI command timed out"

Increase timeout:
```bash
ucx --mode cli review brd docs/01_BRD/BRD-01/
# Or set environment variable
UCX_CLI_TIMEOUT=900 ucx review brd docs/01_BRD/BRD-01/
```

### "No API key found" (API mode)

Set the provider API key:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Large documents timeout

**Option 1**: Use multi-turn mode (recommended):
```bash
ucx review brd docs/01_BRD/BRD-01/ --persona
```

**Option 2**: Increase timeout:
```python
config = UCXConfig(ai_mode="cli", cli_timeout=900)  # 15 minutes
```

### "Session expired" message

Sessions expire after 24 hours by default. To use a longer TTL:
```bash
ucx review brd docs/01_BRD/BRD-01/ --persona --session-ttl 48
```

### Resume interrupted review

Multi-turn reviews automatically resume from the last completed persona:
```bash
# This will skip completed personas and continue
ucx review brd docs/01_BRD/BRD-01/ --persona
```

To start fresh:
```bash
ucx review brd docs/01_BRD/BRD-01/ --persona --no-resume
```

### Truncated output (CLI mode)

If persona responses are very short (500-800 chars) and contain text like "I need permission to write...", this indicates Claude CLI is asking for interactive permission prompts.

**Solution**: UCX v1.3.1+ automatically adds `--dangerously-skip-permissions` flag to Claude CLI calls. If you're on an older version, update UCX:
```bash
cd /opt/data/docs_flow_framework/UCX
git pull
pip install -e .
```

### Model selection in CLI mode

To use a specific model with Claude CLI:
```bash
# Use sonnet model
ucx --mode cli --cli-tool claude --model sonnet review brd docs/01_BRD/BRD-01/ --persona

# Use haiku for faster reviews
ucx --mode cli --cli-tool claude --model haiku review brd docs/01_BRD/BRD-01/ --persona
```

---

## SDD-Compliant Output Format

UCX v1.5.0+ generates review reports that follow SDD framework document standards:

### Report Structure

```markdown
---
title: "UCR Review Report: [DOC-ID]"
tags: [ucr-review, {type}-review, layer-{N}-artifact, quality-assurance]
custom_fields:
  document_type: ucr-review-report
  source_artifact_type: {TYPE}
  layer: {N}
  personas_applied: {COUNT}
  {downstream}_ready_score: "[SCORE]/100"
---

# UCR Review Report: [DOC-ID]

## 0. Document Control
[Standard SDD document control table]

## 1. Executive Summary
## 2. Critical Findings (P0)
## 3. High Priority Findings (P1)
## 4. Required Remediations
## 5. Enhancement Recommendations (P2)
## 6. Items Verified as Present
## 7. Alternative Solutions
## 8. Per-Persona Detailed Analysis
```

### Downstream-Ready Scores

Each document type tracks readiness for its downstream artifact:

| Source | Layer | Downstream Score | Next Artifact |
|--------|-------|------------------|---------------|
| BRD | 1 | PRD-Ready | PRD |
| PRD | 2 | EARS-Ready | EARS |
| EARS | 3 | BDD-Ready | BDD |
| BDD | 4 | ADR-Ready | ADR |
| ADR | 5 | SYS-Ready | SYS |
| SYS | 6 | REQ-Ready | REQ |
| REQ | 7 | CTR-Ready | CTR |
| CTR | 8 | SPEC-Ready | SPEC |
| SPEC | 9 | TSPEC-Ready | TSPEC |
| TSPEC | 10 | Code-Ready | Implementation |

### Persona Flexibility

The number of personas varies by document type and project:

| Type | Default Personas | Can Customize |
|------|------------------|---------------|
| BRD | 9 | Yes (11 with Fact Checker + Chairperson) |
| PRD | 10 | Yes |
| EARS | 5 | Yes |
| BDD | 6 | Yes |
| ADR | 7 | Yes |
| SYS | 6 | Yes |
| REQ | 5 | Yes |
| CTR | 5 | Yes |
| SPEC | 5 | Yes |
| TSPEC | 5 | Yes |

To customize personas, create a project-specific prompt with your persona list.

### Report Versioning (v1.5.2+)

UCX automatically versions review reports to maintain history:

**Output Filename Format**:
```
{DOC_TYPE}_UCR_REVIEW_v{NNN}.md
```
Example: `BRD_UCR_REVIEW_v001.md`, `BRD_UCR_REVIEW_v002.md`

**Review ID Format**:
```
UCR-{DOC_TYPE}-{DOC_ID}-v{NNN}
```
Example: `UCR-BRD-01-v001`, `UCR-BRD-01-v002`

**Features**:
- Auto-increments version number based on existing reports
- Preserves review history for comparison and auditing
- Review ID appears in YAML frontmatter and Document Control section
- Compatible with `--clean-reports` for cleanup

**Version Management**:
```bash
# Review creates v001 (or next version)
ucx review brd docs/01_BRD/BRD-01/
# Output: docs/01_BRD/BRD-01/BRD_UCR_REVIEW_v001.md

# Next review creates v002
ucx review brd docs/01_BRD/BRD-01/
# Output: docs/01_BRD/BRD-01/BRD_UCR_REVIEW_v002.md

# Clean up, keep only 2 most recent versions
ucx review brd docs/01_BRD/BRD-01/ --clean-reports --keep-versions 2
```

---

## Best Practices

### 1. Use Multi-Turn Mode for Large Documents

For documents >50K tokens, always use `--persona`:
```bash
ucx review brd docs/01_BRD/BRD-01/ --persona
```

### 2. Use CLI Mode When Possible

CLI mode leverages existing authentication and is simpler to configure.

### 3. Let Sessions Resume

Don't use `--no-resume` unless you need a fresh start. Resume saves time by skipping completed personas.

### 4. Always Review Before Approval

Even after fixes, run UCR again to verify.

### 5. Use Project-Specific Prompts

Generic prompts miss domain-specific requirements.

### 6. Choose Appropriate Mode

- **CLI mode**: When you have Claude/Gemini CLI installed
- **API mode**: When CLI isn't available or for programmatic access
- **Multi-turn mode**: When reviewing large documents (>50K tokens)

---

## Working with Actions (v1.18.0)

### What are Actions?

Actions are structured handoffs from BRD review to downstream layers. When a reviewer identifies something outside BRD scope (e.g., technical implementation detail), they create an ACTION instead of a P0/P1/P2 finding.

**Key points:**
- Actions do NOT affect BRD score
- Actions target specific downstream documents (PRD, EARS, BDD, ADR, CTR)
- Actions have suggested priority for the target layer

### Action Format

```
<!-- UCX-ACTION-START -->
ACTION_ID: ACT-7f3a2b1c
TYPE: HANDOFF
TARGET: ADR
PRIORITY: P0
SOURCE: BRD-01 Section 10.2
PERSONA: ARCHITECT
CONTEXT: BRD states "platform must survive partner outage"
REQUIREMENT: Document failover architecture decision
<!-- UCX-ACTION-END -->
```

### Target Layers

| Target | Layer | Handoff Purpose |
|--------|-------|-----------------|
| PRD | L2 | Feature details, user stories, acceptance criteria |
| EARS | L3 | Formal requirement syntax |
| BDD | L4 | Behavior specifications, Gherkin scenarios |
| ADR | L5 | Architecture decisions, technical trade-offs |
| CTR | L8 | API contracts, interface definitions |

**NOT in BRD Handoff**: SPEC (L9) receives from ADR/CTR, not directly from BRD.

### Extracting Actions

```bash
# Get summary of all actions
python scripts/extract_actions.py report.md --format summary

# Extract ADR-targeted actions as markdown
python scripts/extract_actions.py report.md --target ADR --format md

# Extract as JSON for processing
python scripts/extract_actions.py report.md --target PRD --format json -o prd_actions.json

# Filter by priority
python scripts/extract_actions.py report.md --priority P0 --format md
```

### Validating Actions

```bash
# Basic validation
python scripts/validate_actions.py report.md

# Strict mode (warnings = errors)
python scripts/validate_actions.py report.md --strict
```

### Action Types

| Type | Status | Purpose |
|------|--------|---------|
| `HANDOFF` | Implemented | Transfer requirement to downstream layer |
| `INFORM` | Reserved | Context sharing, no action required |
| `REVIEW` | Reserved | Needs human review before processing |
| `DEFER` | Reserved | Out of current scope, future consideration |

---

## See Also

- [README.md](../README.md) - Package overview
- [UNIFIED_CONTEXT_FRAMEWORK.md](UNIFIED_CONTEXT_FRAMEWORK.md) - Framework overview
- [HOW_TO_AUDIT.md](HOW_TO_AUDIT.md) - Audit workflows
- [CHANGELOG_v1.18.0.md](CHANGELOG_v1.18.0.md) - Layer Action Handoff release notes
