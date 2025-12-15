# CLI Agent Swarm Architecture

This document defines the **Agent Swarm** for the 16-layer `ai_dev_flow` framework, strictly using **CLI Agents** (`claude`, `gemini`, `codex`) as the workforce.

## Strategy: The "Adversarial Pair" Model
To minimize hallucinations and maximize quality, every layer uses an **Executor** (Writer) and a **Reviewer** (Critic). We alternate models to ensure diverse "thought processes."

*   **Gemini CLI**: Best for **High Context** (Reading entire repo, Drafting long docs).
*   **Claude Code**: Best for **Reasoning & Coding** (Complex logic, Refactoring, Safety).
*   **Codex**: Best for **Strict Syntax** (Code completion, Unit tests, Regex).

---

## Part 1: The Planning Swarm (Layers 1-6)
*Focus: Business Logic, Architecture, and Requirements*

| Layer | Artifact | Agent Role | Executor (The Writer) | Reviewer (The Critic) | Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **L1** | `BRD` | **Business Analyst** | **Gemini** | **Claude** | Gemini's 2M context is ideal for ingesting unstructured business notes. Claude is better at spotting logical gaps. |
| **L2** | `PRD` | **Product Manager** | **Claude** | **Gemini** | Claude excels at structured reasoning and defining strict features. Gemini checks against the original BRD context. |
| **L3** | `EARS` | **Requirements Eng** | **Gemini** | **Codex** | EARS syntax is repetitive; Gemini drafts quickly. Codex verifies strict syntax compliance. |
| **L4** | `BDD` | **QA Engineer** | **Claude** | **Codex** | Claude writes excellent Gherkin scenarios. Codex ensures they map to potential test steps. |
| **L5** | `ADR` | **Architect** | **Gemini** | **Claude** | Gemini absorbs the full context to propose options. Claude critiques the "Consequences" section heavily. |
| **L6** | `SYS` | **SysAdmin** | **Claude** | **Gemini** | Claude is security-conscious and good at defining constraints. |

---

## Part 2: The Detailed Design Swarm (Layers 7-12)
*Focus: Technical Specification and Task Breakdown*

| Layer | Artifact | Agent Role | Executor (The Writer) | Reviewer (The Critic) | Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **L7** | `REQ` | **Tech Analyst** | **Gemini** | **Claude** | "Atomic Requirements" need to be exhaustive. Gemini generates volume; Claude prunes. |
| **L8** | `IMPL` | **Project Manager** | **Gemini** | **Claude** | Planning timelines and resources (Volume task). |
| **L9** | `CTR` | **API Designer** | **Codex** | **Claude** | API Contracts (OpenAPI/Protobuf) require strict syntax. Codex is specialized here. |
| **L10** | `SPEC` | **Tech Lead** | **Claude** | **Gemini** | The `SPEC` is the "Technical Blueprint". Claude's reasoning is crucial here to prevent architectural bugs. |
| **L11** | `TASKS` | **Eng Manager** | **Claude** | **Gemini** | Breaking SPEC into step-by-step TODOs requires understanding dependencies. Claude is best at this logic. |
| **L12** | `IPLAN` | **Session Planner** | **Gemini** | **Claude** | Preparing the immediate context packet for the coder. |

---

## Part 3: The Execution Swarm (Layers 13-16)
*Focus: Code, Tests, and Validation*

| Layer | Artifact | Agent Role | Executor (The Writer) | Reviewer (The Critic) | Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **L13** | `Code` | **Senior Dev** | **Claude Code** | **Codex** | `claude` (Claude Code) is specifically designed for agentic coding loops. Codex reviews for linting/syntax. |
| **L14** | `Tests` | **Test Automation** | **Codex** | **Claude** | Writing unit tests is a pattern-matching task where Codex excels. Claude reviews for test coverage gaps. |
| **L15** | `Valid` | **Release Eng** | **Gemini** | **Claude** | "Read all logs and verifying against BRD". Gemini's large context window is mandatory here. |
| **L16** | `Maint` | **SRE** | **Claude** | **Gemini** | Debugging and fixing specific issues requires high reasoning concepts. |
