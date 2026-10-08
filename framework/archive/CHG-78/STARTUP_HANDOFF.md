# Project Startup Handoff & Kickoff Guide

> [!IMPORTANT]
> **Live Framework Version: 0.90.1.** This document contains the definitive **Project Kickoff Quickstart (Section 0)** for teams initiating new projects with `aidoc-flow-framework`. Sections 1–5 below are preserved verbatim as the authoritative historical migration brief anchoring decisions D-0007..D-0013 in `framework/governance/DECISIONS.md`.

---

## 0. Project Kickoff Quickstart (Version 0.90.1)

### 0.1 The Modern SDD Framework at a Glance

The framework defines an engine-agnostic, 10-layer Specification-Driven Development flow:

```text
BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code → EVAL → Verified
```

- **Autonomous Execution**: Routine development is executed by AI agents in isolated git worktrees without human micro-management.
- **Governance Gate**: Any code write requires an authorizing Change Request (`CHG`) and Implementation Plan (`IPLAN`).
- **3-Tier Multi-Agent Execution Architecture** ([`DURABLE_EXECUTION_STANDARD.md`](../framework/governance/DURABLE_EXECUTION_STANDARD.md)):
  - **Tier 1 (Durable Workflows)**: Orchestrates saga compensations, human gates, zero-cost durable waits, and execution timeouts.
  - **Tier 2 (Cognitive Graphs)**: Executes cyclical reasoning, review loops ([`REVIEW_WORKFLOW_STANDARD.md`](../framework/governance/REVIEW_WORKFLOW_STANDARD.md)), and diagnostic patches. Proposes artifacts without direct git mutation.
  - **Tier 3 (Deterministic Services)**: Executes isolated worktrees ([`WORKTREE_FLOW.md`](../framework/governance/WORKTREE_FLOW.md)), compilation, linters (`sdd_doc_lint`, `sdd_swf_lint`), and test suites.
- **The Golden Rule**: *Reasoning in Cognitive Graphs, Effects in Deterministic Services, Control in Durable Workflows.*

### 0.2 Quickstart: 5 Steps to Launch a New Project

#### Step 1: Deploy `.aidoc/` via Automated Installer

From the framework repository or clone, run [`framework/scripts/install.sh`](../framework/scripts/install.sh):

```bash
# Production deployment (pinned allowlist copy, self-contained):
framework/scripts/install.sh <project-dir> --canon framework/v0.90.1 --kind pin

# Or symlink to a persistent shared framework checkout:
framework/scripts/install.sh <project-dir> --canon framework/v0.90.1 --kind symlink --shared /path/to/framework
```

This executes [`BOOTSTRAP.md`](../framework/governance/aidoc/BOOTSTRAP.md) steps 1–5 automatically and verifies directory structure health.

#### Step 2: Configure Project Adaptation (`.aidoc/profile.yaml`)

Review `<project>/.aidoc/profile.yaml` (seeded from `PROFILE-TEMPLATE.yaml`). Tune only the knobs your project needs:

- `review_mode`: `team` (multi-persona crew fan-out) or `single_pass`.
- `active_layers`: `[BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN, EVAL]` (dropping `BDD` or `ADR` applies the cascade rule).
- `audit_threshold`: raise readiness score floors (raise-only, default 90).
- `exec_*`: bounds on files (8), diff lines (600), token budgets (200k), and patch attempts (3).

#### Step 3: Establish the Root Working Agreement (`<project>/AGENTS.md`)

Create `<project>/AGENTS.md` to bind all AI coding agents to project governance:

````markdown
# AGENTS.md — Working Agreement for AI Coding Agents

## Governance Gate (Non-Negotiable)

Before writing ANY code for a feature, enhancement, or bug fix:
1. Stop: Create an authorizing Change Request (CHG) first.
2. Complete the §3.4 CHG creation checklist before writing code.
3. Validate CHG via `python3 .aidoc/framework/sdd_doc_lint/chg_lint.py <chg-file.yaml>`.
4. Work in a dedicated per-task git worktree: `git worktree add ../<project>-<slug> -b feature/<branch-slug> origin/dev`.
5. Run automated verification suites locally before pushing. Never bypass hooks (`--no-verify` is forbidden).
````

#### Step 4: Instantiate Operational Governance Blueprints

Copy the required governance blueprints under `<project>/.aidoc/project/governance/` (see [`docs/ADAPTATION-GUIDE.md`](ADAPTATION-GUIDE.md) §4.1):

1. `CHG_EXECUTION_FLOW.md` (autonomous 8-step lifecycle, circuit breakers)
2. `CI_SMART_ROUTING.md` (anti-deadlock invariant, required check routing)
3. `CONFLICT_RESOLUTION.md` (forward merges, auto-merge re-arming)
4. `SELF_REVIEW_LOOP.md` (dual-stage multi-lens review)
5. `QA_PROTOCOL.md` (tripartite roles, closing reports)
6. `BROWSER_TESTING.md` (headless testing, port sandboxing)
7. `DURABLE_EXECUTION.md` (3-tier orchestration, thin state, saga rollback)
8. `REVIEW_WORKFLOWS.md` (graph review flows, structural review reports)

#### Step 5: Author Initial Seed & First Cycle

1. Author initial stakeholder requirements under `<project>/seed/` using [`framework/templates/SEED-TEMPLATE.md`](../framework/templates/SEED-TEMPLATE.md).
2. Decompose seed into architecture domains per [`SEED_TO_MODULE_DECOMPOSITION.md`](../framework/governance/SEED_TO_MODULE_DECOMPOSITION.md).
3. Author Layer 1 `BRD` (`docs/sdd/01_BRD/BRD-01/BRD-01.yaml`) to initiate the formal SDD chain.

---

## Historical Archive: AI Doc Flow Framework Migration Brief (2026-05-20)

> **Historical artifact:** written 2026-05-20 during Phase 3/4. Captures the business/product hypothesis at that point. Current project state lives in [`../framework/CHANGELOG.md`](../framework/CHANGELOG.md).
>
> **Purpose:** Distill the business / startup ideas that surfaced during a
> multi-phase technical-migration session into a self-contained brief a
> fresh session can pick up. The migration itself is *evidence and proof-
> of-concept* for the ideas below, not the ideas.
>
> **Origin:** Session worked through Phases 0–4 of porting `legacy/ucx_*`
> code into a multi-platform `aidoc-flow-framework` repo. Along the way,
> recorded decisions (D-0007 … D-0013), roadmap entries, and design
> rationale that revealed a coherent product/business shape.
>
> **Written:** 2026-05-20.
> **Repo:** `https://github.com/vladm3105/aidoc-flow-framework`
> **Branch:** `claude/multi-platform-migration-AamWB` (at commit `d3e2e7a`).

---

## 1. What the project actually is — the one-line elevator pitch

> *AI-assisted Specification-Driven Development (SDD): a gated, traceable,
> 8-layer documentation-to-code flow whose terminal product is the
> Implementation Plan (IPLAN), not the code.*

The migration packaged this as **one engine-agnostic specification**
(`framework/`) plus **two independent platforms** that implement it
(Hermes MCP server, Claude Code plugin). Same contract, different engines,
identical conformance. **This pattern itself is part of the value
proposition.**

---

## 2. The five recorded decisions that anchor the business hypothesis

These are not theoretical — each is a working decision in
`plans/DECISIONS.md` driving real implementation.

- **D-0012 — Framework purpose: the IPLAN is the terminal product.**
  Code generation and deployment are explicitly **out of v1 scope.** v1
  scopes to software + devops as the layer types. The framework's
  deliverable is a *fully-traceable, gate-approved Implementation Plan*
  that an engineer (or AI) executes downstream.

- **D-0012 R1 — IPLAN has planned/executed states with
  criticality-scaled audit depth.** Not all plans need the same review
  rigor; the system scales audit ceremony to risk.

- **D-0012 R2 — Curated corpus of proven IPLANs is the unit of value.**
  This is the strategic destination flagged for post-v1.0. The future
  product is not the framework — it's the **library of validated,
  composable, fresh implementation plans** that consume it. Composition,
  freshness, and provenance are the three properties that matter.

- **D-0013 — Single source of truth for templates.** Platforms consume
  `framework/layers/`; they never carry their own duplicate templates.
  Architectural principle that prevents drift across multiple engine
  implementations.

- **CHG-D1 (ROADMAP "Post-Migration TODOs") — Change Management as
  skills + CI/CD, not a monolith.** Skills handle authoring and
  automatable gate checks (schema, traceability, gate report);
  CI/CD enforces the gate as a required status check; GitHub branch
  protection / required reviewers enforce the human sign-off half. *A
  skill must never self-approve.* Implemented twice (once per platform)
  against the same `framework/` spec.

---

## 3. Business ideas — the menu

Ranked roughly by how directly the migration session validated each one.

### 3.1 IPLAN-as-product (D-0012 core)

**Premise:** AI code generators are a commodity. The differentiator is
the *plan* — a validated, traceable, gate-approved sequence of
implementation steps with every step grounded in BRD/PRD/EARS/BDD/ADR/
SPEC/TDD upstream. Code is downstream of plan; plan is what you sell.

**Evidence in the migration:** The whole project produces nothing but
documents and plans. Phases 1–3 were 30+ plans, each with two review
passes, traceability across `plans/MIGRATION_TODO.md`, audit docs,
verify records, design docs. The pattern was demonstrably effective at
catching errors before they hit code (P2-T9 G16 + G17 caught two bugs
in scaffold/runner.py *because* the plan made downstream implications
explicit; P3-T4 G18 caught 47 broken symlinks the audit had missed).

**Monetization:**

- **SaaS** — host the SDD workflow; users author BRDs and the system
  produces gated IPLANs.
- **Consulting + tooling** — sell the methodology + the platforms to
  enterprises building internal AI tooling. The two-platform structure
  proves portability.
- **Developer-tool layer** — Claude Code plugin distribution + Hermes
  MCP server distribution as separate paid SKUs (or open-source with
  enterprise add-ons).

**Open questions:** Pricing (per-IPLAN? per-seat?). Adoption shape
(top-down enterprise vs bottom-up dev tool). Whether the plan is the
artifact users pay for, or whether it's the gate enforcement.

---

### 3.2 The IPLAN corpus — composition, freshness, provenance (D-0012 R2)

**Premise:** The real long-term value is a *curated library* of proven
IPLANs that:

- **Compose** — bigger plans assemble from smaller validated plans;
  IPLAN-as-Lego.
- **Stay fresh** — older plans decay (stack changes, security
  practices evolve); the library actively curates.
- **Trace** — every plan in the corpus carries its BRD → IPLAN
  derivation, so consumers see *why* a plan exists.

This is explicitly flagged in ROADMAP "Post-v1.0 — Planned
Capabilities" as the strategic destination.

**Evidence in the migration:** Every Pass-3 retrospective (G11–G18 in
various plans) added a lesson that, if encoded as a template / IPLAN,
becomes reusable. P2-T7 G12 (word-boundary regex over slash-prefix
sed) is a one-paragraph IPLAN-fragment that prevented at least 3
later bugs across P2-T3, P3-T2, P3-T4. The corpus grows from
retrospectives.

**Monetization:**

- **Marketplace** — IPLAN authors publish; consumers license / buy;
  curation as the platform's value.
- **Subscription** — pay for access to the curated, vetted, fresh
  set.
- **Enterprise private corpus** — host an org's internal IPLAN
  library with composition and freshness scoring; charge by seat /
  storage.

**Open questions:** Quality / curation model (peer review?
algorithmic? human-gated?). How to measure freshness (decay
function? explicit deprecation?). Who owns IPLAN IP. Whether the
corpus is the moat or whether composition tooling is.

---

### 3.3 Engine-agnostic spec, multiple engine implementations

**Premise:** Standards bodies (W3C, IETF) define the spec once and let
multiple implementations compete. Apply the pattern to AI-assisted dev
tooling. The org-level pain: every AI dev tool wants to own the
workflow; each lock-in creates fragility. **A portable spec with
multiple engines breaks the lock-in.**

**Evidence in the migration:** Two platforms (Hermes MCP, Claude Code
plugin), one spec, conformance test enforces parity. The Phase 4 plan
adds platform-conformance tests as machine-enforced gates. **The
multi-platform structure is the demo.**

**Monetization:**

- **Methodology consulting** — help enterprises adopt the
  spec-engine separation for their internal AI tooling.
- **Reference implementations** — sell support for Hermes (the
  MCP-side) and the plugin (Claude-Code-side).
- **Conformance certification** — third-party "this platform passes
  the AI Doc Flow conformance suite" badge. Industry-association
  style.

**Open questions:** Whether other engines (Cursor, Aider, etc.)
adopt the spec. Whether the conformance suite is the moat (hard
to fork) or the spec itself.

---

### 3.4 Domain profiles — generalize beyond software (ROADMAP Post-v1.0)

**Premise:** The 8 SDD layers (BRD → ... → IPLAN) are software-native
in v1. Post-v1.0, generalize: add **domain profiles** declaring which
layers apply for a domain and their schemas. Same engine, different
profile.

Candidate domains:

- Marketing campaigns (BRD → PRD → assets → measurement plan → IPLAN)
- Sales playbooks (account research → discovery scripts → demo plan
  → IPLAN)
- Legal contracts (intent → terms → review gates → execution plan)
- Scientific research (hypothesis → protocol → pre-registration →
  execution plan)
- Marketing → ads → creative → measurement
- Healthcare procedures (assessment → protocol → consent → execution)

**Evidence in the migration:** Not directly demonstrated (v1 scope is
software), but the framework's core (flow engine, gate model,
traceability, IPLAN schema, conformance suite) is **already domain-
neutral** — recorded explicitly in ROADMAP "Post-v1.0" section.

**Monetization (massively expanded TAM):**

- **Vertical SaaS per domain** — marketing IPLANs, legal IPLANs,
  research IPLANs, each as a separate product.
- **Profile marketplace** — domain experts author profiles; the
  platform takes a cut.
- **Enterprise multi-domain license** — large orgs adopting the
  framework across departments (marketing + legal + engineering)
  pay once, get all profiles.

**Open questions:** Which domain ships first post-v1.0. Whether
profiles are open-source (network effect) or proprietary (moat).
Whether AI doc-flow methodology generalizes well outside engineering.

---

### 3.5 CHG — Governance-as-code for AI-assisted work (CHG-D1)

**Premise:** Enterprises don't trust AI-generated changes today. The
blockers are **traceability** (where did this come from?), **gates**
(was it reviewed?), and **non-repudiation** (who approved it?).
Encode the change-management process as:

- **Skills** for authoring + automated gate checks (AI-assistable).
- **CI/CD** for required status-check enforcement.
- **GitHub branch protection / required reviewers** for human sign-
  off. *A skill must never self-approve.*

**Evidence in the migration:** The framework's `framework/governance/
chg/` directory already specifies the gate process (extracted in
P1-T4). CHG-D1 records the implementation model (post-Phase-5).
**The migration project itself follows a similar discipline** —
two-pass plan review (D-0007) + hook (`plan-review-gate.sh`) that
warns when a plan ships with fewer than two reviews.

**Monetization:**

- **Enterprise compliance product** — auditable AI-assisted-change
  management, sells to regulated industries (finance, healthcare,
  pharma, gov).
- **GitHub / GitLab / Azure DevOps integration** — sell the CHG
  workflow as a marketplace app.
- **SOC 2 / ISO 27001 evidence** — the gate logs become audit
  artifacts.

**Open questions:** Which regulatory frame to optimize for first.
Whether CHG ships standalone or bundled with the SDD framework.
Whether the platform hosts the audit trail or just produces it.

---

### 3.6 Ephemeral-session-friendly AI dev workflow tooling

**Premise:** AI-assisted dev increasingly runs in ephemeral
containers (Claude Code on the web, GitHub Codespaces, etc.).
Standard dev tooling assumes a persistent local machine. The
migration project built explicit infrastructure for ephemeral
sessions:

- `plans/HANDOFF.md` (continuity record across sessions).
- `hooks/pre-compact-snapshot.sh` (snapshot before context
  compaction).
- `hooks/session-start-handoff.sh` (inject handoff at
  session start).
- `hooks/plan-review-gate.sh` (non-blocking quality warning
  on commit).
- The two-pass plan review (D-0007) — every plan documents its own
  review history.

**Evidence in the migration:** The session ran for 30+ tasks across
multiple SessionStart hooks, often after context compaction. The
handoff infrastructure made this possible. Without it, every
session would re-derive context from scratch.

**Monetization:**

- **Open-source the infrastructure** as a Claude-Code-skill /
  GitHub-action package — drives top-of-funnel for everything else.
- **SaaS continuity layer** — host the handoff record + the review
  gate enforcement as a service.
- **Tooling consulting** — help dev teams set up ephemeral-friendly
  workflows.

**Open questions:** Whether this is a separate product or a feature
of the IPLAN / CHG product. Whether to focus on Claude Code
specifically or generalize to all AI dev assistants.

---

### 3.7 The migration as a case study / seed corpus

**Premise:** The migration session produced ~30 plans, 7 audit
docs, 2 verify records, and ~15 retrospectives — all in `plans/`
and committed. Each retrospective (G11, G12, G13, G16, G17, G18,
etc.) is a one-paragraph piece of hard-won knowledge. Together
they are a **seed corpus** for §3.2's IPLAN library.

**Evidence in the migration:** Literally exists in the repo at
`plans/P*-T*-PLAN.md`.

**Monetization:**

- **Marketing asset** — case study for "how to migrate a complex
  legacy AI dev project."
- **Seed for the IPLAN corpus** (§3.2) — the migration plans
  become the first 30 entries in a public corpus.
- **Methodology training material** — the project's own plans
  teach the methodology.

**Open questions:** Whether to publish the migration plans publicly
as marketing or keep them as private case studies for paid
engagements.

---

## 4. Cross-cutting themes (the through-lines)

### 4.1 The flywheel: usage → corpus → composition → freshness

Every project that uses the framework produces IPLANs. Each
IPLAN, after execution, has a planned/executed delta that becomes
*ground truth* for what worked and what didn't. The corpus grows
from real use, not synthetic content. **The flywheel.**

### 4.2 Traceability is the moat, not the framework

The 8-layer SDD model is reproducible (anyone could re-implement
it). The conformance suite is reproducible. **But the corpus +
the audit trail it accumulates is not reproducible without time

- adoption.** This is the long-game moat.

### 4.3 "Spec + multiple engines" is anti-lock-in

The two-platform demo is positioning, not just architecture. It
signals: *adopt this framework and you're not locked into any
single AI vendor.* Critical sell to enterprises burned by
proprietary AI dev tools.

### 4.4 Human in the loop is the differentiator, not a limitation

CHG-D1 explicitly forbids skill self-approval. The framework is
designed around *augmenting* human judgment, not replacing it.
This is a defensive moat against pure-automation competitors and
an active sell into regulated industries.

---

## 5. Strategic open questions (start a new session here)

1. **Wedge product?** Which of the 7 ideas in §3 is the first
   product to ship for revenue? Candidates: developer tool (Claude
   Code plugin commercialization), enterprise compliance (CHG), or
   methodology consulting.

2. **Open core vs commercial?** The framework spec is naturally
   open-source. What's behind the paywall? Conformance certification?
   The curated corpus? Hosted infrastructure? CHG enforcement?

3. **Target user — dev / team / enterprise?** Bottom-up (individual
   devs adopting the plugin) vs top-down (CTO selecting the
   methodology) drives different funnels and pricing.

4. **First domain post-v1.0?** Software is in scope for v1. Domain
   profiles (§3.4) are the TAM expansion. Which vertical first?
   Marketing has the most repeat customers; legal has the highest
   willingness-to-pay; research has the strongest network effects.

5. **Partnership shape with Anthropic / Claude Code?** The plugin
   ships in Claude Code's marketplace. What's the relationship —
   independent vendor, Anthropic partner, white-label?

6. **Where does the IPLAN corpus live?** GitHub-hosted (free,
   visible)? Custom platform (controlled, monetizable)? Hybrid
   (free tier on GitHub, premium tier hosted)?

7. **Funding shape?** Bootstrap (small, organic) vs VC (push for
   domain expansion + corpus growth fast). The corpus-and-
   composition long game (§3.2) likely needs capital to reach
   network-effect scale before someone copies it.

---

## 6. Key references (file paths in the repo for deeper context)

- `framework/README.md` — the engine-agnostic spec; 8-layer overview.
- `framework/registry/LAYER_REGISTRY.yaml` — the formal layer model.
- `framework/governance/` — the gate process documentation.
- `framework/governance/chg/` — the CHG overlay (spec only; not
  enforced until post-Phase-5).
- `framework/layers/<NN>_<X>/` — per-layer templates.
- `ROADMAP.md` Phases 4–5 + Post-Migration TODOs + Post-v1.0 sections.
- Retired D-series decisions — D-0007 (review gate), D-0009 (versioning),
  D-0011 (tagging), D-0012 (IPLAN purpose + R1/R2), D-0013 (single
  source of truth for templates). The D-series was never logged live;
  see the D-series annex in `framework/governance/DECISIONS.md`.
- `plans/P2-T1-DESIGN.md` — example of the design-pass discipline.
- `plans/P2-T7-PLAN.md` G11–G13 — examples of retrospective
  knowledge generation.
- `plans/P3-AUDIT-claude-code-plugin.md` — example of the audit
  discipline.
- `plans/P4-AUDIT-conformance.md` — current Phase 4 in-flight
  (conformance and independence between platforms).
- `tests/conformance/` — the spec-enforcement test suite.
- `tests/conformance/README.md` — documents the platform-conformance
  contract (Phase 4 implements PC1 + PC4).

---

## 7. How to use this handoff in a new session

Open a fresh session (a different repo or working area is fine —
this isn't migration work). Paste this whole file as context. Then
work through one of these next-step prompts:

- **"Wedge product analysis"** — work §5.Q1 to a recommendation:
  ship one of the 7 ideas as the first revenue product. Output: a
  one-pager naming the product, target user, pricing model, GTM,
  3-month milestones, risk surface.

- **"Corpus economics"** — work §3.2 in detail. Output: a model of
  how the corpus grows (sources, curation cost, freshness decay),
  pricing options, and a 12-month MVP shape.

- **"Engine-agnostic positioning"** — work §3.3 + §4.3. Output:
  positioning doc against incumbent AI dev tools, the lock-in
  story, the conformance-certification angle.

- **"CHG enterprise pitch"** — work §3.5 + §4.4. Output: a one-
  pager for a SOC2 / ISO 27001-style audience, with concrete
  references to the framework's gate model.

- **"Open questions"** — pick one of §5.Q1–Q7 and develop it into
  a decision-ready brief.

The migration project at `vladm3105/aidoc-flow-framework` is the
**existing implementation** of the framework spec. Don't re-build
it; reference it. The current branch is
`claude/multi-platform-migration-AamWB` at commit `d3e2e7a` (Phase 4
audit just landed; P4-T1 design is the next migration step but is
independent of the business work).

If you want to pull the latest state in a new session, the repo is
public at `https://github.com/vladm3105/aidoc-flow-framework`.

---

## Source — what this handoff distilled from

This handoff was assembled from a multi-phase migration session that
ran 2026-05-18 through 2026-05-20:

- Phase 0 — Planning & Scaffolding (`v0.1.0`)
- Phase 1 — Framework Spec Extraction (`v0.2.0` + `framework/v0.1.0`)
- Phase 2 — Platform A: Hermes Re-homing (`v0.3.0` + `hermes/v0.1.0`)
- Phase 3 — Platform B: Claude Code plugin (`v0.4.0` +
  `claude-code-plugin/v0.1.0`)
- Phase 4 — Conformance & Independence (in flight; P4-T0 audit done)

The business ideas were never explicit in the session; they emerged
from the architectural decisions, ROADMAP entries (especially the
"Post-v1.0 — Planned Capabilities" section), and the recorded
decisions in `plans/DECISIONS.md`. This document interprets the
implementation as the *evidence* that the ideas are tractable.
