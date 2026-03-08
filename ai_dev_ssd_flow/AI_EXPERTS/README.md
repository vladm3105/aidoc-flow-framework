# AI Expert Board (Red Team Auditing)

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

Each expert persona (whether in a generation board `generate.*.yaml` or an audit board `project_experts.*.yaml`) can be independently configured with its own LLM settings under the `agent:` block.

This allows you to mix and match models within the same board (e.g., using Claude for architectural drafting and GPT-4o via LiteLLM for strict framework judging).

### Example Configurations

You can define agents using direct engine integrations (like Claude or LiteLLM), or by overriding the execution completely with a custom shell command (`cmd`).

**1. Standard API Engine (Claude)**
```yaml
  qa_lead:
    name: "The QA Lead"
    skill_file: "qa_lead.md"
    agent:
      engine: "claude"            # The runner/adapter to use (claude, litellm, openai-api, gemini, ollama)
      model: "claude-3-7-sonnet"  # The specific model name
      temperature: 0.2            # Lower for stricter analysis, higher for ideation
      max_tokens: 3000
    prompt: |-
      You are the QA Lead...
```

**2. LiteLLM Proxy Engine**
```yaml
  judge:
    name: "The Framework Judge"
    agent:
      engine: "litellm"           # Maps to the openai-api curl adapter in ai_exec.sh
      model: "gpt-4o"
      temperature: 0.1
      max_tokens: 4000
      api_base: "http://0.0.0.0:4000/v1" # Your proxy URL
      api_key_env: "LITELLM_MASTER_KEY"  # The env var holding your key
    prompt: |-
      You are an impartial Judge...
```

**3. Custom Command Override**
```yaml
  auditor:
    name: "The Security Auditor"
    agent:
      cmd: "opencode --model sonnet-3.5" # Bypasses engine parsing; ai_exec.sh will directly run this CLI command and append the prompt file.
    prompt: |-
      You are the Security Auditor...
```

**Key Parameters**:
*   `engine`: Dictates which execution path `ai_exec.sh` will take.
*   `model`: The model identifier passed to the CLI/API.
*   `temperature`: Adjusts creativity vs. deterministic output.
*   `max_tokens`: Safety limit for response length.
*   `api_base`: (Optional) Custom endpoint URL for proxy servers like LiteLLM/Ollama.
*   `api_key_env`: (Optional) The name of the environment variable (e.g. `LITELLM_MASTER_KEY`) mapped in your `.env` file that holds the secret. Do **not** hardcode actual keys in the YAML!
*   `cmd`: If provided, ignores the other parameters and executes this raw bash command instead.

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
*   **Crucial Constraint**: The board is instructed to evaluate the document from scratch, without bias, and to be deeply critical. They do not assume you followed their Phase 1 advice.
*   **Action**: Each of the 7 experts reviews the document independently using `project_experts.<type>.yaml`.
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

