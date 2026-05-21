# Decision Log

Non-obvious decisions made during the migration, with rationale, so the "why"
survives across ephemeral sessions. Newest first. Timestamps are ISO 8601 UTC.

Decisions that affect the **shared spec** graduate into `framework/governance/`
when change management returns post-Phase 5 (see `ROADMAP.md` CHG-D2).

---

---

## D-0014 — Retain `legacy/` + root `.claude/` in-tree; archive the pre-migration project as a protected branch

- **Date:** 2026-05-21T05:50:00Z
- **Decision:** At the Phase 5 cutover the project does **not** delete
  `legacy/` or root `.claude/` from the working branch (→ new `main`).
  Both are retained in-tree. The pristine pre-migration `ucx_framework`
  project (at its original root layout) is preserved separately as the
  **protected, read-only branch `legacy-ucx-v3.2-read-only`** (created off
  `main` at commit `491e8db`, byte-identical to it).
- **Why:** User directive ("do not remove legacy files"; "keep legacy root
  `.claude/` too"). A protected branch is a more discoverable and
  enforceably-immutable archive than relying on git history after a
  deletion, and keeping the dev-time root `.claude/` in-tree lets the
  repository keep dogfooding its own Claude Code setup. Deleting nothing
  also removes the only destructive operations Phase 5 had, lowering
  cutover risk.
- **Overrides:** the prior cutover policy ("`legacy/` is removed at/after
  the Phase 5 cutover" — `docs/REPO_STRUCTURE.md`; "legacy archived" —
  `docs/PROJECT.md` §4 / `ROADMAP.md` Phase 5; "`legacy/` is removed at the
  Phase 5 cutover" — `CLAUDE.md`). These are reconciled to "legacy
  retained in-tree; pre-migration project preserved as the
  `legacy-ucx-v3.2-read-only` branch" in P5-T4.
- **Consequence:** Phase 5 drops its two destructive tasks (P5-T2 remove
  `legacy/`, P5-T3 remove root `.claude/`); cutover becomes design → docs
  finalization → verify → close. The migration plan docs that cite
  `legacy/...` paths remain valid (the dir stays in-tree). The
  `CLAUDE.md` "Legacy is frozen / copy-don't-move" rules still hold for
  the in-tree `legacy/` (it remains read-only history).

## D-0013 — Framework templates are the single source of truth; platforms consume, not duplicate

- **Date:** 2026-05-19T14:50:00Z
- **Decision:** The 8 layer document templates
  (`<X>-TEMPLATE.yaml` for BRD/PRD/EARS/BDD/ADR/SPEC/TDD/IPLAN) live
  exclusively in `framework/layers/<NN>_<X>/`. Platforms do **not** ship
  their own copies. Hermes' legacy `templates/` directory is dropped at the
  port (P2-T1 Q3); the platform's runtime template-loader reads from
  `framework/layers/`. Any platform-specific runtime data the legacy
  templates carried (e.g. `server: ucx_hermes`, `tool: sdd_validate`) moves
  to platform-side config — never into the engine-agnostic templates.
- **Why:** The framework is engine-agnostic by D-0006 and the conformance
  spec-hygiene tests. Embedding engine names in shared templates violates
  that contract. The legacy duplicate had already drifted from the framework
  by exactly that engine-named block (audit §3b), proving the maintenance
  burden of dual ownership. Single source of truth + clear runtime/document
  separation. Generalises: future platforms (Claude Code plugin and beyond)
  follow the same rule.
- **Notes:** Resolves the audit's §3b prose-coupling in `templates/*.yaml`
  automatically — those files are not copied to `platforms/hermes/`. The
  lone `BRD-MD-TEMPLATE.md` (no framework equivalent) is investigated at
  P2-T3 and ported-or-dropped based on call-site usage.

## D-0012 — Framework purpose: the IPLAN is the product; v1 scope is software/devops

- **Date:** 2026-05-19T12:45:00Z
- **Decision:**
  - aidoc-flow's purpose is to transform business intent into a
    fully-traceable, gate-approved **IPLAN** — the framework's *terminal
    artifact*. Source-code generation and deployment are **out of scope**:
    they are downstream, agent-agnostic steps performed by any capable AI
    agent, not by the framework.
  - The **IPLAN is the product**: a machine-readable, auditable handoff
    contract bundling reasoning (BRD/PRD), states (EARS), behavior (BDD),
    infrastructure decisions (ADR), testing procedures (TDD/TSPEC), and
    specifications — self-contained enough that any agent can execute it
    without further clarification.
  - **v1 scope is software + devops domains only.** The current SDD layers
    (EARS, BDD, ADR, TDD) are software-native. Non-technical task domains are
    deferred to a post-v1.0 **domain-profile** mechanism (see `ROADMAP.md`,
    "Post-v1.0 — Planned Capabilities").
  - Promise framing is **"rigorous, auditable, gap-surfacing"** — *not*
    "bullet-proof". The framework enforces structure and blocks on unresolved
    open questions, but cannot manufacture requirements a human never supplied.
- **Why:** Code generation and deployment are commoditized across AI agents;
  the scarce, defensible value is auditable reasoning with end-to-end
  traceability. Terminating scope at the IPLAN keeps the name `aidoc-flow`
  accurate — the framework *is* the document flow. Limiting v1 to
  software/devops keeps the existing layers fit-for-purpose; chasing
  universality early would dilute the framework into being vague at everything.
- **Notes:** The conformance suite gains a job — verifying IPLAN
  *agent-readiness* (no TBDs, full upstream traceability, bundled test specs,
  explicit stack/runtime constraints). Domain generalization is an
  architectural goal (a generic flow engine + per-domain profiles), sketched
  in `ROADMAP.md` as post-v1.0.

### Refinements

- **R1 — 2026-05-19T13:10:00Z — the IPLAN has a *planned* and an *executed*
  state.** The IPLAN is one artifact in two states: *planned* (YAML
  instructions with confirmations pending) and *executed* (each confirmation
  satisfied with evidence — what ran, results, actual vs expected). The
  *executed* IPLAN is the auditable trail behind a result; in practice humans
  scrutinise the result, not the forward plan, and often accept the planned
  IPLAN blindly. **Criticality scales audit depth:** low-criticality work
  (e.g. a throwaway MVP cloud deploy) — the IPLAN is internal quality control,
  nobody audits; high-criticality work — the executed IPLAN's evidence *is*
  the deliverable. Audit depth is a dial set by criticality, not all-or-nothing.

- **R2 — 2026-05-19T13:10:00Z — the unit of value is the curated corpus, not a
  single IPLAN.** A single IPLAN is reproducible and low-value. A curated,
  maintained library of *proven* IPLANs is codified, executable institutional
  knowledge — the customer's IP. An IPLAN earns library membership by being
  executed and audited (R1). The library — plus **composition** (IPLAN
  templates vs instances; IPLANs composing IPLANs) and **freshness**
  (re-validation, versioning, staleness flags) — is the post-v1.0 strategic
  destination: the framework as a system of record for an organisation's
  executable process knowledge. Sketched in `ROADMAP.md`.

## D-0011 — Bookmark tags alongside release tags

- **Date:** 2026-05-19T11:20:00Z
- **Decision:** Git tags serve two roles. **Release tags** (`vX.Y.Z`,
  `framework/vX.Y.Z`, `<platform>/vX.Y.Z`) are annotated, immutable, and
  permanent. **Bookmark tags** (`mark/<slug>`) are annotated, mutable, and
  disposable — they mark notable non-release commits (baselines, known-good
  states, audit points) for easy retrieval via `git tag -l 'mark/*'`. The full
  policy lives in `docs/TAGGING.md`; `docs/PROJECT.md` §3 links it.
- **Why:** Tags are a cheap, searchable way to mark history. Restricting them
  to releases wastes that. A separate, clearly non-SemVer namespace keeps
  bookmarks from being mistaken for versions.
- **Notes:** `docs/TAGGING.md` is the single authority; the tag-namespace
  table was moved there from `docs/PROJECT.md` §3 to avoid two copies drifting.

## D-0010 — Framework docs drop legacy version-lineage content

- **Date:** 2026-05-19T10:00:00Z
- **Decision:** When extracting docs into `framework/`, drop content that only
  documents the legacy SDD version lineage — the `## v3.2 Changes from v3.0`
  sections (P1-T7, in the guide and the testing-strategy doc) and the
  `CHG_MIGRATION_PLAN.md` (v2→v3) reference in `QUICK_REFERENCE.md`.
- **Why:** `framework/` is a fresh `0.1.0` version stream (D-0006); it does not
  continue the legacy `v3.x` numbering, so "changes from v3.0" history is both
  inaccurate framing and carries `v3.x` tokens the conformance hygiene check
  bans. The current layer order/rationale those sections explained is already
  stated as present-tense fact elsewhere in each doc.
- **Notes:** Removal is limited to version-lineage framing; all genuinely
  engine-agnostic methodology content is copied verbatim.

## D-0009 — Namespaced version tags; framework tag at Phase 1 close

- **Date:** 2026-05-19T09:15:00Z
- **Decision:** Each SemVer stream tags in its own namespace — project
  milestones `vX.Y.Z`, framework spec `framework/vX.Y.Z`, platforms
  `<platform>/vX.Y.Z`. `VERSION` files hold the bare SemVer; the tag adds the
  `v` and namespace. The `framework/v0.1.0` tag is created at Phase 1 close
  (after P1-T7), not at P1-T6 — so it marks a fully assembled spec — alongside
  the `v0.2.0` project milestone.
- **Why:** `docs/PROJECT.md` defined only bare milestone tags; the independent
  framework/platform streams need distinct, collision-free tag names.
  Slash-namespaced refs let `git tag -l 'framework/*'` filter one stream.
  Tagging an incomplete spec would burn a version on a partial assembly.
- **Notes:** Convention recorded in `docs/PROJECT.md` §3 (extended, not a new
  doc). P1-T6 delivers `framework/VERSION` + the convention; the deferred tag
  is tracked as the Phase 1 close task (P1-T8).

## D-0008 — Conformance suite is stdlib-only (`unittest`)

- **Date:** 2026-05-18T21:20:00Z
- **Decision:** Build `tests/conformance/` on the Python 3.11 standard library
  (`unittest`) plus `PyYAML`. No `pytest` dependency.
- **Why:** The conformance suite is the shared, engine-agnostic contract; it
  must be runnable by any platform with zero install friction. `pytest` is not
  installed in the environment, and `python -m unittest discover` runs the
  suite anywhere. `unittest.TestCase` classes remain `pytest`-discoverable for
  platforms that prefer that runner.
- **Notes:** Discovery uses a flat package-less layout (`tests/conformance/`
  with no `__init__.py`) so test modules can `import _spec` directly under
  `unittest discover`. The plan listed an `__init__.py`; it was dropped during
  implementation for clean discovery.

## D-0007 — Plan review is a two-pass, recorded gate

- **Date:** 2026-05-18T18:45:00Z
- **Decision:** Every plan file carries a `## Review log` with **≥2**
  ISO-stamped passes; a plan may not be presented, handed off, or implemented
  until it does. New plans start from `plans/PLAN-TEMPLATE.md`. A non-blocking
  `PreToolUse(git commit)` hook warns when a staged plan file falls short.
- **Why:** The review/harden step was prose-only, so a skipped second pass was
  invisible — it happened once on the P1-T2 plan. Making each pass a named,
  checkable artifact turns a silent omission into a visible gap.
- **Notes:** The hook enforces that a pass is *recorded*, not that it is
  thoughtful — review quality stays a manual judgment step.

## D-0006 — First `framework/` spec version is `0.1.0`

- **Date:** 2026-05-18T18:00:00Z
- **Decision:** The extracted `framework/` spec starts its independent version
  stream at `0.1.0`, carrying a `derived_from: "SDD v3.2"` metadata field.
  `1.0.0` is reserved for when both platforms pass the shared conformance suite.
- **Why:** The content is mature, but as a freshly re-packaged engine-agnostic
  artifact it is not yet conformance-proven and no platform is wired to it.
  `0.x` is the honest signal; the lineage field preserves provenance.

## D-0005 — `framework/` ships per-layer index templates

- **Date:** 2026-05-18T18:00:00Z
- **Decision:** Each `framework/layers/` directory ships a
  `{TYPE}-00_index.TEMPLATE.{md,yaml}` skeleton. Legacy `*-00_index.*` instance
  files are dropped (project data, not spec).
- **Why:** The index/registry *format* is a conformance concern — both
  platforms must produce and validate index files identically. Pinning the
  format in the spec prevents platform divergence.

## D-0004 — Compaction/continuity automation via hooks

- **Date:** 2026-05-18T17:27:00Z
- **Decision:** Add a `PreCompact` hook that auto-commits and pushes a WIP
  snapshot, and a `SessionStart` hook that injects `plans/HANDOFF.md` into
  context. Scripts live in `.claude/hooks/`.
- **Why:** Containers are ephemeral; only pushed work survives. The PreCompact
  hook guarantees a durable snapshot before any memory-reduction event; the
  SessionStart hook restores continuity automatically.
- **Notes:** Hooks run shell commands, not Claude reasoning — they cannot
  *write* the handoff narrative. `plans/HANDOFF.md` is refreshed manually as a
  workflow step; the hook only snapshots whatever is on disk. The PreCompact
  hook no-ops off the working branch as a safety guard.

## D-0003 — Project memory + development workflow in `CLAUDE.md`

- **Date:** 2026-05-18T00:00:00Z
- **Decision:** Maintain a root `CLAUDE.md` as auto-loaded project memory, and
  codify the change flow (plan → review → harden → implement → verify → land).
- **Why:** Each session starts cold in a fresh container. Persistent memory
  prevents re-discovery; an explicit flow keeps quality consistent.

## D-0002 — `plans/` workspace for migration tracking

- **Date:** 2026-05-18T00:00:00Z
- **Decision:** Create a fresh root `plans/` (distinct from the frozen
  `legacy/plans/`) holding `MIGRATION_TODO.md` (live tracker), `HANDOFF.md`,
  `DECISIONS.md`, and ad hoc working notes.
- **Why:** Separates volatile working state from the stable published
  `ROADMAP.md`.

## D-0001 — Isolate the pre-migration project into `legacy/`

- **Date:** 2026-05-18T00:00:00Z
- **Decision:** Move the entire pre-migration project into `legacy/` via git
  renames; freeze it (copy-don't-move); disable legacy CI.
- **Why:** A clean root for the new multi-platform structure with zero path
  overlap, while preserving the old project for content extraction in
  Phases 1–3 and full git history.
