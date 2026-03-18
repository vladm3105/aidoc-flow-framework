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
- `claude` - Claude Code CLI (default) - supports `--model opus/sonnet/haiku` and `--enable-web-search`
- `gemini` - Google Gemini CLI
- `ollama` - Ollama local LLM CLI
- `aider` - Aider AI coding assistant

**Note**: For Claude CLI, UCX automatically adds `--dangerously-skip-permissions` to prevent interactive permission prompts that would truncate output in subprocess mode.

### Web Search Mode

Enable internet search for deeper analysis with `--enable-web-search` (`-W`):

```bash
# Enable web search for fact-checking, best practices, solutions
ucx -W review brd docs/01_BRD/BRD-01/
ucx --enable-web-search review brd docs/01_BRD/BRD-01/

# Via environment variable
UCX_ENABLE_WEB_SEARCH=true ucx review brd docs/01_BRD/BRD-01/

# Full autopilot with web search
ucx -W autopilot brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/
```

Web search is useful for:
- **Fact-checking**: Regulatory references (FinCEN, OFAC, PCI-DSS)
- **Best practices**: Technology patterns, security recommendations
- **Solutions**: Finding fixes for identified issues
- **Documentation**: Verifying partner API specifications

**Note**: Web search is only supported in CLI mode with Claude CLI (uses `--allowedTools WebSearch`).

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

## AI Backends & Providers Reference

UCX supports multiple AI backends through a provider-agnostic architecture.

### CLI Mode Agents

| CLI Tool | Provider | Command | Features | Status |
|----------|----------|---------|----------|--------|
| **claude** | Anthropic | `--cli-tool claude` | Web search, opus/sonnet/haiku models | Default |
| **gemini** | Google | `--cli-tool gemini` | stdin input | Supported |
| **ollama** | Local | `--cli-tool ollama` | Any ollama model | Supported |
| **aider** | Aider AI | `--cli-tool aider` | Code-focused analysis | Supported |

### API Mode Providers (via LiteLLM)

| Provider | Model Format | Auth Variable | Features |
|----------|--------------|---------------|----------|
| **Anthropic** | `anthropic/claude-opus-4-5-20251101` | `ANTHROPIC_API_KEY` | 200K context |
| **OpenAI** | `openai/gpt-4o` | `OPENAI_API_KEY` | Full model family |
| **Azure OpenAI** | `azure/gpt-4` | `AZURE_*` env vars | Azure endpoints |
| **Google Gemini** | `gemini/gemini-pro` | `GEMINI_API_KEY` | Native API |
| **Mistral** | `mistral/mistral-large` | `MISTRAL_API_KEY` | Mistral family |
| **Ollama** | `ollama/llama3` | localhost:11434 | Local inference |
| **Custom APIs** | `provider/model` | Custom `--api-base` | Proxy support |

### Architecture

UCX uses a factory pattern with clean abstraction:

```
┌─────────────────────────────────────────┐
│     UCX Core (review, remediate, etc)   │
└──────────────┬──────────────────────────┘
               │ uses
        ┌──────▼───────┐
        │ get_client() │  Factory
        └──────┬───────┘
        ┌──────┴────────────────┐
        │                       │
    ┌───▼────┐            ┌────▼──────┐
    │ CLI    │            │ API       │
    │ Mode   │            │ Mode      │
    └───┬────┘            └────┬──────┘
        │                      │
  ┌─────▼──────┐         ┌────▼────────┐
  │ CLIClient  │         │LiteLLMClient│
  │            │         │             │
  │ • claude   │         │ • Anthropic │
  │ • gemini   │         │ • OpenAI    │
  │ • ollama   │         │ • Azure     │
  │ • aider    │         │ • Gemini    │
  └────────────┘         │ • 20+ more  │
                         └─────────────┘
```

**Key Files:**
- `ucx/ai/__init__.py` - `get_client()` factory function
- `ucx/ai/base.py` - `BaseAIClient` abstract class
- `ucx/ai/cli_client.py` - `CLIClient` for shell-based agents
- `ucx/ai/litellm_client.py` - `LiteLLMClient` for HTTP APIs

### Quick Examples

```bash
# CLI Mode - Claude (default)
ucx review brd docs/01_BRD/BRD-01/

# CLI Mode - Gemini
ucx --cli-tool gemini review brd docs/01_BRD/BRD-01/

# CLI Mode - Local Ollama
ucx --cli-tool ollama review brd docs/01_BRD/BRD-01/

# API Mode - OpenAI
export OPENAI_API_KEY="sk-..."
ucx --mode api --model openai/gpt-4o review brd docs/01_BRD/BRD-01/

# API Mode - Azure
export AZURE_API_KEY="..."
export AZURE_API_BASE="https://your-resource.openai.azure.com"
ucx --mode api --model azure/gpt-4 review brd docs/01_BRD/BRD-01/

# API Mode - Custom endpoint
ucx --mode api --model provider/model --api-base https://proxy.example.com review brd ...
```

### Configuration Priority

1. **CLI arguments** (highest)
2. **Environment variables** (`UCX_*` prefix)
3. **Configuration file** (YAML)
4. **Hardcoded defaults** (lowest)

### Model Aliases

| Alias | CLI Mode | API Mode (LiteLLM) |
|-------|----------|-------------------|
| `opus` | `opus` | `anthropic/claude-opus-4-5-20251101` |
| `sonnet` | `sonnet` | `anthropic/claude-sonnet-4-20250514` |
| `haiku` | `haiku` | `anthropic/claude-3-5-haiku-20241022` |

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

# Persona prompts mode (recommended for large documents)
ucx review brd docs/01_BRD/BRD-01/ --persona

# Review with API mode (requires API key)
ucx --mode api --model opus review brd docs/01_BRD/BRD-01/

# Run autopilot
ucx autopilot brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/

# Create new document
ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01

# Validate document structure (always fixes by default v1.17.0+)
ucx validate brd docs/01_BRD/BRD-01.md

# Skip fixing (validation only)
ucx validate brd docs/01_BRD/BRD-01.md --no-fix

# Remove LLM_COMPLETION markers after remediation
ucx clean-markers docs/01_BRD/BRD-01.md

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
├── skills/                         # Project-specific persona skills (v1.8.0+)
│   ├── architect.md                # Domain-tuned architect knowledge
│   ├── auditor.md                  # Domain-tuned compliance focus
│   └── ...
├── review/
│   ├── UCR_PROMPT_BRD_PROJECT.md   # Project-specific BRD review prompt
│   ├── UCR_PROMPT_PRD_PROJECT.md   # Project-specific PRD review prompt
│   └── ...
├── creation/
│   └── UCC_PROMPT_BRD_PROJECT.md   # Project-specific creation prompts
└── remediation/
    └── UCRem_PROMPT_BRD_PROJECT.md
```

**Prompt search order** (project-specific ONLY - no fallback):
1. Project prompt dir: `{project}/docs/UCX/review/UCR_PROMPT_BRD_PROJECT.md`
2. Project prompt dir: `{project}/docs/UCX/review/UCR_PROMPT_BRD.md`

**Skill search order** (project first, framework fallback):
1. Project skills: `{project}/docs/UCX/skills/{persona}.md`
2. Framework skills: `/UCX/skills/{persona}.md`

**Benefits of project-specific prompts**:
- Domain-specific personas (e.g., compliance focus for fintech)
- Custom finding priorities (P0/P1/P2 thresholds)
- Project-specific sections to cross-reference
- Additional personas (Fact Checker, Chairperson)

See `docs/UCX/review/` for example project-specific prompts.

### Project-Specific Skills (v1.8.0+)

Skills provide domain knowledge that gets injected into persona prompts. Create project-tuned skills for better reviews:

```bash
# Project skills directory
mkdir -p docs/UCX/skills/

# Create domain-tuned skill (example: fintech compliance)
cat > docs/UCX/skills/auditor.md << 'EOF'
# Project Auditor Domain Knowledge

## Role
Compliance Auditor for [your domain - e.g., payments, healthcare, e-commerce].

## Regulatory Focus
- **Primary Regulations**: [e.g., PCI-DSS, HIPAA, GDPR, SOC2]
- **Industry Standards**: [e.g., ISO 27001, NIST]
- **Compliance Tiers**: [e.g., transaction limits, data classification]

## Review Questions
1. Are compliance requirements explicitly documented?
2. Are audit trail requirements specified?
3. Are data retention policies defined?
EOF
```

**Skill Loading Priority:**

| Priority | Location | Behavior |
|----------|----------|----------|
| 1 | `{project}/docs/UCX/skills/` | Project-tuned skills (preferred) |
| 2 | `/UCX/skills/` | Framework defaults (fallback) |

**Verify skills are loaded:**
```bash
UCX_LOG_LEVEL=DEBUG ucx review brd docs/01_BRD/BRD-01/
# Look for: "Loaded project-specific skill: auditor from .../docs/UCX/skills"
```

**Key difference from prompts:**
- **Prompts**: Project-specific ONLY (no fallback)
- **Skills**: Project first, framework fallback if not found

---

## Skills System Architecture

Skills are domain knowledge files that provide expertise to UCX personas during document review, creation, and remediation.

### Framework Personas (13 Built-in)

| Persona | Focus Area | Used In |
|---------|------------|---------|
| `architect` | System design, scalability, integration patterns | All phases |
| `auditor` | Compliance, security, standards | All phases |
| `tech_lead` | Implementation feasibility, technical debt | All phases |
| `strategist` | Economics, trade-offs, long-term vision | UCC, UCR |
| `chaos_engineer` | Edge cases, failure modes, safety | All phases |
| `operator` | Observability, deployment, runbooks | All phases |
| `integration_lead` | Dependencies, contracts, boundaries | All phases |
| `product_owner` | Business value, scope, prioritization | UCC, UCR |
| `business_analyst` | Requirements clarity, business logic | UCC, UCR |
| `qa_lead` | Testing strategy, BDD syntax, quality metrics | UCR, UCRem |
| `requirements_specialist` | EARS/INCOSE syntax, traceability | EARS, REQ |
| `fact_checker` | Verification, accuracy, cross-validation | UCR |
| `chairperson` | Synthesis, de-duplication, scoring | UCR, UCRem |

### Skill File Format

Skills are markdown files with domain knowledge and metadata:

```markdown
# Platform Architect Domain Knowledge

## Role
Software/System Architect responsible for technical decisions and system design.

## Core Principles
1. Separation of Concerns (SoC)
2. Single Point of Failure (SPOF) elimination
3. Statelessness where possible
4. Asynchronous Decoupling

## Review Focus
- System structure and modularity
- Integration patterns and boundaries
- Scalability and performance implications
- Technical debt and maintainability

## Common Anti-Patterns to Flag
- Distributed Monolith
- Premature Optimization
- Tight Coupling
- Ignoring Data Gravity

## Review Questions
1. Does the architecture support stated requirements?
2. Are component boundaries well-defined?
3. Are failure modes documented?

## Category Tagging (v1.12.0)
**Primary Categories**: architecture, quality, integration

**Finding Output Format**:
[CAT:architecture] Finding description here

## Scoring Weight
- BRD: 15%
- ADR: 40%
- SPEC: 35%

## Tags
- phase: ucr
- doc_types: [brd, prd, adr, sys, spec]
```

### Phase-Specific Skill Selection

UCX loads different personas based on the operation phase:

| Phase | Purpose | Personas Loaded |
|-------|---------|-----------------|
| **UCC** (Create) | Document authoring | 5 focused personas |
| **UCR** (Review) | Comprehensive review | 8-9 reviewer personas |
| **UCRem** (Fix) | Targeted remediation | Domain fixers + mandatory |

**Remediation Fixer Categories:**

| Category | Personas | Loading Rule |
|----------|----------|--------------|
| **Domain Fixers** | architect, auditor, qa_lead, integration_lead | Adaptive (only if findings exist) |
| **Mandatory** | chaos_engineer, chairperson | Always loaded |

### Project Customization Examples

Override framework skills with domain-specific knowledge:

**E-Commerce Project** (`docs/UCX/skills/architect.md`):
```markdown
# E-Commerce Platform Architect

## Domain-Specific Architecture
- **Cart Service**: Stateless with Redis session store
- **Inventory**: Event-sourced with CQRS pattern
- **Payments**: PCI-DSS compliant isolated subnet
- **Search**: Elasticsearch with async indexing

## Scalability Targets
- MVP: 10K daily orders
- Scale: 100K daily orders
- Peak: 5x during sales events

## Anti-Patterns to Flag
- Cart state in application memory
- Synchronous inventory checks at checkout
- Payment credentials in application logs
```

**Healthcare Project** (`docs/UCX/skills/auditor.md`):
```markdown
# Healthcare Compliance Auditor

## Regulatory Focus
- **HIPAA**: PHI handling, BAA requirements, breach notification
- **HITECH**: EHR incentives, meaningful use
- **FDA 21 CFR Part 11**: Electronic signatures, audit trails

## Data Classification
- PHI: Protected Health Information (highest protection)
- PII: Personally Identifiable Information
- De-identified: Safe for analytics

## Review Questions
1. Is PHI encrypted at rest and in transit?
2. Are access controls role-based with audit logging?
3. Is data retention policy HIPAA-compliant (6 years)?
```

**IoT/Embedded Project** (`docs/UCX/skills/operator.md`):
```markdown
# IoT Operations Specialist

## Operational Focus
- **Fleet Management**: OTA updates, device provisioning
- **Connectivity**: Offline-first, intermittent network handling
- **Monitoring**: Edge telemetry aggregation, anomaly detection

## Failure Modes
- Network partition between edge and cloud
- Firmware rollback scenarios
- Battery/power failure recovery

## SLA Targets
- Device heartbeat: 5-minute intervals
- OTA deployment: 24-hour fleet rollout
- Incident response: 15-minute acknowledgment
```

### Skill Injection Strategies

Skills are injected into prompts using configurable strategies:

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `prepend` | Add skills before main prompt | Default, most common |
| `append` | Add skills after main prompt | When context comes first |
| `section` | Insert at `<!-- SKILLS_START -->` marker | Precise placement |
| `replace` | Replace `{{ skills }}` placeholder | Template-based |

### Key Implementation Files

| File | Purpose |
|------|---------|
| `ucx/skills/loader.py` | `SkillLoader` - two-tier priority loading with caching |
| `ucx/skills/injector.py` | `SkillInjector` - prompt injection strategies |
| `ucx/config/layer_skills.py` | Phase-to-skill mapping configuration |
| `/UCX/skills/*.md` | 13 framework persona definitions |

### Python API Usage

```python
from ucx.skills.loader import SkillLoader
from ucx.skills.injector import SkillInjector
from pathlib import Path

# Initialize with project directory for customization
loader = SkillLoader(
    project_dir=Path("/path/to/your/project")
)

# Load skills for review phase
skills = loader.load_for_phase("ucr", "brd")
# Returns: {"architect": "...", "auditor": "...", ...}

# Load single skill
architect_skill = loader.load("architect")

# List available skills
available = loader.list_skills()
# Returns: ["architect", "auditor", "business_analyst", ...]

# Inject into prompt
injector = SkillInjector(strategy="prepend")
final_prompt = injector.inject(base_prompt, skills)
```

### Review Modes: Unified vs Persona

UCX supports two review modes with different trade-offs:

| Aspect | Unified Prompt (Default) | Persona Prompts (`--persona`) |
|--------|--------------------------|-------------------------------|
| **API Calls** | 1 | 12 (one per persona) |
| **Document Context** | Full document to all personas | Filtered per persona |
| **Prior Findings** | N/A | Summarized (anti-repetition) |
| **Context Engineering** | None | Hierarchical 4-level |
| **Resume Support** | No | Yes |
| **Cost** | Lower | Higher |
| **Best For** | Small/medium docs (<50K tokens) | Large docs (>50K tokens) |

**When to Use Each:**

| Document Size | Recommendation |
|---------------|----------------|
| < 30K tokens | Unified prompt |
| 30K - 80K tokens | Either (preference) |
| > 80K tokens | Persona prompts |

**Trade-offs:**
- **Unified prompt advantages**: All personas see full document (cross-domain detection), no filtering risk, faster/cheaper
- **Persona prompts advantages**: Full attention per persona, no truncation risk, finding deduplication, resume capability

**For critical reviews**: Run both and compare. Persona prompts catch depth, unified prompt catches breadth.

See [UNIFIED_CONTEXT_REVIEW.md](docs/UNIFIED_CONTEXT_REVIEW.md) for detailed comparison.

### Persona Prompts Mode

For large documents, use `--persona` to break the review into per-persona calls:

```bash
# Persona prompts with memory (auto-resumes if interrupted)
ucx review brd docs/01_BRD/BRD-01/ --persona

# Fresh start (clear previous memory)
ucx review brd docs/01_BRD/BRD-01/ --persona --no-resume

# Custom session TTL (default: 24 hours)
ucx review brd docs/01_BRD/BRD-01/ -p --session-ttl 48
```

**Benefits:**
- **No timeouts** - Each persona call is smaller (~45K tokens vs 200K+)
- **Resume capability** - Skip completed personas if interrupted
- **Debug/audit** - Inspect prompts and responses in `.ucx_review_session/`
- **Better quality** - Each persona generates detailed output (8-10K chars)
- **Anti-repetition** - Later personas see prior findings summary, preventing redundant analysis
- **Deduplication** - Report assembly consolidates duplicate findings across personas

**Session Management:**

| Option | Behavior |
|--------|----------|
| `--persona` / `-p` | Resume from last session (if valid) |
| `--no-resume` | Clear memory and start fresh |
| `--session-ttl N` | Expire sessions older than N hours (default: 24) |

Sessions auto-invalidate when:
- Document content changes (hash mismatch)
- Session TTL expires
- `--no-resume` flag is used

**Memory Directory Structure:**
```
docs/01_BRD/BRD-01/.ucx_review_session/
├── session.json           # Session state with TTL tracking
├── shared_context.txt     # Document content
├── prompt_architect.txt   # Prompt sent to architect persona
├── response_architect.txt # Response from architect
├── prompt_auditor.txt     # ...
├── response_auditor.txt   # ...
└── assembled_report.md          # Assembled report
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
# Remove stale session memory (.ucx_review_session/)
ucx review brd docs/01_BRD/BRD-01/ --clean-memory

# Remove old review reports, keep only latest version
ucx review brd docs/01_BRD/BRD-01/ --clean-reports

# Keep N most recent report versions (default: 1)
ucx review brd docs/01_BRD/BRD-01/ --clean-reports --keep-versions 3

# Clean both memory and old reports
ucx review brd docs/01_BRD/BRD-01/ --clean-all
```

### Anti-Repetition & Deduplication (v1.7.0)

Multi-turn reviews now prevent redundant findings across personas:

**Anti-Repetition Rules:**
- Each persona receives a summary of prior findings (P0/P1 only)
- Prompts include explicit rules: "DO NOT REPEAT findings already identified"
- Personas focus ONLY on their specialty domain
- Cross-persona confirmations noted as "Confirmed: [P0-X from Architect]"

**Report Deduplication:**
- Report assembly extracts findings using P0/P1 patterns
- Jaccard similarity (60% threshold) identifies duplicates
- Consolidated findings section shows:
  - Unique findings (from single persona)
  - Confirmed findings (same issue from multiple personas)
  - Deduplication stats (e.g., "45 total → 22 unique, 51% duplicates removed")

**Report Structure:**
```markdown
## Consolidated Findings Summary

**Deduplication Stats**: 45 total findings → 22 unique (51% duplicates removed)

### P0 Critical Findings
- **[P0-1]** Missing state machine *(confirmed by 3 personas: architect, tech_lead, operator)*
- **[P0-2]** No API version pinning *(from integration_lead)*

### P1 High Priority Findings
...

---

## 1. Architect Review
[Full persona response]

## 2. Auditor Review
...
```

### Document Validation (v1.9.0+, report-by-default v1.11.1+)

Fast, non-AI validation for pre-commit hooks and CI/CD pipelines.
**v1.11.1+**: Generates validation report to document directory by default (like review).

```bash
# Basic validation (generates report by default)
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/
# → Creates: docs/01_BRD/BRD-01_platform_architecture/BRD-01.V_validation_report_v001.md

# Console-only output (no report)
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/ --no-report

# Tier 1 only (fast, blocking checks for pre-commit)
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/ --tier1-only

# Strict mode (warnings as errors)
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/ --strict

# JSON output for CI/CD (console only)
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/ --format json --no-report

# Write validation report to specific file
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/ -o tmp/BRD-01_validation.md

# Validation ALWAYS fixes by default (v1.17.0+)
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/

# Skip fixing (validation only) - add --no-fix
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/ --no-fix

# Clean up old reports (keep only latest)
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/ --clean-reports

# Tier 1 only (fast) - still fixes by default
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/ --tier1-only

# Clean up old validation reports, keep only latest (v1.9.5+)
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/ --clean-reports

# Keep N most recent validation report versions (default: 1)
ucx validate brd docs/01_BRD/BRD-01_platform_architecture/ --clean-reports --keep-versions 3
```

**Auto-Fix (v1.15.2 - 21 codes):**

The `--fix` flag automatically fixes structural issues without AI:

| Error Code | Tier | Issue | Auto-Fix |
|------------|------|-------|----------|
| `BRD-E002` | 1 | Missing custom_fields / Section 0 | Adds custom_fields OR Section 0 (context-aware) |
| `BRD-E003` | 1 | Missing 'brd' tag | Adds to tags array |
| `BRD-E004` | 1 | Missing 'layer-1-artifact' tag | Adds to tags array |
| `BRD-E009` | 1 | Missing Document Control | Adds Section 0 template |
| `BRD-E020` | 1 | Invalid element type code | Remaps to valid code (01-32, 91-99) |
| `GATE-E001` | 1 | **Placeholder text [TBD]** | **Converts to `<!-- DEFERRED: ... -->` comments** |
| `GATE-E008` | 1 | Duplicate element ID | Renumbers duplicates with next available sequence |
| `GATE-E010` | 1 | File exceeds 20K tokens | Auto-splits at section boundaries |
| `DIAG-E001` | 1 | **Missing architecture diagram** | **Adds `<!-- DIAGRAM-REQUIRED: ... -->` placeholder** |
| `FWDREF-E001` | 1 | **Forward reference to non-existent doc** | **Converts to `<!-- FWDREF-DEFERRED: ... -->` comment** |
| `VAL-E002` | 1 | Missing/invalid frontmatter | Creates YAML frontmatter from scratch |
| `BRD-W005` | 1 | Legacy development_status | Renames to status |
| `VAL-W002` | 1 | Legacy status value | Updates (active→production, draft→development) |
| `GATE-W003` | 2 | Count mismatch | Updates prose count to match actual |
| `GATE-W008` | 2 | Element in wrong section | Moves element to correct section file |
| `DIAG-W001` | 2 | Diagram node count | Updates prose to match diagram |
| `BRD-W010` | 2 | Missing @depends tags | Auto-detects BRD references and adds tags |
| `BRD-W011` | 2 | Missing C4-L1 diagram | Adds @diagram-request for ADR layer |
| `BRD-W012` | 2 | Missing DFD-L0 diagram | Adds @diagram-request for ADR layer |
| `BRD-W013` | 2 | Sequence diagram unclassified | Auto-detects sync/async/error type |
| `BRD-W014` | 2 | Missing diagram intent | Adds diagram metadata fields |

**Validation Report Format (v1.9.3+):**

When writing to a file (`-o`), validation reports follow SDD framework standards:

```yaml
---
doc_id: BRD-01.V
title: "BRD-01 Validation Report - Structural Quality Check"
report_version: v001
validation_date: 2026-03-11T16:21:51
validator: UCX Framework v1.9.3
tags:
  - validation-report
  - brd-quality
  - structural-validation
custom_fields:
  artifact_type: VALIDATION
  validated_document: BRD-01
  validation_score: 85.5
  status: PASS
  tier1_errors: 0
  tier2_warnings: 5
---

# BRD-01 Validation Report v001

## 0. Document Control
| Item | Details |
|------|---------|
| **Source Document** | BRD-01 |
| **Report ID** | VAL-BRD-01-v001 |
| **Status** | PASS ✅ |

## 1. Executive Summary
## 2. Validation Score Breakdown
## 3. Tier 1 Findings (Core Checks)
## 4. Tier 2 Findings (Advisory Checks)
## 5. Checks Performed
## 6. Recommended Next Steps
```

**Report Naming Convention:**

| Output Type | Filename Pattern | Example |
|-------------|------------------|---------|
| Validation | `.precommit_validation_report.md` | `.precommit_validation_report.md` |
| Review | `{DOC-ID}.UCR_review_report_v{NNN}.md` | `BRD-01.UCR_review_report_v001.md` |
| Remediation | `{DOC-ID}.UCRem_remediation_report.md` | `BRD-01.UCRem_remediation_report.md` |

> **Note (v1.16.1)**: Validation reports now use a single file that overwrites on each run. Review reports retain versioning for history tracking.

**Tiered Validation:**

| Tier | Type | Blocking | Checks |
|------|------|----------|--------|
| **Tier 1** | Core | Yes | Element codes, structure, metadata, quality gates (errors) |
| **Tier 2** | Advisory | No | Links, references, diagrams, glossary |

**Tier 1: Core Checks (Blocking)**

These are critical checks that **must pass** before proceeding. If any Tier 1 errors exist, the document is considered invalid and blocks pre-commit/CI.

| Check | Description | Error Codes |
|-------|-------------|-------------|
| **Element Codes** | Validates `BRD.NN.TT.SS` format, uniqueness, section mapping | `GATE-E008` (duplicates), `BRD-E001` (invalid format) |
| **Structure** | Required sections present, H1 headings, file naming conventions | `BRD-E006` (missing sections), `BRD-E002` (missing Document Control) |
| **Metadata** | YAML frontmatter validity, `custom_fields.document_type`, required tags | `BRD-E002`, `BRD-E003` (missing tags) |
| **Quality Gates** | Placeholder detection (TODO/TBD), downstream refs, file size limits | `GATE-E001`, `GATE-E002`, `GATE-E010` |

**Valid Element Type Codes (TT):**
- Core: `01-10` (FR, QA, Constraint, Assumption, Dependency, AC, Risk, Metric, User Story, Decision)
- Extended: `22-24, 32` (Feature Item, Business Objective, Stakeholder Need, Architecture Topic)
- **QA Subcategories (91-99)**: Performance (91), Reliability (92), Scalability (94), Security (96), Observability (98), Maintainability (99)

> See `ai_dev_ssd_flow/ID_NAMING_STANDARDS.md` for complete element type code reference.

**Tier 2: Advisory Checks (Non-Blocking)**

These are recommendations for quality improvement. Tier 2 warnings don't block commits but should be addressed.

| Check | Description | Warning Codes |
|-------|-------------|---------------|
| **Links** | Markdown link validation, broken internal references | `LINK-W*` |
| **Forward References** | SDD layer compliance (no refs to unwritten downstream artifacts) | `FWDREF-W*` |
| **Diagrams** | Mermaid/SVG consistency with prose, node count mismatches | `DIAG-W001` |
| **Quality Gates** | Glossary consistency, stated vs actual counts, cost format | `GATE-W003`, `GATE-W007`, `GATE-W009` |
| **Advisory Tags** | Missing diagram tags (`@diagram: c4-l1`, `@diagram: dfd-l0`) | `BRD-W011`, `BRD-W012` |

**Quality Gates (10 GATE Checks):**

| GATE | Check | Tier | Description |
|------|-------|------|-------------|
| GATE-01 | Placeholder text detection | 1 | Detects TODO, TBD, FIXME, [placeholder] |
| GATE-02 | Premature downstream references | 1 | References to PRD/ADR before they exist |
| GATE-03 | Internal count consistency | 2 | Stated counts vs actual item counts |
| GATE-04 | Index synchronization | 1 | Index file matches section files |
| GATE-06 | Diagram contract validation | 1 | Diagrams match documented contracts |
| GATE-07 | Glossary consistency | 2 | Terms used vs glossary definitions |
| GATE-08 | Element ID uniqueness | 1 | No duplicate BRD.NN.TT.SS IDs |
| GATE-09 | Cost estimate format | 2 | Proper currency/range formatting |
| GATE-10 | File size compliance | 1 | Files under 20K token limit |

**Pre-commit Integration:**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ucx-brd-validate
        name: UCX BRD Validation (Tier 1)
        entry: bash -c 'source /opt/data/docs_flow_framework/.venv/bin/activate && ucx validate brd docs/01_BRD --tier1-only'
        language: system
        files: ^docs/01_BRD/.*\.md$
        stages: [pre-commit]
```

**Exit Codes:**

| Code | Meaning | Pre-commit |
|------|---------|------------|
| 0 | All checks passed | ✅ Pass |
| 1 | Warnings only | ✅ Pass (unless --strict) |
| 2 | Errors present | ❌ Fail |

> **Note**: Exit code 2 indicates validation completed successfully but found blocking errors - this is expected behavior, not a command failure. The validation report is still generated. These exit codes enable CI/CD integration where pipelines can distinguish between warnings (1) and errors (2).

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

### Prompt Inspection (v1.14.0+)

Pre-LLM analysis of generated prompts. Large documents (150K+ chars) merged into 40-50K token prompts are impossible to review manually. The prompt inspection toolset lets you analyze prompts **before** running expensive LLM reviews.

```bash
# Analyze token usage per persona
ucx prompt tokens brd docs/01_BRD/BRD-01/

# Show section inclusion matrix
ucx prompt sections brd docs/01_BRD/BRD-01/

# Inspect a generated prompt
ucx prompt inspect tmp/prompts/prompt_architect.txt

# Validate document for prompt generation
ucx prompt check brd docs/01_BRD/BRD-01/ --strict

# Generate prompts with metadata
ucx prompt generate brd docs/01_BRD/BRD-01/ -o tmp/prompts/
```

**Commands:**

| Command | Purpose |
|---------|---------|
| `ucx prompt tokens` | Per-persona token breakdown with budget tracking |
| `ucx prompt sections` | Section inclusion matrix (FULL/OPT/IDX/-) |
| `ucx prompt inspect` | Analyze prompt structure and detect issues |
| `ucx prompt check` | Validate document readiness for prompt generation |
| `ucx prompt generate` | Generate prompts with `.meta.json` metadata |

**Sample tokens output:**
```
Per-Persona Breakdown:
------------------------------------------------------------
Persona              Sections      Doc  Instr    Total   Budget
------------------------------------------------------------
architect                   7   12,903  3,500   16,403   70,000
auditor                    12   33,939  4,000   37,939   60,000

Context Engineering Savings:
  Without CE: 80,614 tokens
  With CE: 54,342 tokens
  Savings: 26,272 tokens (33%)
```

**Use cases:**
- Debug token budget issues before LLM execution
- Verify section inclusion for specific personas
- Check format instruction positioning (should be at END)
- Validate document structure before expensive API calls

See [CHANGELOG_v1.14.0](docs/CHANGELOG_v1.14.0.md) for full documentation.

### Layer Action Handoff (v1.18.0+)

UCX review automatically identifies items that belong in downstream layers and creates structured ACTIONS for handoff instead of penalizing BRD scores.

**Target Layers:**

| Target | Layer | Purpose |
|--------|-------|---------|
| PRD | L2 | Feature details, user stories |
| EARS | L3 | Formal requirement syntax |
| BDD | L4 | Test scenarios |
| ADR | L5 | Architecture decisions |
| CTR | L8 | API contracts |

**Actions do NOT affect BRD score** - they are handoffs, not findings.

**Action Format:**
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

**Extract actions:**
```bash
# Get summary of all actions
python scripts/extract_actions.py report.md --format summary

# Extract ADR-targeted actions as markdown
python scripts/extract_actions.py report.md --target ADR --format md

# Extract as JSON for processing
python scripts/extract_actions.py report.md --format json -o actions.json
```

**Validate actions:**
```bash
# Basic validation
python scripts/validate_actions.py report.md

# Strict mode (warnings = errors)
python scripts/validate_actions.py report.md --strict
```

See [CHANGELOG_v1.18.0](docs/CHANGELOG_v1.18.0.md) for full documentation.

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

## CLI Arguments Reference

### Global Options

| Option | Env Var | Default | Description |
|--------|---------|---------|-------------|
| `--model` | `UCX_MODEL` | `opus` | AI model selection (see below) |
| `--mode` | `UCX_AI_MODE` | `cli` | `cli` for CLI agents, `api` for LiteLLM |
| `--cli-tool` | `UCX_CLI_TOOL` | `claude` | CLI tool: claude, gemini, ollama, aider |
| `-P, --project-dir` | `UCX_PROJECT_DIR` | auto | Project root with docs/UCX/ |
| `-W, --enable-web-search` | `UCX_ENABLE_WEB_SEARCH` | false | Enable internet search |
| `-l, --log-level` | `UCX_LOG_LEVEL` | `INFO` | DEBUG, INFO, WARNING, ERROR |
| `-v, --verbose` | - | false | Sets log level to DEBUG |
| `-q, --quiet` | - | false | Sets log level to WARNING |

### Model Selection

| Model | Quality | Speed | Cost | Best For |
|-------|---------|-------|------|----------|
| `opus` | Highest | Slow | $$$ | Complex reviews, critical documents |
| `sonnet` | High | Medium | $$ | Most tasks (recommended default) |
| `haiku` | Good | Fast | $ | Quick validation, simple reviews |

```bash
# Using --model flag
ucx --model sonnet review brd docs/01_BRD/BRD-01/
ucx --model haiku validate brd docs/01_BRD/BRD-01/

# Using environment variable
export UCX_MODEL=sonnet
ucx review brd docs/01_BRD/BRD-01/

# One-time override
UCX_MODEL=opus ucx review brd docs/01_BRD/BRD-01/
```

### Commands Quick Reference

| Command | Purpose | Key Options |
|---------|---------|-------------|
| `review` | AI-powered document review | `--persona`, `--unified`, `--model`, `--clean-reports` |
| `validate` | Fast structural validation (no AI) | `--no-fix`, `--tier1-only`, `--strict` |
| `clean-markers` | Remove LLM_COMPLETION markers (v1.17.0+) | - |
| `remediate` | Generate fixes from review | `--model` |
| `create` | Create new document | `--from-ref`, `--from-upstream` |
| `autopilot` | Full cycle (create→review→fix) | `--max-iterations` |
| `scan` | Analyze review report | `--verbose`, `--format json` |

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `UCX_AI_MODE` | `cli` | AI client mode: `cli` or `api` |
| `UCX_CLI_TOOL` | `claude` | CLI tool for cli mode |
| `UCX_CLI_TIMEOUT` | `300` | CLI command timeout in seconds |
| `UCX_MODEL` | `opus` | Model: opus (best), sonnet (balanced), haiku (fast) |
| `UCX_API_BASE` | - | Custom API base URL |
| `UCX_MAX_ITER` | `3` | Maximum review/fix cycles |
| `UCX_MIN_SCORE` | `90` | Minimum passing score |
| `UCX_SKIP_DRIFT` | `false` | Skip drift monitoring |
| `UCX_ENABLE_WEB_SEARCH` | `false` | Enable internet search for deeper analysis |
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

# Web Search (CLI mode with Claude only)
enable_web_search: false  # Enable for deeper analysis

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

# CLI mode with web search enabled
config = UCXConfig(
    ai_mode="cli",
    cli_tool="claude",
    enable_web_search=True,  # Enable internet search
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
├── skills/                     # Framework persona skills (fallback)
│   ├── architect.md            # Architect domain knowledge
│   ├── auditor.md              # Auditor domain knowledge
│   ├── tech_lead.md            # Tech Lead domain knowledge
│   ├── ...                     # 14 persona skill files
│   └── chairperson.md
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
│   │   ├── review_memory.py    # ReviewMemory for persona prompts + finding extraction
│   │   ├── persona_prompts.py  # Persona prompt templates + skill loading
│   │   └── context_engine.py   # Context engineering (v1.13.0+)
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
│   │   ├── settings.py         # Pydantic settings (project_dir)
│   │   └── layer_skills.py     # Layer-to-skill mapping (DOMAIN/MANDATORY)
│   │
│   ├── prescreening/           # UCX Scanner (v1.11.0+, renamed from pre-screening)
│   │   ├── __init__.py         # Public exports
│   │   └── ucr_analyzer.py     # ScanResult, scan_ucr_report(), ManifestResult
│   │
│   ├── models/                 # Data models
│   │   ├── enums.py            # DocType, Status enums
│   │   ├── document.py         # Document model
│   │   ├── review.py           # Review result
│   │   └── drift_cache.py      # Drift cache
│   │
│   ├── validators/             # Document validators
│   │   ├── common/             # Shared validation utilities (v1.9.0+)
│   │   │   ├── error_codes.py  # Severity, ErrorCode, ERROR_REGISTRY
│   │   │   ├── file_utils.py   # File collection, companion detection
│   │   │   ├── frontmatter.py  # YAML frontmatter parsing
│   │   │   ├── result.py       # ValidationIssue, UnifiedValidationResult
│   │   │   ├── links.py        # Link validation (Tier 2)
│   │   │   ├── references.py   # Forward reference validation (Tier 2)
│   │   │   └── diagrams.py     # Diagram consistency (Tier 2)
│   │   ├── brd/                # UnifiedBRDValidator (v1.9.0+)
│   │   │   ├── __init__.py     # UnifiedBRDValidator class
│   │   │   ├── schema.py       # BRD constants, sections, codes
│   │   │   ├── element_codes.py # BRD.NN.TT.SS validation
│   │   │   ├── structure.py    # Document structure validation
│   │   │   ├── metadata.py     # YAML frontmatter validation
│   │   │   └── quality_gate.py # 10 GATE quality checks
│   │   ├── brd_validator.py    # Registry-compatible BRD validator
│   │   ├── prd.py, ears.py     # Other layer validators (legacy)
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
│   │   ├── loader.py           # SkillLoader (project_dir support)
│   │   ├── injector.py         # Prompt injection
│   │   └── personas/           # DEPRECATED - use /skills/
│   │
│   └── utils/                  # Utilities
│       ├── file_ops.py
│       ├── hash.py
│       └── logging.py
│
└── tests/                      # Test suite

Project Structure (recommended):
project/
├── docs/
│   └── UCX/
│       ├── skills/             # Project-specific skills (priority 1)
│       │   ├── architect.md    # Domain-tuned architect
│       │   ├── auditor.md      # Domain-tuned auditor
│       │   └── ...
│       ├── review/             # Project-specific prompts (required)
│       │   └── UCR_PROMPT_BRD_PROJECT.md
│       ├── creation/
│       └── remediation/
└── ...
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
| Chaos Engineer | Edge cases, failure modes |
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

# Review (persona prompts mode - recommended for large docs)
result = ucr.review_multi_turn(
    doc_type="brd",
    doc_path=path,
    resume=True,           # Skip completed personas (default)
    session_ttl_hours=24,  # Expire old sessions (default: 24)
)

# Remediation (with automatic pre-screening)
ucrem = UCRemPhase(config)
fixes, report_path = ucrem.generate_fixes(review_report=report_path, doc_path=path)

# Check which fixers were loaded
print(f"Domain fixers: {ucrem.last_screening.domain_fixers_needed}")
print(f"Excluded: {ucrem.last_screening.excluded_fixers}")
```

### Unified UCX Scanner (v1.11.0+) - VALIDATED

The `ucx scan` command provides unified report analysis with two extraction methods.
**Validated** with BRD-02 review (2026-03-12): Raw P0=115 → Manifest P0=10 (91% reduction).

```bash
# Scan a review report (uses manifest if present, else persona extraction)
ucx scan BRD-02.UCR_review_report_v001.md

# Actual output (BRD-02 validation):
# ✓ Chairperson Manifest detected (authoritative)
# Total findings: 33 | P0: 10 | P1: 14 | P2: 9
# PRD-Ready Score: 62/100
# → Remediation will load 6 fixers

# Verbose mode shows comparison
ucx scan BRD-02.UCR_review_report_v001.md --verbose

# JSON output for automation
ucx scan BRD-02.UCR_review_report_v001.md -f json -o scan_results.json
```

**Two-Layer Extraction:**

| Layer | Source | Purpose |
|-------|--------|---------|
| **Manifest** (authoritative) | Chairperson's `<!-- UCX-MANIFEST-START -->` section | Unique counts, score, fixer assignments |
| **Persona** (fallback) | Individual persona sections | Backward compat, fixer routing for pre-manifest reports |

**Chairperson Manifest Format:**

Reports generated with UCX v1.11.0+ include a structured manifest:

```markdown
<!-- UCX-MANIFEST-START -->
### Manifest Summary
| Metric | Count |
|--------|-------|
| Total Unique Findings | 16 |
| P0 (Critical) | 5 |
| P1 (High) | 8 |

### Findings Table
| ID | Priority | Status | Fixer | Target File | Description |
|----|----------|--------|-------|-------------|-------------|
| REM-P0-001 | P0 | OPEN | architect | BRD-01.6.md | Missing state machine |
<!-- UCX-MANIFEST-END -->
```

**Benefits:**
- **Eliminates discrepancy**: CLI counts match Chairperson synthesis
- **Authoritative source**: PRD-Ready score from Chairperson
- **Skip pre-screening**: Remediation reads manifest directly
- **Backward compatible**: Falls back to persona extraction for older reports

### Finding ID Format Standard (v1.13.0+)

All persona findings use the canonical format: `PREFIX-P{0-2}-NNN`

| Component | Rule | Example |
|-----------|------|---------|
| PREFIX | 2-4 char persona abbreviation | ARCH, AUD, TL, OP |
| PRIORITY | P0 (critical), P1 (high), P2 (medium) | P0 |
| NNN | 3-digit sequence (001-999) | 001 |

**Persona Prefixes:**

| Persona | Prefix | Example |
|---------|--------|---------|
| Architect | ARCH | `ARCH-P0-001` |
| Auditor | AUD | `AUD-P0-001` |
| Tech Lead | TL | `TL-P1-001` |
| Strategist | STR | `STR-P1-001` |
| Chaos Engineer | DA | `DA-P0-001` |
| Operator | OP | `OP-P0-001` |
| Integration Lead | IL | `IL-P0-001` |
| Product Owner | PO | `PO-P1-001` |
| Business Analyst | BA | `BA-P1-001` |
| Fact Checker | FC | `FC-P0-001` |
| Chairperson (manifest) | REM | `REM-P0-001` |

**Context Engineering (v1.13.0+):**

UCX uses context engineering to optimize prompt size and improve LLM output quality:

| Technique | Description | Impact |
|-----------|-------------|--------|
| Hierarchical Context | 3-level document filtering (Overview/Relevant/Reference) | 30-50% prompt reduction |
| Prior Findings Summary | Summarizes prior persona findings | 90% reduction (50K → 5K tokens) |
| Attention Steering | Format instructions at END of prompt | Better format adherence |
| Persona Section Mapping | Each persona gets only relevant sections | Focused analysis |

### Adaptive Remediation (v1.10.0+)

Remediation uses **pre-screening** to load only the fixer personas needed:

```bash
# Auto-detect latest review report (v1.16.0+, recommended)
ucx remediate docs/01_BRD/BRD-01/

# Explicit report path (override auto-detection)
ucx remediate docs/01_BRD/BRD-01/ -r BRD-01.UCR_review_report_v003.md

# Pre-screen command for analysis (standalone)
ucx prescreen BRD-01.UCR_review_report_v003.md --verbose
```

**Fixer Classification:**

| Category | Personas | Loading Rule |
|----------|----------|--------------|
| **Domain Fixers** | architect, auditor, qa_lead, integration_lead | Adaptive (only if findings exist) |
| **Mandatory** | chaos_engineer, chairperson | Always loaded (v1.14.3+) |

**Benefits:**
- **Token savings**: 30-60% reduction in prompt size
- **Focused attention**: AI focuses on relevant domains only
- **Quality synthesis**: Chairperson provides de-duplication and final conclusion

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

# CLI mode with web search
client = get_client(mode="cli", cli_tool="claude", enable_web_search=True)

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
| 1.18.0 | 2026-03-17 | **Layer Action Handoff System**: Capture out-of-scope items as ACTIONS that handoff to downstream layers (PRD, EARS, BDD, ADR, CTR) without penalizing BRD score. New scripts: `extract_actions.py` and `validate_actions.py`. ACTION format with fields: ACTION_ID, TYPE, TARGET, PRIORITY, SOURCE, PERSONA, CONTEXT, REQUIREMENT. Actions Manifest in Chairperson output. See [CHANGELOG_v1.18.0.md](docs/CHANGELOG_v1.18.0.md). |
| 1.17.0 | 2026-03-15 | **Fixer-to-LLM Hand-off System**: Validation now ALWAYS fixes by default (no `--fix` flag needed). Added `--no-fix` flag to opt out. New FixerContext tracks fixed/partial/skipped issues. Section 7 "Fixer Session Summary" added to validation reports with embedded JSON. LLM_COMPLETION markers inserted for partial fixes. New `ucx clean-markers` command. UCRem reads fixer context and injects into prompts. All 6 fixer personas updated with hand-off protocol. See [CHANGELOG_v1.17.0.md](docs/CHANGELOG_v1.17.0.md). |
| 1.16.2 | 2026-03-15 | **Duplicate Fixer Guardrails & Reference Detection Sync**: Fixed circular rename bug in GATE-E008 fixer (could cause infinite loops). Added backtick reference detection. Synced reference logic between validator and fixer. Protected historical reports from fixer modifications. See [CHANGELOG_v1.16.2.md](docs/CHANGELOG_v1.16.2.md). |
| 1.16.1 | 2026-03-15 | **Single-File Validation Reports**: Changed validation report from versioned format (`{doc_id}.V_validation_report_v{NNN}.md`) to single file (`.precommit_validation_report.md`) that overwrites on each run. Cleaner repos, no accumulation. See [CHANGELOG_v1.16.1.md](docs/CHANGELOG_v1.16.1.md). |
| 1.16.0 | 2026-03-15 | **Auto-Detection of Latest Review Report**: `ucx remediate` now auto-detects latest UCR review report. No need to specify exact report version. New `--report` / `-r` flag for explicit override. See [CHANGELOG_v1.16.0.md](docs/CHANGELOG_v1.16.0.md). |
| 1.15.2 | 2026-03-14 | **Extended Auto-Fix Suite (21 codes)**: Added `GATE-E001` (placeholder → DEFERRED comment), `DIAG-E001` (missing diagram → DIAGRAM-REQUIRED placeholder), `FWDREF-E001` (forward ref → FWDREF-DEFERRED comment). Total: 21 auto-fixable codes. Expected impact: ~524 Tier 1 errors converted to deferred. See [CHANGELOG_v1.15.2.md](docs/CHANGELOG_v1.15.2.md). |
| 1.15.1 | 2026-03-14 | **BRD-E020 Invalid Type Code Fixer**: Added auto-fix for invalid element type codes (1,260 errors fixed). New `INVALID_CODE_REMAP` table with 60+ mappings. Remaps invalid codes to valid BRD codes (01-32, 91-99). Total: 18 auto-fixable codes. See [CHANGELOG_v1.15.1.md](docs/CHANGELOG_v1.15.1.md). |
| 1.15.0 | 2026-03-14 | **Extended Auto-Fix Suite (17 codes)**: Added `GATE-E010` (auto-split large files), `GATE-W008` (move elements to correct section), `BRD-W010` (auto-detect @depends), `VAL-E002` (create frontmatter from scratch). BRD-E002 now context-aware (custom_fields OR Section 0). BRD-03 improved 89.5→96.0 (PASS). See [CHANGELOG_v1.15.0.md](docs/CHANGELOG_v1.15.0.md). |
| 1.14.9 | 2026-03-14 | **Duplicate ID Auto-Fixer**: Added `GATE-E008` to auto-fix. New `DuplicateElementFixer` renumbers duplicate element IDs. Improved reference detection for category lists, range notation, multiple IDs. BRD-03 score improved 0.0→89.5. See [CHANGELOG_v1.14.9.md](docs/CHANGELOG_v1.14.9.md). |
| 1.14.8 | 2026-03-14 | **Terminology Update**: Renamed "one-turn" → "unified prompt" and "multi-turn" → "persona prompts" for clarity. CLI flags: `--multi-turn` → `--persona` (`-p`), `--force-single` → `--unified` (`-u`). Updated documentation, comments, and file naming. See [CHANGELOG_v1.14.8.md](docs/CHANGELOG_v1.14.8.md). |
| 1.14.7 | 2026-03-14 | **Attention Steering Fix**: Format instructions now placed at END of prompt for better LLM attention. Added `_load_format_instructions()` method and `UCR_FORMAT_{TYPE}_PROJECT.md` file pattern. See [CHANGELOG_v1.14.7.md](docs/CHANGELOG_v1.14.7.md). |
| 1.14.6 | 2026-03-14 | **Session Directory Rename & Review Mode Docs**: Renamed `.doc_review_memory/` → `.ucx_review_session/` and `final_body.md` → `assembled_report.md` for clarity. Added comprehensive One-Turn vs Multi-Turn review mode documentation. See [CHANGELOG_v1.14.6.md](docs/CHANGELOG_v1.14.6.md). |
| 1.14.5 | 2026-03-14 | **Unified Prompt Feature Parity & Naming Standardization**: Unified prompt review now has full feature parity with persona prompts (project-first skill loading). Renamed `integration_expert` → `integration_lead` for consistent persona/skill naming. Added Category Tagging to auditor, fact_checker, product_owner. Fixed `get_skill_dir()` path. See [CHANGELOG_v1.14.5.md](docs/CHANGELOG_v1.14.5.md). |
| 1.14.4 | 2026-03-14 | **Extraction Pattern Fixes**: Fixed 5 old patterns that truncated at `###` headers. 15 new extraction patterns for all 12 personas. 11/12 personas at 5%+ instruction ratio. See [CHANGELOG_v1.14.4.md](docs/CHANGELOG_v1.14.4.md). |
| 1.14.3 | 2026-03-14 | **QA Lead Persona & Chaos Engineer Rename**: Added `qa_lead` as core persona (12 total). Renamed `devils_advocate` → `chaos_engineer` for industry alignment. 9 new qa_lead extraction patterns (BDD, test coverage, testability). See [CHANGELOG_v1.14.3.md](docs/CHANGELOG_v1.14.3.md). |
| 1.14.2 | 2026-03-14 | **Enhanced Skill Extraction**: 27 extraction patterns covering all personas. Instruction ratio improved to 5-10% target. See [CHANGELOG_v1.14.2.md](docs/CHANGELOG_v1.14.2.md). |
| 1.14.1 | 2026-03-13 | **Prompt Quality Improvements**: Content preprocessing strips YAML frontmatter, HTML comments, navigation breadcrumbs, document metadata from prompts. System instructions loaded from skill manifests with project-specific overrides (`docs/UCX/skills/`). Numeric section ordering (BRD-01.5 before BRD-01.11). Fixed anti-pattern regex extraction. Token optimization: ~455 tokens saved per prompt (~5,000 across 11 personas). See [CHANGELOG_v1.14.1.md](docs/CHANGELOG_v1.14.1.md). |
| 1.14.0 | 2026-03-13 | **Prompt Inspection Toolset**: Pre-LLM analysis of generated prompts. New CLI commands: `ucx prompt tokens/sections/inspect/check/generate`. `UCPromptPhase` API class. Token analysis per persona with budget tracking. Section inclusion matrix. Prompt structure analysis with attention steering detection. Metadata files (`.meta.json`) alongside generated prompts. See [CHANGELOG_v1.14.0.md](docs/CHANGELOG_v1.14.0.md) and [PLAN-005](docs/plans/PLAN-005_prompt_engineering_toolset.md). |
| 1.13.1 | 2026-03-13 | **Advanced Context Engineering**: Completes deferred features from v1.13.0. Hybrid keyword scan (`RelevantSnippet`, `_scan_other_sections_for_keywords()`) discovers relevant content in non-mapped sections. Appendix-on-demand (`AppendixInfo`, lightweight index ~500 tokens vs 20-50K). Dynamic section mapping (`SECTION_CATEGORIES`, `DynamicSectionMapper`) for semantic filtering across document types. VERIFY tag pattern `[VERIFY: appendix-id]` with `AppendixVerifier` for post-processing verification. See [CHANGELOG_v1.13.1.md](docs/CHANGELOG_v1.13.1.md) and [PLAN-004](docs/plans/PLAN-004_advanced_context_engineering.md). |
| 1.13.0 | 2026-03-13 | **Context Engineering & Finding ID Standardization**: Canonical Finding ID format (`PREFIX-P0-NNN` e.g., `ARCH-P0-001`). Context engineering reduces prompts from 170KB to ~60-80KB. Attention steering places format instructions at prompt END. Prior findings summarization (90% token reduction). Hierarchical document context (4-level structure). Chairperson manifest validation. Updated UCR prompts (BRD/PRD) with Finding ID format. See [CONTEXT_ENGINEERING.md](docs/CONTEXT_ENGINEERING.md) and [PLAN-003](docs/plans/PLAN-003_persona_prompt_restructuring.md). |
| 1.12.0 | 2026-03-12 | **Category-Weighted Scoring**: New scoring system with 8 categories (functional, quality, compliance, constraints, integration, acceptance, risk, architecture). Per-category weights and deduction caps prevent runaway scores. Categories align with ID_NAMING_STANDARDS element codes. Legacy `--scoring legacy` CLI option removed. Manifest includes category summary table with weighted score. See [SCORING_GUIDE.md](docs/scoring/SCORING_GUIDE.md). |
| 1.11.1 | 2026-03-12 | **Validate: Report Generation by Default**: `ucx validate` now generates report to document directory by default (like review). Use `--no-report` for console-only output. Aligns validate behavior with review command. |
| 1.11.0 | 2026-03-12 | **Unified UCX Scanner with Chairperson Manifest** (VALIDATED): New `ucx scan` command replaces `prescreen` as unified report scanner. Chairperson now outputs structured Remediation Findings Manifest with authoritative counts, fixer assignments, and PRD-Ready score. Scanner extracts from manifest when present (authoritative) or falls back to persona extraction (backward compat). Eliminates discrepancy between CLI counts and Chairperson synthesis. Remediation can skip pre-screening when manifest present. **Validated**: BRD-02 review confirmed 91% reduction (Raw P0=115 → Manifest P0=10). |
| 1.10.3 | 2026-03-12 | **Pre-Screening Accuracy Improvements**: Fixed duplicate counting (unique vs total findings). Fixed summary row extraction (excludes range expressions). Fixed false DEFERRED/RESOLVED detection (word boundary matching, context-aware). |
| 1.10.0 | 2026-03-12 | **Adaptive Remediation with Pre-Screening**: Pre-screening phase automatically analyzes UCR reports before remediation. New `ucx prescreen` command for standalone analysis. Adaptive fixer loading - only domain fixers with findings are loaded. Mandatory fixers: chaos_engineer (safety) + chairperson (synthesis). Token savings of 30-60% by excluding unnecessary personas. Chairperson skill updated with remediation synthesis responsibilities. |
| 1.9.9 | 2026-03-12 | **UCRem project path resolution & Prior Review Reconciliation**: Fixed UCRem prompt path to check project-specific paths first. Fixed project directory auto-detection bug. UCRem report writes to document folder (`{DOC-ID}.UCRem_report.md`). **New**: Prior Review Reconciliation - Fact Checker verifies resolution status of prior findings, Chairperson only counts UNRESOLVED findings in score, Auditor adds verification status table. |
| 1.9.8 | 2026-03-11 | **Tier 2 diagram advisory auto-fix**: Added auto-fix for BRD-W011/W012 (adds @diagram-request for ADR layer), BRD-W013 (auto-detects sequence type), BRD-W014 (adds diagram intent). New @diagram-request pattern for honest traceability. Fixed version numbering bug (max+1 instead of len+1). Fixed FIXER_SKILLS (integration_expert → integration_lead). |
| 1.9.7 | 2026-03-11 | **Tier 2 count mismatch auto-fix**: Extended `--fix` to handle GATE-W003 (count mismatch) and DIAG-W001 (diagram node count). Updates prose counts to match actual element or diagram node counts. |
| 1.9.6 | 2026-03-11 | **Auto-fix structural issues**: Added `--fix` flag to `ucx validate`. Added `--report` flag to auto-generate report after fixing. Combined `--fix --report --clean-reports` to fix, report, and cleanup in one command. New `BRDFixer` module auto-fixes: missing metadata, missing tags, legacy status. Fixed Document Control regex bug. |
| 1.9.5 | 2026-03-11 | **Validation report cleanup**: Added `--clean-reports` flag to `ucx validate` command. Added `--keep-versions` option (default: 1) to control retention. Cleans up old `*.V_validation_report_v*.md` files by modification time, keeping N most recent. |
| 1.9.4 | 2026-03-11 | **QA subcategory codes 91-99**: Added Performance (91), Reliability (92), Scalability (94), Security (96), Observability (98), Maintainability (99) to valid element codes. Added Section 3/4 mappings (Feature Item=22, Stakeholder Need=24). Updated traceability tag patterns to require 2+ digits. Fixed ADR filename pattern. |
| 1.9.3 | 2026-03-11 | **SDD-compliant validation reports**: Added `--output` (`-o`) option to `ucx validate`. Reports include YAML frontmatter, Document Control section, score breakdown, and structured findings tables. Auto-versioning when writing to document directory. Report naming: `{DOC-ID}.V_validation_report_v{NNN}.md`. |
| 1.9.2 | 2026-03-11 | **Registry integration**: `BRDValidator` (registry) now delegates to `UnifiedBRDValidator`. `ucx review brd` and `ucx validate brd` use same validation logic. Renamed `brd.py` to `brd_validator.py` to avoid package conflict. Pre-commit hooks migrated to UCX unified validation. |
| 1.9.1 | 2026-03-11 | **Tier 2 advisory validators**: New `common/links.py` for markdown link validation. New `common/references.py` for SDD forward reference validation. New `common/diagrams.py` for Mermaid/SVG diagram consistency. Error codes: LINK-*, FWDREF-*, DIAG-*. |
| 1.9.0 | 2026-03-11 | **Unified BRD Validation**: New `ucx/validators/common/` module with shared validation utilities. New `ucx/validators/brd/` module with `UnifiedBRDValidator`. Tiered validation: Tier 1 (core, blocking) and Tier 2 (advisory). CLI: `ucx validate brd <path>` with `--tier1-only`, `--strict`, `--format`. Quality gates: 10 GATE checks (GATE-01 to GATE-10). Element code validation: BRD.NN.TT.SS format with section mapping. Deprecated: `ai_dev_ssd_flow/01_BRD/scripts/` validators (removal in v2.0.0). |
| 1.8.0 | 2026-03-10 | **Project-specific skills support**: Skills now load from `{project}/docs/UCX/skills/` first, falling back to framework skills. Prompts remain project-specific only (no fallback). `SkillLoader` accepts `project_dir` parameter. `UnifiedPromptLoader` injects project skills into persona prompts. UCR/UCC/UCRem engines pass `project_dir` to skill loading. |
| 1.7.2 | 2026-03-10 | **Skill consolidation**: Merged `/UCX/ucx/skills/personas/` (lightweight) into `/UCX/skills/` (detailed). Single source of truth for persona skills with both domain knowledge AND review metadata (scoring weights, tags, checklists). SkillLoader now defaults to `/UCX/skills/`. |
| 1.7.1 | 2026-03-10 | **Skill file integration**: Domain knowledge now loaded from `/UCX/skills/*.md` files instead of hardcoded templates. Enables easier customization of persona expertise. Added `fact_checker.md` skill. Falls back to embedded templates if skill file not found. |
| 1.7.0 | 2026-03-10 | **Anti-repetition and deduplication**: Multi-turn reviews now prevent persona repetition via anti-repetition rules in prompts. Report assembly includes automated finding deduplication with Jaccard similarity (60% threshold). Consolidated findings section shows unique vs. confirmed-by-multiple-personas findings. Dynamic version in report headers. |
| 1.6.0 | 2026-03-10 | **Web search support**: Added `--enable-web-search` (`-W`) flag for internet-enabled analysis. Fact-checking regulatory references, verifying best practices, finding solutions. CLI mode with Claude only. |
| 1.5.5 | 2026-03-10 | **Report naming standardization**: Changed from `{TYPE}_UCR_REVIEW_v{NNN}.md` to `{DOC_ID}.UCR_review_report_v{NNN}.md`. **Layer-appropriate finding classification**: BRD reviews now distinguish requirements (P0) from implementation details (defer to SPEC). **Pre-validation separation**: YAML/schema errors reported separately from content P0 findings. **Complexity scale**: Replaced time estimates with 1-5 complexity scale. |
| 1.5.4 | 2026-03-10 | Added Fact Checker and Chairperson as required personas. Added Judge and Chairperson Editor as optional personas. |
| 1.5.1 | 2026-03-10 | Added `--clean-reports` and `--clean-all` flags to clean old review reports while keeping latest. |
| 1.5.0 | 2026-03-10 | SDD-compliant output format for all review reports. YAML frontmatter, Document Control section, layer-specific downstream-ready scores. All 10 UCR templates updated. |
| 1.4.1 | 2026-03-10 | Added `--clean-memory` flag to remove stale session memory. |
| 1.4.0 | 2026-03-10 | Project-specific prompts support with `-p/--project-prompts` flag. One-prompt with Fact Checker/Chairperson personas. |
| 1.3.1 | 2026-03-10 | CLI mode fix: Added `--dangerously-skip-permissions` flag to prevent truncated output from permission prompts. |
| 1.3.0 | 2026-03-09 | Multi-turn review mode with session memory for large documents. |
| 1.2.0 | 2026-03-09 | Dual-mode architecture: CLI mode (default) + API mode. Extended logging. |
| 1.1.0 | 2026-03-09 | LiteLLM integration for multi-provider LLM support. |
| 1.0.0 | 2026-03-09 | Python migration complete. API, CLI, full test suite. |

---

## Roadmap

See [ROADMAP.md](docs/ROADMAP.md) for planned features and release timeline.

**Latest Release**: v1.18.0 - Layer Action Handoff System
- NEW: ACTION handoff system captures out-of-scope items without score penalty
- NEW: Target layers: PRD (L2), EARS (L3), BDD (L4), ADR (L5), CTR (L8)
- NEW: `extract_actions.py` script with filter by target/type/priority
- NEW: `validate_actions.py` script with strict mode
- NEW: Actions Manifest in Chairperson output
- NEW: Section 12 "Downstream Layer Actions" in UCR reports
- See [CHANGELOG_v1.18.0](docs/CHANGELOG_v1.18.0.md) for details

**Previous Releases**: v1.17.x / v1.16.x / v1.15.x / v1.14.x
- v1.17.0: Fixer-to-LLM hand-off system
- v1.16.2: Duplicate fixer guardrails & reference detection sync
- v1.16.1: Single-file validation reports (`.precommit_validation_report.md`)
- v1.16.0: Auto-detection of latest review report for remediation
- v1.15.2: Extended auto-fix suite (21 codes)
- v1.15.1: BRD-E020 invalid type code fixer (1,260 errors fixed)
- v1.15.0: Extended auto-fix suite (17 codes), GATE-E010, GATE-W008, BRD-W010, VAL-E002
- v1.14.9: Duplicate element ID auto-fixer (GATE-E008)
- v1.14.8: Terminology update (unified prompt / persona prompts)
- v1.14.7: Attention steering fix (format instructions at END)
- v1.14.0: Prompt inspection commands

**Next Release**: v1.19.0 - Multi-Document Validation
- Corpus-wide validation (`ucx validate --all`)
- Cross-document traceability validation
- Dependency graph visualization
- Batch review mode

---

## Documentation

| Document | Description |
|----------|-------------|
| [ROADMAP.md](docs/ROADMAP.md) | Release roadmap and planned features |
| [DEVELOPMENT_WORKFLOW.md](docs/DEVELOPMENT_WORKFLOW.md) | Development process: plans, changelogs, versioning |
| [QUICK_START.md](docs/QUICK_START.md) | Quick start guide with review process explanation |
| [HOW_TO_USE.md](docs/HOW_TO_USE.md) | Detailed usage instructions |
| [HOW_TO_AUDIT.md](docs/HOW_TO_AUDIT.md) | Running document audits |
| [PERSONA_DESIGN_GUIDE.md](docs/PERSONA_DESIGN_GUIDE.md) | Creating custom personas |
| [UNIFIED_CONTEXT_FRAMEWORK.md](docs/UNIFIED_CONTEXT_FRAMEWORK.md) | Framework architecture |
| [WORKFLOW_ARCHITECTURE.md](docs/WORKFLOW_ARCHITECTURE.md) | How UCX orchestrates AI calls (skills, personas, prompts) |
| [CONTEXT_ENGINEERING.md](docs/CONTEXT_ENGINEERING.md) | Context engineering guide (v1.13.0+) |
| [Skills README](skills/README.md) | Framework persona skills reference |
| [UCRem Personas](remediation/UCRem_PERSONAS.md) | Fixer personas and adaptive loading |
| [CHANGELOG v1.10.0](docs/CHANGELOG_v1.10.0.md) | Adaptive remediation release notes |
| [CHANGELOG v1.11.0](docs/CHANGELOG_v1.11.0.md) | Unified scanner and manifest release notes |
| [CHANGELOG v1.12.0](docs/CHANGELOG_v1.12.0.md) | Category-weighted scoring release notes |
| [CHANGELOG v1.13.0](docs/CHANGELOG_v1.13.0.md) | Context engineering & Finding ID |
| [CHANGELOG v1.14.0](docs/CHANGELOG_v1.14.0.md) | Prompt inspection toolset |
| [CHANGELOG v1.14.1](docs/CHANGELOG_v1.14.1.md) | Prompt quality improvements |
| [CHANGELOG v1.14.2](docs/CHANGELOG_v1.14.2.md) | Enhanced skill extraction |
| [CHANGELOG v1.14.3](docs/CHANGELOG_v1.14.3.md) | QA Lead persona, Chaos Engineer rename |
| [CHANGELOG v1.14.4](docs/CHANGELOG_v1.14.4.md) | Extraction pattern fixes, 15 new patterns |
| [CHANGELOG v1.14.5](docs/CHANGELOG_v1.14.5.md) | One-turn feature parity, naming standardization |
| [CHANGELOG v1.14.6](docs/CHANGELOG_v1.14.6.md) | Session directory rename, review mode documentation |
| [CHANGELOG v1.14.7](docs/CHANGELOG_v1.14.7.md) | Attention steering fix (format instructions at END) |
| [CHANGELOG v1.14.8](docs/CHANGELOG_v1.14.8.md) | Terminology update (unified prompt / persona prompts) |
| [CHANGELOG v1.14.9](docs/CHANGELOG_v1.14.9.md) | Duplicate element ID auto-fixer (GATE-E008) |
| [CHANGELOG v1.15.0](docs/CHANGELOG_v1.15.0.md) | Extended auto-fix suite (17 codes) |
| [CHANGELOG v1.15.1](docs/CHANGELOG_v1.15.1.md) | BRD-E020 invalid type code fixer |
| [CHANGELOG v1.16.0](docs/CHANGELOG_v1.16.0.md) | Auto-detection of latest review report |
| [CHANGELOG v1.16.1](docs/CHANGELOG_v1.16.1.md) | Single-file validation reports |
| [CHANGELOG v1.16.2](docs/CHANGELOG_v1.16.2.md) | Duplicate fixer guardrails & reference detection sync |
| [CHANGELOG v1.17.0](docs/CHANGELOG_v1.17.0.md) | Fixer-to-LLM hand-off system |
| [CHANGELOG v1.18.0](docs/CHANGELOG_v1.18.0.md) | Layer Action Handoff System |
| [PLAN-002](docs/plans/PLAN-002_category_weighted_scoring.md) | Category-weighted scoring implementation |
| [PLAN-003](docs/plans/PLAN-003_persona_prompt_restructuring.md) | Context engineering & Finding ID standardization |
| [PLAN-006](docs/plans/PLAN-006_fixer_to_llm_handoff.md) | Fixer-to-LLM hand-off implementation |
| [PLAN-007](docs/plans/PLAN-007_layer_notice_handoff.md) | Layer Action Handoff implementation |

### Scoring Documentation (v1.12.0)

| Document | Description |
|----------|-------------|
| [SCORING_GUIDE.md](docs/scoring/SCORING_GUIDE.md) | Primary scoring user guide |
| [WEIGHT_MATRIX.md](docs/scoring/WEIGHT_MATRIX.md) | Per-document-type weight matrices |
| [CATEGORY_REFERENCE.md](docs/scoring/CATEGORY_REFERENCE.md) | Category definitions and element codes |
| [PERSONA_CATEGORY_MAPPING.md](docs/scoring/PERSONA_CATEGORY_MAPPING.md) | Persona to category assignment rules |
| [SCORING_TROUBLESHOOTING.md](docs/scoring/SCORING_TROUBLESHOOTING.md) | Common issues and solutions |
| [SCORING_CUSTOMIZATION.md](docs/scoring/SCORING_CUSTOMIZATION.md) | Project-specific overrides guide |
| [MIGRATION_FROM_BRD_SCORING.md](docs/scoring/MIGRATION_FROM_BRD_SCORING.md) | Migration from deprecated BRD scoring |

---

## Legacy Shell Scripts

The following shell scripts are deprecated:
- `run_ucx_autopilot.sh` - Use `ucx autopilot` CLI instead
- `run_ucc.sh`, `run_ucr.sh`, `run_ucrem.sh` - Use `ucx create/review/remediate`

For legacy documentation, see `SKILL_INDEX.md`.
