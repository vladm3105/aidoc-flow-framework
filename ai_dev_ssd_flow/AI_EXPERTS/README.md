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

## The Two-Phase Workflow

The Expert Board is used at two critical junctures in the SDD (Specification-Driven Development) lifecycle:

### Phase 1: Pre-Creation Ideation (The "Blind" Solutioning)
Before you write your BRD or PRD, you bring the raw problem statement to the board.
*   **Input**: "We need a way to orchestrate 5 AI agents to handle customer KYC."
*   **Action**: The board debates the problem from 7 distinct angles.
*   **Output**: Identifying potential pitfalls, architecture recommendations, and edge-cases *before* any code or documentation is written.

### Phase 2: Post-Creation Audit (The "Zero-Bias" Review)
After you have drafted a document (BRD, PRD, BDD, ADR), the board is called in to audit the result.
*   **Crucial Constraint**: The board is instructed to evaluate the document from scratch, without bias, and to be deeply critical. They do not assume you followed their Phase 1 advice.
*   **Action**: Each of the 7 experts reviews the document independently.
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
