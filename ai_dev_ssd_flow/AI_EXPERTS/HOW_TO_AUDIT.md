# How to Run an Expert Audit Workflow

The AI Expert Board operates in two distinct phases. Follow this Standard Operating Procedure (SOP) to get the most out of your multi-persona board.

## Phase 1: Pre-Creation Ideation (The "Blind" Solutioning)

Use this phase *before* you write any formal technical documentation (BRD, PRD, ADR, etc.).

1.  **Define the Problem**: Write a clear, raw problem statement.
    *   *Example*: "We need to build a system that orchestrates 5 different AI agents using the Claude SDK to handle customer support tickets concurrently without hallucinating."
2.  **Initialize the Board**: Load your 7 project-specific personas into your AI environment.
3.  **Prompt the Board**: Present the problem statement and ask the board to debate the best architectural approach.
    *   *Tip*: In a chat interface, you can pass the problem statement and say: *"Act as the 7-persona Expert Board. Debate this problem. Provide a synthesized recommendation."*
4.  **Synthesize**: Take the board's recommendations, warnings, and proposed architecture, and use them to draft your formal project documentation.

## Phase 2: Automated Post-Creation Audit (The "Zero-Bias" Review)

Use this phase to audit completed documents (BRDs, PRDs, ADRs) using the framework automation scripting. This forces the document through a mandatory quality gate.

1.  **Prepare your Project Configuration**: Copy `project_experts.template.yaml` to `docs/AI_EXPERTS/project_experts.yaml`. Fill it out with your project's specific personas and anti-bias directives.
2.  **Run the Automation Script**: Use the unified persona review script provided by the framework to execute all 7 personas plus the synthesis Chairperson in parallel.
    ```bash
    bash /opt/data/docs_flow_framework/automation/pipelines/doc_review/run_review.sh path/to/PRD-50_octo_agent.md
    ```
    *   *Note on Context Injection*: If the `integration_expert` persona is defined, the script will automatically search for an `*INTEGRATION_MATRIX*.md` and inject its contents. If missing, it will dynamically scan the target document's current layer directory and append the metadata of sibling documents as fallback context.
3.  **Review the Output**: The script will automatically parse the parent document's metadata and generate an official `{DOCUMENT_ID}_PERSONA_REVIEW_REPORT.md` in the *exact same directory* as the target document.

## The Output Format: `PERSONA_REVIEW_REPORT.md`

Your aggregated audit report will formally adhere to the `EXPERTS` document template structure, utilizing the metadata layout required for framework gating. A document that fails this review cannot progress to the next SDD layer.

# Expert Board Audit Report: [Document Name]

> **Target Document**: [Document Name] (Version X.Y)
> **Audit Date**: YYYY-MM-DD
> **Board Configuration**: docs/AI_EXPERTS/project_experts.yaml

## 1. Executive Summary
*   **Consensus Recommendation**: (Proceed, Remediation Required, Fundamental Redesign)

## 2. Critical Findings & Edge Cases (The Devil's Advocate / Security)
*   **Race Condition Risk**: [Description of vulnerability]
*   **Unhandled Pathway**: [Description of missing logic flow]

## 3. Structural & Architectural Debts (The Architect / SRE)
*   **Scalability Bottleneck**: [Description of coupling or load issues]
*   **Observability Gap**: [Description of missing telemetry]

## 4. Business & Domain Impacts (The Strategist / System Specialist)
*   **Friction Points**: [Description of user/business friction]
*   **Domain-Specific Risks**: [e.g., Prompt drift in AI, Gas fees in Blockchain]

## 5. Alternative Solution (If Applicable)
*   [How the board would redesign the system if the current approach is deemed fatally flawed]
```
