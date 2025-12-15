# .aidev Architecture

`.aidev` acts as the **Operating System** for the `ai_dev_flow` framework. It separates the **Methodology** (the process) from the **Tooling** (the models).

## Core Principles

1.  **OS vs App**: The framework (`docs/`, `task.md`) is the OS. The logic that fills them (`plugin/workflow.sh`) are the Apps.
2.  **Roles, Not Models**: Plugins define abstract needs (e.g., "I need an Architect"). The User maps those needs to concrete models (e.g., "Use Gemini 1.5 Pro").

## Directory Structure

```text
.aidev/
├── config.yaml          # Global Configuration (Model Routing)
├── plugins/             # The "Apps" installed
│   └── product-manager/ 
│       ├── workflow.sh     # The Orchestrator
│       └── prompts/        # The Intelligence
│           ├── writer.md
│           └── reviewer.md
└── docs/                # System Documentation
```

## Plugin Architecture

A plugin is simply a directory containing:
1.  **Orchestrator**: A script (`workflow.sh`, `workflow.py`) that manages the flow.
2.  **Prompts**: System instructions for the specific agents involved.

### Example Workflow Script
```bash
# 1. Call Executor (Claude)
claude --prompt "$(cat prompts/writer.md)" > draft.md

# 2. Call Reviewer (Gemini)
gemini --prompt "$(cat prompts/reviewer.md)" --context draft.md > review.md
```

## Multi-LLM Routing

We use an **Adapter Pattern** (conceptually similar to LiteLLM) to standardize calls.

In your `config.yaml` (conceptual):
```yaml
roles:
  architect: gemini_pro
  coder: claude_sonnet
```

This allows you to hot-swap "Brains" without rewriting the Plugin logic.
