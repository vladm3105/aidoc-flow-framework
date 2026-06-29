# aidoc-flow-framework

**AI-First, Specification-Driven Development for the agent era.**

A framework whose artifacts are written **for AI agents to implement, deploy, and
maintain** — not for humans to read. It turns a human's project seed into a
structured, traceable, machine-verifiable chain that an agent can build from
without drifting, and keeps that chain alive as reality changes.

> A human never reads the whole chain. A human asks an agent to summarize, review,
> or change it. The documents are the machine-readable contract; the natural-language
> view is generated on demand.

---

## Why this exists

AI writes code fast. The problem isn't writing — it's that **AI-generated code
without proper specification, plans, and traceability is unmaintainable**. An agent
will happily produce nice-looking, plausible, *partially-wrong* code and silently
drop a requirement it never noticed. And the next agent — fresh context, months
later, modifying code it didn't write — reconstructs intent *from the code itself*,
which is exactly how silent breakage compounds into a black box.

This framework is the **anti-drift harness**. It gives every agent — the one that
builds and every one that later maintains — the authoritative intent, the addressable
contract, and the test oracle that proves nothing broke. Structured intent +
traceability + test oracles is not bureaucracy in the agent era; it's the only thing
that makes AI-generated code maintainable instead of disposable.

---

## The model: seed → chain → adaptive loop

The framework does not invent the business and does not claim to know the world. It
sits between a **human seed** and the **agents** that realize and maintain it.

```
   HUMAN (owner / architect)                  FRAMEWORK + AI                       WORLD
   ─────────────────────────                  ──────────────                       ─────
   vision · strategy · real-world   ──seed──▶  BRD→PRD→EARS→BDD→ADR→SPEC→TDD→IPLAN  ◀─signal─ spikes
   constraints (pre-framework docs)           (traceable, verifiable, buildable)            prod telemetry
                                                        │                                    canary
                                              PO review at EARS/BDD                          │
                                              (right definition of done)                     │
                                                        │                                    │
                                                   CHG + lifecycle  ◀──────reality delta─────┘
                                              MVP → PROD → New MVP → Updated PROD
```

1. **Human seeds the intent.** The business owner or architect creates the initial
   project documents (vision, strategy, constraints, prior-art corpus). This is where
   ground truth and real-world assumptions enter — the framework never originates them.
2. **The chain transforms the seed** into eight cumulative layers, each addressable and
   cross-linked, ending in code-ready implementation plans.
3. **The product owner (human or AI-as-PO) validates the oracle early** — at the EARS/BDD
   layer, *before* any architecture is committed (see "Why BDD before ADR").
4. **The world produces the truth signal** — a sandbox spike, a canary, production
   telemetry. No document can manufacture this; someone has to go observe reality.
5. **CHG ingests reality as bounded, traceable deltas.** The chain is not frozen; it is a
   living `MVP → PROD → New MVP → Updated PROD` loop.

---

## The layers

| Layer | Artifact | Answers |
|------|----------|---------|
| L1 | **BRD** — Business Requirements | Why are we building this? (C4 Context) |
| L2 | **PRD** — Product Requirements | What product capability? (C4 Container) |
| L3 | **EARS** — Formal Requirements | Precisely, what must it do? |
| L4 | **BDD** — Acceptance Scenarios | What does "correct" look like? (the **oracle**) |
| L5 | **ADR** — Architecture Decisions | How, and why this way? |
| L6 | **SPEC** — Component Contracts | The buildable interface (C4 Component) |
| L7 | **TDD** — Test Definitions | The tests that prove it, test-first |
| L8 | **IPLAN** — Implementation Plan | The exact, resumable build manifest for an agent |

Overlays: **CHG** governance gates (adaptive change control with approval + re-gate),
and markdown **development/work plans** (`plans/*.md`) — the human-and-agent-readable
plan-of-record for a single change.

Document numbers are **per-layer counters with no cross-layer alignment**; an upstream
item may fan out to many downstream documents. Lineage is carried by `@`-tags and
content-hash element IDs, never by matching numbers.

---

## What makes agents safe here

- **Content-hash element IDs + cumulative `@`-tags** — every requirement, decision, and
  test has a stable address; a future agent cannot quietly reinterpret "this exact
  requirement."
- **Coverage checks** — every requirement/scenario must map to a component (or be
  explicitly deferred); silently-missing functionality is detectable, not discovered in
  production.
- **Test-first manifests (TDD/IPLAN)** — the oracle exists before the code; an agent
  cannot "finish" a component without the test that defines done.
- **Deterministic gates** — resolution, ID format, required tags, and coverage are
  mechanically checkable; "the chain verifies clean" is a fact, not an opinion.
- **Maker-checker for change (CHG)** — reality-driven changes propagate with a computable
  blast radius and a re-validation gate, not by code archaeology.

---

## Division of labor (who owns what)

| Owner | Responsibility |
|---|---|
| **Human (owner/architect)** | The **seed**: intent + real-world assumptions. The quality of the seed. |
| **Framework + AI** | Faithful **transformation** of the seed into a traceable, verifiable, buildable chain. |
| **Product owner (human or AI-PO)** | Validate the **oracle** at EARS/BDD: *is this the right definition of done?* |
| **The world** | Produce the **truth signal** (spike, canary, prod) — the only source of "is this assumption true?" |
| **CHG + lifecycle** | **Adapt** the chain to reality as bounded, traceable deltas. |

---

## Why BDD before ADR

Acceptance scenarios (L4) are authored **before** architecture decisions (L5) on
purpose. Two reasons:

1. **Review at the right altitude.** Plain Given/When/Then is exactly what a product
   owner — human or an AI acting as PO — can validate, with no implementation noise, and
   *before* a cent is spent on architecture.
2. **The oracle is pinned independently of the implementer.** Deciding "what correct
   means" before "how we'll build it" stops the common failure where the architecture
   quietly redefines the acceptance criteria to whatever's convenient. That's anti-drift
   at the *requirements* level, complementing the anti-drift at the code level.

---

## The correctness boundary

The framework guarantees **internal consistency, completeness, and adaptability**. It
does **not** guarantee the spec is true about the world — and it doesn't try to.

- An agent will faithfully implement a flawless spec of a **false assumption**. So the
  human's irreducible job narrows to two things only a human (or the world) can own:
  **is this assumption true**, and **is this the right definition of done**.
- Garbage-in still gives garbage-out — but **legible, reviewable, correctable** garbage
  that a PO catches at BDD and CHG fixes with a computable blast radius, instead of
  silent garbage compounding inside code.
- The framework's promise is to make a wrong idea's **consequences visible and its
  corrections cheap** — not to make a wrong idea right.

What used to look like "a gap inside the framework" is actually its **edge**: the seed
(human) and the act of observing reality (world). Naming those as outside the
framework's contract completes the model rather than exposing a weakness.

---

## Using it

1. **Seed it.** Provide vision/strategy/constraints/prior-art as the pre-framework input.
2. **Author the current cycle's set in full; stub the rest.** A cycle = a BRD *set*
   (platform BRD + its feature BRDs). Don't over-author distant features that depreciate
   before their cycle.
3. **Traverse the chain** BRD → … → IPLAN, assigning content-hash IDs and cumulative tags;
   keep references resolving and coverage complete.
4. **Gate it** (CHG): deterministic floor (IDs, references, required tags, coverage) +
   no unresolved P0/P1; the numeric readiness score is advisory.
5. **Validate the oracle** at EARS/BDD with a PO before building.
6. **Build test-first** from the IPLANs; sessions hand off via the IPLAN session-handoff.
7. **Observe reality**, then **adapt** via CHG — the chain is a control loop, not a
   blueprint.

---

## Issues this framework solves

The framework targets a specific cluster of failures that show up when AI agents — not
humans — write, ship, and maintain code. Grouped by what they actually break:

### 1. The generated code is plausible but wrong or incomplete

- **Silent requirement loss** — an agent produces a clean-looking module that quietly
  omits a requirement nobody noticed was missing. → **Coverage checks** force every EARS
  requirement and BDD scenario to map to a component or be explicitly deferred. On
  BeeLocal this literally surfaced two whole missing components (compliance/resilience,
  recipient management) that read as "done" until measured.
- **No oracle, so "looks right" passes for "is right"** — agents are confident and
  wrong. → **Test-first (BDD→TDD→IPLAN)**: the acceptance test exists before the code,
  so an agent can't "finish" a component without satisfying the definition of done.

### 2. Drift across agents, sessions, and time

- **The second-agent problem** — a fresh-context agent months later modifies code it
  didn't write and reconstructs intent from the code, which is how silent breakage
  compounds. → **Content-hash IDs + cumulative `@`-tags** give every requirement a stable
  address it can't quietly reinterpret; **IPLAN session-handoff** preserves state across
  stateless agent calls so a resumed session doesn't regenerate or contradict prior work.
- **"Why is this here / what breaks if I change it?"** — untraceable code. → **End-to-end
  traceability** (component → ADR → BDD → EARS → PRD → BRD) makes the change blast-radius
  computable instead of guessed.

### 3. Building the wrong thing

- **Architecture silently redefines "done"** to whatever's convenient to implement. →
  **BDD-before-ADR** pins the oracle, reviewable by a product owner (human or AI-PO),
  before a cent goes into architecture — "what correct means" decided independently of
  "how we'll build it."
- **No safe checkpoint before spending** — teams build, then discover it's wrong. →
  **Deterministic gates** (structural floor + no unresolved P0/P1) give a mechanical
  "ready to proceed" at each layer boundary.

### 4. Verification is opinion, not fact

- **"Is it complete/consistent?" is a judgment call.** → The framework makes it
  mechanical: 0 unresolved references, 0 duplicate IDs, 100% coverage are **computed, not
  asserted**. "The chain verifies clean" is a fact.

### 5. Ambiguous human→agent instructions

- **Vague specs make agents guess.** → **Formal EARS** (WHEN…SHALL…WITHIN), typed **SPEC
  contracts**, and exact **IPLAN file manifests** give an agent unambiguous, addressable
  instructions it can't misread.

### 6. Documentation that rots / scope sprawl

- **Frozen docs that drift from reality and start lying.** → **CHG governance** + the
  MVP→PROD→New MVP lifecycle absorb reality as bounded, traceable, re-gated deltas — a
  living chain, not a blueprint.
- **Over-engineering distant features that depreciate before they're built.** → **"Author
  the current cycle's BRD set in full; stub the rest"** — bounded authoring tied to cycles.

### 7. Unmaintainable AI-built systems

- **The overarching one:** AI code without spec/plan/traceability becomes a black box. →
  The chain is the **durable intent + test oracle every future agent inherits**, so
  maintenance is a bounded, traceable delta instead of archaeology — and onboarding
  (human or agent) becomes "query the chain," not "reverse-engineer the code."

**What it deliberately does *not* solve** — and shouldn't be expected to: it doesn't
verify that your assumptions are *true about the world* (e.g., "Privy supports custodial
USDC on Solana"), and it can't make a bad **seed** good. Those stay with the human
(quality of the seed) and the world (the spike/canary/prod signal that tells you an
assumption is false). The framework's job is to make a wrong idea's consequences
**visible and cheap to correct** — caught at BDD, fixed via CHG — not to make a wrong
idea right.

**In one line:** it converts *"AI writes code fast but you can't trust, trace, or maintain
it"* into *"AI writes code that is provably complete against an explicit oracle, fully
traceable, and safely modifiable by the next agent."*

---

## Field note: why the volume isn't overhead

If the consumer is an agent, then the volume and the rigid structure aren't overhead —
they're the entire mechanism. A human skims; an agent needs an unambiguous, addressable,
machine-checkable contract or it drifts. So "too much ceremony for a person to read" is
a **category error**: nobody reads it, they query it.

The core claim is the strongest argument for the whole approach: the documents are the
**anti-drift harness**. The exact failure mode named here — an agent producing
nice-looking, plausible, partially-wrong code and silently dropping a requirement — is
precisely what the framework's machinery is built to prevent. On a real build it worked:
the coverage check found genuine components that didn't exist yet (would've been silently
missing); the reference resolver caught dangling links the moment they appeared; the
test-first manifests mean an agent can't "finish" a component without the oracle that
proves it. Content-hash IDs + cumulative tags give every future agent a stable address
for "this exact requirement" so it can't quietly reinterpret it. That's not documentation
theater — that's the leash.

The place this pays off most is the one easiest to under-weight: **maintenance by a
different agent, months later, in fresh context.** Writing the first version is the cheap
part. The expensive, dangerous part is the second agent modifying code it never wrote —
and without the spec + traceability + tests, that agent reconstructs intent from the code,
which is exactly how silent breakage compounds. The framework hands every future agent the
authoritative intent and the test that proves it didn't break the invariant. For an
AI-maintained system over years, that's the difference between maintainable and a
slowly-rotting black box.

**Verdict:** for an AI-driven build-deploy-maintain loop, this is closer to **necessary**
than merely worth it. The "is it worth the weight" question was a human-era question.

---

*This README captures the framework's design intent for the AI-agent era: a
transformation-and-maintenance layer between a human's seed and the agents that build
and keep a system alive — with its responsibilities drawn honestly.*

---

## Platforms

The framework spec is engine-agnostic; two independent platforms implement it, each
versioned independently. Both pass the same shared conformance suite.

| Platform | Engine | Release |
|----------|--------|---------|
| **Hermes AI** | MCP server | `hermes/v0.3.0` (`platforms/hermes/`) |
| **Claude Code plugin** | Native Claude Code (skills / agents / commands) | `claude-code-plugin/v0.22.0` (`platforms/claude-code-plugin/`) |

See [`docs/PARITY.md`](docs/PARITY.md) for the capability comparison and a
"which platform should I use?" guide.

### Install the Claude Code plugin

This repo doubles as a plugin marketplace (`.claude-plugin/marketplace.json`).
From Claude Code:

```
/plugin marketplace add vladm3105/aidoc-flow-framework
/plugin install aidoc-flow@aidoc-flow-framework
```

## Status

The migration is complete (cutover shipped as `v1.0.0`); the project is now in
**post-cutover development** (latest project release `v1.1.0`), tracking
framework spec `0.29.0`. The Claude Code plugin is a **pre-1.0 preview** — APIs
and surfaces may change before 1.0. Platform release versions are in the
[Platforms](#platforms) table above.

Post-v1.0 development — delivered and planned — is tracked in
[`ROADMAP.md`](ROADMAP.md); per-release detail is in
[`CHANGELOG.md`](CHANGELOG.md). Development lands on the Claude Code plugin
first, with Hermes follow-on batches per
[`plans/HERMES-BACKLOG.md`](plans/HERMES-BACKLOG.md).

## Contributing

Enable the pre-commit hooks before committing:

```sh
pip install pre-commit && pre-commit install
```

See `.pre-commit-config.yaml` for the hook set and [`SECURITY.md`](SECURITY.md)
for the vulnerability-reporting policy.

## Documentation

- `ROADMAP.md` — delivery plan and post-v1.0 work (migration complete at `v1.0.0`).
- `CHANGELOG.md` — project-level changelog.
- `SECURITY.md` — security policy and vulnerability reporting.
- `docs/REPO_STRUCTURE.md` — repository layout (as-built).
- `docs/PROJECT.md` — versioning, branching, milestones, conformance, change management.
- `docs/TAGGING.md` — git-tag policy (release + bookmark tags).
- `docs/PARITY.md` — Hermes ↔ plugin capability comparison.
- `framework/README.md` — the engine-agnostic SDD specification.
- [`framework/docs/AIDOC.md`](framework/docs/AIDOC.md) — the `.aidoc/` provenance tier (third committed documentation tier).
- [`tests/ACCEPTANCE.md`](tests/ACCEPTANCE.md) — pre-deployment acceptance-test methodology (driver, log layout, schema, `--promote`, phase definitions, partial-execution flags, CI integration).
- [`tests/README.md`](tests/README.md) — tiered test-suite navigation hub.
- [`plans/ACCEPTANCE-SUITE-HISTORY.md`](plans/ACCEPTANCE-SUITE-HISTORY.md) — per-PR implementation timeline + design evolution + lessons learned for the acceptance suite.
- [`docs/STARTUP_HANDOFF.md`](docs/STARTUP_HANDOFF.md) — historical session brief from the Phase-3/4 migration period.

## Pre-migration history

This project was migrated from the pre-migration `ucx_framework` (v0.20.4)
into the multi-platform structure above. The **pristine pre-migration project**
is preserved on the protected, read-only branch
**`legacy-ucx-v3.2-read-only`** (`git checkout legacy-ucx-v3.2-read-only`).
The full migration record — per-task plans, audits, verify records, and the
decision log — lives under `plans/`.
