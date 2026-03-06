# AI Expert Board (Red Team Auditing)

## Overview
The **AI Expert Board** is an advanced QA and ideation methodology built into `docs_flow_framework/ai_dev_ssd_flow`. 

Instead of relying on a single AI context window (which is prone to bias, "yes-man" behavior, and hallucination), this framework utilizes a **Board of 6 Specialized AI Personas**. These personas act as an adversarial "Red Team" to audit your system designs, requirements, and business logic.

## Why 6 Personas?
A 6-persona board is an industry best practice for complex engineering reviews. It prevents "groupthink" by forcing the AI into highly constrained, sometimes adversarial viewpoints. For example, while the "Product Strategist" argues for speed-to-market, the "Security Auditor" argues for slower, deeply verified data flows. This tension produces a far superior final solution.

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
*   **Action**: The board debates the problem from 6 distinct angles.
*   **Output**: Identifying potential pitfalls, architecture recommendations, and edge-cases *before* any code or documentation is written.

### Phase 2: Post-Creation Audit (The "Zero-Bias" Review)
After you have drafted a document (BRD, PRD, BDD, ADR), the board is called in to audit the result.
*   **Crucial Constraint**: The board is instructed to evaluate the document from scratch, without bias, and to be deeply critical. They do not assume you followed their Phase 1 advice.
*   **Action**: Each of the 6 experts reviews the document independently.
*   **Output**: A structured audit report detailing Pros/Cons, Security Risks, Edge Cases, and alternative approaches if the solution is fundamentally flawed.

---

## 📚 Documentation Reference
Follow these guides to set up and run your board:

1. [How to Design Your Personas](PERSONA_DESIGN_GUIDE.md)
2. [How to Execute an Audit](HOW_TO_AUDIT.md)
3. [Example: Fintech Architecture Board](examples/fintech_board.md)
