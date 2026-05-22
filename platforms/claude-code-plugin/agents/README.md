# AI Team — Specialist Agent Roster

**Specialist Claude Code subagents for the AI Doc Flow Framework's Specification-Driven Development (SDD) flow.**

This directory defines a team of nine specialist Claude Code subagents that mirror the SDD lifecycle. They are the **Claude Code plugin's** native team: each agent owns a function and orchestrates the relevant plugin `doc-*` skills. Agents auto-register via Claude Code's `agents/` directory convention.

> This framework is "one specification, two platforms." This roster is the Claude Code plugin's native team, driving the lifecycle through the plugin's `doc-*` skills. The framework's separate MCP-server platform implements the same spec independently; both satisfy the same conformance suite.

---

## Why a Team (Design Rationale)

The roster is shaped by 2026 multi-agent success-story data (sources below). The recurring lessons:

1. **Role specialization beats one mega-agent.** Agents act as digital team members, each with a defined role, shared context, and a common review layer.
2. **The biggest delivery gains come from compressing downstream work** — testing, review, and traceability — not from code generation. The roles marked downstream-heavy (★) are built out in the most depth for this reason.
3. **Humans steer, agents execute.** Approval authority stays with a human reviewer or an independent LLM-as-judge at every gate, matching the project's `ai:ready → ai:in-progress → ai:review-requested` governance flow.
4. **Cover the whole pipeline.** Measured gains (cycle time, error reduction) come from spanning requirements → architecture → test → code → review → deploy, not from optimizing a single stage.

---

## Design Principles

### Native plugin engine

Every agent drives document-lifecycle work through the plugin's native skills — the `doc-flow` orchestrator plus the `doc-*` autopilot/audit/fixer skill families. **Never mix engines within a single artifact.**

The `pm-orchestrator` is the PM seat the team plugs into — it sequences the lifecycle and delegates to the specialists.

### Read-only quality gates

`code-reviewer`, `security-engineer`, and `traceability-auditor` are **read-only**. They report findings and a verdict but never edit, write, or commit. This preserves independent review (a reviewer that fixes its own findings cannot be trusted as a gate). The `software-engineer` applies the fixes, then re-requests review.

### Model tiers

Models are assigned to balance capability against cost:

- **opus** — deep-reasoning roles: architecture, code review, security, orchestration.
- **sonnet** — execution and authoring: test design, implementation, devops.
- **haiku** — mechanical, high-frequency work: the traceability gate.

---

## Org Structure

```
                    ┌──────────────────────────────┐
                    │  PM / Orchestrator            │  planning, roadmap,
                    │  (plans + delegates)          │  issue governance
                    └───────────────┬──────────────┘
        ┌───────────────────────────┼───────────────────────────┐
   SPEC LANE (authors)        EXECUTION LANE             QUALITY GATES (read-only)
   ┌────────────────────┐    ┌────────────────────┐     ┌──────────────────────────┐
   │ requirements-analyst│    │ software-engineer  │     │ code-reviewer        ★   │
   │ solutions-architect │ ─▶ │ devops-release-eng │  ─▶ │ security-engineer        │
   │ test-architect    ★ │    └────────────────────┘     │ traceability-auditor ★   │
   └────────────────────┘                                └──────────────────────────┘
                                ★ = downstream-heavy (built out in most depth)
```

**Flow:** PM plans → Spec lane authors BRD→SPEC/TDD (integrity-checked by the Traceability Auditor) → Execution lane implements from approved IPLAN → Quality Gates review every change before merge → DevOps deploys and feeds evidence/incidents back to the PM.

### SDD lifecycle mapping (v3, 8 layers)

```
BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code
└── requirements-analyst ──┘   └── solutions-architect ──┘  └ test-arch ┘ └ software-engineer ┘
```

> The canonical layer model is the 8 layers above (see `framework/layers/`). The plugin also ships per-test-type authoring skills (`doc-utest/itest/stest/ftest/ptest/sectest`) and SPEC-subtype skills (`doc-cspec/dspec/uxspec/riskspec/procspec`) as helpers under the SPEC and TDD layers; these are pending PLM-B5 reconciliation.

---

## The Roster

| Agent | Lane | Model | Access | Delegation |
|-------|------|-------|--------|-----------|
| `pm-orchestrator` | Orchestration | opus | full + `Task` | spawns all 8 |
| `requirements-analyst` | Spec | inherit | author | — |
| `solutions-architect` | Spec | opus | author | — |
| `test-architect` ★ | Spec | sonnet | author | — |
| `software-engineer` | Execution | sonnet | full | — |
| `devops-release-engineer` | Execution | sonnet | full | — |
| `code-reviewer` ★ | Quality gate | opus | read-only | — |
| `security-engineer` | Quality gate | opus | read-only | — |
| `traceability-auditor` ★ | Quality gate | haiku | read-only | — |

---

## Agent Details

### `pm-orchestrator` — PM / Orchestrator
- **Purpose:** Plan, sequence, and orchestrate the whole team across the SDD lifecycle; own planning-first governance and GitHub issue/label governance.
- **Drives** the lifecycle through the native `doc-flow` orchestrator plus the `doc-*` skill families.
- **Delegates to** all eight specialists via the `Task` tool, giving each a self-contained brief; runs independent work in parallel and sequences dependent work; never lets an author gate its own work.
- **Governance:** Enforces *analyze → roadmap → planning index → changelog plan → gap review → IPLAN → approval → implementation*. Approval authority is a human reviewer or independent LLM-as-judge — never self-approval. Only `ai:ready` issues are eligible for autonomous execution.
- **Skills:** `workflow-optimizer`, `project-init`, `adr-roadmap`.
- **Model:** opus.

### `requirements-analyst` — Requirements Analyst
- **Purpose:** Decompose, analyze, and validate requirements across the SDD workflow; traceability and coverage analysis (not code).
- **Owns:** BRD → PRD → EARS. Formal requirements with SMART criteria, cumulative upstream tags, and SPEC-Ready scoring.
- **Skills:** `doc-brd/prd/ears-*` families.
- **Handoff:** validated PRD/EARS → Solutions Architect.
- **Model:** inherit.

### `solutions-architect` — Solutions Architect
- **Purpose:** Design system architecture and author the decision/component layers; C4 + DFD modeling in Mermaid.
- **Owns:** BDD, ADR, SPEC. Captures every significant decision as an ADR (Context → Decision → Consequences) and produces interface-complete SPECs (interfaces and data contracts live in the SPEC).
- **Skills:** `doc-bdd/adr/spec-*`, `charts-flow`, `mermaid-gen`, `adr-roadmap`.
- **Handoff:** SPEC-Ready architecture → Test Architect + Software Engineer.
- **Model:** opus.

### `test-architect` — Test Architect (QA Lead) ★
- **Purpose:** Design the test strategy and author every test specification layer; own coverage targets and readiness scoring.
- **Owns:** TDD guide (Layer 7) + per-test-type authoring skills — UTEST (unit), ITEST (integration), STEST (smoke), FTEST (functional), PTEST (performance), SECTEST (security, co-owned with Security Engineer).
- **Discipline:** chooses the right test type per obligation (avoids redundant coverage), maps every case to a requirement/scenario, enforces threshold rules, flags untested requirements.
- **Skills:** `doc-tdd/utest/itest/stest/ftest/ptest/sectest-*`, `test-automation`, `contract-tester`.
- **Handoff:** test design + coverage matrix → Software Engineer + Code Reviewer.
- **Model:** sonnet.

### `software-engineer` — Software Engineer
- **Purpose:** Implement source code and tests from an approved IPLAN.
- **Planning-first rule:** implements only `ai:ready` scope with an approved IPLAN; routes unplanned work back to PM + Architect rather than free-styling architecture.
- **Owns:** the execution lane — small verifiable increments, runs the suite, opens PRs with traceability tags, test evidence, and risk flags; applies fixes from the read-only gates.
- **Skills:** `doc-iplan*`, `doc-flow`, `test-automation`, `contract-tester`.
- **Model:** sonnet.

### `devops-release-engineer` — DevOps / Release Engineer
- **Purpose:** CI/CD, build/test pipelines, deployment governance, and release readiness.
- **Owns:** the path from merged code to verified production release — staging→prod gates, smoke (STEST) validation, observability loop, tested rollback paths, post-deploy evidence.
- **Risk posture:** confirms shared/irreversible actions (prod deploys, tag/secret changes, force ops) with the human approver unless pre-authorized; never skips hooks/signing.
- **Skills:** native (Bash, pipeline config); coordinates STEST with the Test Architect; uses `framework/governance/` CI/CD scripts.
- **Model:** sonnet.

### `code-reviewer` — Code Reviewer ★ (read-only)
- **Purpose:** Review PRs/code for correctness, acceptance-criteria conformance, spec/test alignment, standards, and security hygiene.
- **Read-only gate:** reports findings and a verdict (Approve / Approve-with-nits / Request-changes / Block); never edits. Findings carry severity (P0–P3) and `file:line`.
- **Verifies:** acceptance criteria explicitly (met/unmet/unverifiable) and coverage against the Test Architect's bar.
- **Skills:** `doc-review`, `contract-tester`; `trace-check`/`doc-validator` for conformance.
- **Model:** opus.

### `security-engineer` — Security Engineer (read-only)
- **Purpose:** Threat modeling, security review of code and specs, and authoring/validating SECTEST. Defensive/authorized scope only.
- **Read-only gate:** enumerates threats (STRIDE-style across trust boundaries/DFDs), maps each to a required control, verifies a SECTEST case exists per control, flags untested controls; reports remediation direction without editing.
- **Skills:** `security-audit`, `doc-sectest*` (co-owned with Test Architect), `doc-riskspec*`.
- **Model:** opus.

### `traceability-auditor` — Traceability & Quality Auditor ★ (read-only)
- **Purpose:** Verify cross-layer traceability and project-wide document integrity; a mechanical, high-frequency gate.
- **Read-only gate:** runs the validation tooling and reports gaps, broken links, ID/naming violations, and orphaned artifacts; routes fixes to the owning author agent or the relevant `doc-*-fixer` skill.
- **Audits:** cumulative upstream tags, link/anchor resolution, ID and threshold naming, coverage/orphans, readiness scores.
- **Skills:** `trace-check`, `doc-validator`, `doc-naming`, `quality-advisor`, per-type `*-validator` skills.
- **Model:** haiku.

---

## Closed-Loop Operating Model

1. **Plan & approve** — PM drives BRD→IPLAN through the native skills; human/LLM-judge approves.
2. **Delegate** — approved `ai:ready` scope goes to the execution lane (Software Engineer, DevOps).
3. **Gate** — every change passes the read-only gates (Code Reviewer, Security, Traceability) before merge.
4. **Deploy & observe** — DevOps promotes through staging→prod gates with smoke tests and monitoring.
5. **Verify & close** — PM verifies post-deploy evidence; issues close only when acceptance criteria and monitoring pass.

---

## Sources

Research informing the team design (2026):

- [The State of AI Coding Agents (2026): From Pair Programming to Autonomous AI Teams](https://medium.com/@dave-patten/the-state-of-ai-coding-agents-2026-from-pair-programming-to-autonomous-ai-teams-b11f2b39232a)
- [Agentic Engineering: How Swarms of AI Agents Are Redefining Software Engineering — LangChain](https://www.langchain.com/blog/agentic-engineering-redefining-software-engineering)
- [The AI revolution in software development — McKinsey](https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/the-ai-revolution-in-software-development)
- [ChatCollab: Exploring Collaboration Between Humans and AI Agents in Software Teams — arXiv](https://arxiv.org/pdf/2412.01992)
- [AgentMesh: A Cooperative Multi-Agent Generative AI Framework for Software Development Automation — arXiv](https://arxiv.org/pdf/2507.19902)
- [The Orchestration of Multi-Agent Systems: Architectures, Protocols, and Enterprise Adoption — arXiv](https://arxiv.org/html/2601.13671v1)
- [Multi-Agent Systems & AI Orchestration Guide 2026 — Codebridge](https://www.codebridge.tech/articles/mastering-multi-agent-orchestration-coordination-is-the-new-scale-frontier)
- [The Enterprise AI Playbook: Lessons from 51 Successful Deployments — Stanford Digital Economy Lab](https://digitaleconomy.stanford.edu/app/uploads/2026/03/EnterpriseAIPlaybook_PereiraGraylinBrynjolfsson.pdf)

Project architecture references:

- [aidoc-flow-framework — engine-agnostic spec + two platforms](https://github.com/vladm3105/aidoc-flow-framework)
- [aidoc-flow-framework/platforms — the two platform implementations](https://github.com/vladm3105/aidoc-flow-framework/tree/main/platforms)
