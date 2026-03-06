# Agent-Agnostic Automation Sub-Framework

The `automation/` directory acts as the centralized engine for all AI-driven workflows and pipelines within the documentation flow framework.

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
    └── council/             # The AI Expert Council Audit & Remediation Pipeline
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

### Council Pipeline (`pipelines/council/`)
Automates the mandatory review and remediation process for the "Documentation as Code" governance cycle.
- **Review**: `run_review.sh` summons 7 AI expert personas to blindly audit a document and synthesizes a master audit report.
- **Remediate**: `run_remediate.sh` parses the audit report, auto-applies structural P0 fixes with git commits, and generates GitHub Issues for deeper architectural flaws.

See [pipelines/council/README.md](pipelines/council/README.md) for detailed usage.

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
