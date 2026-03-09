# Persona Design Guide

To prevent the Expert Board from becoming a rubber-stamp committee, you must design distinct, adversarial personas tailored to your project. This guide shows you how to construct the `docs/AI_EXPERTS/review.yaml` (or system prompts) effectively.

## 1. The 8 Required Archetypes

Every board must contain these 8 foundational archetypes, regardless of the project domain. When you start a new project, adapt the *Prompt* strictly to match your industry.

### 🏛️ Archetype 1: The Architect (Integration & Scalability)
*   **Role**: Evaluates system boundaries, decoupling, state management, and scalability.
*   **Project Modification**: 
    *   *SaaS Web App*: Focuses on microservices, database sharding, and GraphQL vs REST.
    *   *Embedded Systems*: Focuses on memory constraints, RTOS task scheduling, and power management.

### ⚖️ Archetype 2: The Auditor (Compliance & Risk)
*   **Role**: Exclusively hunts for vulnerabilities, regulatory breaches, and data privacy risks.
*   **Project Modification**:
    *   *Fintech*: Focuses on PCI-DSS, SOC2, ledger immutability, and AML bounds.
    *   *Healthcare*: Focuses on HIPAA, PHI masking, and BAA compliance.

### 🧠 Archetype 3: The Tech Lead
*   **Role**: The deep technical expert for the project's defining technology.
*   **Project Modification**:
    *   *AI Agent Platform*: Focuses on LLM orchestration, prompt drift, and token limits.
    *   *Blockchain App*: Focuses on smart contract gas fees, reentrancy attacks, and consensus logic.

### 📈 Archetype 8: The Product Owner
*   **Role**: Evaluates the business value, user alignment, go-to-market speed, and ROI of the document.
*   **Project Modification**:
    *   *Startups*: Focuses entirely on shipping speed and cutting scope creep to ensure a faster MVP.
    *   *Enterprise*: Focuses on mapping technical deliverables directly back to stated OKRs and user pain points.

### 👔 Archetype 4: The Strategist (Value & Economics)
*   **Role**: Evaluates operational costs, cloud economics, time-to-market trade-offs, and user friction.
*   **Project Modification**: (Generally universally applicable, but tweak the cost focuses—e.g., AWS compute vs API ingestion costs).

### 🕵️ Archetype 5: The Devil's Advocate (Edge-Cases)
*   **Role**: Tries to break the system. Only looks at negative paths, race conditions, and unhandled errors.
*   **Project Modification**:
    *   *E-commerce*: Focuses on inventory race conditions during checkout and payment gateway timeouts.
    *   *IoT Data Pipeline*: Focuses on intermittent connectivity, packet loss, and sensor drift.

### 🔧 Archetype 6: The Operator (DevOps/SRE)
*   **Role**: Evaluates observability, deployment safety, rollback mechanisms, and SLI/SLOs.
*   **Project Modification**: Focuses on the specific CI/CD and hosting ecosystem (e.g., Kubernetes vs Serverless vs On-Prem).

### 🔗 Archetype 7: The Integration Lead (Dependencies & Contracts)
*   **Role**: Evaluates cross-module dependencies, event publishing, API consumption overlapping, and data entity ownership to prevent collisions.
*   **Dynamic Context Fallback**: By default, this persona expects a formal `INTEGRATION_MATRIX`. If one is not found, the automation script will dynamically scan the current document layer (e.g., all other PRDs in the folder) and inject their metadata directly into the persona's context to spot redundancies.
*   **Project Modification**:
    *   *Microservices Apps*: Focuses on event bus schemas, API gateway routing, and synchronized databases.
    *   *Complex Monoliths*: Focuses on namespace collisions and tight coupling between internal modules.

---

## 2. Setting the "Prompt" for Auditing (Phase 3)

When designing a persona for **Auditing** (`review.<type>.yaml`), the most important part is the explicit **Anti-Bias constraint**. AI models are natural people-pleasers; if you don't force them to be critical, they will just agree with whatever document you feed them.

Every auditing persona `prompt:` block MUST be adversarial.

### Examples of Strong Auditing Directives:

**Good (Adversarial)**:
> *"You are reviewing this document from scratch. Do not assume the authors followed any prior advice. Evaluate ONLY what is written in the text. Your job is exclusively to find race conditions and edge cases that will break the system. Be deeply critical. Do not compliment the design."*

**Bad (Biased/Passive)**:
> *"Please review this document and provide your thoughts from a QA perspective. Point out what we did well and what we can improve."*

## 3. Setting the "Prompt" for Generation (Phase 2)

When designing a persona for **Document Generation** (`generate.<type>.yaml`), the adversarial nature is swapped for strict **Boundary and Output Enforcement**. The prompt must map the persona's framework expertise directly into drafting specific sections, explicitly instructing them NOT to write the rest of the document.

### Examples of Strong Generation Directives:

**Good (Strict Drafting Boundaries)**:
> *"You are the Tech Lead generating a PRD. Your role is strictly to Draft Constraints & Assumptions, and Implementation Approach. Rely on the upstream BRD context. Output ONLY your drafted sections in markdown format."*

**Bad (Unbounded Drafting)**:
> *"You are a Tech Lead. Please write the PRD for this project based on the BRD provided."* (The AI will attempt to write the entire 21-section document poorly, overlapping with other experts).

## 4. Assembling the Prompts

When configuring your board, structure each persona prompt inside `review.yaml` as follows:
1.  **Identity/Focus Statement**: Set the immediate context.
2.  **Explicit Focus**: Detail exactly what domains to look for.
3.  **Anti-Bias Directive**: Include adversarial phrasing ("Be deeply skeptical... Do not sugarcoat").
4.  **Expected Output Format**: "Output your findings in EXACTLY three sections: Major Risks, Unhandled Edge Cases, Alternative Approach."
