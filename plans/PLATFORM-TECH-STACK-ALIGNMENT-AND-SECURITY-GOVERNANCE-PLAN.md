# Plan: Platform Technology Stack Alignment, Security Invariants, and Missing Tools Governance (CHG-124)

## Executive Summary

This plan implements **CHG-124** to strictly bind the entire Specification-Driven Development (SDD) framework, working agreements, governance documents, skills, and templates to the **Authoritative Platform Technology Stack** codified at `/home/ya/devd/technology_stack` (and upstream `vladm3105/technology-stack` specifications 00–23).

It establishes three immutable, non-negotiable operational invariants across the ecosystem:

1. **Platform Technology Stack Adherence**: All AI agents, architectural designs, runtime components, libraries, schemas, and tools must strictly conform to the approved platform technology stack defined in `/home/ya/devd/technology_stack`.
2. **Strict Prohibition of Insecure Options**: AI agents must NEVER offer, suggest, recommend, or use insecure options, weakened security postures, relaxed container sandboxing, disabled linters/verification, plain-text secret workarounds, or unsafe shortcuts under any circumstances.
3. **Missing Tools Operator Escalation Protocol**: If any tool, runtime, software, or library required for a task or implementation is missing from the approved technology stack, the AI agent MUST NOT invent tools or pick arbitrary unapproved external packages: the agent MUST explicitly inform the human operator and request instructions on what tools or software to use. In autonomous sessions, always file a GitHub issue on the repository detailing the missing tool requirement.
4. **Conflict Disposition**: For anything needing real deployment, infrastructure changes, container runtime provisioning, or technology selection work, file GitHub issues on the repository.

---

## 1. Scope & Impacted Surfaces

### Component 1: AGENTS.md & Working Agreements

- **`AGENTS.md`**: Enhance `## Non-negotiables` to mandate platform standards based on `/home/ya/devd/technology_stack`, prohibit insecure options, codify the Missing Tools Operator Escalation Protocol (with autonomous session issue filing), and declare conflict disposition.
- **`framework/templates/AGENTS-TEMPLATE.md`**: Update `## Non-negotiables` to mirror these binding invariants for all consumer repositories.

### Component 2: Governance Documents Modernization

- **`framework/governance/RECOMMENDED_PLATFORM_STACK.md`**:
  - Update authority and citations to include specifications 00 through 23 of `/home/ya/devd/technology_stack`.
  - Update Secret Management from legacy Infisical to Two-Tier Secrets (Tier 1 OCI Vault + Tier 2 OpenBao) per `06` and `09`.
  - Update Object Storage from legacy MinIO to Hybrid S3 (SeaweedFS on-prem/dev + Cloudflare R2 / OCI Object Storage) per `09` and `22`.
  - Update Federated Graph Lake to Embedded Kùzu (edge) + Central GraphDB (Memgraph / Apache AGE / Neo4j) per `23`.
  - Codify the Missing Tools Operator Escalation Protocol and Insecure Options Prohibition into the platform tenets.
- **`framework/governance/TECHNOLOGY_STACK_USAGE_GUIDE.md`**:
  - Mandate that all technology candidates in Layer 05 ADR, SPEC, IPLAN, and Code must resolve against `/home/ya/devd/technology_stack`.
  - Codify Section 4.1 "Missing Tools & Operator Escalation Protocol", Section 4.2 "Prohibition of Insecure Options", and Section 4.3 "Conflict Disposition".
- **`framework/AI_ASSISTANT_RULES.md`**:
  - Add section "Platform Technology Stack Compliance & Insecure Options Prohibition" including autonomous session issue filing and conflict disposition.
- **`framework/governance/DOC_GOVERNANCE_CORE.md`**:
  - Add governance gate enforcement for tech stack compliance, missing tools escalation, and conflict disposition.
- **`framework/governance/aidoc/AIDOC-GVISOR-SANDBOX-EXECUTION-PROFILE.md` & `framework/governance/aidoc/README.md`**:
  - Modernize secret injection and runtime profiles to Two-Tier Secrets (OCI Vault + OpenBao) under gVisor isolation.

### Component 3: Skills Alignment

- **`approval-gate`** (`.agents/skills/approval-gate/SKILL.md` & `framework/skills/approval-gate/SKILL.md`):
  - Mark any tool introduction outside `/home/ya/devd/technology_stack` as a hard block requiring operator approval; forbid approving or offering insecure options; codify missing tools escalation and conflict disposition.
- **`verified-planning`** (`.agents/skills/verified-planning/SKILL.md` & `framework/skills/verified-planning/SKILL.md`):
  - Add Section on Tech Stack Verification: plans must verify all tools against `/home/ya/devd/technology_stack`, reject insecure options, explicitly escalate missing tools to the operator (filing issues in autonomous sessions), and declare conflict disposition.
- **`preprod-review`** (`.agents/skills/preprod-review/SKILL.md` & `framework/skills/preprod-review/SKILL.md`):
  - Add tech stack compliance and security posture checks to the review lenses (`lens-briefs.md`).
- **`start-session`** (`.agents/skills/start-session/SKILL.md` & `framework/skills/start-session/SKILL.md`):
  - Add tech stack grounding check at session startup.
- **`aidoc-triage`** (`.agents/skills/aidoc-triage/SKILL.md`):
  - Align issue review against platform technology stack and security standards.

### Component 4: Templates Alignment Audit

- **`framework/templates/STACK-POLICY-TEMPLATE.yaml`**:
  - Update runtime versions (Python 3.15 default via `uv`, Rust stable, Go 1.25, Node 24 LTS) and embed missing tools escalation instructions.
- **`framework/templates/MODULE-TEMPLATE.md`**:
  - Remove obsolete/unapproved candidate examples (CockroachDB) and ground examples in approved stack (PostgreSQL 18, Valkey 8 / Redis 7.2, NATS JetStream, Temporal).
- **`framework/layers/05_ADR/ADR-00_index.TEMPLATE.yaml`**:
  - Update example package URL from `postgres:16.3-alpine` to `postgres:18-alpine`.
- **`framework/layers/05_ADR/ADR-TEMPLATE.yaml`**:
  - Update technology selection guidance and add Missing Tools Protocol.
- **`framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`**:
  - Reinforce driver bindings against `/home/ya/devd/technology_stack` and add Missing Tools Protocol.
- **`framework/layers/07_TDD/TDD-TEMPLATE.yaml`**:
  - Reinforce testcontainer images matching `/home/ya/devd/technology_stack` (PostgreSQL 18, NATS JetStream).
- **`framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml`**:
  - Add execution command guard checking tools against approved stack and prohibiting insecure flags (`--insecure`, `--privileged`, `--no-verify`).

### Component 5: Conformance Testing & Spec Bump Protocol

- Add conformance tests in `tests/conformance/test_governance.py` verifying that governance documents, skills, and templates enforce the approved platform technology stack and prohibit insecure options.
- Bump `framework/VERSION` from `0.96.10` to `0.96.11`.
- Append `0.96.10` to `OLD_VERSIONS` in `hooks/sync-version-refs.sh`.
- Run `bash hooks/sync-version-refs.sh`.
- Verify with `python3 tests/chg/spec_gate.py --base origin/dev`.

---

## 2. Claim ledger

| # | Claim | Symbol | Citation |
|---|---|---|---|
| 1 | AGENTS.md non-negotiable rule on platform standards | `Follow platform standards; do not offer or use insecure options.` | AGENTS.md:81 |
| 2 | AGENTS-TEMPLATE.md non-negotiables | `## Non-negotiables` | framework/templates/AGENTS-TEMPLATE.md:34 |
| 3 | Authoritative Tech Stack Master Matrix | `Authoritative Platform Technology Stack` | /home/ya/devd/technology_stack/09-authoritative-platform-technology-stack.md:1 |
| 4 | Two-Tier Secrets in Tech Stack | `Two-Tier Secrets (OCI Vault + OpenBao)` | /home/ya/devd/technology_stack/09-authoritative-platform-technology-stack.md:64 |
| 5 | Single node dev/stage servers in Tech Stack | `Avoiding "High-Availability Theater" on dev and stage` | /home/ya/devd/technology_stack/06-security-rbac.md:8 |
| 6 | Hybrid S3 Storage Specification | `Hybrid S3 Object Storage` | /home/ya/devd/technology_stack/22-hybrid-s3-object-storage-seaweedfs-and-cloudflare-r2.md:1 |
| 7 | Federated Graph Lake Specification | `Federated Graph Architecture` | /home/ya/devd/technology_stack/23-federated-graph-lake-embedded-kuzu-and-central-graphdb.md:1 |
| 8 | RECOMMENDED_PLATFORM_STACK.md Authority | `[vladm3105/technology-stack]` | framework/governance/RECOMMENDED_PLATFORM_STACK.md:13 |
| 9 | RECOMMENDED_PLATFORM_STACK.md Secret Management entry | `Two-Tier Secrets (Tier 1 OCI Vault + Tier 2 OpenBao)` | framework/governance/RECOMMENDED_PLATFORM_STACK.md:81 |
| 10 | RECOMMENDED_PLATFORM_STACK.md Object Storage entry | `Hybrid S3 (SeaweedFS + Cloudflare R2 / OCI Object Storage)` | framework/governance/RECOMMENDED_PLATFORM_STACK.md:95 |
| 11 | TECHNOLOGY_STACK_USAGE_GUIDE.md Progressive Refinement | `PROGRESSIVE REFINEMENT FUNNEL` | framework/governance/TECHNOLOGY_STACK_USAGE_GUIDE.md:37 |
| 12 | STACK-POLICY-TEMPLATE.yaml runtime version | `version_or_edition: "3.15"` | framework/templates/STACK-POLICY-TEMPLATE.yaml:18 |
| 13 | MODULE-TEMPLATE.md datastore example | `PrimaryDB[("Primary Datastore<br/>(e.g., PostgreSQL 18)")]` | framework/templates/MODULE-TEMPLATE.md:66 |
| 14 | ADR-00_index.TEMPLATE.yaml postgres example | `postgres@18-alpine` | framework/layers/05_ADR/ADR-00_index.TEMPLATE.yaml:75 |
| 15 | SPEC-TEMPLATE.yaml platform stack alignment | `platform_stack_alignment:` | framework/layers/06_SPEC/SPEC-TEMPLATE.yaml:224 |
| 16 | TDD-TEMPLATE.yaml testcontainer dependencies | `dependencies: "Ephemeral containerized database instances matching production engine"` | framework/layers/07_TDD/TDD-TEMPLATE.yaml:163 |
| 17 | Verified planning skill rules | `## 1. Draft with a Claim ledger` | .agents/skills/verified-planning/SKILL.md:27 |
| 18 | Approval gate skill tiers | `## Tiers` | .agents/skills/approval-gate/SKILL.md:19 |
| 19 | Live framework spec version | `0.96.11` | framework/VERSION:1 |
| 20 | sync-version-refs.sh sweep list | `OLD_VERSIONS` | hooks/sync-version-refs.sh:128 |

---

## 3. Review log

### Pass 1: Initial Drafting Review

- **Cycle Date**: 2026-10-19
- **Gaps found**:
  1. The initial idea only mentioned updating `AGENTS.md`, but the user request explicitly spans `AGENTS.md`, governance docs, skills, and templates.
  2. Legacy references to `Infisical` and `MinIO` remained in `RECOMMENDED_PLATFORM_STACK.md` and `AIDOC-GVISOR-SANDBOX-EXECUTION-PROFILE.md` despite `/home/ya/devd/technology_stack` standardizing on Two-Tier Secrets (OCI Vault + OpenBao) and Hybrid S3 (SeaweedFS + Cloudflare R2 / OCI Object Storage).
  3. `MODULE-TEMPLATE.md` still carried obsolete example `CockroachDB`.
  4. `ADR-00_index.TEMPLATE.yaml` still carried legacy `postgres:16.3-alpine` instead of `postgres:18-alpine`.
  5. The Missing Tools Operator Escalation Protocol needed explicit behavioral definition across skills (`verified-planning`, `approval-gate`) so agents never assume or guess tools outside the approved stack.
- **Resolution**:
  - Expanded scope to 5 comprehensive components covering all requested surfaces.
  - Aligned all secret and storage references with specifications 00–23 of `/home/ya/devd/technology_stack`.
  - Added explicit Missing Tools Protocol text to `AGENTS.md`, `AGENTS-TEMPLATE.md`, `TECHNOLOGY_STACK_USAGE_GUIDE.md`, `AI_ASSISTANT_RULES.md`, and skills.
  - Added conformance tests enforcing that governance docs and templates disallow insecure options and mandate the approved tech stack.

### Pass 2: Adversarial Independent Audit

- **Cycle Date**: 2026-10-19
- **Review Lens**: Evaluated against live tree and `/home/ya/devd/technology_stack`.
- **Gaps found**:
  1. `framework/skills/` mirrors `.agents/skills/` for all repo skills; both locations must be kept synchronized.
  2. Spec change gate `GATE-SPEC-E005` will require bumping `framework/VERSION` to `0.96.11` and running `hooks/sync-version-refs.sh`.
  3. In `framework/governance/workflows/stack-policy-validation.sw.yaml`, verify that the state machine evaluates stack policy constraints cleanly without regressions.
  4. Missing-tools protocol must explicitly instruct: in autonomous sessions, always file a GitHub issue on the repository detailing the missing tool requirement.
  5. Conflict disposition must explicitly instruct: file GitHub issues for anything needing real deployment, infrastructure changes, or technology selection work.
- **Resolution**:
  - Ensured both `.agents/skills/` and `framework/skills/` are updated in lockstep.
  - Added Component 5 explicitly executing the normative spec change bump protocol.
  - Verified `stack-policy-validation.sw.yaml` compatibility.
  - Folded autonomous session issue filing and conflict disposition into `AGENTS.md`, `AGENTS-TEMPLATE.md`, governance docs, and skills.

---

## 4. Implementation Steps (IPLAN-124 Execution)

1. **Step 1: Worktree Setup**
   - Create worktree at `/home/ya/devd/aidoc-framework-chg-124` on branch `feature/chg-124-tech-stack-security`.
   - Archive original pre-modification files into `framework/archive/CHG-124/`.
   - Author `CHG-124.yaml` and `IPLAN-124.yaml` and validate with `python3 sdd_doc_lint/chg_lint.py`.

2. **Step 2: Component 1 (AGENTS.md & AGENTS-TEMPLATE.md)**
   - Update `AGENTS.md` and `framework/templates/AGENTS-TEMPLATE.md` with the platform tech stack mandate, insecure options ban, missing tools operator escalation protocol (with autonomous session issue filing), and conflict disposition.

3. **Step 3: Component 2 (Governance Documents)**
   - Update `RECOMMENDED_PLATFORM_STACK.md`, `TECHNOLOGY_STACK_USAGE_GUIDE.md`, `AI_ASSISTANT_RULES.md`, `DOC_GOVERNANCE_CORE.md`, `AIDOC-GVISOR-SANDBOX-EXECUTION-PROFILE.md`, and `aidoc/README.md`.

4. **Step 4: Component 3 (Skills)**
   - Update `.agents/skills/` and `framework/skills/` for `approval-gate`, `verified-planning`, `preprod-review`, `start-session`, and `aidoc-triage`.

5. **Step 5: Component 4 (Templates Audit & Fixes)**
   - Update `STACK-POLICY-TEMPLATE.yaml`, `MODULE-TEMPLATE.md`, `ADR-00_index.TEMPLATE.yaml`, `ADR-TEMPLATE.yaml`, `SPEC-TEMPLATE.yaml`, `TDD-TEMPLATE.yaml`, and `IPLAN-TEMPLATE.yaml`.

6. **Step 6: Component 5 (Conformance Tests & Spec Bump Protocol)**
   - Add conformance tests in `tests/conformance/test_governance.py`.
   - Bump `framework/VERSION` to `0.96.11`.
   - Append `0.96.10` to `OLD_VERSIONS` in `hooks/sync-version-refs.sh` and run script.
   - Verify `python3 tests/chg/spec_gate.py --base origin/dev` and `pytest tests/conformance/`.
   - Verify `bash hooks/pre_push_check.sh origin/dev`.

7. **Step 7: Commit, Push, PR, and Auto-Merge**
   - Commit with audit phrase: `Multi-agent self-review per OPS-0065 (primary, self-audit): approved`.
   - Push to `origin feature/chg-124-tech-stack-security`.
   - Create PR to `dev`, watch checks to green, auto-merge, and clean up worktree.
