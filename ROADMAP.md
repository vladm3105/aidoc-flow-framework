# AI Doc Flow Framework — Multi-Platform Roadmap

| Field            | Value                                                        |
|------------------|--------------------------------------------------------------|
| Project          | AI Doc Flow Framework (multi-platform)                       |
| Status           | **Migration complete** (cutover shipped as `v1.0.0`); post-cutover development — latest project release `v1.1.0` |
| Development      | `main` + short-lived `claude/*` feature branches (the migration branch is merged and deleted) |
| Origin           | Forked from `ucx_framework` v0.20.4 (preserved on `legacy-ucx-v3.2-read-only`) |
| Cutover          | `v1.0.0` — done; `main` is the multi-platform project        |
| Created          | 2026-05-18                                                   |

## Goal

Deliver the document-flow framework as **one engine-agnostic specification**
with **two independent delivery platforms**:

- **Platform A — Hermes AI**: MCP-server engine (existing `ucx_hermes`).
- **Platform B — Claude Code plugin**: native Claude Code engine — skills,
  agents, commands, hooks. No MCP backend; Claude itself replaces Hermes.

The two platforms share the `framework/` spec and nothing else. Each versions,
releases, and changes independently.

## Version Streams

Three independent SemVer streams (see `docs/PROJECT.md`):

- **Framework spec** — the shared contract.
- **Hermes AI platform** — declares the spec version it conforms to.
- **Claude Code plugin** — declares the spec version it conforms to.

The *project-level* version below tracks migration milestones only.

## Phases

### Phase 0 — Planning & Scaffolding  → `v0.1.0`

- Working branch created; planning baseline tagged.
- `ROADMAP.md`, `CHANGELOG.md`, `docs/PROJECT.md`, `docs/REPO_STRUCTURE.md`.
- `platforms/` directories established.
- Status: **complete** (`v0.1.0`).

### Phase 1 — Framework Spec Extraction  → `v0.2.0`

- **Step 0 — Legacy isolation (done):** all pre-migration content moved into
  `legacy/`; legacy GitHub Actions workflows disabled.
- Consolidate engine-agnostic content from `legacy/` into `framework/` (layers,
  registry, governance, CHG overlay).
- Define the shared conformance test suite under `tests/conformance/`.
- Tag `framework/VERSION` at its first independent release.
- Status: **complete** (`v0.2.0`) — `framework/` fully assembled, 25-test
  conformance suite green, framework spec released as `framework/v0.1.0`.

### Phase 2 — Platform A: Hermes Re-homing  → `v0.3.0`

- Copy `legacy/ucx_hermes/` + `legacy/mcp_ucx/` into `platforms/hermes/`.
- Point Hermes at `framework/`; declare `framework_spec_version`.
- Hermes passes the conformance suite.
- Status: **complete** (`v0.3.0`, `hermes/v0.1.0`).

### Phase 3 — Platform B: Claude Code Plugin  → `v0.4.0`

- Scaffold `.claude-plugin/plugin.json`.
- Port the `doc-*` skill set, commands, and agents into the plugin.
- Remove all Hermes/MCP dependency — Claude is the engine.
- Plugin passes the same conformance suite.
- Status: **complete** (`v0.4.0`, `claude-code-plugin/v0.1.0`).

### Phase 4 — Conformance & Independence  → `v0.5.0`

- Both platforms green on the shared conformance suite.
- Independent per-platform `CHANGELOG.md` and CI.
- Parity report: feature gaps between platforms documented.
- Status: **complete** (`v0.5.0`).

### Phase 5 — Cutover  → `v1.0.0`

- New project replaces `main`.
- Legacy trees archived.
- Tag `v1.0.0`; platforms tag their own first stable releases.
- Status: **complete** (`v1.0.0`). In-tree `legacy/` + dev-time root
  `.claude/` removed (archived on `legacy-ucx-v3.2-read-only`); docs
  finalized; final verify PASS 17/17 (`plans/P5-T5-VERIFY.md`).
  Tag scope (P5-T1 Q4): project `v1.0.0` only; `framework/` stays
  `0.1.0`; plugin stays `0.1.0`; optional `hermes/v0.1.1` for the
  api_runner fix. The `main` force-replace + tag pushes are
  user-authorized local-clone actions (see `plans/MIGRATION_TODO.md`
  P5-T6).

## Development sequencing — plugin-first

**Policy (2026-06-06):** post-cutover development sequences
**plugin-first, Hermes-second.** Each feature is developed and verified
on the Claude Code plugin first (where the acceptance suite exercises
it end-to-end against the url-shortener seed); the Hermes equivalent
batches at a natural completion point — currently after Phase 4
propagates the saga driver to PRD..IPLAN.

Deferred Hermes work is tracked in
[`plans/HERMES-BACKLOG.md`](plans/HERMES-BACKLOG.md) — the single
source of truth for "what Hermes still needs to catch up on." Current
items: H-1 SAGA-PARITY-001 Phase 3 (G-R1 invariant), H-2
REVIEW-CALIBRATION-001 lens sub-checks. New items get appended there
when plugin features land.

Plugin-first is a sequencing choice, not a permanent asymmetry. Both
platforms still ship against every framework-spec change (GATE-SPEC).

## Post-Migration — Tracked TODOs

Change management (the gated CHG process) is **deliberately deferred** during
migration. It is re-introduced after Phase 5. See `docs/PROJECT.md` §
Change Management for the full policy.

| TODO | Decision (recorded) | Revisit |
|------|---------------------|---------|
| ~~**CHG-D1 — CHG implementation model**~~ ✅ **DONE (2026-05-23, D-0020)** | CHG implemented as **skills + CI/CD**, both platforms, against the shared spec. Added **GATE-SPEC**, the *meta* gate governing `framework/` spec changes (orthogonal to the artifact gates). Record-level checks (E001–E004) run in the plugin `gate-check`/`doc-chg` skills and the Hermes `validation/chg_rules.py`; diff-aware checks (E005 VERSION bump, E008 CHANGELOG) ship as `tests/chg/spec_gate.py` + a staged CI workflow; static checks (E006 spec-version match, E007 suite green) are the conformance suite; the human sign-off (E004) is GitHub branch protection / required reviewers — a skill never self-approves. Unblocks `knowledge-extractor` spec promotion. | Done |
| ~~**CHG-D2 — CHG as a `framework/` decision**~~ ✅ **DONE (2026-05-23)** | Established `framework/governance/DECISIONS.md` — the spec's own durable decision register — and recorded CHG-D1 there as **GD-01** (engine-agnostic). The migration log's spec-affecting decisions now graduate here; D-0013 + D-0019 are listed pending. Recording it was itself a GATE-SPEC change (framework spec 0.3.0 → 0.3.1). | Done |

## Post-v1.0 — Shipped

Delivered after the cutover (project release `v1.1.0`; framework spec `0.1.0 →
0.13.0`):

- **Canonical plugin skill set** — the corpus was pruned/recreated to one
  standard (P3-T6/T7) and settled at **52 skills (50 active + 2 deprecated stubs)** in plugin v0.4.0, after `skill-recommender`/`workflow-optimizer`/`context-analyzer` folded into `doc-flow` and `doc-review`/`trace-check` were folded into `doc-validator` (the latter two retained as deprecation redirects through v0.5.0).
- **Project adaptation overlay** (ADAPT, D-0019) — `framework/governance/
  ADAPTATION.md` + `ADAPTATION_SURFACE.yaml` (a closed knob set) and the
  `project-profile` / `knowledge-extractor` skills.
- **Change management returned** (CHG-D1/D2 above) — **GATE-SPEC**, the
  framework-spec change gate, enforced by skills + CI + branch protection;
  recorded as **GD-01** in `framework/governance/DECISIONS.md`.
- **Review-team model** (framework `0.8.0`) — `framework/governance/REVIEW_TEAM.md` defines the multi-persona review crews, the hub blackboard, the deterministic weighted/capped scoring + conflict policy with the structural gate as a reproducible floor, and the create/review/remediate shapes; `REVIEW_CREWS.yaml` declares the per-layer crews + weights. `ADAPTATION_SURFACE.yaml` gains the `review_mode` knob (`team`|`single_pass`).
- **C4 + DFD + sequence diagram standards** (framework `0.8.1`) — `framework/governance/DIAGRAM_STANDARDS.md` is the authority for per-layer diagrams: BRD c4-l1/dfd-l1, PRD c4-l2/dfd-l2/sequence, ADR decision sequence (now required, not optional), SPEC c4-l3/dfd-l3. Both platforms' review and creation agents wired to the standard.
- **Token-efficient authoring governance** (framework `0.9.0` → `0.10.0`) — `framework/governance/AUTHORING_STYLE.md` canonicalises the elimination list, form enforcement, form-preference order, and per-section size targets; promoted to canonical via `DOC_GOVERNANCE_CORE.md` principle 7. Every section in every layer template (76 sections) gains a `_size_target` key; `sdd_doc_lint` STY02 reads the per-section target instead of a flat default. Wired into every `doc-<layer>` (creation) and `doc-<layer>-audit` skill.
- **`.aidoc/` provenance tier** (framework `0.11.1`) — `framework/docs/AIDOC.md` formalises a third committed documentation tier per project: audit, review consensus, remediation, validation, security, and quality reports — the AI's working notes that answer *"how did the AI arrive at the output in `docs/`?"* without a re-run. Four-tier layout: `seed/`+`chg/` (inputs), `docs/` (outputs), `.aidoc/` (provenance), `logs/<TS>/` (tool internals, gitignored).
- **Pre-deployment acceptance test suite** — `tests/scripts/test-acceptance.sh` drives every active plugin surface element (50 skills + 11 agents + 1 command + 1 hook = 63 total) against a named example's seed as the release gate. Methodology lives at `tests/ACCEPTANCE.md` (engine-agnostic, applies to any future example). Driver supports `--mock`/`--no-live`/`--dry-run`/`--live`, `--promote` (archives prior chain to `docs-archive/v<X.Y.Z>/` and commits the freshly-produced chain), `--push`, resume on SIGINT/TERM with incremental `summary.json` + RUNNING stubs, partial execution via `--element=<name>` / `--from-layer=<N>` / `--to-layer=<N>`, retry-on-transient-HTTP, per-skill timeout, per-layer runtime cap, `--cost-cap=<USD>`, and `--skip-completed=<path>`. Schema v1.2 (`tests/scripts/test-acceptance.schema.json`) covers the combined summary + per-element shape. First seed: `examples/url-shortener/` (URL-shortener service + visit-rate analytics dashboard CHG). Adding a sibling example is a `seed/` + `chg/` + thin README — no script changes. Wired into `release.yml` on tag push.
- **Test runners co-located under `tests/scripts/`** — `test-plugin.sh`, `test-layer.sh`, `test-fullpath.sh`, `test-acceptance.sh` all live inside the framework; the framework is fully self-testable with no parent-repo dependency.
- **Pre-commit + security tooling** — `.pre-commit-config.yaml` (ruff, bandit,
  markdownlint, yamllint, detect-secrets, **gitleaks**, pip-audit, conformance) and CI
  workflows for pre-commit, **CodeQL**, and the GATE-SPEC gate; `SECURITY.md`;
  refreshed `.github/` metadata (CODEOWNERS, dependabot, labeler — INFRA-1).
- **`adversary` lens partition** (framework `0.12.0`, CHAOS-SEC-SPLIT-001, D-0030) — split the single `adversary` review lens into `chaos_engineer` (reliability / NFR / failure-mode) + `security_engineer` (threat-model / security-controls) with per-layer crew weight redistribution in `REVIEW_CREWS.yaml` (BRD: chaos 12 / security 8; ADR: chaos 8 / security 12; PRD/SPEC/TDD equal; IPLAN chaos-only). `REVIEW_TEAM.md` adds a `## Weight allocation rules` subsection codifying the four-category allocation protocol.
- **Review-saga lifecycle promoted to framework spec** (framework `0.13.0`, SAGA-PARITY-001 Phase 1, D-0031) — `framework/governance/REVIEW_SAGA.md` codifies the engine-agnostic saga state machine (11 states), transition table, journal schema, break-circuit policy, and `FRAMEWORK_SPEC_VERSION` semantics; `framework/governance/saga.schema.json` is the formal JSON Schema for the per-run saga journal. Supersedes D-0005's scope-narrowing premise; both platforms declare intent to conform.
- **Plugin BRD saga driver** (plugin `0.6.0` → `0.6.1`, SAGA-PARITY-001 Phase 2 + Amendment 1) — first plugin implementation of the saga lifecycle. v0.6.0 used cooperative enforcement (SKILL-prompt-driven) and empirically failed live verification. Amendment 1 (v0.6.1) replaced it with `tools/saga_driver.py` (Python stdlib-only, vendored alongside the framework bundle): preemptive script-driven enforcement; reads/writes `saga.json` directly; validates every transition against an embedded table; dispatches each phase as a separate `claude -p` subprocess with `timeout 1800s`. 7 in-flight bugs (B1-B7) fixed on the same branch per the submit-only-finalized-work principle. Verified end-to-end on the 4th live BRD cascade (`status: CLOSED`, score 96/100, 10/10 pass criteria). PRD..IPLAN propagation deferred to Phase 4.
- **5 content sub-checks across 8 audit SKILLs** (plugin `0.6.2`, REVIEW-CALIBRATION-001) — adds A1 cell-actionability + A2 assumption-capture + A3 cross-section pointer-validity (auditor lens), BA1 acceptance-criterion testability (business_analyst lens), SE1 deferred-decision safety (security_engineer lens) uniformly across all 8 layer audit SKILLs. Catches 5 substantive content-quality issues that v0.6.1's review missed; before/after BRD comparison confirmed remediation. Section references use concept names not § numbers so wording is uniform across layer templates. No spec touch, no new lens.
- **Project-level conventions** — "Submit only finalized work" + "Minimal-and-realistic plans" + "Two-cycle plan review" + "Plugin-first sequencing" — codified in CLAUDE.md and ROADMAP.md. Deferred Hermes work tracked in `plans/HERMES-BACKLOG.md`.

## Post-v1.0 — Planned Capabilities

### Domain profiles — generalizing the IPLAN beyond software

The framework's purpose is to produce a fully-traceable, gate-approved
**IPLAN** as its terminal artifact (D-0012). v1 scopes this to **software +
devops** — the current SDD layers (EARS, BDD, ADR, TDD) are software-native
and stay that way for v1.

Post-v1.0, generalize the IPLAN to other task domains via a **domain-profile**
mechanism — additively, without reworking the core:

- **Core (domain-neutral):** the flow engine, the gate model, traceability,
  the IPLAN schema, and conformance. Already domain-independent.
- **A profile:** declares which layers apply for a domain and their schemas.
  - `profile: software` — ships in v1 (the current layer set).
  - `profile: devops` — v1 (devops-flavored layers and thresholds).
  - `profile: <non-technical>` — post-v1.0, additive: e.g. operational
    runbooks, compliance/audit planning, research plans. Each new profile is
    new layer definitions, not a change to the core.

This makes "an IPLAN for any purpose" an architectural property of the engine
while keeping every release's scope honest. Revisit after the v1.0.0 cutover.

### The IPLAN library — the corpus is the asset

A single IPLAN is reproducible and low-value. The strategic asset is a
**curated, maintained library of proven IPLANs** — codified, executable
institutional knowledge (D-0012, refinement R2). Post-v1.0, build the library
as a first-class capability:

- **Planned vs executed state** — an IPLAN is *planned* (confirmations
  pending) or *executed* (confirmations satisfied with evidence). The executed
  IPLAN is the auditable trail; audit depth scales with the work's criticality
  (D-0012, R1).
- **Proven-entry gate** — an IPLAN earns library membership only once executed
  and audited.
- **Composition** — distinguish an IPLAN *template* (the proven pattern) from
  an *instance* (a parameterised run); allow IPLANs to compose other IPLANs.
- **Freshness** — each library IPLAN records when it was last proven and
  against which versions; conformance flags stale entries for re-validation.

This is the post-v1.0 strategic destination — the framework as a system of
record for an organisation's executable process knowledge. Revisit after the
v1.0.0 cutover.
