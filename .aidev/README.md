# .aidev: The Agentic Core

**Current Status**: Beta / Reference Implementation

`.aidev` is the **Agentic Orchestration Layer** for the `ai_dev_flow` framework. It implements the **docs_flow_framework** methodology by treating AI Agents as specialized workers who operate on the framework's documentation.

## 🚀 Quick Start

### 1. Run a Plugin (The "App" Model)
To execute a specific agent workflow (e.g., creating a PRD from a BRD), run the corresponding plugin script:

```bash
# Example: Run the Product Manager Agent (Layer 2)
./.aidev/plugins/product-manager/workflow.sh
```

### 2. Available Plugins
We have scaffolded the following Core Agents (see `plugins/` directory):
*   **Product Manager** (L2): Converts BRD -> PRD.
*   **Architect** (L5): Converts BDD -> ADR.
*   **Tech Lead** (L10): Converts REQ -> SPEC.
*   **eng-manager** (L11): Converts SPEC -> TASKS.

## 🧠 The Agent Swarm
We utilize a **16-Layer Swarm** where every layer is managed by an **Adversarial Pair** (Executor + Reviewer).

> **See [docs/AGENT_SWARM.md](docs/AGENT_SWARM.md) for the full 16-layer mapping.**

## 🏗 Architecture
`.aidev` follows an **"OS vs App"** philosophy:
*   **Non-Invasive**: It lives in `.aidev/` and doesn't clutter your project root.
*   **Multi-Model**: Designed to mix Claude, Gemini, and Codex.

> **See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for technical details.**

## 🛠 Configuration
Currently, configuration is handled within the individual `workflow.sh` scripts.
*   **Future Roadmap**: Unified `config.yaml` for global model routing.

## 📖 Usage Guide

### The Core Loop (How to use the Swarm)

The swarm is designed to move your documents through the **16 Layers of docs_flow_framework**.

#### Step 1: Initialize (The Business Analyst)
The journey starts with raw notes.
*   **Input**: `docs/init/notes.txt` (You create this)
*   **Command**:
    ```bash
    ./.aidev/plugins/business-analyst/workflow.sh
    ```
*   **Output**: `docs/BRD/BRD.md` (A drafted Business Requirements Document)

#### Step 2: Refine (The Product Manager)
Convert the business goals into structured product requirements.
*   **Input**: `docs/BRD/BRD.md`
*   **Command**:
    ```bash
    ./.aidev/plugins/product-manager/workflow.sh
    ```
*   **Output**: `docs/PRD/PRD.md`

#### Step 3: Design (The Architect)
Convert requirements into technical decisions.
*   **Input**: `docs/BDD/Features.feature` (Derived from PRD)
*   **Command**:
    ```bash
    ./.aidev/plugins/architect/workflow.sh
    ```
*   **Output**: `docs/ADR/ADR.md`

### 🔧 Customizing the Brains
Every plugin has a `prompts/` folder.
*   **To change behavior**: Edit `.aidev/plugins/<role>/prompts/writer.md`.
*   **Example**: If the Architect is too verbose, edit `prompts/writer.md` and add "Be concise."

### ⚠️ Prerequisite
Ensure you have the CLI tools installed and in your PATH:
*   `claude` (Claude Code)
*   `gemini` (Google Cloud CLI or similar wrapper)
*   `codex_wrapper` (Your internal alias for Codex)
