# AI Doc Flow Framework — Roadmap

Where the project is heading. Work is **event-triggered, not calendar-bound** — items
advance when their dependencies and review gates clear, not on fixed dates.

For shipped detail, see [`CHANGELOG.md`](CHANGELOG.md). Backlog and defect tracking live in [GitHub issues](https://github.com/vladm3105/aidoc-flow-framework/issues).

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

- **Hermes parity catch-up** — both platforms declare current spec surface
  (spec `0.41.x`). Hermes has advanced substantially (team-mode + 8-layer playbook
  injection + saga conformance, and now the `audit_threshold` gate + `.aidoc/profile.yaml`
  runtime consumption + the opt-in bounded review→remediate→re-review **quality loop**
  (`hermes/v0.11.0`, HERMES-REVIEW-LOOP-001 Phase 1); the full spec arc is
  satisfied via its vendored `sdd_doc_lint` + shared templates). The residual items
  are capability-level parity deltas — **H-11c** (SHA-256 residue, now unblocked by
  PROVISIONAL-IDS-002) + the cosmetic H-11a sweep — plus the quality-loop **Phase 2**
  (cross-invocation resume / G-R1, and the parallel-review global-lock latency fix from
  the 2026-07-11 pre-prod audit). Tracked in
  [GitHub issues](https://github.com/vladm3105/aidoc-flow-framework/issues?q=is%3Aopen+label%3A%22platform%3A+hermes%22).

- **FRWK-REVIEW-002 (in flight, 2026-07-09):** fixing 46 findings from the 2026-07-09
  plugin + core-docs review across 7 tier-scoped PRs. Plugin PRs (A/B) + docs-of-record
  (F) landed; spec-tier (C/D), engine-agnosticism (E), and CLAUDE.md (G) held for the
  founder. See [`plans/FRWK-REVIEW-002-PLAN.md`](plans/FRWK-REVIEW-002-PLAN.md).

---

## Next

Planned, scoped, not yet started.

- **Claude Code plugin `1.0` cut** — the plugin ships as a pre-1.0 preview (`0.25.0`).
  The enumerated gates for the `1.0` release (consolidated from the 2026-07-11 pre-prod
  audit; previously scattered across `CLAUDE.md` / stubs):
  1. **Hermes parity** — Hermes no longer lags the plugin on the recent spec (see the
     "Hermes parity catch-up" item under **Now**; GitHub issues `platform: hermes`).
  2. **Remove the 2 deprecated redirect stubs** — `doc-review` + `trace-check`
     (both self-document `v1.0.0` removal → `doc-validator`); drops the skill set 52 → 50.
  3. **The "Next" cleanups below** — doc-number independence (#18), the optional
     decomposition layer (#19), and domain profiles.
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

- **PLUGIN-PREPROD-001 (2026-08-02, plugin `0.25.0`).** The pre-production
  hardening that unblocked the plugin deploy: a five-lens review returned
  **BLOCKER** on 2026-07-31 with 23 findings, and **all 23 are closed** across
  five staged PRs ([#410](https://github.com/vladm3105/aidoc-flow-framework/pull/410),
  [#413](https://github.com/vladm3105/aidoc-flow-framework/pull/413),
  [#415](https://github.com/vladm3105/aidoc-flow-framework/pull/415),
  [#418](https://github.com/vladm3105/aidoc-flow-framework/pull/418), and PR 5's
  stages). The review hook no longer executes code from the user's working
  directory and gates on project adoption; the permission-model bypass is
  disclosed and opt-in; the saga driver cannot wedge permanently or report `PASS`
  on reviews that never ran, and its exit codes distinguish terminal states;
  missing PyYAML or an unmet Python floor is diagnosed rather than surfaced as
  lint findings; shipped agents declare their tools; the plugin ships its
  `LICENSE`. **The 23rd finding (M6) closed on 2026-08-02**: the tag cut and the
  public Release are outward-facing acts and were separately founder-gated, and
  the founder authorized both. `claude-code-plugin/v0.25.0` is cut (annotated →
  `e6c6539d`, on the remote) and **the latest published Release is now
  `claude-code-plugin/v0.25.0`**, a pre-release matching `v0.18.0`'s tier since
  the plugin is a declared pre-1.0 preview.
- **IDGEN-NO-GENERATOR (2026-07-26, plugin `0.24.0`, Hermes `0.12.0`).** The
  element-ID generator ships (`rehash --compute`), and no authoring surface
  computes SHA-256 in-prompt any more. 25 surfaces rewritten: BRD calls the tool;
  the five layers without a defined extraction boundary emit a stable opaque
  identifier. Nine of those surfaces — loaded Hermes references shipping runnable
  ad-hoc hash code — were absent from the issue's census and were found by the new
  guard. `--fix` deferred: it would break citations in 8 downstream files, so it
  needs a re-cascade design first. See
  [`plans/IDGEN-NO-GENERATOR-PLAN.md`](plans/IDGEN-NO-GENERATOR-PLAN.md).
- **CHG-OVERLAY-AND-GRANULARITY (2026-08-23, framework `0.41.2 → 0.41.3`, GD-13).**
  Two unrelated clarifications in one spec bump, bundled because GATE-SPEC-E005 makes
  any `framework/**` touch one versioned event. Change management: `09_CHG` is named
  an operational namespace rather than a 9th lifecycle layer, `change_source: spec` is
  stated as always `>= C2` routing to GATE-SPEC, and `GATE-CODE_IMPLEMENTATION.md` §6's
  bubble-up procedure becomes five explicit steps — the draft of which had paired
  `change_source: feedback` with `entry_gate: GATE-03`, a combination Hermes rejects
  outright as `CHG-002`. Citation granularity: six authoring surfaces had drifted from
  GD-03 and told authors that ADR and TDD may be cited at document level, which
  `REFGRAN01` has flagged since June; all six are reconciled. Erratum, so PATCH.
- **GATE-FORM-PARITY (2026-08-16, framework `0.41.0 → 0.41.1`, GD-12).** The gate
  approval form — the surface a reviewer actually fills in — disagreed with the gate
  definitions in both directions, and now cannot. `GATE-03-E008` and
  `GATE-SPEC-W003`, both Security-category and both defined and catalogued since
  `817d9a1a`, had never been added to the form: two checks nobody performed. §2.2's
  upstream-tag counts said 2/3/4 against the registry's 1/1/2, and two further
  documents stated the ADR requirement as the full `@brd @prd @ears @bdd` chain.
  `tests/conformance/test_governance.py::GateCheckIdParity` now asserts check-id
  parity across all six gates × `{E, W}` × the three surfaces, comparing the form's
  *fillable* items rather than its mentions. Closes
  [#433](https://github.com/vladm3105/aidoc-flow-framework/issues/433),
  [#434](https://github.com/vladm3105/aidoc-flow-framework/issues/434),
  [#445](https://github.com/vladm3105/aidoc-flow-framework/issues/445).
- **SPEC-0.41.0-FOLD (2026-08-16, framework `0.40.0 → 0.41.0`, GD-11).** Four
  independent spec corrections shipped as one release, because GATE-SPEC binds
  concurrent `framework/**` edits to a single `VERSION` — the unit of release is
  the version, not the defect. `saga.schema.json` accepts registry-valid 3+ digit
  document IDs; `TAG_SYNTAX.md` **defines** `@chg: CHG-NN`, which the CHG
  auditor's C1 had required at P1 while it was defined nowhere (the one
  additive-normative item, and why this is MINOR); `AI_ASSISTANT_RULES.md`
  generation-order `from` clauses now match the registry's `required_tags`
  instead of contradicting the same document's doctrine; and the PRD auditor's
  C3 section list matches `PRD-TEMPLATE.yaml`, which declares no NFR section.
  Each keeps its own issue and changelog entry, so the per-defect record
  survives the fold.
- **GOV-TODO-ISSUE-SPLIT (2026-07-26, framework `0.39.0 → 0.40.0`, GD-10).** *(Note: superseded on 2026-08-15 when `plans/FRAMEWORK-TODO.md` was retired to a tombstone in favour of GitHub issues as the sole backlog surface).* A
  backlog file is a capture queue, not a publication channel. Tier 2 gains a
  second surface: the queue is unchanged, and an entry that is actionable by a
  non-finder, reproducible at `file:line` with a fix shape, or consumer-visible
  also gets a tracker issue — carrying reproduction, blast radius, a suggested
  fix and what is *not* broken, linked both ways and closed on the same SHA.
  Purely local or speculative entries stay queue-only, so the tracker does not
  become a second copy of the backlog.
- **ELEMENT-ID-LAYER-CONTRACT-001 (2026-07-26, framework `0.38.0 → 0.39.0`,
  GD-09).** One element-ID hash contract with one source: the re-specified
  algorithm is **deleted** from four layer templates and three layer READMEs in
  favour of the `norm()` shape line plus a cross-reference to
  `ID_NAMING_STANDARDS.md`, closing the drift D-0062 left when it reached only
  `BRD-TEMPLATE.yaml`. TDD gains the `## Element IDs` contract it never had
  despite being one of six layers that must carry element IDs — while stating
  explicitly that its field-extraction mapping is Phase 2+, not invented here.
  The inert `placeholder: "0000"` key is removed from all five templates. Locked
  by `tests/conformance/test_element_id_layer_contract.py` over
  `framework/layers/**`; the 19 platform authoring surfaces (#342) and the
  acceptance harness's second implementation (#351) remain open. See
  [`plans/ELEMENT-ID-LAYER-CONTRACT-001-PLAN.md`](plans/ELEMENT-ID-LAYER-CONTRACT-001-PLAN.md).
- **SEED-ABSORPTION-001 (2026-07-24, framework `0.37.2 → 0.38.0`, GD-08).** The
  seed→SDD absorption contract (`SEED_CONTRACT.md`: frozen seed, total
  disposition, `seed_disposition:` BRD carrier, `SEED01`); a regression lock that
  a produced artifact can never carry a templated `TYPE.NN.SS.xxxx` ID
  (`ID03`/`ID01`); and BDD→TDD acceptance pairing (`ACC01` + `acceptance_layers`,
  case-scoped so a traceability-block citation cannot fake a paired test). See
  [`plans/SEED-ABSORPTION-001-PLAN.md`](plans/SEED-ABSORPTION-001-PLAN.md).
- **PROVISIONAL-IDS-002 Phase 1 (2026-07-08, framework `0.34.2 → 0.35.0`).** The
  Model-2 element-ID drift verifier — formalized hash-input contract + opt-in
  `rehash --check` (`IDDRIFT01`, advisory, not in the default lint). Phase 2+
  (`rehash --fix`, all-layer extraction, corpus reconciliation) is
  founder-decided. See
  [`plans/PROVISIONAL-IDS-002-PLAN.md`](plans/PROVISIONAL-IDS-002-PLAN.md).
- **Governance-decision ratifications (framework `0.34.2`).** GD-02…GD-05 spec
  governance decisions ratified.
- **COV03 phase-leak advisory (framework `0.34.0`).** The inverse of COV01's
  escape — flags a `Future`-banded element that a downstream layer already
  realizes.
- **GD-05 author self-claim strip (framework `0.33.0`).** The review lens
  disregards any author-supplied readiness score before scoring.
- **Provisional IDs + first-class reuse (D-0040 / D-0041).** Manual-mode
  provisional IDs (`id_state`/`PROV01`) with the normative SHA-256 algorithm,
  and satisfied-by-reference reuse (`reuse:` frontmatter, `REUSE01`/`REUSE02`).
- **YAML-BDD arc (framework `0.28`–`0.29`).** BDD authored as structured
  `scenarios:` YAML (not Gherkin-in-markdown); `doc-bdd*` skills, template, and
  layer README moved to the YAML carrier.
- **Element-level coverage engine (framework `0.24`–`0.27`).** COV01/COV02
  element-level forward/backward coverage over the `REALIZING_LAYERS` map
  (D-0039) — catches orphaned requirement/scenario elements a doc-level check
  misses.

- **Acceptance-fixtures drift fix (ACCEPTANCE-FIXTURES-DRIFT, no
  VERSION change).** Closes 12 long-standing failures in
  `tests/acceptance/deterministic/` (red on umbrella `PR Checks`
  since 2026-06-02). Three coordinated fixes: `template_sections()`
  honors `_required: false` and `_required_when_subtype: [list]`;
  fullpath upstream goldens gain the element IDs downstream layers
  cite (BRD.01.07.aaaa, PRD.01.09.aaaa) plus `doc_id` for
  SPEC/TDD/IPLAN; per-layer fixture dirs gain 28 upstream sibling
  goldens. Plan: PR #147.
- **Support channels — framework slice (IPLAN-0008 steps 3 + 6, no
  VERSION change).** New public-facing `docs/SUPPORT.md` channel
  directory (four channels: in-product `/aidoc-flow:bug-report` and
  `/feedback`, GitHub Issues direct, web-site `/support`);
  `scripts/sync-version-refs.sh` extended for the web-site home-page
  version badge (sibling fix to the plugin-README drift fixed in
  v0.20.1). Tracked as issue #489 (`WEBSITE-VERSION-BADGE-DRIFT`).
- **Platform README Version cell drift fix (`0.20.0 → 0.20.1`, PATCH).**
  Fixed long-standing drift in `platforms/claude-code-plugin/README.md`
  Platform info table (`Version` cell stuck at `0.6.3` since plugin v0.7.0)
  by canonicalizing the cell to the tag form (`claude-code-plugin/v<X.Y.Z>`)
  and extending `scripts/sync-version-refs.sh` to propagate the tag form
  in platform READMEs. Bug class closed; same drift in
  `platforms/hermes/README.md` flagged in issue tracker for
  Hermes's next bump.
- **bug-report / feedback LLM-drafted issues (`0.19.0 → 0.20.0`, MINOR).**
  `/aidoc-flow:bug-report` and `/aidoc-flow:feedback` now accept a user
  prompt argument (e.g. `/aidoc-flow:bug-report status crashes on empty
  docs/`) and draft a structured GitHub issue from it — concise title +
  sectioned body — using the conversation context (recent commands,
  errors, files) and the environment stamp. Drafted title + body are
  URL-encoded into `?title=&body=`, previewed in chat, then handed to the
  user as a clickable URL. User reviews on github.com and clicks Submit;
  plugin never auto-submits. Refined `.github/ISSUE_TEMPLATE/bug_report.md`
  and `feedback.md` to match. Supersedes the in-flight v0.19.1 PATCH
  (which used `&body=` for a static env block).
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
