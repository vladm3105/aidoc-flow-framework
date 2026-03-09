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
├── SKILL_INDEX.md              # Claude skill mapping
│
├── ucx/                        # Python package
│   ├── __init__.py             # Public API exports
│   ├── api/                    # Public API classes
│   │   ├── autopilot.py        # UCXAutopilot
│   │   ├── creation.py         # UCCPhase
│   │   ├── review.py           # UCRPhase
│   │   └── remediation.py      # UCRemPhase
│   │
│   ├── ai/                     # AI clients
│   │   ├── litellm_client.py   # LiteLLM multi-provider client
│   │   └── claude.py           # Claude-only client (legacy)
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
│   │   └── templates/          # Jinja2 templates
│   │
│   └── skills/                 # Persona definitions
│       └── personas/           # 12 expert personas
│
├── docs/                       # Documentation
│   ├── UNIFIED_CONTEXT_FRAMEWORK.md
│   ├── HOW_TO_USE.md
│   └── PERSONA_DESIGN_GUIDE.md
│
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

## LiteLLM Multi-Provider Support

UCX uses **LiteLLM** for unified access to multiple LLM providers:

### Supported Providers

| Provider | Model Format | API Key Env |
|----------|-------------|-------------|
| Anthropic | `opus`, `sonnet`, `haiku` | `ANTHROPIC_API_KEY` |
| OpenAI | `openai/gpt-4o` | `OPENAI_API_KEY` |
| Azure | `azure/gpt-4` | `AZURE_API_KEY` |
| Gemini | `gemini/gemini-pro` | `GEMINI_API_KEY` |
| OpenRouter | `openrouter/openai/gpt-4o` | `OPENROUTER_API_KEY` |
| Ollama | `ollama/llama3` | - (local) |

### Configuration

```bash
# Environment variables
export UCX_MODEL=opus
export UCX_API_BASE=           # Optional: custom endpoint
export ANTHROPIC_API_KEY=sk-ant-...

# Or in ucx.yaml
model: opus
api_base: null
```

### Usage Examples

```bash
# Default (Anthropic Claude)
ucx review brd docs/01_BRD/BRD-01.md

# OpenAI
UCX_MODEL="openai/gpt-4o" ucx review brd docs/01_BRD/BRD-01.md

# Local Ollama
UCX_MODEL="ollama/llama3" UCX_API_BASE="http://localhost:11434" ucx review brd docs/01_BRD/BRD-01.md
```

---

## Quick Start

### 1. Activate Environment

```bash
source /opt/data/docs_flow_framework/.venv/bin/activate
```

### 2. Set API Key

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 3. Create Document

```bash
ucx create brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/
```

### 4. Review Document

```bash
ucx review brd docs/01_BRD/BRD-01.md
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
from pathlib import Path

# Configuration
config = UCXConfig(
    model="opus",           # or "openai/gpt-4o", "ollama/llama3"
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

UCX shares the LiteLLM gateway pattern with [TradegentSwarm](/opt/data/tradegent_swarm/). Both systems can use the same provider credentials:

```bash
# Shared provider keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Tradegent: role-based routing
export LITELLM_ROUTE_REASONING_STANDARD=openrouter/openai/gpt-4o-mini

# UCX: model aliases
export UCX_MODEL=opus
```

See [Tradegent LiteLLM Integration](/opt/data/tradegent_swarm/docs/architecture/litellm-integration.md) for details.

---

## See Also

- [HOW_TO_USE.md](HOW_TO_USE.md) - Detailed usage guide
- [PERSONA_DESIGN_GUIDE.md](PERSONA_DESIGN_GUIDE.md) - Creating custom personas
- [SKILL_INDEX.md](../SKILL_INDEX.md) - Claude skill integration
- [README.md](../README.md) - Package overview
