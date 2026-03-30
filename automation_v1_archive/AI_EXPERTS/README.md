# AI Expert Board (Red Team Auditing)

> ## ⚠️ DEPRECATED
>
> **This directory is deprecated as of 2026-03-09.**
>
> Replaced by: `/opt/data/docs_flow_framework/ai_dev_ssd_flow/UCX/`
>
> - Personas → `UCX/skills/`
> - Review prompts → `UCX/review/UCR_PROMPT_*.md`
> - Documentation → `UCX/docs/`
>
> See `../DEPRECATED.md` for migration guide.

---

## Overview
The **AI Expert Board** is an advanced QA and ideation methodology built into `docs_flow_framework/ai_dev_ssd_flow`. 

Instead of relying on a single AI context window (which is prone to bias, "yes-man" behavior, and hallucination), this framework utilizes a **Board of 7 Specialized AI Personas**. These personas act as an adversarial "Red Team" to audit your system designs, requirements, and business logic.

## Why 7 Personas?
A 7-persona board is an industry best practice for complex engineering reviews. It prevents "groupthink" by forcing the AI into highly constrained, sometimes adversarial viewpoints. For example, while the "Product Strategist" argues for speed-to-market, the "Security Auditor" argues for slower, deeply verified data flows, and the "Integration Lead" ensures cross-module compatibility. This tension produces a far superior final solution.

## The Project-Specific Approach
There is no "one size fits all" expert board.
When you start a new project (e.g., a Fintech App vs. a Healthcare SaaS), you will **instantiate a project-specific board**. 

The personas must map specifically to your project's unique domain and risk profile.

*   *Fintech Example*: The auditor focuses on SOC2, PCI-DSS, and ledger immutability.
*   *Healthcare Example*: The auditor focuses on HIPAA, BAA agreements, and PHI encryption.

## Configuring the Experts LLM

Each expert persona (whether in a generation board `generate.*.yaml` or an audit board `review.*.yaml`) can be independently configured with its own LLM settings under the `agent:` block.

This allows you to mix and match models within the same board (e.g., using Claude for architectural drafting and GPT-4o via LiteLLM for strict framework judging).

### Model Diversity Requirements

The framework enforces model diversity at multiple levels to prevent self-evaluation bias and ensure rigorous cross-validation.

#### Rule 1: Judge ≠ Chairperson/Editor

**CRITICAL**: Judge and Chairperson/Editor roles **MUST** use different models.

| Role | Purpose | Model Constraint |
|------|---------|------------------|
| **Chairperson** | Assembles drafts, synthesizes findings | Must differ from Judge |
| **Editor** | Applies fixes from Judge critique | Same model as Chairperson (continuity) |
| **Judge** | Impartial framework compliance evaluation | Must differ from Chairperson/Editor |

**Valid Combinations**:
```
Chairperson: Claude    →  Judge: GPT-4o     ✓
Chairperson: Gemini    →  Judge: Claude     ✓
Chairperson: Claude    →  Judge: Claude     ✗ INVALID
```

#### Rule 2: Generate ≠ Review (Same Persona)

**CRITICAL**: The same persona **MUST** use different models in `generate.*.yaml` vs `review.*.yaml`.

| Persona | Generate Pipeline | Review Pipeline |
|---------|-------------------|-----------------|
| business_analyst | Claude | GPT-4o |
| product_owner | GPT-4o | Claude |
| architect | Claude | Gemini |
| tech_lead | Gemini | Claude |
| qa_lead | Claude | GPT-4o |
| operator | Claude | Gemini |

**Rationale**: Like code review — the reviewer should not be the author:
- A model reviewing its own generation patterns may miss systematic issues
- Cross-model review catches blind spots specific to each model family
- Different models have different analytical strengths

**Example**:
```yaml
# generate.brd.yaml
business_analyst:
  agent:
    cmd: "claude -p --model $P_MODEL --max-budget-usd 0.5"  # Claude generates
    model: "claude-sonnet-4-20250514"

# review.brd.yaml
business_analyst:
  agent:
    engine: "litellm"                   # GPT-4o reviews
    model: "gpt-4o"
```

**Engine Flexibility**: Both rules constrain **models**, not engines. A persona can use `cmd` in one pipeline and `engine: litellm` in another.

### Engine Configuration Options

Two execution engines are supported via `ai_exec.sh`. **All agents require an explicit `engine` key.**

| Engine | Required Keys | Use Case |
|--------|---------------|----------|
| **cmd** | `engine: "cmd"` + `cmd: "..."` | Direct CLI execution (Claude CLI, Codex, etc.) |
| **litellm** | `engine: "litellm"` + API params | OpenAI-compatible API via LiteLLM proxy |

### Example Configurations

**IMPORTANT**: Every agent block must include an explicit `engine` key. This standardization ensures consistent parsing by `ai_exec.sh`.

**1. CLI Command Mode (`engine: "cmd"`)**

Uses direct CLI execution with variable substitution. Variables `$P_MODEL`, `$P_MAX_TOKENS`, `$P_TEMP` are exported by `run_review.sh` before calling `ai_exec.sh`.

```yaml
  business_analyst:
    name: "The Business Analyst"
    agent:
      # CLI mode: explicit engine key + command string
      engine: "cmd"
      cmd: "claude -p --model $P_MODEL --max-budget-usd 0.5"
      model: "claude-sonnet-4-20250514"  # Exported as P_MODEL
      temperature: 0.3                    # Exported as P_TEMP
      max_tokens: 5000                    # Exported as P_MAX_TOKENS
    prompt: |-
      You are the Business Analyst...
```

**2. LiteLLM API Mode (`engine: "litellm"`)**

Uses OpenAI-compatible API calls via curl to a LiteLLM proxy server.

```yaml
  judge:
    name: "The Framework Judge"
    agent:
      # API mode: calls LiteLLM proxy endpoint
      engine: "litellm"
      model: "gpt-4o"
      temperature: 0.1
      max_tokens: 4000
      api_base: "http://0.0.0.0:4000/v1"  # LiteLLM proxy URL
      api_key_env: "LITELLM_MASTER_KEY"   # Env var name (not the actual key!)
    prompt: |-
      You are an impartial Judge...
```

**3. Mixed Board Example (Model Diversity)**

Demonstrates the required model separation between Chairperson and Judge:

```yaml
chairperson:
  name: "The Board Chairperson"
  agent:
    # Chairperson uses Claude via CLI - explicit engine key required
    engine: "cmd"
    cmd: "claude -p --model $P_MODEL --max-budget-usd 0.5"
    model: "claude-sonnet-4-20250514"
    max_tokens: 8000

judge:
  name: "The Framework Judge"
  agent:
    # Judge uses GPT-4o via API - DIFFERENT model for impartial evaluation
    engine: "litellm"
    model: "gpt-4o"
    temperature: 0.1
    max_tokens: 4000
    api_base: "http://0.0.0.0:4000/v1"
    api_key_env: "LITELLM_MASTER_KEY"
```

**Key Parameters**:

| Parameter | Engine | Required | Description |
|-----------|--------|----------|-------------|
| `engine` | both | **Yes** | `"cmd"` or `"litellm"` - determines execution method |
| `cmd` | cmd | Yes | Shell command with `$P_MODEL`, `$P_MAX_TOKENS` variables |
| `model` | both | Yes | Model identifier (exported as `P_MODEL` for cmd) |
| `temperature` | both | No | 0.1-0.5 for analysis, 0.5+ for ideation |
| `max_tokens` | both | No | Response length limit |
| `api_base` | litellm | Yes | LiteLLM/OpenAI-compatible endpoint URL |
| `api_key_env` | litellm | Yes | Environment variable name holding the API key |

**Security Note**: Never hardcode API keys in YAML. Use `api_key_env` to reference environment variables.

**Migration Note**: Legacy configurations without explicit `engine` key are still supported via fallback inference (presence of `cmd` implies `engine: "cmd"`), but new configurations should always include the explicit `engine` key.

## The Three-Phase Workflow

The Expert Board is deeply integrated into the SDD (Specification-Driven Development) lifecycle across three core phases:

### Phase 1: Pre-Creation Ideation (The "Blind" Solutioning)
Before you write your BRD or PRD, you bring the raw problem statement to the board.
*   **Input**: "We need a way to orchestrate 5 AI agents to handle customer KYC."
*   **Action**: The board debates the problem from 7 distinct angles.
*   **Output**: Identifying potential pitfalls, architecture recommendations, and edge-cases *before* any code or documentation is written.

### Phase 2: Multi-Agent Document Generation (`run_generate.sh`)
Instead of writing a document by hand, or using a single AI prompt, you can use the board to collaboratively author the document. 
*   **Input**: A raw topic definition (`--topic`) and optionally an upstream document (`--upstream`, e.g., a BRD when generating a PRD).
*   **Action**: 
    1. **Drafting**: Personas defined in `generate.<type>.yaml` draft specific sections based on their expertise (e.g. QA Lead writes Acceptance Criteria).
    2. **Assembler**: The Chairperson stitches the drafts into a V1 unified markdown document.
    3. **Judge**: A distinct, impartial LLM evaluates the V1 Draft strictly against the framework schema (e.g. Doc Control rules, Traceability format).
    4. **Final Editor**: The Chairperson applies the Judge's feedback to finalize the exact, compliant framework template.
*   **Output**: A fully generated, compliance-ready Markdown document adhering perfectly to the 18/21-section framework rules.

### Phase 3: Post-Creation Audit (`run_review.sh`)
After a document (BRD, PRD, BDD, ADR) has been manually drafted or significantly edited by humans, the board is called in to audit the result.

**5-Step Review Pipeline:**

```
Step 1: Persona Blind Audits
    ↓ (each expert reviews independently)
Step 2: Chairperson Synthesis
    ↓ (combines all findings into draft report)
Step 3: Judge Validation
    ↓ (verifies no findings lost/misrepresented)
Step 4: Editor Fixes (if REVISION_REQUIRED)
    ↓ (applies Judge's corrections)
Step 5: Final Report Assembly
```

| Role | Model Constraint | Purpose |
|------|------------------|---------|
| **Personas** | Any | Independent blind audits |
| **Chairperson** | Different from Judge | Synthesizes findings |
| **Judge** | Different from Chairperson | Validates synthesis accuracy |
| **Editor** | Same as Chairperson | Applies Judge's fixes |

*   **Crucial Constraint**: The board is instructed to evaluate the document from scratch, without bias, and to be deeply critical. They do not assume you followed their Phase 1 advice.
*   **Action**: Each of the 7 experts reviews the document independently using `review.<type>.yaml`.
*   **Judge Validation**: Ensures no P0/P1 findings were dropped, minimized, or mischaracterized in the synthesis.
*   **Output**: A structured audit report detailing Pros/Cons, Security Risks, Edge Cases, and alternative approaches if the solution is fundamentally flawed.

---

## 🔗 The Integration Lead: Addressing Cross-Document Conflicts

The 7th persona — **The Integration & Dependencies Lead** — is unique because it is the only expert that reviews the target document *against the rest of the project*, not just independently.

The automation script handles context injection automatically in two tiers:

| Scenario | Behavior |
|----------|----------|
| **Integration Matrix exists** (`*INTEGRATION_MATRIX*.md` found in `docs/`) | The full matrix is injected into the persona's prompt, giving cross-module event, API, and entity ownership data |
| **Matrix is missing** (early-stage project) | The script scans the **target document's sibling layer** (e.g., all other `*.md` files in `docs/01_BRD/`) and injects a list of their `doc_id` and headings as fallback context |

This means the Integration Lead is useful from **Day 1 of a project**, even before a formal matrix is written.

---

## 📚 Documentation Reference
Follow these guides to set up and run your board:

1. [How to Design Your Personas](PERSONA_DESIGN_GUIDE.md)
2. [How to Execute an Audit](HOW_TO_AUDIT.md)
3. [Example: Fintech Architecture Board](examples/fintech_board.md)

