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

## Priority order

1. **TODO-AS3** — automated linter (highest leverage; catches violations
   deterministically across the whole corpus on every commit)
2. **TODO-AS5** — CHG extension (closes the symmetry gap)
3. **TODO-AS2** — per-section `_size_target` (gives the linter and audit
   precise per-section bounds)
4. **TODO-AS6** — template `_guidance` tightening
5. **TODO-AS4** — auto-fix for style violations
6. **TODO-AS1** — skill-body retrofit (lowest urgency; current skills are
   already reasonable)
