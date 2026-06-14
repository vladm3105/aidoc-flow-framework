# AI Doc Flow Framework — Roadmap

Where the project is heading. Work is **event-triggered, not calendar-bound** — items
advance when their dependencies and review gates clear, not on fixed dates.

For shipped detail, see [`CHANGELOG.md`](CHANGELOG.md). For deferred Hermes work, see
[`plans/HERMES-BACKLOG.md`](plans/HERMES-BACKLOG.md).

---

## Version streams

Three independent SemVer streams (see [`docs/PROJECT.md`](docs/PROJECT.md)):

| Stream | What it versions |
|--------|------------------|
| **Framework spec** | The engine-agnostic shared contract — the source of truth both platforms conform to. |
| **Claude Code plugin** | Native Claude Code engine; declares the spec version it conforms to. |
| **Hermes AI** | MCP-server engine; declares the spec version it conforms to. |

Both platforms ship against every framework-spec change (**GATE-SPEC**). Day-to-day
development is **plugin-first, Hermes-second**: each feature is built and verified on the
plugin first (where the acceptance suite exercises it end-to-end), and the Hermes
equivalent batches at a natural completion point. This is a sequencing choice, not a
permanent asymmetry.

---

## Now

Near-term, in-flight work.

- **Hermes parity catch-up** — propagate the BRD saga driver through PRD…IPLAN and land
  the review-calibration lens sub-checks, so Hermes matches the plugin's current surface.
  Tracked in [`plans/HERMES-BACKLOG.md`](plans/HERMES-BACKLOG.md).

---

## Next

Planned, scoped, not yet started.

- **Doc-number independence** *(deferred cleanup #18)* — decouple per-layer document
  numbering so layers can be authored and renumbered without cross-layer coupling.
- **Decomposition layer for complex projects** *(deferred cleanup #19)* — promote an
  optional `02b_DECOMP` layer (building on the existing optional PRD §7b component
  decomposition) for projects large enough to need an explicit decomposition step.
- **Domain profiles — generalize the IPLAN beyond software.** The framework's terminal
  artifact is a fully-traceable, gate-approved **IPLAN**. v1 scopes this to **software +
  devops** (the current EARS/BDD/ADR/TDD layers are software-native and stay that way).
  Next, make domain support additive via a **profile** mechanism:
  - *Core stays domain-neutral* — the flow engine, gate model, traceability, IPLAN
    schema, and conformance are already domain-independent.
  - *A profile declares which layers apply for a domain and their schemas* —
    `profile: software` and `profile: devops` ship today; new domains are new layer
    definitions, not changes to the core.

---

## Later

Strategic direction.

- **Non-technical domain profiles** — extend the profile mechanism to non-software work:
  operational runbooks, compliance/audit planning, research plans. Each is additive — new
  layer definitions, never a core rewrite — making "an IPLAN for any purpose" an
  architectural property of the engine.
- **The IPLAN library — the corpus is the asset.** A single IPLAN is reproducible and
  low-value; the strategic asset is a curated, maintained library of *proven* IPLANs —
  codified, executable institutional knowledge:
  - **Planned vs. executed state** — an IPLAN is *planned* (confirmations pending) or
    *executed* (confirmations satisfied with evidence). The executed IPLAN is the
    auditable trail; audit depth scales with the work's criticality.
  - **Proven-entry gate** — an IPLAN earns library membership only once executed and
    audited.
  - **Composition** — distinguish an IPLAN *template* (the proven pattern) from an
    *instance* (a parameterised run); allow IPLANs to compose other IPLANs.
  - **Freshness** — each library IPLAN records when it was last proven and against which
    versions; conformance flags stale entries for re-validation.

  This is the destination: the framework as a system of record for an organization's
  executable process knowledge.

---

## Recently shipped

Headline capabilities now in the framework (full detail in
[`CHANGELOG.md`](CHANGELOG.md)):

- **Claude Code plugin user-facing commands (`0.18.0 → 0.19.0`).** 11 commands
  for meta, workflow, lifecycle, and config — `/about`, `/help`, `/bug-report`,
  `/contact-us`, `/feedback`, `/status`, `/next`, `/uninstall`, `/configure`,
  `/budget`, `/model`. Optional project-local `.claude/aidoc-flow.config.yaml`
  config format with single-source-of-truth schema in `docs/CONFIG.md`. Closes
  the first-time-user discoverability gap (was 1 command + 53 skills with no
  meta/help/status surface). Honest caveats baked in: `/budget` is a behavior
  knob (not a token cap), `/model` is advisory (cannot switch the session
  model), `/uninstall` is a guided exit (native `/plugin uninstall` does the
  removal). Plan: `plans/PLUGIN-USER-COMMANDS-PLAN.md`.
- **Multi-persona review team** — per-layer review crews with deterministic
  weighted/capped scoring, a structural gate as a reproducible floor, and split
  `chaos_engineer` / `security_engineer` lenses.
- **Layer playbooks — 45 across all 8 layers** — per-layer, per-lens authoring and
  review guidance wired into team-mode review.
- **`.aidoc/` provenance tier** — a third committed documentation tier (audit, review,
  remediation, validation, security) that answers *"how was this produced?"* without a
  re-run.
- **Pre-deployment acceptance suite** — drives every active plugin surface element against
  a named example's seed as the release gate; methodology in
  [`tests/ACCEPTANCE.md`](tests/ACCEPTANCE.md).
- **Necessary-upstream trace contract** — each layer declares only what its own evaluation
  reads; deeper lineage is discoverable transitively, enforced by a corpus-level lint rule.
- **Token-efficient authoring governance** — per-section size targets across all layer
  templates, enforced by `sdd_doc_lint`.
- **C4 + DFD + sequence diagram standards** — per-layer diagram authority wired into both
  platforms' creation and review agents.
- **Change management (GATE-SPEC)** — the framework-spec change gate, enforced by skills +
  CI + branch protection.
- **Framework-feedback pipeline** — a two-tier loop that converts friction found in real
  projects into durable framework improvements.

---

## History

AI Doc Flow Framework began as the `ucx_framework`, restructured into the current
engine-agnostic spec + two-platform layout. The pristine pre-restructure project is
preserved on the read-only branch `legacy-ucx-v3.2-read-only`.
