# Agent-Agnostic Automation Sub-Framework

> ## ⚠️ DEPRECATED
>
> **This directory is deprecated as of 2026-03-09.**
>
> All functionality has been superseded by the **UCx (Unified Context) Framework**:
> ```
> /opt/data/docs_flow_framework/ucx_flow_v3/UCX/
> ```
>
> See `DEPRECATED.md` for migration guide.
>
> **Planned removal: 2026-06-09**

---

The `automation/` directory acts as the centralized engine for all AI-driven workflows and pipelines within the documentation flow framework.

---

## Document Validation Methods

### Primary Method: Single-Pass Claude Opus 4.5

**Status**: PREFERRED for all document validation/verification

The Single-Pass Claude Opus 4.5 method is the recommended approach for validating SDD artifacts including **BRD, PRD, EARS, and ADR** documents.

| Metric | Value |
|--------|-------|
| **Accuracy** | 100% (0 false positives) |
| **Verification Quality** | Full document context maintained |
| **Cost Efficiency** | 1 API call per review |
| **Weighted Quality Score** | 87.5/100 |

**How to Use**:
```bash
# Using Claude Code CLI with persona-based review
claude -p "Review this BRD using 8 expert personas (Architect, Auditor, Tech Lead,
Strategist, Devil's Advocate, Operator, Integration Lead, Product Owner).
Check Section 18 (Appendices) before claiming any requirement is missing."
```

**Advantages**:
- Zero false positives due to maintained context coherence
- Better cross-reference verification (reads all sections sequentially)
- More cost-effective (single model invocation)
- Thorough Section 18 verification prevents false "missing" claims

### Alternative Method: Multi-Model Pipeline (Backup)

**Status**: BACKUP - Use when maximum adversarial coverage required

The multi-model pipeline (`pipelines/doc_review/`) uses 8 specialized AI personas with a Fact-Checker, Chairperson, Judge, and Editor for synthesis.

| Metric | Value |
|--------|-------|
| **Accuracy** | 93% (1 false positive risk) |
| **Coverage** | Higher (more findings) |
| **Cost** | 10+ API calls per review |
| **Weighted Quality Score** | 84.0/100 |

**When to Use Multi-Model**:
- Pre-audit maximum coverage needed
- Fact-Checker upgraded to Claude Opus (not GPT-4o-mini)
- Alternative solutions section required in report

**Known Limitation**: Context fragmentation between experts may cause false positives (e.g., claiming circuit breaker missing when defined in Section 5.6/10.2.1).

### Method Comparison Summary

| Factor | Single-Pass Opus | Multi-Model Pipeline |
|--------|------------------|---------------------|
| **Precision** | 100% | 93% |
| **Coverage** | Good (11 findings) | Better (14 findings) |
| **False Positives** | 0 | 1+ |
| **Cost** | Low (1 call) | High (10+ calls) |
| **Recommendation** | **PRIMARY** | Backup |

> **Reference**: See `docs/01_BRD/BRD-01_platform_architecture/BRD-01_METHOD_COMPARISON_ANALYSIS.md` for detailed analysis.

---

## Core Design Principles

1. **Agent-Agnostic Interface**: Pipelines should never hardcode calls to `claude`, `opencode`, etc. Instead, they use `core/ai_exec.sh` which dynamically routes the text prompt to the agent specified in configuration.
2. **Infrastructure as Code**: Configuration is governed by precedence (Environment Variables > local `.env` > `config/automation.yaml`).
3. **Graceful Degradation**: Optional infrastructure (like the Knowledge Base Neo4j graph or external issue trackers) should fail silently or skip if not enabled, allowing local testing.
4. **Standardized Interfaces**: All pipelines expose a consistent `run.sh` orchestrator with common flags (`--dry-run`).

---

## Directory Layout

```text
automation/
├── config/                  # Configuration files
│   ├── .env.example         # Template for required environment variables (copy to .env)
│   └── automation.yaml      # Default pipeline and routing settings
├── core/                    # Shared framework utilities
│   ├── ai_exec.sh           # The agent routing adapter
│   ├── config.sh            # Loader script for env and yaml config
│   └── utils.sh             # Common bash functions (logging, JSON, guardrails)
└── pipelines/               # The actual automation workflows
    ├── doc_review/          # Final audit/review pipeline (The AI Experts Board)
    │   ├── run_review.sh    # Executes post-creation document audits against framework standards
    └── doc_generate/            # Multi-Agent Document Generation Pipeline
```

---

## How to Configure

1. Copy the environment template to create a local configuration file:
   ```bash
   cp automation/config/.env.example automation/config/.env
   ```
2. Open `automation/config/.env` and specify your preferred agent and credentials.

> [!NOTE] 
> The framework uses `AI_AGENT` to determine which CLI installed on your machine should process the prompt. Supported agents natively mapped in `ai_exec.sh` include: `claude`, `opencode`, `codex`, `cline`, `ollama`, `openai-api`, `gemini`.

---

## Existing Pipelines

### Doc Review Pipeline (`pipelines/doc_review/`) - BACKUP METHOD
> **Note**: This multi-model pipeline is the **backup method**. For production use, prefer Single-Pass Claude Opus 4.5 (see Document Validation Methods above).

Automates the mandatory review and remediation process for the "Documentation as Code" governance cycle using 8 specialized AI personas.
- **Review**: `run_review.sh` summons 8 AI expert personas to blindly audit a document and synthesizes a master audit report.
- **Remediate**: `run_remediate.sh` parses the audit report, auto-applies structural P0 fixes with git commits, and generates GitHub Issues for deeper architectural flaws.

**Accuracy**: 93% (risk of false positives due to context fragmentation between experts)

See [pipelines/doc_review/README.md](pipelines/doc_review/README.md) for detailed usage.

### Doc Generate Pipeline (`pipelines/doc_generate/`)
Automates writing perfectly compliant framework documents using a multi-agent authoring board.
- **Generate**: `run_generate.sh` coordinates an Assembler, multiple domain Drafters, an LLM Judge, and a Final Editor to produce strict SDD-compliant markdown templates from scratch.

See [pipelines/doc_generate/README.md](pipelines/doc_generate/README.md) for detailed usage.

---

## How to Add a New Pipeline

To build a new pipeline (e.g., an `autopilot` generator or `translation` workflow), follow this pattern:

1. **Create the directory**: `pipelines/<your_pipeline_name>/`
2. **Write Prompt Templates**: Place your instruction text files in a `prompts/` sub-folder. Use placeholders (like `{CONTENT}`) that bash can substitute.
3. **Use the Core Framework**:
   Start your new script by sourcing the framework core:
   ```bash
   #!/usr/bin/env bash
   set -euo pipefail
   
   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
   CORE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")/core"
   
   source "$CORE_DIR/config.sh"
   source "$CORE_DIR/utils.sh"
   ```
4. **Call the Agent**:
   Write your prompt to a temporary file, then pass it to `AI_EXEC_SH`:
   ```bash
   cat prompts/my_prompt.txt > /tmp/prompt.txt
   echo "My dynamic content" >> /tmp/prompt.txt
   
   RESPONSE=$(bash "$AI_EXEC_SH" /tmp/prompt.txt)
   ```
5. **Add a standard orchestrator**: Expose a `run.sh` or `run_<task>.sh` that accepts `--dry-run` and uses the standard `log_info`, `log_step`, and `log_error` functions from `utils.sh`.
