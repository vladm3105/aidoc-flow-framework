# AUTHORING-STYLE-FOLLOWUP — TODO

| Field      | Value                              |
|------------|------------------------------------|
| Source     | Authoring-style scope confirmation |
| Status     | PLANNED — 2026-05-30T23:30:00Z     |
| Feeds      | future PRs (one per item)          |

## Context

The initial token-efficient authoring rollout landed in PR `feat/authoring-style-governance`:
new `AUTHORING_STYLE.md`, governance-core principle 7, references and a style
check in all 8 layer creation + audit skills, and a conformance test. The
items below were explicitly **out of scope** for that PR and remain as
follow-up work.

## Follow-up items

### TODO-AS1 — Skill-body terseness retrofit

Audit each SKILL.md prose for token bloat (verbose introductions, redundant
restatement of templates, prose where a table fits). Today the skills total
~42 000 words across 55 files; targeted compaction can reduce that by an
estimated 20–30 % without losing instructional content.

Suggested approach: for each skill, collapse Purpose + When to Use + Layer
Guidance preambles into bullets + tables; remove restatement of upstream
template content (`@brd`/`@prd`/etc. references suffice); keep Examples
sections terse (one example each, not a gallery).

Acceptance: average SKILL.md word count drops to ≤ 600 (currently 756); no
skill exceeds 1 200 words (currently 1 608 max).

### TODO-AS2 — Per-section size targets in templates

`AUTHORING_STYLE.md` defines section-body defaults (≤ 200 words, table, or
diagram + caption). Some sections genuinely need more — e.g. a complex BRD
§4 Business Objectives or a SPEC §5 Behavior. The right mechanism is a
template-declared `_size_target:` key per section that overrides the default,
making the bound discoverable at audit time without prose surgery.

Suggested approach: add `_size_target:` to every section in each template
(`<LAYER>-TEMPLATE.yaml`); update audit skills to read it; tighten the global
default in `AUTHORING_STYLE.md` accordingly.

Acceptance: each template section has an explicit `_size_target` (words, items,
or `default`); audit skills consume it.

### TODO-AS3 — Automated style linter

Today the audit-time style check is **declarative** (the auditor reads
`AUTHORING_STYLE.md` and applies it). A deterministic structural linter would
catch banned phrases and oversized sections without LLM judgement, matching
the role `sdd_doc_lint` plays for structure.

Suggested approach: extend `tools/sdd_doc_lint/` with a `style` check pass —
regex list for banned phrases + word-count comparison vs `_size_target` (or
the global default) per section. Wire into the existing `doc-review.yml` CI
workflow alongside the structural lint.

Acceptance: `python3 -m sdd_doc_lint --style <docs/>` reports banned phrases
and oversized sections; CI green is required for `pre_merge`.

### TODO-AS4 — Audit-fixer auto-fix path for style violations

`doc-<layer>-fixer` skills currently apply structural fixes. They should also
apply mechanical style fixes flagged by audit: collapse paragraphs to bullets,
remove banned filler ("in order to", "the fact that"), substitute superlatives
with measurable claims (where the underlying number is available in upstream
docs).

Suggested approach: add a "Style fixes" subsection to each fixer's
auto-fixable list with a small ruleset (filler substitution, paragraph →
bullet collapse when ≥3 homogeneous items, etc.). Leave verbose-paragraph
rewrites as `manual_required`.

Acceptance: fixer skills cite `AUTHORING_STYLE.md`; auto-fix table includes a
"Style" row with specific rules; audit-fixer cycle resolves Tier-2 style
findings without manual edits.

### TODO-AS5 — CHG family extension

Scope confirmation excluded the CHG (change-management) family from the
initial rollout. CHG records are also published artifacts that benefit from
the same style discipline.

Suggested approach: extend `doc-chg`, `doc-chg-audit`, `doc-chg-fixer`,
`doc-chg-autopilot` to reference `AUTHORING_STYLE.md`; add the style check to
`doc-chg-audit`'s checklist; extend the conformance test to cover CHG skills.

Acceptance: CHG family is symmetric with the 8 layer families; conformance
test sees CHG.

### TODO-AS6 — Tighten verbose template `_guidance` text

Spot-check found a few minor inflators in current templates (e.g. PRD
`_guidance` uses "Elaborate" repeatedly; BRD section 4 has long narrative
preambles in `_guidance`). These don't violate `AUTHORING_STYLE.md` (the
`_guidance` is not the artifact prose) but they encourage verbose authoring.

Suggested approach: pass through each template's `_guidance` blocks and
substitute concrete imperative instructions ("Define X in ≤ 1 sentence") for
narrative guidance ("Elaborate on X"). Coordinate with `AUTHORING_STYLE.md`
size targets.

Acceptance: no template `_guidance` block exceeds 5 sentences; no `_guidance`
contains a banned phrase from `AUTHORING_STYLE.md`.

## Document drift-detection gaps

Surfaced during a follow-on review of the framework's document drift detection
posture. Each item below is a gap where document-side drift can slip past the
current five-layer defense (authoring skill → audit skill → `doc-flow` →
`sdd_doc_lint` → conformance tests). Scope shifts here from authoring style
to drift detection broadly; items kept in this plan to avoid scattering.

### TODO-AS7 — `@threshold:` cross-layer value consistency

Threshold values appear in multiple layers (EARS quality attributes → BDD
scenarios → SPEC behavior → TDD test thresholds). The same `@threshold:` key
should resolve to the same numeric value everywhere it is cited. Today this
is enforced only by `doc-<layer>-audit` Tier 2 prose ("thresholds consistent
across sections and with the BRD source") — LLM judgement, not deterministic,
and silently misses cross-layer inconsistencies.

Suggested approach: extend `tools/sdd_doc_lint/` with a `thresholds` pass —
walk every artifact, collect `@threshold: TYPE.NN.{category}.{key}` declarations
and resolutions, fail when one key resolves to ≥ 2 distinct numeric values
across the corpus, or when a numeric value appears inline in prose without a
matching `@threshold:` key (the "duplicated inline" case in
`THRESHOLD_NAMING_RULES.md`).

Acceptance: `python3 -m sdd_doc_lint --thresholds <docs/>` reports per-key
value tables and flags every cross-layer mismatch; wired into the existing
`doc-review.yml` CI as a blocking check.

### TODO-AS8 — Frontmatter ↔ Document Control ↔ revision-history consistency

Every artifact carries three parallel statements of status/version/dates:
YAML frontmatter, the Document Control table, and the revision-history block.
They drift trivially (frontmatter says `Approved`, table says `Draft`;
frontmatter `version: 1.0.0`, latest revision-history row `1.1.0`).
Detectable deterministically.

Suggested approach: extend `sdd_doc_lint` with a `frontmatter-consistency`
pass — parse the three sources, fail on any mismatch. Specifically: frontmatter
`status`/`version`/`last_updated` must match the Document Control table row;
Document Control `Version` must match the most recent revision-history
`Version` cell.

Acceptance: structural lint catches frontmatter↔body drift; existing audit
skills' Tier 2 "frontmatter metadata" check is upgraded from advisory to
blocking-via-lint.

### TODO-AS9 — Staleness detection (last-audited + template-version-at-audit)

Audit reports (`<TYPE>-NN.A_audit_report_v*.md`) are generated against the
*current* template, but artifacts can carry an `Approved` status from an audit
run six months ago against a template that has since grown sections.
`doc-flow` cannot tell the artifact is "approved against an older spec." No
deterministic check exists.

Suggested approach: have each audit report record the
`framework_spec_version` and template hash it ran against; have the artifact's
frontmatter carry a `last_audited_spec: 0.8.1` field; `doc-flow` and a new
conformance lint pass flag `Approved` artifacts whose `last_audited_spec` is
older than the current `framework/VERSION` minor — recommending a re-audit.

Acceptance: artifacts approved under an older framework spec surface as a
"re-audit due" finding; CHG flow recognises template-version drift as a C2
trigger (re-validates against newer spec).

### TODO-AS10 — `@diagram:` asset existence + per-layer level cascade

Templates declare diagram contracts (`@diagram: c4-l1` for BRD,
`@diagram: c4-l2` for PRD, etc., per `DIAGRAM_STANDARDS.md`). Two failure
modes are currently undetected: the diagram tag is present but no diagram
file exists in the artifact's `diagrams/` directory; the diagram level is
wrong for the layer (e.g., `@diagram: c4-l2` in a BRD).

Suggested approach: extend `sdd_doc_lint` with a `diagrams` pass — collect
every `@diagram:` tag, resolve the expected `diagrams/` path, fail when the
file is missing; cross-check the level against the layer (BRD = L1, PRD = L2,
SPEC = L3) per `DIAGRAM_STANDARDS.md`'s per-layer map.

Acceptance: missing or mis-levelled diagram tags surface as blocking lint
findings; audit Tier 2 diagram check is upgraded.

### TODO-AS11 — Element-ID hash integrity

Element IDs use a 4-hex hash of `"{doc_id}:{section_id}:{title}:{description}"`
(per `ID_NAMING_STANDARDS.md`). If a section title or description is edited
without recomputing the hash, the existing ID becomes stale — downstream
references still resolve syntactically but no longer match the canonical hash
that should be computed from the current content. Today undetected.

Suggested approach: `sdd_doc_lint --hashes` pass — for every element ID,
recompute the SHA256 prefix from current `{doc_id}:{section_id}:{title}:
{description}` and verify it matches the ID's hash segment. Mismatch =
finding (either fix the ID or restore the content).

Acceptance: stale-hash IDs surface as findings with the expected vs actual
hash and a one-line `action_hint` ("rename ID to TYPE.NN.SS.<newhash>"); fixer
skills auto-apply when confidence = `auto-safe`.

### TODO-AS12 — `deliverable_type` / `brd_type` cascade enforcement

`BRD.deliverable_type` (`code` / `document` / `ux` / `risk` / `process`)
cascades to every downstream artifact unchanged (per template guidance), as
does `brd_type` (`platform` / `feature`). Today the audit skills cite "must
match upstream" in prose but no deterministic check verifies it across the
chain.

Suggested approach: `sdd_doc_lint --cascade` pass — walk the
`@brd → @prd → @ears → @bdd → @adr → @spec → @tdd → @iplan` chain for each
artifact, verify `deliverable_type` and (where applicable) `brd_type` are
identical to the parent BRD's values. Fail on divergence.

Acceptance: cascade mismatches surface as blocking lint findings; PRD/ADR/etc.
audit Tier 1 picks them up automatically via the lint shell.

## Priority order

1. **TODO-AS3** — automated linter (highest leverage; catches violations
   deterministically across the whole corpus on every commit)
2. **TODO-AS7** — threshold cross-layer consistency (also a linter pass;
   bundles cleanly with AS3's authoring-style pass)
3. **TODO-AS8** — frontmatter ↔ body consistency (linter pass; one of the
   highest false-confidence bug classes today)
4. **TODO-AS5** — CHG extension (closes the symmetry gap)
5. **TODO-AS9** — staleness detection (requires audit-report metadata
   capture; coordinates with AS5)
6. **TODO-AS2** — per-section `_size_target` (gives the linter and audit
   precise per-section bounds)
7. **TODO-AS10** — `@diagram:` asset + level cascade (linter pass)
8. **TODO-AS11** — element-ID hash integrity (linter pass; relatively rare
   but a correctness invariant)
9. **TODO-AS12** — `deliverable_type` / `brd_type` cascade (linter pass)
10. **TODO-AS6** — template `_guidance` tightening
11. **TODO-AS4** — auto-fix for style violations
12. **TODO-AS1** — skill-body retrofit (lowest urgency; current skills are
    already reasonable)

`sdd_doc_lint` is the implementation centre of gravity: AS3, AS7, AS8, AS10,
AS11, AS12 are all new passes inside the same tool, all deterministic, all
shippable in a single PR or sequenced as the priority dictates.

## Explicit non-goals

Two classes of drift are out of scope for **all** AS items above and should
not be re-proposed as future TODOs. They are recorded here so the boundary
of "what drift detection can do" is unambiguous.

### NON-GOAL-1 — Pure cross-document semantic drift

Contradictions between artifacts where **no element-ID link exists** to
follow.

Examples:

- BRD prose says feature X is "P1 critical"; PRD prose treats X as "nice-to-
  have" — both reference X by name but neither tags the other.
- EARS quality attribute "≤ 500 ms p99" sits in §4; BDD background says
  "system must respond instantly" — semantically inconsistent, no shared key.
- ADR `Context` cites a market constraint that BRD §1 never mentioned.

**Why out of scope.** Detecting this deterministically requires natural-
language understanding of when two prose passages contradict — there is no
oracle a linter can consult. The framework's chosen mechanism is the
**review-team** crew (per-layer persona lenses + synthesizer) plus
`doc-<layer>-audit` Tier 2 content checks; both are LLM-judgement and
non-deterministic by design. Do not propose a deterministic detector for
this class.

**Where the responsibility lands.** Audit Tier 2 content review · review-
team adversary persona · human review at `pre_merge`.

### NON-GOAL-2 — External-reality drift

The artifact accurately reflects what was written, but the **world has
moved**.

Examples:

- BRD claims iOS 12 is the lowest supported version; product reality
  shipped iOS 16 last quarter.
- PRD KPI target ("MAU > 100 k by Q2") set 18 months ago, never refreshed.
- ADR cites GCP regional pricing that has changed.
- Compliance reference (`@regulation: GDPR Art. 32`) when the regulation
  text has been amended.

**Why out of scope.** Detection requires an oracle outside the corpus —
production telemetry, the App Store, GCP pricing pages, the EUR-Lex
gazette. The framework is deliberately self-contained; integrating
external feeds is a separate platform concern (could live in a future
Hermes plugin, not in `framework/`).

**Where the responsibility lands.** CHG flow (an external change becomes a
C1–C3 record that re-validates downstream) · periodic human review · the
audit `last_audited_spec` staleness signal (see **AS9**) is the closest
in-framework proxy and intentionally stops at *spec* staleness, not
*world* staleness.

### How to tell a proposed TODO is a non-goal

If a proposed detector requires either (a) natural-language semantic
comparison between two un-linked passages, or (b) data the corpus itself
does not contain, it falls into one of the two non-goals and belongs in
the CHG / review-team / human-review layers, not in `sdd_doc_lint` or the
skill checks.
