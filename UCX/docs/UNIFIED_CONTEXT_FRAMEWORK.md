# Unified Context (UCX) Framework

## Overview

The Unified Context (UCX) Framework provides a multi-persona approach to document creation, review, and remediation in the SDD (Specification-Driven Development) workflow.

**Location**: `/opt/data/docs_flow_framework/UCX/`

---

## Three Phases

| Phase | Acronym | Purpose | CLI | Python API |
|-------|---------|---------|-----|------------|
| **Creation** | UCC | Multi-persona document authoring | `ucx create` | `UCCPhase.create()` |
| **Review** | UCR | Multi-persona validation | `ucx review` | `UCRPhase.review()` |
| **Remediation** | UCRem | Multi-persona fix generation | `ucx remediate` | `UCRemPhase.generate_fixes()` |
| **Autopilot** | - | Full UCC→UCR→UCRem cycle | `ucx autopilot` | `UCXAutopilot.run()` |

---

## Two Modes of AI Interaction

UCX supports two modes for executing AI workloads:

| Mode | Client | Description |
|------|--------|-------------|
| **CLI** (default) | `CLIClient` | Execute CLI agents via shell (Claude CLI, Gemini CLI, Ollama) |
| **API** | `LiteLLMClient` | Direct HTTP API calls via LiteLLM |

### CLI Mode

Executes AI CLI tools via subprocess. Uses existing CLI authentication.

```bash
# Default: uses Claude CLI
ucx review brd docs/01_BRD/BRD-01/

# Specify tool
ucx --mode cli --cli-tool gemini review brd docs/01_BRD/BRD-01/
```

Supported CLI tools:
- `claude` - Claude Code CLI (default)
- `gemini` - Google Gemini CLI
- `ollama` - Ollama local LLM
- `aider` - Aider AI coding assistant

### API Mode

Direct API calls via LiteLLM. Requires provider API keys.

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
ucx --mode api --model opus review brd docs/01_BRD/BRD-01/
```

Supported providers via LiteLLM:
- Anthropic (Claude)
- OpenAI
- Azure OpenAI
- Google Gemini
- Ollama (local)
- OpenRouter

---

## Philosophy

### Why Multi-Persona?

Different stakeholders have different concerns:

| Stakeholder | Focus | Catches |
|-------------|-------|---------|
| Architect | Structure, patterns | Design flaws |
| Auditor | Compliance, security | Regulatory gaps |
| Tech Lead | Implementation | Technical issues |
| QA Lead | Testability | Verification gaps |
| Devil's Advocate | Edge cases | Hidden assumptions |

**A single reviewer misses what another catches.** UCX applies all relevant personas to every document.

### Error Philosophy

| Phase | Worse Error | Strategy |
|-------|-------------|----------|
| **UCC** | Missing content | Over-specify, let review trim |
| **UCR** | Missing finding (False Negative) | Flag when in doubt |
| **UCRem** | Incomplete fix (Under-fix) | Manual-required when uncertain |

---

## Package Structure

```
UCX/
├── pyproject.toml              # Package configuration
├── README.md                   # Package overview
│
├── ucx/                        # Python package
│   ├── __init__.py             # Public API exports
│   ├── api/                    # Public API classes
│   │   ├── autopilot.py        # UCXAutopilot
│   │   ├── creation.py         # UCCPhase
│   │   ├── review.py           # UCRPhase
│   │   └── remediation.py      # UCRemPhase
│   │
│   ├── ai/                     # AI clients (dual-mode)
│   │   ├── __init__.py         # get_client() factory
│   │   ├── base.py             # BaseAIClient ABC
│   │   ├── cli_client.py       # CLIClient (shell subprocess)
│   │   ├── litellm_client.py   # LiteLLMClient (HTTP API)
│   │   └── claude.py           # ClaudeClient (legacy)
│   │
│   ├── cli/                    # CLI commands
│   │   └── main.py             # Click CLI
│   │
│   ├── config/                 # Configuration
│   │   └── settings.py         # UCXConfig (Pydantic)
│   │
│   ├── validators/             # Document validators
│   │   └── *.py                # Per-layer validators
│   │
│   ├── prompts/                # Prompt management
│   │   └── templates/          # UCR_PROMPT_*.md files
│   │
│   └── skills/                 # Persona definitions
│       └── personas/           # 12 expert personas
│
├── docs/                       # Documentation
└── tests/                      # Test suite
```

---

## Layer Coverage

UCX supports all SDD layers:

| Layer | Type | Creation | Review | Remediation |
|-------|------|----------|--------|-------------|
| 1 | BRD | ✓ | ✓ | ✓ |
| 2 | PRD | ✓ | ✓ | ✓ |
| 3 | EARS | ✓ | ✓ | ✓ |
| 4 | BDD | ✓ | ✓ | ✓ |
| 5 | ADR | ✓ | ✓ | ✓ |
| 6 | SYS | ✓ | ✓ | ✓ |
| 7 | REQ | ✓ | ✓ | ✓ |
| 8 | CTR | ✓ | ✓ | ✓ |
| 9 | SPEC | ✓ | ✓ | ✓ |
| 10 | TSPEC | ✓ | ✓ | ✓ |

---

## Cross-Layer Dependencies

```
L1 BRD ──┬──▶ L2 PRD ──▶ L3 EARS ──▶ L4 BDD
         │
         └──▶ L5 ADR ──▶ L6 SYS ──▶ L7 REQ ──┬──▶ L8 CTR
                                              │
                                              └──▶ L9 SPEC ──▶ L10 TSPEC
```

UCX handles dependencies with:
- `--from-ref`: Load reference documents
- `--from-upstream`: Load upstream artifacts

---

## Quick Start

### 1. Activate Environment

```bash
source /opt/data/docs_flow_framework/.venv/bin/activate
```

### 2. Review Document (CLI Mode - Default)

```bash
# Uses Claude CLI
ucx review brd docs/01_BRD/BRD-01/
```

### 3. Review Document (API Mode)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
ucx --mode api review brd docs/01_BRD/BRD-01/
```

### 4. Create Document

```bash
ucx create brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/
```

### 5. Generate Fixes (if needed)

```bash
ucx remediate brd docs/01_BRD/BRD-01.md --review-report docs/01_BRD/BRD_UCR_REVIEW.md
```

### 6. Or Run Autopilot

```bash
ucx autopilot brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/ --max-iterations 3
```

---

## Python API

```python
from ucx import UCXAutopilot, UCXConfig, UCCPhase, UCRPhase, UCRemPhase
from ucx.ai import get_client
from pathlib import Path

# Configuration
config = UCXConfig(
    ai_mode="cli",           # or "api"
    cli_tool="claude",       # for cli mode
    cli_timeout=600,         # for cli mode
    model="opus",            # for api mode
    max_iterations=3,
    min_score=90,
)

# Autopilot (full cycle)
pilot = UCXAutopilot(config)
result = pilot.run(
    doc_type="brd",
    target=Path("docs/01_BRD/BRD-01"),
    from_ref=Path("docs/00_REF/"),
)

# Or individual phases
ucc = UCCPhase(config)
ucr = UCRPhase(config)
ucrem = UCRemPhase(config)

# Direct AI client usage
client = get_client(mode="cli", cli_tool="claude")
response = client.generate("Analyze this requirement...")
```

---

## Integration with Claude Skills

UCX integrates with Claude skills via thin wrappers:

| Skill | UCX Phase | CLI Equivalent |
|-------|-----------|----------------|
| `/doc-{type}` | UCC | `ucx create {type}` |
| `/doc-{type}-audit` | UCR | `ucx review {type}` |
| `/doc-{type}-fixer` | UCRem | `ucx remediate {type}` |
| `/doc-{type}-autopilot` | All | `ucx autopilot {type}` |

See `SKILL_INDEX.md` for complete mapping.

---

## Tradegent Integration

UCX shares patterns with [TradegentSwarm](/opt/data/tradegent_swarm/):

- Both support CLI mode (agent CLIs) and API mode (LiteLLM)
- Shared provider credentials work for both systems

```bash
# Shared provider keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# UCX: dual mode
ucx --mode cli review brd docs/01_BRD/BRD-01/
ucx --mode api review brd docs/01_BRD/BRD-01/
```

---

## See Also

- [HOW_TO_USE.md](HOW_TO_USE.md) - Detailed usage guide
- [HOW_TO_AUDIT.md](HOW_TO_AUDIT.md) - Audit workflow guide
- [UNIFIED_CONTEXT_REVIEW.md](UNIFIED_CONTEXT_REVIEW.md) - UCR method details
- [SKILL_INDEX.md](../SKILL_INDEX.md) - Claude skill integration
- [README.md](../README.md) - Package overview
