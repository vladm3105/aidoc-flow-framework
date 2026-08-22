# Framework spec review — 2026-07-19

Multi-agent review of `framework/` (engine-agnostic spec), branch
`feat/mvp-templates-and-bdd-docs` @ `dad219a7`. Five parallel lenses:
registry/structure, governance coherence, template drift, playbooks,
entry-docs + industry trends. All findings verified against both sides
(quote + grep) before inclusion. Paths relative to `framework/framework/`
unless noted.

Verdict: **NOT ready to tag** — 2 blocker clusters, both introduced or
exposed by the MVP-templates commit, plus pre-existing governance drift
concentrated in the `chg/` subtree and the two earliest auditor playbooks.

---

## BLOCKER

**BL-1 — VERSION 0.37.2 has no CHANGELOG heading; release gate fails.**
`framework/VERSION` = 0.37.2 (bumped by `dad219a7`), but `CHANGELOG.md`
has no `0.37.2` heading — the `[Unreleased]` MVP entry lacks the
`### Added — Framework Spec 0.37.1 → 0.37.2` stamp the file's own
convention (CHANGELOG.md:853-855) requires.
`python3 -m unittest tests.release.test_changelog_entry` **FAILS** on this
branch (`test_changelog_has_entry_for_current_version`).
Fix: retitle the Unreleased entry with the version stamp.

**BL-2 — The 8 new MVP skeleton bodies are non-conformant with the
framework's own normative governance; a doc authored from them cannot pass
`sdd_doc_lint`.** Violation classes (each verified per file):

- **Legacy sequential IDs the governance bans** (ID03): `FR-01`
  (BRD-MVP:49), `REQ-E-01` (EARS-MVP:20), `SC-01` (BDD-MVP:25), `TC-01`
  (TDD-MVP:29) — ID_NAMING_STANDARDS.md:162-163 mandates
  `TYPE.NN.SS.hash` element IDs; EARS-TEMPLATE.yaml:237's own antipattern
  bans exactly this class.
- **No required upstream `@`-tags at all** (TAG01) and doc-level refs where
  element-level is mandatory (GD-03/REFGRAN01). Worse, several drop
  required upstreams entirely vs `LAYER_REGISTRY.yaml` `required_tags`:
  SPEC-MVP:68-71 lists only ADR (registry: ears, bdd, adr);
  TDD-MVP:60-63 only SPEC (registry: ears, bdd, adr, spec);
  IPLAN-MVP:50-53 only TDD (registry: spec, tdd).
- **BDD-MVP violates the normative YAML-BDD carrier** (BDD-SCHEMA-001 +
  REFGRAN01): doc-level `ears: ["REQ-E-01"]` (BDD-MVP:29-30) vs mandated
  element-level `ears: [EARS.01.03.5e2a]` (TAG_SYNTAX.md:64); no `name:`
  field; `priority: "P1"` vs enum `p0-critical|p1-high|p2-medium|p3-low`.
- **"Validates against the same schema" claim is false** (BRD-MVP:2): no
  MVP template has the `metadata:` block conformance requires
  (test_layers.py LayerTemplateMetadata), and section keys diverge from
  the full templates in every layer (STRUCT01 exposure) — e.g. PRD-MVP
  lacks `functional_requirements` entirely; IPLAN-MVP `execution` vs the
  required `execution_commands` for its own declared `code_build` subtype.

---

## MAJOR

### MVP-template governance (root cause of BL-2)

**M1 — MVP templates float ungoverned: unregistered, untested, profile
undefined.** `LAYER_REGISTRY.yaml` registers one `template:` per layer —
no MVP entries; `grep -rn MVP tests/conformance/` is empty; no governance
doc defines an MVP profile; new frontmatter fields (`lifecycle: "mvp"`,
`document_control.*`) are defined nowhere. Contradicts registry/README.md:8-10
("single source of truth") and framework/README.md:88-91 (conformance
"verifies templates match the registry").

**M2 — MVP ID collisions/inconsistencies.** BRD-MVP:6 claims
`brd_id: "BRD-00"` — colliding with the reserved `-00` index number
(ID_NAMING_STANDARDS.md:251-252); PRD-MVP:69 propagates it. IPLAN-MVP:6
uses 3-digit `IPLAN-001` vs `IPLAN-NN` everywhere else in the spec
(leak from the user-global IPLAN-NNN convention — different artifact family).

**M3 — No playbook handles MVP-profile documents.** Any doc authored
structurally from PRD-MVP misfires every §-numbered PRD check; nothing
tells a lens what to do with an MVP-lineage doc.

### Registry / README drift

**M4 — Layer README "Upstream" rows drifted from `required_tags`.**
SPEC/README.md:37 "ADR + BDD" (registry: ears, bdd, adr);
TDD/README.md:26 "SPEC + ADR + BDD" (registry adds ears);
IPLAN/README.md:59 names ADR, in neither `required_tags` nor
`can_reference`. SPEC:36 and TDD:28 also still claim "Single unified
template" while the same README's Files table lists two variants.

### Governance cross-doc contradictions (pre-existing)

**M5 — saga.schema.json:29-30 pattern `^[A-Z]+-[0-9]{2}$` vs the
authoritative `id_patterns.document` `^[A-Z]+-\d{2,}$`** (REVIEW_SAGA.md:71,
ID_NAMING_STANDARDS.md:5, LAYER_REGISTRY.yaml:215). The schema's own
"must change in lockstep" comment was not honored; a `BRD-100` journal
fails schema validation while conforming to the spec.

**M6 — chg/ subtree still teaches the abolished cumulative-tag contract.**
GATE-03:232-238 and GATE_ERROR_CATALOG.md:206,214-220 instruct "add all
4 upstream tags @brd/@prd/@ears/@bdd to ADR" while their own E007 rows
say 2 tags (`@ears @bdd`, per necessary-upstream). TRACEABILITY.md:42-46
records the 4-tag contract was abolished because it caused trace
fabrication. Also GATE-01:199, GATE-03:235-238, GATE-08:227 give
document-level tag examples that GD-03/REFGRAN01 now flags.

**M7 — "CHG C1 = no self-approval" citation is inverted.**
REVIEW_REMEDIATION_FLOW.md:134, DEFINITION_OF_DONE.md:21-22,
DECISIONS.md:235 (GD-02) cite "CHG C1: no self-approval" — but in the
CHG overlay C1 is the *trivial* change level whose approval matrix is
literally "Self" (CHG-TEMPLATE.yaml:212-213,
GATE_INTERACTION_DIAGRAM.md:244). No such failure code exists in chg/.

**M8 — Two incompatible threshold models.** THRESHOLD_NAMING_RULES.md:42-57
mandates BRD/PRD/ADR `## Thresholds` blocks and citations like
`@threshold: ADR.15...` / `BRD.02...`; REVIEW_TEAM.md:130-134 (TH-RES-001)
and the reference linter (sdd_doc_lint:2375, PRD-only regex) resolve
PRD citations only; BRD/ADR templates have no thresholds block — every
BRD./ADR. citation the rules mandate is unresolvable-by-design and
unchecked. Also LINT_RULES.md:54 flat "error" vs REVIEW_TEAM.md:139-141
two-tier P1/P2.

**M9 — playbooks/08_IPLAN/auditor.md:59-70 mandates (P1) what
ID_NAMING_STANDARDS.md:172-176,191-194 exempts and forbids penalizing:**
required `IPLAN.NN.SS.xxxx` step IDs (spec: MAY, "do not penalize") and
element-level `@spec: SPEC.NN...` resolution (spec: SPEC is
element-ID-exempt; `@spec: SPEC-NN` is doc-level per TAG_SYNTAX.md:24,67-68).

**M10 — playbooks/02_PRD/auditor.md:56-72 enforces a fictitious PRD
outline.** Its C3 mandatory-section list (§1 Overview … §15 Document
Control) matches neither PRD-TEMPLATE.yaml (15 sections, Document
Control = §1, §14 Traceability, §15 Glossary; no Overview/Non-Goals/
Personas/NFRs) nor the corpus; C4/C5 §-pointers are off accordingly.
Sole outlier — sister PRD playbooks use correct numbering.

### Entry-doc overclaim

**M11 — Repo README.md:90 (+ :158,:189,:261, mirrored in DESC.md)
presents "content-hash element IDs" as a delivered guarantee.** The spec
defines them as "intended as content hashes"; IDs are LLM-generated
stable strings, hash-verification is opt-in/advisory (`rehash --check`,
IDDRIFT01) and not run over the corpus (ID_NAMING_STANDARDS.md:129,142-146;
D-0040/D-0061). Qualify the claim.

---

## MINOR (grouped)

- **MVP integration gaps:** QUICK_REFERENCE.md:11-20 Templates table and
  AI_ASSISTANT_RULES.md:5 omit MVP skeletons + the "not standalone"
  selection rule; framework/README.md:61-64 layout omits them;
  08_IPLAN's YAML index template alone got no MVP reference line
  (asymmetric vs the 7 .md indexes). Intra-family drift: BRD-MVP uses
  `upstream_documents`/`downstream_artifacts` vs `upstream`/`downstream`
  in the other 7; MVP status enums lowercase (`"draft"`) vs capitalized
  full-template enums (`Draft`/`Proposed`) — STALE01/DoD tooling matching
  `Approved` never matches MVP-lineage docs.
- **Registry nits:** LAYER_REGISTRY.yaml:230 dead anchor
  (TRACEABILITY.md has no §"Element-level coverage"; content lives under
  "## Coverage gates"); :127 IPLAN tmp/ path wrong per its own path
  convention; `optional:` field (BDD/ADR `false`) contradicts
  ADAPTATION_SURFACE.yaml `skippable: [BDD, ADR]` and is read by no tool.
- **Governance nits:** REVIEW_TEAM.md:144-145 dead anchor ("Structural
  floor checks"); :305 Auditor-C1 layer list wrong at both ends (omits
  IPLAN/CHG, includes BRD whose C1 is different); PROFILE-TEMPLATE.yaml:28
  says 5 knobs (actual: 6; missing `quality_loop_max_iterations`) and
  carries Claude-Code vocabulary ("Task subagent fan-out") in the
  engine-agnostic spec; TRACEABILITY.md:122 BDD-Ready gate names
  `spec_trace`, a field no EARS artifact carries;
  THRESHOLD_NAMING_RULES.md:282 "max 5 segments" vs its own 4-segment
  grammar; ADAPTATION_SURFACE.yaml:75 `default: "team"` unqualified vs
  ADAPTATION.md:133-134 "team at gates, single_pass at write-time".
- **Playbook nits:** 01_BRD/auditor.md:49-51 lists "§Personas" as
  mandatory (BRD template: PRD owns personas); BRD/PRD auditors state a
  `{doc-slug}` element-ID pattern vs the standard's two-digit `doc_id`;
  08_IPLAN/operator.md:85-89 attributes reversibility to SPEC (ADR owns
  it; SPEC template has zero such content); playbooks require fields no
  template scaffolds (ADR reversibility label; TDD per-class runtime/flake
  budgets → every conformant TDD draws those findings); "No-findings
  rationale" section duplicated in 19/51 files, absent in 32.
- **Doc nits:** DESC.md is an unreferenced, drifting near-duplicate of
  README (Hermes 0.7.3 vs 0.11.1, spec 0.36.2 vs 0.37.2 — dated snapshot
  disclaimer present); docs/REPO_STRUCTURE.md "as-built" misses 3 of 16
  workflows, omits `playbooks/`+`templates/` from the framework tree,
  names 3 of 10 tools; docs/PARITY.md self-contradicts on stub-removal
  target (v1.0.0 at :10 vs v0.6.0 at :148); entry docs reduce EARS to
  "(WHEN-THE-SHALL-WITHIN)" though the template mandates 5 patterns;
  04_BDD/README.md:22-23 claims Gherkin "supported as an output format" —
  no such capability exists anywhere; IPLAN-MVP:25 comment says "from TDD
  contract" on a SPEC ID; CHG-00_index title "CHG-000" (3 digits).

---

## Verified consistent (checked, no defect)

Playbook rosters/weights match REVIEW_CREWS.yaml byte-for-byte for all 9
crews (SPEC's missing auditor and BRD's missing tech_lead/operator are
declared crew design); severity vocabulary and the 0-100 scoring table
are identical across all 51 playbooks; CHG-as-overlay modeling is
consistent everywhere (8 layers + overlay); gate numbering gaps are
declared range-coverage; ADAPTATION_SURFACE cascade_rule matches the
registry verbatim; SPEC_DRIVEN_DEVELOPMENT_GUIDE layer table matches the
registry; QUICK_REFERENCE's upstream-tags column matches `required_tags`
for all 8 layers; governance/README's 21-row table matches the directory;
LINT_RULES exactly covers the 22 linter rule IDs; repo README platform
versions match VERSION files; PARITY playbook counts match disk;
conformance suite currently passes (208 OK) — which is precisely why
BL-2/M1 matter: the MVP surface is invisible to it.

---

## Structural recommendations

1. **Register or explicitly de-govern the MVP skeletons.** Add
   `mvp_template:` per layer to LAYER_REGISTRY.yaml + conformance
   assertions (existence, metadata parity, required-tag slots), or state
   in registry/README.md that they are non-normative conveniences.
2. **Derive skeletons mechanically from the full templates** (strip
   `_guidance`/`_example`/`_antipatterns`, keep exact section keys,
   `TYPE.NN.SS.0000` placeholders, required `@`-tag slots) — the current
   bodies read as authored from a pre-migration UCX-era schema.
3. **One GATE-SPEC sweep of the chg/ subtree** for the two systematic
   staleness classes (cumulative-tag resolutions; doc-level tag examples)
   — the subtree predates GD-03 + NECESSARY-UPSTREAM-001.
4. **Make prose-vs-machine contracts enforceable:** conformance assertion
   that saga.schema.json's `artifact_id.pattern` equals the registry's
   `id_patterns.document`; derive README "Upstream" rows and
   QUICK_REFERENCE tags from the registry; add a canonical
   `section_number` map to template metadata so playbook §-references are
   mechanically checkable; give the registry's `optional:` field defined
   semantics tied to `skippable` or delete it.
5. **Name the real invariant** behind "CHG C1 no self-approval"
   (judge ≠ generator) and map/disclaim the two severity vocabularies
   (P0-P3 vs critical/medium/low).

## Industry-trend opportunities (mid-2026)

- **TREND-1 — AGENTS.md:** emit an `AGENTS.md` in scaffolded target
  projects (and consider aliasing AI_ASSISTANT_RULES.md to it) — now the
  de-facto agent-instruction file auto-discovered by Claude Code, Codex,
  Cursor, Copilot, Gemini CLI, etc. (<https://agents.md>)
- **TREND-2 — Constitution slot:** Spec Kit's `memory/constitution.md`
  (non-negotiable project principles every generation step checks against)
  has become the recognizable SDD idiom; the adaptation surface is knobs,
  not principles. (<https://github.com/github/spec-kit>)
- **TREND-3 — Post-implementation spec↔code drift detection:** gates stop
  at IPLAN; nothing flags later code edits diverging from SPEC/TDD.
  (<https://arxiv.org/pdf/2606.27045>)
- **TREND-4 — Spec citations in commit metadata:** commit-level code→spec
  linkage (e.g. `refs @spec: SPEC-NN`) is a cheap, lintable extension of
  the existing tag machinery; docs/TAGGING.md covers release tags only.
- **Validation, no action:** AWS Kiro's EARS adoption independently
  validates the L3 choice; a Kiro `requirements.md` → EARS import is a
  possible future interop point. (<https://kiro.dev/docs/specs/>)
