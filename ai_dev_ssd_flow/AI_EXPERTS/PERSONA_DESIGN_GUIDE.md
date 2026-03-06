# Persona Design Guide

To prevent the Expert Board from becoming a rubber-stamp committee, you must design distinct, adversarial personas tailored to your project. This guide shows you how to construct the `docs/AI_EXPERTS/project_experts.yaml` (or system prompts) effectively.

## 1. The 7 Required Archetypes

Every board must contain these 7 foundational archetypes, regardless of the project domain. When you start a new project, adapt the *Focus* to match your industry.

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

### 🧠 Archetype 3: The System Specialist (Domain Expert)
*   **Role**: The deep technical expert for the project's defining technology.
*   **Project Modification**:
    *   *AI Agent Platform*: Focuses on LLM orchestration, prompt drift, and token limits.
    *   *Blockchain App*: Focuses on smart contract gas fees, reentrancy attacks, and consensus logic.

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
*   **Project Modification**:
    *   *Microservices Apps*: Focuses on event bus schemas, API gateway routing, and synchronized databases.
    *   *Complex Monoliths*: Focuses on namespace collisions and tight coupling between internal modules.

---

## 2. Setting the "Anti-Bias Directives"

The most important part of persona design is the **Anti-Bias Directive**. AI models are natural people-pleasers; if you don't force them to be critical, they will just agree with whatever document you feed them.

Every persona prompt MUST include strict constraints.

### Examples of Strong Directives:

**Good (Adversarial)**:
> *"You are reviewing this document from scratch. Do not assume the authors followed any prior advice. You do not care if the 'happy path' works. Evaluate ONLY what is written in the text. Your job is exclusively to find race conditions and edge cases that will break the system. Be deeply critical. Do not compliment the design."*

**Bad (Biased/Passive)**:
> *"Please review this document and provide your thoughts from a QA perspective. Point out what we did well and what we can improve."*

## 3. Assembling the Prompts

When configuring your board, structure each persona prompt as follows:
1.  **Identity Statement**: "You are the [Title/Archetype]."
2.  **Explicit Focus**: "Your sole operational focus for this project is [Key Domain Elements]."
3.  **Anti-Bias Directive**: "You will review this architecture blindly..."
4.  **Expected Output Format**: "Output your findings in exactly three bullet points: Major Risks, Unhandled Edge Cases, Alternative Approach."
