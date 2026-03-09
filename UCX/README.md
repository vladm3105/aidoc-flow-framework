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

### Python API (Recommended)

```python
from ucx import UCXAutopilot, UCXConfig

# Create autopilot with config
config = UCXConfig(model="opus", max_iterations=3, min_score=90)
pilot = UCXAutopilot(config)

# Run autopilot on a document
result = pilot.run(
    doc_type="brd",
    target="docs/01_BRD/BRD-01",
    from_ref="docs/00_REF/",
)

print(f"Score: {result.score}, Status: {result.status}")
```

### CLI

```bash
# Activate venv first
source /opt/data/docs_flow_framework/.venv/bin/activate

# Run autopilot
ucx autopilot brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/

# Review existing document
ucx review brd docs/01_BRD/BRD-01.md

# Create new document
ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01

# Validate document structure
ucx validate brd docs/01_BRD/BRD-01.md

# Show help
ucx --help
```

### MCP Server

```bash
# Start MCP server (stdio transport)
ucx serve

# Or with HTTP transport
ucx serve --transport http --port 8765
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `UCX_MODEL` | `opus` | Model alias or LiteLLM format (see below) |
| `UCX_API_BASE` | - | Custom API base URL |
| `UCX_MAX_ITER` | `3` | Maximum review/fix cycles |
| `UCX_MIN_SCORE` | `90` | Minimum passing score |
| `UCX_SKIP_DRIFT` | `false` | Skip drift monitoring |
| `UCX_LOG_LEVEL` | `INFO` | Logging level |

### LLM Provider Configuration

UCX uses **LiteLLM** for multi-provider LLM support. Set provider-specific API keys:

```bash
# Anthropic (default)
export ANTHROPIC_API_KEY="sk-ant-..."

# OpenAI
export OPENAI_API_KEY="sk-..."

# Azure OpenAI
export AZURE_API_KEY="..."
export AZURE_API_BASE="https://your-resource.openai.azure.com"

# Google Gemini
export GEMINI_API_KEY="..."

# Ollama (local)
export UCX_API_BASE="http://localhost:11434"
```

### Model Selection

| Alias | Full Model ID |
|-------|---------------|
| `opus` | `anthropic/claude-opus-4-5-20251101` |
| `sonnet` | `anthropic/claude-sonnet-4-20250514` |
| `haiku` | `anthropic/claude-3-5-haiku-20241022` |

Or use LiteLLM format directly:
```bash
# OpenAI
UCX_MODEL="openai/gpt-4o" ucx review brd docs/01_BRD/BRD-01.md

# Azure
UCX_MODEL="azure/gpt-4" ucx review brd docs/01_BRD/BRD-01.md

# Ollama (local)
UCX_MODEL="ollama/llama3" UCX_API_BASE="http://localhost:11434" ucx review brd docs/01_BRD/BRD-01.md

# Gemini
UCX_MODEL="gemini/gemini-pro" ucx review brd docs/01_BRD/BRD-01.md
```

### Configuration File

Create `ucx.yaml` in your project root:

```yaml
model: opus
max_iterations: 3
min_score: 90
skip_drift: false
load_skills: true
log_level: INFO

retry:
  max_attempts: 3
  base_delay: 1.0

otel:
  enabled: true
  service_name: ucx
```

### Python Config

```python
from ucx import UCXConfig

config = UCXConfig(
    model="opus",
    max_iterations=5,
    min_score=85,
    skip_drift=False,
)

# Or load from file
config = UCXConfig.from_yaml("ucx.yaml")
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
│   │   ├── review.py           # UCRPhase
│   │   └── remediation.py      # UCRemPhase
│   │
│   ├── cli/                    # CLI commands
│   │   ├── main.py             # Click CLI
│   │   └── formatters.py       # Rich output
│   │
│   ├── mcp/                    # MCP Server
│   │   ├── server.py           # FastMCP server
│   │   ├── tools.py            # MCP tools
│   │   └── resources.py        # MCP resources
│   │
│   ├── core/                   # Core logic
│   │   ├── orchestrator.py     # Phase orchestration
│   │   ├── ucc.py              # UCC implementation
│   │   ├── ucr.py              # UCR implementation
│   │   ├── ucrem.py            # UCRem implementation
│   │   ├── drift.py            # Drift monitoring
│   │   ├── batch.py            # Batch processing
│   │   └── checkpoint.py       # Checkpointing
│   │
│   ├── config/                 # Configuration
│   │   ├── settings.py         # Pydantic settings
│   │   ├── defaults.py         # Default values
│   │   └── schema.py           # Config file schema
│   │
│   ├── models/                 # Data models
│   │   ├── enums.py            # DocType, Status enums
│   │   ├── document.py         # Document model
│   │   ├── review.py           # Review result
│   │   └── drift_cache.py      # Drift cache
│   │
│   ├── validators/             # Document validators
│   │   ├── brd.py, prd.py      # Layer validators
│   │   ├── ears.py, bdd.py     # (all 10 doc types)
│   │   └── registry.py         # Validator registry
│   │
│   ├── prompts/                # Prompt management
│   │   ├── loader.py           # Template loading
│   │   ├── renderer.py         # Jinja2 rendering
│   │   └── templates/          # Jinja2 templates
│   │       ├── ucc/            # Creation templates
│   │       ├── ucr/            # Review templates
│   │       └── ucrem/          # Remediation templates
│   │
│   ├── skills/                 # Skill/persona management
│   │   ├── loader.py           # Skill loading
│   │   ├── injector.py         # Prompt injection
│   │   └── personas/           # Persona definitions
│   │       ├── architect.md
│   │       ├── auditor.md
│   │       └── ... (12 personas)
│   │
│   ├── observability/          # Observability
│   │   ├── logging.py          # structlog
│   │   ├── tracing.py          # OpenTelemetry
│   │   ├── metrics.py          # OTEL metrics
│   │   └── llm_instrumentation.py  # gen_ai.* conventions
│   │
│   ├── plugins/                # Plugin system
│   │   ├── base.py             # Plugin base class
│   │   ├── registry.py         # Plugin registry
│   │   └── hooks.py            # Hook definitions
│   │
│   └── ai/                     # AI client
│       ├── litellm_client.py   # LiteLLM multi-provider client
│       ├── claude.py           # Claude-only client (legacy)
│       ├── retry.py            # Retry policies
│       └── tokens.py           # Token management
│
└── tests/                      # Test suite
    ├── unit/                   # Unit tests
    └── integration/            # Integration tests
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

UCX uses 12 expert personas for document review:

| Persona | Focus |
|---------|-------|
| Architect | System design, scalability |
| Auditor | Compliance, security |
| Tech Lead | Implementation feasibility |
| Strategist | Economics, trade-offs |
| Devil's Advocate | Edge cases, failure modes |
| Operator | Observability, deployment |
| Integration Expert | Dependencies, contracts |
| Product Owner | Business value, scope |
| Business Analyst | Requirements completeness |
| QA Lead | Testability, BDD syntax |
| Requirements Specialist | EARS/INCOSE syntax |
| UX Strategist | User journey, accessibility |

---

## API Reference

### UCXAutopilot

```python
from ucx import UCXAutopilot

pilot = UCXAutopilot(config)

# Single document
result = pilot.run(
    doc_type="brd",
    target=Path("docs/01_BRD/BRD-01"),
    from_ref=Path("docs/00_REF/"),
)

# Access results
print(result.score)          # 92
print(result.status)         # Status.PASS
print(result.iterations)     # 2
print(result.drift_detected) # False
```

### Phase APIs

```python
from ucx import UCCPhase, UCRPhase, UCRemPhase

# Creation
ucc = UCCPhase(config)
doc = ucc.create(doc_type="brd", output_path=path, from_ref=ref_dir)

# Review
ucr = UCRPhase(config)
result = ucr.review(doc_type="brd", doc_path=path)

# Remediation
ucrem = UCRemPhase(config)
fixes = ucrem.generate_fixes(review_report=report_path, doc_path=path)
```

---

## MCP Tools

When running as MCP server, UCX exposes:

| Tool | Description |
|------|-------------|
| `ucx_autopilot` | Full UCC→UCR→UCRem cycle |
| `ucx_create` | Create document (UCC) |
| `ucx_review` | Review document (UCR) |
| `ucx_remediate` | Generate fixes (UCRem) |
| `ucx_validate` | Validate document structure |
| `ucx_check_drift` | Check for upstream drift |
| `ucx_batch` | Batch processing |
| `ucx_status` | Document status |

---

## Testing

```bash
# Activate venv
source /opt/data/docs_flow_framework/.venv/bin/activate

# Run all tests
cd /opt/data/docs_flow_framework/UCX
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=ucx --cov-report=term-missing
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1.0 | 2026-03-09 | LiteLLM integration for multi-provider LLM support. |
| 1.0.0 | 2026-03-09 | Python migration complete. API, CLI, MCP server, full test suite. |

---

## Legacy Shell Scripts

The following shell scripts are deprecated but retained for reference:
- `run_ucx_autopilot.sh` - Use `ucx autopilot` CLI instead
- `init_ucx.sh` - Use `pip install -e .` instead

For legacy documentation, see `SKILL_INDEX.md`.
