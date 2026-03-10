# UCX - Unified Context Framework

## Overview

**UCX** (Unified Context Framework) is a Python-based document lifecycle management system for AI-driven specification development. It uses a **Unified Context** approach where multiple expert personas collaborate within a single context window.

**Location**: `/opt/data/docs_flow_framework/UCX/`

The system consists of three phases:
1. **UCC (Creation)** - Multi-persona document authoring with skill injection
2. **UCR (Review)** - Multi-persona document validation identifying gaps and issues
3. **UCRem (Remediation)** - Multi-persona fix proposal generation

**Plus**: Full **Autopilot** mode that orchestrates all phases automatically.

---

## Two Modes of Operation

UCX supports two modes for interacting with AI:

| Mode | Client | Description |
|------|--------|-------------|
| **CLI** (default) | `CLIClient` | Execute CLI agents (Claude CLI, Gemini CLI, etc.) via shell commands |
| **API** | `LiteLLMClient` | Direct HTTP API calls via LiteLLM to providers |

### CLI Mode (Default)

Executes AI CLI tools via subprocess. No API keys required - uses your existing CLI authentication.

```bash
# Uses Claude CLI by default
ucx review brd docs/01_BRD/BRD-01/

# Specify CLI tool and model
ucx --mode cli --cli-tool claude --model sonnet review brd docs/01_BRD/BRD-01/
ucx --mode cli --cli-tool gemini review brd docs/01_BRD/BRD-01/
```

Supported CLI tools:
- `claude` - Claude Code CLI (default) - supports `--model opus/sonnet/haiku`
- `gemini` - Google Gemini CLI
- `ollama` - Ollama local LLM CLI
- `aider` - Aider AI coding assistant

**Note**: For Claude CLI, UCX automatically adds `--dangerously-skip-permissions` to prevent interactive permission prompts that would truncate output in subprocess mode.

### API Mode

Direct API calls via LiteLLM. Requires API keys for the provider.

```bash
# Anthropic API
export ANTHROPIC_API_KEY="sk-ant-..."
ucx --mode api --model opus review brd docs/01_BRD/BRD-01/

# OpenAI API
export OPENAI_API_KEY="sk-..."
ucx --mode api --model openai/gpt-4o review brd docs/01_BRD/BRD-01/

# Local Ollama API
ucx --mode api --model ollama/llama3 review brd docs/01_BRD/BRD-01/
```

---

## Installation

### Using the shared venv (recommended)

```bash
# Activate the docs_flow_framework venv
source /opt/data/docs_flow_framework/.venv/bin/activate

# UCX is already installed in editable mode
python -c "from ucx import UCXAutopilot; print('UCX ready')"
```

### Fresh installation

```bash
cd /opt/data/docs_flow_framework
python -m venv .venv
source .venv/bin/activate
pip install -e ./UCX
```

---

## Quick Start

### CLI Usage

```bash
# Activate venv first
source /opt/data/docs_flow_framework/.venv/bin/activate

# Review with Claude CLI (default mode)
ucx review brd docs/01_BRD/BRD-01/

# Multi-turn review (recommended for large documents)
ucx review brd docs/01_BRD/BRD-01/ --multi-turn

# Review with API mode (requires API key)
ucx --mode api --model opus review brd docs/01_BRD/BRD-01/

# Run autopilot
ucx autopilot brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/

# Create new document
ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01

# Validate document structure
ucx validate brd docs/01_BRD/BRD-01.md

# Show help
ucx --help
```

### Project-Specific Prompts (Recommended)

For best results, create project-specific prompts tailored to your domain:

```bash
# Use project prompts directory
ucx -p docs/UCX/ review brd docs/01_BRD/BRD-01/

# Or with full path
ucx --project-prompts /path/to/project/docs/UCX/ review brd docs/01_BRD/BRD-01/
```

**Project prompt directory structure**:
```
docs/UCX/
├── review/
│   ├── UCR_PROMPT_BRD_PROJECT.md   # Project-specific BRD review prompt
│   ├── UCR_PROMPT_PRD_PROJECT.md   # Project-specific PRD review prompt
│   └── ...
├── creation/
│   └── UCC_PROMPT_BRD_PROJECT.md   # Project-specific creation prompts
└── remediation/
    └── UCRem_PROMPT_BRD_PROJECT.md
```

**Prompt search order**:
1. Project prompt dir: `{project_prompts}/review/UCR_PROMPT_BRD_PROJECT.md`
2. Project prompt dir: `{project_prompts}/review/UCR_PROMPT_BRD.md`
3. Framework fallback: `UCR_PROMPT_BRD_PROJECT.md`
4. Framework base: `UCR_PROMPT_BRD.md`

**Benefits of project-specific prompts**:
- Domain-specific personas (e.g., compliance focus for fintech)
- Custom finding priorities (P0/P1/P2 thresholds)
- Project-specific sections to cross-reference
- Additional personas (Fact Checker, Chairperson)

See `docs/UCX/review/UCR_PROMPT_BRD_BEELOCAL.md` for an example 11-persona fintech prompt.

### Multi-Turn Review Mode

For large documents, use `--multi-turn` to break the review into per-persona calls:

```bash
# Multi-turn with memory (auto-resumes if interrupted)
ucx review brd docs/01_BRD/BRD-01/ --multi-turn

# Fresh start (clear previous memory)
ucx review brd docs/01_BRD/BRD-01/ --multi-turn --no-resume

# Custom session TTL (default: 24 hours)
ucx review brd docs/01_BRD/BRD-01/ --multi-turn --session-ttl 48
```

**Benefits:**
- **No timeouts** - Each persona call is smaller (~45K tokens vs 200K+)
- **Resume capability** - Skip completed personas if interrupted
- **Debug/audit** - Inspect prompts and responses in `.doc_review_memory/`
- **Better quality** - Each persona generates detailed output (8-10K chars)

**Session Management:**

| Option | Behavior |
|--------|----------|
| `--multi-turn` | Resume from last session (if valid) |
| `--no-resume` | Clear memory and start fresh |
| `--session-ttl N` | Expire sessions older than N hours (default: 24) |

Sessions auto-invalidate when:
- Document content changes (hash mismatch)
- Session TTL expires
- `--no-resume` flag is used

**Memory Directory Structure:**
```
docs/01_BRD/BRD-01/.doc_review_memory/
├── session.json           # Session state with TTL tracking
├── shared_context.txt     # Document content
├── prompt_architect.txt   # Prompt sent to architect persona
├── response_architect.txt # Response from architect
├── prompt_auditor.txt     # ...
├── response_auditor.txt   # ...
└── final_body.md          # Assembled report
```

**Session JSON Structure:**
```json
{
  "doc_path": "/path/to/document",
  "doc_type": "brd",
  "started_at": "2026-03-09T21:26:20",
  "last_updated_at": "2026-03-09T21:28:37",
  "content_hash": "6b2b23ae4aedcea4",
  "personas": ["architect", "auditor", "tech_lead", ...],
  "completed_personas": ["architect", "auditor"],
  "status": "in_progress"
}
```

**Cleanup Options:**
```bash
# Remove stale session memory (.doc_review_memory/)
ucx review brd docs/01_BRD/BRD-01/ --clean-memory

# Remove old review reports, keep only latest version
ucx review brd docs/01_BRD/BRD-01/ --clean-reports

# Keep N most recent report versions (default: 1)
ucx review brd docs/01_BRD/BRD-01/ --clean-reports --keep-versions 3

# Clean both memory and old reports
ucx review brd docs/01_BRD/BRD-01/ --clean-all
```

### SDD-Compliant Output Format

All UCR review reports and UCRem fix reports now follow SDD framework standards:

**YAML Frontmatter:**
```yaml
---
title: "UCR Review Report: [DOC-ID]"
tags:
  - ucr-review
  - {type}-review
  - layer-{N}-artifact
  - quality-assurance
custom_fields:
  document_type: ucr-review-report
  source_artifact_type: {TYPE}
  source_artifact_id: "[DOC-ID]"
  review_id: "[UCR-TYPE-NN-vNNN]"
  layer: {N}
  review_method: unified-context-review
  personas_applied: {COUNT}
  {downstream}_ready_score: "[SCORE]/100"
  findings_p0: [COUNT]
  findings_p1: [COUNT]
  findings_p2: [COUNT]
---
```

**Document Control Section:**
```markdown
## 0. Document Control

| Item | Details |
|------|---------|
| **Source Document** | [DOC-ID] (Version X.X) |
| **Review ID** | [UCR-TYPE-NN-vNNN] |
| **Review Date** | [YYYY-MM-DDTHH:MM:SS] |
| **Review Method** | UCR (Unified Context Review) |
| **Personas Applied** | {COUNT} ({list of personas}) |
| **Reviewer** | UCX Framework v1.5.x |
| **Status** | [Draft / Final] |
| **{Downstream}-Ready Score** | [SCORE]/100 |
```

**Downstream-Ready Score Mapping:**

| Source Type | Layer | Downstream Score |
|-------------|-------|------------------|
| BRD | 1 | PRD-Ready |
| PRD | 2 | EARS-Ready |
| EARS | 3 | BDD-Ready |
| BDD | 4 | ADR-Ready |
| ADR | 5 | SYS-Ready |
| SYS | 6 | REQ-Ready |
| REQ | 7 | CTR-Ready |
| CTR | 8 | SPEC-Ready |
| SPEC | 9 | TSPEC-Ready |
| TSPEC | 10 | Code-Ready |

### Report Versioning (v1.5.5+)

Review reports are automatically versioned to maintain history:

**Filename Format**: `{DOC_ID}.UCR_review_report_v{NNN}.md`
- Example: `BRD-01.UCR_review_report_v001.md`, `BRD-01.UCR_review_report_v002.md`

**Review ID Format**: `UCR-{TYPE}-{DOC_ID}-v{NNN}`
- Example: `UCR-BRD-01-v001`, `UCR-BRD-01-v002`

```bash
# First review creates v001
ucx review brd docs/01_BRD/BRD-01/
# → BRD-01.UCR_review_report_v001.md (Review ID: UCR-BRD-01-v001)

# Next review creates v002
ucx review brd docs/01_BRD/BRD-01/
# → BRD-01.UCR_review_report_v002.md (Review ID: UCR-BRD-01-v002)

# Clean up old versions, keep latest 2
ucx review brd docs/01_BRD/BRD-01/ --clean-reports --keep-versions 2
```

### Python API

```python
from ucx import UCXAutopilot, UCXConfig

# CLI mode (uses Claude CLI)
config = UCXConfig(ai_mode="cli", cli_tool="claude")
pilot = UCXAutopilot(config)

# Or API mode (uses LiteLLM)
config = UCXConfig(ai_mode="api", model="opus")
pilot = UCXAutopilot(config)

# Run autopilot
result = pilot.run(
    doc_type="brd",
    target="docs/01_BRD/BRD-01",
    from_ref="docs/00_REF/",
)

print(f"Score: {result.score}, Status: {result.status}")
```

### Using the AI Client Directly

```python
from ucx.ai import get_client, CLIClient, LiteLLMClient

# Factory function (recommended)
client = get_client(mode="cli", cli_tool="claude")
response = client.generate("Analyze this code...")

# Or direct instantiation
cli_client = CLIClient(cli_tool="claude", timeout=600)
api_client = LiteLLMClient(model="opus", api_key="sk-ant-...")
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `UCX_AI_MODE` | `cli` | AI client mode: `cli` or `api` |
| `UCX_CLI_TOOL` | `claude` | CLI tool for cli mode |
| `UCX_CLI_TIMEOUT` | `300` | CLI command timeout in seconds |
| `UCX_MODEL` | `opus` | Model for API mode |
| `UCX_API_BASE` | - | Custom API base URL |
| `UCX_MAX_ITER` | `3` | Maximum review/fix cycles |
| `UCX_MIN_SCORE` | `90` | Minimum passing score |
| `UCX_SKIP_DRIFT` | `false` | Skip drift monitoring |
| `UCX_LOG_LEVEL` | `INFO` | Logging level |

### API Mode: Provider Configuration

Set provider-specific API keys for API mode:

```bash
# Anthropic (default for API mode)
export ANTHROPIC_API_KEY="sk-ant-..."

# OpenAI
export OPENAI_API_KEY="sk-..."

# Azure OpenAI
export AZURE_API_KEY="..."
export AZURE_API_BASE="https://your-resource.openai.azure.com"

# Google Gemini
export GEMINI_API_KEY="..."

# OpenRouter
export OPENROUTER_API_KEY="sk-or-..."
```

### API Mode: Model Selection

| Alias | Full Model ID |
|-------|---------------|
| `opus` | `anthropic/claude-opus-4-5-20251101` |
| `sonnet` | `anthropic/claude-sonnet-4-20250514` |
| `haiku` | `anthropic/claude-3-5-haiku-20241022` |

Or use LiteLLM format directly:
```bash
ucx --mode api --model openai/gpt-4o review brd docs/01_BRD/BRD-01.md
ucx --mode api --model azure/gpt-4 review brd docs/01_BRD/BRD-01.md
ucx --mode api --model ollama/llama3 review brd docs/01_BRD/BRD-01.md
```

### Configuration File

Create `ucx.yaml` in your project root:

```yaml
# AI Client
ai_mode: cli           # cli or api
cli_tool: claude       # for cli mode
cli_timeout: 600       # for cli mode
model: opus            # for api mode

# Autopilot
max_iterations: 3
min_score: 90
skip_drift: false

# Skills
load_skills: true

# Logging
log_level: INFO

# Retry (API mode)
retry:
  max_attempts: 3
  base_delay: 1.0

# OpenTelemetry
otel:
  enabled: true
  service_name: ucx
```

### Python Config

```python
from ucx import UCXConfig

# CLI mode config
config = UCXConfig(
    ai_mode="cli",
    cli_tool="claude",
    cli_timeout=600,
    max_iterations=3,
)

# API mode config
config = UCXConfig(
    ai_mode="api",
    model="opus",
    api_key="sk-ant-...",
    max_iterations=3,
)

# Or load from file
config = UCXConfig.from_yaml("ucx.yaml")

# Get AI client from config
client = config.get_ai_client()
```

---

## Package Structure

```
UCX/
├── pyproject.toml              # Package configuration
├── README.md                   # This file
│
├── ucx/                        # Python package
│   ├── __init__.py             # Public API exports
│   ├── api/                    # Public API classes
│   │   ├── autopilot.py        # UCXAutopilot
│   │   ├── creation.py         # UCCPhase
│   │   ├── review.py           # UCRPhase (+ review_multi_turn)
│   │   └── remediation.py      # UCRemPhase
│   │
│   ├── core/                   # Core orchestration
│   │   ├── review_memory.py    # ReviewMemory for multi-turn
│   │   └── persona_prompts.py  # Persona prompt templates
│   │
│   ├── cli/                    # CLI commands
│   │   └── main.py             # Click CLI
│   │
│   ├── ai/                     # AI clients (dual-mode)
│   │   ├── __init__.py         # get_client() factory
│   │   ├── base.py             # BaseAIClient ABC
│   │   ├── cli_client.py       # CLIClient (shell subprocess)
│   │   ├── litellm_client.py   # LiteLLMClient (HTTP API)
│   │   ├── claude.py           # ClaudeClient (legacy)
│   │   ├── retry.py            # Retry policies
│   │   └── tokens.py           # Token management
│   │
│   ├── config/                 # Configuration
│   │   ├── settings.py         # Pydantic settings
│   │   └── layer_skills.py     # Layer-to-skill mapping
│   │
│   ├── models/                 # Data models
│   │   ├── enums.py            # DocType, Status enums
│   │   ├── document.py         # Document model
│   │   ├── review.py           # Review result
│   │   └── drift_cache.py      # Drift cache
│   │
│   ├── validators/             # Document validators
│   │   ├── brd.py, prd.py      # Layer validators
│   │   └── registry.py         # Validator registry
│   │
│   ├── prompts/                # Prompt management
│   │   ├── loader.py           # Template loading
│   │   ├── renderer.py         # Jinja2 rendering
│   │   └── templates/          # Prompt templates
│   │       ├── ucc/            # Creation templates
│   │       └── ucr/            # Review templates (UCR_PROMPT_*.md)
│   │
│   ├── skills/                 # Skill/persona management
│   │   ├── loader.py           # Skill loading
│   │   ├── injector.py         # Prompt injection
│   │   └── personas/           # 12 persona definitions
│   │
│   └── utils/                  # Utilities
│       ├── file_ops.py
│       ├── hash.py
│       └── logging.py
│
└── tests/                      # Test suite
```

---

## Supported Document Types

| Layer | Type | Description |
|-------|------|-------------|
| L1 | BRD | Business Requirements Document |
| L2 | PRD | Product Requirements Document |
| L3 | EARS | Easy Approach to Requirements Syntax |
| L4 | BDD | Behavior-Driven Development (Gherkin) |
| L5 | ADR | Architecture Decision Records |
| L6 | SYS | System Requirements |
| L7 | REQ | Atomic Requirements |
| L8 | CTR | Data Contracts |
| L9 | SPEC | Technical Specifications |
| L10 | TSPEC | Test Specifications |

---

## Core Philosophy

**FALSE NEGATIVES ARE UNACCEPTABLE.** Missing a real issue is far worse than flagging something that turns out to be present.

| Error Type | Risk Level | Consequence |
|------------|------------|-------------|
| **False Positive** | LOW | Extra verification - easily corrected |
| **False Negative** | **CRITICAL** | Missing requirements propagate downstream |

**Rule: When in doubt, FLAG IT.**

---

## Personas

UCX uses up to 13 expert personas for document review (11 required + 2 optional):

### Core Personas (Required)

| Persona | Focus |
|---------|-------|
| Architect | System design, scalability |
| Auditor | Compliance, security |
| Tech Lead | Implementation feasibility |
| Strategist | Economics, trade-offs |
| Devil's Advocate | Edge cases, failure modes |
| Operator | Observability, deployment |
| Integration Lead | Dependencies, contracts |
| Product Owner | Business value, scope |
| Business Analyst | Requirements completeness |
| Fact Checker | Cross-validation, false positive detection |
| Chairperson | Consensus synthesis, score calculation |

### Quality Assurance Personas (Optional)

| Persona | Focus |
|---------|-------|
| Judge | Validates Chairperson analysis for bias/accuracy |
| Chairperson Editor | Final polish and consistency check |

### Layer-Specific Personas

| Persona | Focus | Used In |
|---------|-------|---------|
| QA Lead | Testability, BDD syntax | PRD, EARS, BDD, TSPEC |
| Requirements Specialist | EARS/INCOSE syntax | EARS, REQ |
| UX Strategist | User journey, accessibility | PRD |

---

## API Reference

### UCXAutopilot

```python
from ucx import UCXAutopilot

pilot = UCXAutopilot(config)

result = pilot.run(
    doc_type="brd",
    target=Path("docs/01_BRD/BRD-01"),
    from_ref=Path("docs/00_REF/"),
)

print(result.score)          # 92
print(result.status)         # Status.PASS
print(result.iterations)     # 2
```

### Phase APIs

```python
from ucx import UCCPhase, UCRPhase, UCRemPhase

# Creation
ucc = UCCPhase(config)
doc = ucc.create(doc_type="brd", output_path=path, from_ref=ref_dir)

# Review (single call - may timeout on large docs)
ucr = UCRPhase(config)
result = ucr.review(doc_type="brd", doc_path=path)

# Review (multi-turn - recommended for large docs)
result = ucr.review_multi_turn(
    doc_type="brd",
    doc_path=path,
    resume=True,           # Skip completed personas (default)
    session_ttl_hours=24,  # Expire old sessions (default: 24)
)

# Remediation
ucrem = UCRemPhase(config)
fixes = ucrem.generate_fixes(review_report=report_path, doc_path=path)
```

### Review Memory API

```python
from ucx.core.review_memory import ReviewMemory

# Initialize memory
memory = ReviewMemory(doc_path, doc_type="brd")
memory.initialize(personas=["architect", "auditor"], content_hash="abc123")

# Save/load prompts and responses
memory.save_prompt("architect", prompt_text)
memory.save_response("architect", response_text, duration_ms=68000)

# Check resume state
if memory.is_persona_complete("architect"):
    response = memory.get_response("architect")

# Assemble final report
final_report = memory.assemble_report()
```

### AI Client Factory

```python
from ucx.ai import get_client

# CLI mode
client = get_client(mode="cli", cli_tool="claude", timeout=600)

# API mode
client = get_client(mode="api", model="opus", api_key="...")

# Generate
response = client.generate("Analyze this document...")
```

---

## Testing

```bash
source /opt/data/docs_flow_framework/.venv/bin/activate
cd /opt/data/docs_flow_framework/UCX

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=ucx --cov-report=term-missing
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.5.5 | 2026-03-10 | **Report naming standardization**: Changed from `{TYPE}_UCR_REVIEW_v{NNN}.md` to `{DOC_ID}.UCR_review_report_v{NNN}.md`. **Layer-appropriate finding classification**: BRD reviews now distinguish requirements (P0) from implementation details (defer to SPEC). **Pre-validation separation**: YAML/schema errors reported separately from content P0 findings. **Complexity scale**: Replaced time estimates with 1-5 complexity scale. |
| 1.5.4 | 2026-03-10 | Added Fact Checker and Chairperson as required personas. Added Judge and Chairperson Editor as optional personas. |
| 1.5.1 | 2026-03-10 | Added `--clean-reports` and `--clean-all` flags to clean old review reports while keeping latest. |
| 1.5.0 | 2026-03-10 | SDD-compliant output format for all review reports. YAML frontmatter, Document Control section, layer-specific downstream-ready scores. All 10 UCR templates updated. |
| 1.4.1 | 2026-03-10 | Added `--clean-memory` flag to remove stale session memory. |
| 1.4.0 | 2026-03-10 | Project-specific prompts support with `-p/--project-prompts` flag. One-prompt with Fact Checker/Chairperson personas. |
| 1.3.1 | 2026-03-10 | CLI mode fix: Added `--dangerously-skip-permissions` flag to prevent truncated output from permission prompts. |
| 1.3.0 | 2026-03-09 | Multi-turn review mode with doc_review_memory for large documents. |
| 1.2.0 | 2026-03-09 | Dual-mode architecture: CLI mode (default) + API mode. Extended logging. |
| 1.1.0 | 2026-03-09 | LiteLLM integration for multi-provider LLM support. |
| 1.0.0 | 2026-03-09 | Python migration complete. API, CLI, full test suite. |

---

## Legacy Shell Scripts

The following shell scripts are deprecated:
- `run_ucx_autopilot.sh` - Use `ucx autopilot` CLI instead
- `run_ucc.sh`, `run_ucr.sh`, `run_ucrem.sh` - Use `ucx create/review/remediate`

For legacy documentation, see `SKILL_INDEX.md`.
