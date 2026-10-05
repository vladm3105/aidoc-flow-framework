---
document_control:
  document_id: "SEED-<slug>"                     # e.g., SEED-auth-architecture
  version: "1.0"                                 # SemVer (must be near top for regex parse)
  status: Approved                               # Draft | Approved | Superseded
  author: "human: <architect/stakeholder> (+ ai-agent: <id>)"
  created_date: "YYYY-MM-DD"
  last_updated: "YYYY-MM-DD"
  framework_version: "0.74.0"
  supersedes: []                                 # e.g., ["seed/architecture/auth.md v1.0 (docs/sdd/09-CHG/archive/CHG-NN/seed/auth-v1.0.md)"]
  revision_history:
    - version: "1.0"
      date: "YYYY-MM-DD"
      author: "human: <name>"
      chg_ref: "None (initial seed)"             # or CHG-ID if created/superseded post-first-BRD
      description: "Initial foundational architecture and vision"
---

# SEED: <Title / Domain Name>

> **Seed Tier Contract ([`SEED_CONTRACT.md`](../governance/SEED_CONTRACT.md)):**  
> Seed documents reside at `<project>/seed/` (Tier 1 Inputs). They are **not** SDD chain artifacts, carry no element IDs, and are frozen per version once absorbed. Changed assumptions are superseded (`vN → vN+1`) via F3 Change Requests (Phase 0a `seed_scope`).

---

## 1. Intent & "True North" Vision
- **Problem Statement:** What fundamental user, business, or operational problem are we solving?
- **Desired Destination:** What does the end state look like once fully realized?
- **Core Value Proposition:** Who benefits and why is this solution compelling?

---

## 2. Environmental Realities & Constraints
- **Business Context:** Target markets, resource boundaries, critical timeline assumptions.
- **Technology & Infrastructure Baseline:** Existing platforms, external dependencies, system boundaries.
- **Regulatory, Compliance & Security Drivers:** Data residency, privacy constraints, compliance baselines.

---

## 3. Options Considered & Trade-Off Analysis
> *Note: Seed docs preserve the trade-off exploration. The formal choice is recorded downstream in the SDD ADR.*

### Option A: <Approach Name>
- **Description:** Summary of how this approach works.
- **Pros:** Key advantages and capabilities unlocked.
- **Cons & Risks:** Trade-offs, operational burdens, failure modes.

### Option B: <Approach Name> (Selected / Recommended)
- **Description:** Summary of how this approach works.
- **Pros:** Why this best satisfies the project requirements and constraints.
- **Cons & Risks:** Known trade-offs accepted.

---

## 4. Architectural Principles & Non-Negotiable Invariants
- **Guiding Principles:** Fundamental design rules (e.g., *vendor-neutral telemetry*, *offline-first sync*, *zero-trust perimeter*).
- **Invariants:** Core technical boundaries that downstream SDD layers (`BRD` through `SPEC`) must not violate without an explicit supersede.

---

## 5. Explicit Non-Goals & Out-of-Scope
- Explicitly state what this initiative will **not** attempt to solve, preventing downstream scope creep.

---

## 6. Seed Claims for SDD Absorption (Handoff to BRD)
State discrete, high-level assertions in natural language for the Business Analyst to map into the BRD [`seed_disposition:`](../layers/01_BRD/BRD-TEMPLATE.yaml) table.

> **CRITICAL RULE:** Do NOT assign synthetic or pseudo-element IDs (e.g., `[CLAIM-01]`, `SEED.01`) to seed assertions. Seed claims are natural-language assertions absorbed by quoting their text directly in the BRD ledger.

- "Every issued short code must be unique across the platform."
- "Visitors must be able to follow links without creating an account."
- "High-throughput telemetry ingestion must tolerate temporary cloud provider disconnections."
