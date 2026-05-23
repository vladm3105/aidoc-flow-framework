# Decision Log

Non-obvious decisions made during the migration, with rationale, so the "why"
survives across ephemeral sessions. Newest first. Timestamps are ISO 8601 UTC.

Decisions that affect the **shared spec** graduate into `framework/governance/`
when change management returns post-Phase 5 (see `ROADMAP.md` CHG-D2).

---

---

## D-0019 — Project adaptation overlay + knowledge extractor (ADAPT)

- **Date:** 2026-05-23T17:50:00Z
- **Context:** Give a consuming project a bounded way to adapt the SDD flow
  without forking, plus a manual path to promote proven adaptations upward.
  Full design + review (Pass 1–4) in `plans/ADAPT-PLAN.md`.
- **Decisions:**
  1. **Promotion routes by governance owner** (corrects the original draft). Per
     `docs/PROJECT.md` §6: `framework/` spec changes are CHG-governed; platform
     (skill/tool) changes are ordinary PRs, *not* CHG. The knowledge-extractor
     classifies each candidate and routes spec→CHG / tool→PR.
  2. **ADAPT-0 — defer the spec→CHG path (option b).** The spec-change CHG gate
     is unbuilt (ROADMAP CHG-D1). v1 ships the tool-PR promotion path
     (plugin-only reach); spec-level candidates are drafted but flagged
     "blocked — needs CHG-D1". Building CHG-D1 is an out-of-scope follow-up.
  3. **Surface is closed + declarative** (`framework/governance/ADAPTATION.md`
     + machine-readable `ADAPTATION_SURFACE.yaml`). **v1 = 4 knobs**
     (`active_layers`, `section_toggles`, `audit_threshold`, `glossary`);
     **`id_format` deferred** pending an `ID_NAMING_STANDARDS.md` review to
     enumerate genuinely-selectable conventions (narrow-surface principle —
     don't invent options).
  4. **`audit_threshold` is raise-only** — a project may only make a layer's
     quality gate stricter, never lower it (preserves CLAUDE.md "never weaken a
     check"). The Tier-1 score (default 90) is the real model; the CHG
     gate-approval model has no score and is untouched.
  5. **Skippable layers = `[BDD, ADR]`** (the two non-C4 bridge layers);
     `[BRD, PRD, EARS, SPEC, TDD, IPLAN]` mandatory. A **cascade rule** removes a
     disabled layer from downstream `required_tags`/`can_reference` so
     traceability stays consistent. Conservative + reviewable; lives in the
     adaptation surface, not the core `LAYER_REGISTRY.yaml` (`optional` there is
     a separate default-flow concern).
  6. **User-global profile is an authoring-time seed, not a runtime input**
     (reproducibility). Runtime (incl. audits) reads the version-controlled
     project profile `.aidoc/profile.yaml` only; `~/.aidoc/profile.yaml` is
     merged into it at authoring time. Same precedence semantics, merge moved
     earlier so CI audits identically.
  7. **The adapting set is wider than the base skills** — `-audit`/`-autopilot`
     must honor the profile or they false-fail adapted docs; `trace-check`,
     `project-init`, `project-adopt` consult `active_layers`. (Implemented in a
     later ADAPT-A increment.)
- **Status — ADAPT complete (2026-05-23):** landed across 7 commits on
  `claude/skill-revision`. ADAPT-A: `framework/governance/ADAPTATION.md` +
  `ADAPTATION_SURFACE.yaml` (4-knob closed surface); `adapts:` + consult-clause
  wired into the 35-skill adapting set; `project-profile` skill; full doc
  registration. ADAPT-B: `ADAPTATION.md` §7 learnings-log convention +
  `knowledge-extractor` skill (owner-routing; spec→CHG draft stamped blocked on
  the unbuilt CHG-D1 gate; guidance→PR). **Single feature-close version bump**
  (sequencing refinement vs the plan's per-step bump): `framework/VERSION` +
  both platform `FRAMEWORK_SPEC_VERSION` `0.1.0 → 0.2.0`, and all 54 plugin
  skills' `framework_spec_version` (user decision: bump everything). Conformance
  **33 → 37** (governance surface well-formedness, `adapts ⊆ surface` +
  authority-ref + ≥35-wired, framework leakage guard); `plm_lint` clean.
  **Deferred (CHG-D1):** the spec→CHG promotion gate — until built, spec-level
  promotions are drafted but cannot be gated.

## D-0018 — Cut Claude Code plugin `v0.2.0`; add a repo-root plugin marketplace

- **Date:** 2026-05-23T00:00:00Z
- **Context:** The plugin's last tag (`claude-code-plugin/v0.1.0`) predates the
  8-layer migration; everything since (124-skill 8-layer corpus, 9-agent roster,
  `project-mngt` parking) sat in CHANGELOG `[Unreleased]`. There was also no way
  to *install* the plugin — only a per-plugin `plugin.json`, no marketplace
  manifest.
- **Decisions:**
  1. **Version `0.2.0` (minor), not `1.0.0`.** The 8-layer migration is a large
     feature jump but the skill/command surface may still move; staying pre-1.0
     signals that. Bumped `platforms/claude-code-plugin/VERSION` + `plugin.json`
     `version`. `FRAMEWORK_SPEC_VERSION` stays `0.1.0` (independent streams,
     `docs/PROJECT.md` §2; the conformance test checks `FRAMEWORK_SPEC_VERSION`
     against `framework/VERSION`, not the platform version — verified green).
  2. **Repo-root `.claude-plugin/marketplace.json`** (schema confirmed against
     code.claude.com/docs): marketplace `name: aidoc-flow-framework` (matches the
     repo; reads as `aidoc-flow@aidoc-flow-framework` on install) → plugin
     `aidoc-flow` via relative subdir `source: ./platforms/claude-code-plugin`.
     `version`/`description` set on the entry (optional, not inherited). Install
     command added to root + plugin READMEs.
  3. **Tag deferred to the user.** Annotated `claude-code-plugin/v0.2.0` is cut
     locally on the release commit; the in-container push 403s (5th occurrence
     of the `refs/tags/*` restriction), so the user pushes it from a local clone
     — alongside merging this branch into `main` and relocating CI.
- **Conformance:** 32/32. Recorded in plugin CHANGELOG `[0.2.0]`,
  `docs/TAGGING.md`, and `plans/HANDOFF.md`.

## D-0017 — Park `project-mngt` as legacy (pending review); pull it from the shipped plugin

- **Date:** 2026-05-22T00:00:00Z
- **Context:** `project-mngt` is a generic MVP/MMP/MMR planning *methodology*
  skill (frontmatter `layer: null`, domain-generic `REQ-NN` requirement IDs) —
  it teaches HOW to plan, not an SDD-layer artifact. It does not cleanly fit the
  8-layer engine and needs re-evaluation for fit/placement, so it should not
  ship with the plugin in the meantime.
- **Decision / actions:**
  1. **Parked**, not deleted: moved `platforms/claude-code-plugin/skills/project-mngt/`
     → `legacy/claude-code-plugin/project-mngt/` (Claude Code auto-discovers
     everything under `skills/`, so leaving `skills/` is the only reliable way to
     stop shipping it). Frontmatter `development_status: active → legacy`; park
     rationale + un-park procedure in `legacy/claude-code-plugin/README.md`.
  2. **Neutralized all inbound references** in the shipped surface: `README`
     skill table + prose; `skill-recommender` intent-map + catalog rows;
     `adr-roadmap` (SKILL + quickref) "use instead"/"combine"/related-skills;
     `doc-flow`, `trace-check`, `mermaid-gen`, `workflow-optimizer` cross-links;
     `pm-orchestrator` + `agents/README` rosters. Where a recommendation pointed
     at it for requirement planning, repointed to the requirements layers
     (`doc-brd`/`doc-prd`/`doc-ears`).
  3. **Dropped** the now-dead `("legacy-doc-ref", "project-mngt")` `plm_lint`
     exception (the skill no longer lives under any scanned scope).
  4. **Corrected** the plugin `README` skill counts to the as-built totals
     (112 `doc-*` + 12 non-doc = 124). The migration's documented 142 → 125
     reduction (plugin CHANGELOG `[Unreleased]`) had never been reflected in the
     README; parking `project-mngt` then took 125 → 124.
- **Skill count:** 125 → 124. Conformance unaffected (no count assertion; the
  parked tree is outside `skills/`, `agents/`, `commands/`).
- **Follow-up (review later):** decide whether `project-mngt` is reworked into
  an IPLAN-layer (Layer 8) helper, kept as an out-of-band methodology doc, or
  retired. Tracked in `plans/MIGRATION_TODO.md`.

## D-0016 — Post-migration gap audit: fix plugin-surface residue + harden the gate (not bare-token/prose patterns)

- **Date:** 2026-05-22T03:10:00Z
- **Context:** A post-completion review (cross-checked against the v3.2 source
  on `legacy-ucx-v3.2-read-only`) confirmed the **framework** 8-layer model
  correctly absorbs the deprecated SYS/REQ/CTR layers (SYS→SPEC C4-Component,
  CTR→SPEC interfaces, REQ→EARS atomic-testable). But `plm_lint`'s blind spots
  (it scanned only `skills/`, and its element-code pattern needs a trailing
  `.digit`) let deprecated-layer residue survive in the **plugin surface**:
  `agents/requirements-analyst.md` still modeled REQ as a live layer
  (`BRD→PRD→EARS→REQ→SPEC`, `docs/REQ/`, `REQ-NNN`, 3-segment IDs);
  `skills/trace-check/examples/example_validation_report.md` traced to
  `SYS-002`/`REQ-001`; `doc-validator` linked a non-existent
  `../doc-brd-validator/`.
- **Decision / actions:**
  1. **Fixed** all three: requirements-analyst's lane now terminates at EARS
     (atomic-testable requirements = EARS, per v3.2 REQ→EARS mapping), 4-segment
     IDs, `docs/03_EARS/`; the trace-check example rewritten to 8-layer
     traceability + 2-digit doc refs; the doc-validator BRD row points at the
     existing `../doc-brd-audit/` (doc-brd ships no validator).
  2. **Hardened `plm_lint`:** scan scope extended to `agents/` + `commands/`
     (always enforced); added `legacy-doc-ref` (dash refs `SYS-002`…),
     `legacy-layer-dir` (`06_SYS`/`10_TSPEC`…), and a **context-aware**
     `legacy-3seg-id` pattern (skips lines marked ❌/legacy/→/reject so
     validators' "wrong-format" teaching examples don't false-fail). Already
     wired into conformance via `test_plm_lint.py` (suite stays 32).
- **Deliberately NOT added:** bare-token (`SYS`/`REQ`/`TSPEC`) and N-layer prose
  (`12-layer`) patterns — these occur legitimately in Version-History changelog
  rows across migrated skills; flagging them would force per-file exceptions or
  false failures. The 3-seg line-context heuristic is the safe middle ground.
- **`project-mngt` kept as-is:** it uses domain-generic `REQ-NN` requirement IDs
  (a general MVP/MMP/MMR methodology skill, not SDD-layer-specific); excepted
  from `legacy-doc-ref` in the checker. `doc-naming` is excepted from
  `legacy-3seg-id` (it is the ID-format teaching authority).

## D-0015 — Plugin SPEC-/test-subtype skill families: migrate & keep as helpers (PLM-B4/B5)

- **Date:** 2026-05-22T01:30:00Z
- **Decision:** The plugin's SPEC-subtype families
  (`doc-cspec/dspec/uxspec/riskspec/procspec`) and test-subtype families
  (`doc-utest/itest/stest/ftest/ptest/sectest`) are **kept as plugin-only
  authoring helpers** under SPEC (Layer 6) and TDD (Layer 7) respectively,
  and their bodies are **migrated to the 8-layer model** (paths, IDs,
  chains) like every other family — they are NOT retired and NOT folded
  into `doc-spec`/`doc-tdd`.
- **Why:** The framework defines SPEC and TDD as single unified templates
  with no subtypes, but the *plugin* is free to ship finer-grained
  authoring skills as a value-add (its per-operation granularity is a
  documented Plugin advantage in `docs/PARITY.md`). Retiring them would be
  a real capability loss; folding them into two skills would lose the
  per-subtype slash-commands users rely on. Keeping them as helpers under
  the canonical layers preserves capability while staying spec-conformant
  (they reference, not redefine, the L6/L7 contracts).
- **Consequence:** PLM-B4 migrates `doc-spec` + the 5 SPEC-subtype
  families; PLM-B5 migrates the 6 test-subtype families. Each subtype skill
  must position itself as a specialization of its parent layer (SPEC L6 /
  TDD L7) and reference the single framework template, not a legacy subtype
  template or element-code.

- **Date:** 2026-05-21T05:50:00Z (revised same day — see Note)
- **Decision:** Preserve the pristine pre-migration `ucx_framework`
  project (original root layout) as the **protected, read-only branch
  `legacy-ucx-v3.2-read-only`** (created off `main` at commit `491e8db`,
  byte-identical; branch protection enabled). **Then**, at the Phase 5
  cutover, remove `legacy/` and root `.claude/` from the working branch
  (→ new `main`) so the shipped project is clean. The archive branch +
  git history are the durable record.
- **Why:** User directive — preserve everything ("do not remove legacy
  files"; ensure root `.claude/` is captured too), **then** clean up the
  working branch ("keeping legacy files in [a] separated archived branch
  for future reference then clean up current branch"). A protected branch
  is a more discoverable, enforceably-immutable archive than relying on
  post-deletion git history; with it in place the working-branch removals
  lose nothing substantive.
- **Safety (verified before restoring the removals):** the archive branch
  contains all 7 legacy trees (`ucx_flow_v3`, `ucx_hermes`, `mcp_ucx`,
  `ai_dev_ssd_flow_v2`, `ucx_kb`, `ucx_knowledge`, `hermes_agent_skills`)
  and root `.claude/`. **Caveat:** the archive holds the *pre-migration*
  `.claude/` (236 files, no hooks); the working branch's *migration-era*
  `.claude/` (240 files, incl. the 3 migration hooks) survives removal
  only in the working branch's git history — acceptable, as those hooks
  are obsolete migration scaffolding and the skills were productized into
  `platforms/claude-code-plugin/`.
- **Aligns with** the original cutover policy ("`legacy/` removed /
  archived at the Phase 5 cutover" — `docs/REPO_STRUCTURE.md`,
  `docs/PROJECT.md` §4, `ROADMAP.md` Phase 5, `CLAUDE.md`) — now realised
  via the archive branch rather than history-only deletion. P5-T4
  reconciles those docs to name the `legacy-ucx-v3.2-read-only` branch as
  the archive.
- **Consequence:** Phase 5 keeps its two removal tasks **restored**
  (P5-T2 remove `legacy/`, P5-T3 remove root `.claude/`), each gated on
  the archive branch existing (it does) + explicit confirmation at
  execution; root `.claude/` removal is sequenced **late** (it disables
  the session's own hooks). `CLAUDE.md` is **rewritten** to post-migration
  memory in P5-T4 (it's a root file, not under `.claude/`, so it survives
  the `.claude/` removal).
- **Note (revision):** an interim reading of the user's directives
  (recorded briefly the same day) had this as "retain `legacy/` + root
  `.claude/` in-tree, no removals." Once the protected archive branch was
  created and confirmed, the user restored the original archive-then-clean
  intent; this entry reflects the final decision.

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
