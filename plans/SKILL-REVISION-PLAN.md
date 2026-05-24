# SR Plan — Claude Code plugin skill revision (frontmatter + content audit)

| Field      | Value                          |
|------------|--------------------------------|
| Task       | SR (Skill Revision)            |
| Depends on | PLM (8-layer migration, complete); D-0017 (project-mngt parked); plugin v0.2.0 released |
| Status     | PLANNED — 2026-05-23T00:00:00Z |
| Feeds      | Plugin patch release (`claude-code-plugin/v0.2.1`) |
| Branch     | `claude/skill-revision`        |

## Objective

Bring the 124 shipped plugin skills (`platforms/claude-code-plugin/skills/`) to a
single, current, internally-consistent state. The 8-layer **content** is already
current (the PLM migration; `plm_lint` clean) — the staleness is **structural and
cosmetic**: three different frontmatter shapes coexist, 99 skills carry stale
inline date/version footers that duplicate (and contradict) the frontmatter, and
no canonical SKILL.md frontmatter schema is written down. This task normalizes
frontmatter, removes the stale footers, audits every skill body for residual
staleness, and records the canonical schema so the drift cannot silently return.

## Scope

**In:**

- **A — Frontmatter normalization.** Convert the **22 flat-form** skills to the
  canonical `metadata`-nested schema; drop the redundant `title:` key (**14**
  skills); fix the literal `last_updated: "YYYY-MM-DDTHH:MM:SS"` placeholder.
- **B — Stale footer / date cleanup.** Per **D-SR3** (default: *remove*) strip
  inline `Version History` / `**Created**` / `**Last Updated**` body footers
  (**99** skills) — frontmatter is the single source of truth. Re-stamp
  `last_updated` **only on skills actually modified by this task** (re-stamping
  the 95 already-fresh files would churn untouched skills and make the date
  meaningless).
- **C — Content audit (all 124 bodies).** Per-skill read for: dead internal
  links (`../<skill>/` to skills that no longer exist), broken `framework/…`
  paths, references to removed skills/layers, stale model labels (e.g. the
  `GPT-4` node in `mermaid-gen`), old element-id / 3-segment-ID prose, and any
  other outdated practice. Findings logged; mechanical fixes applied.
- **D — Write the canonical schema down.** Add a short authoring standard at
  **`platforms/claude-code-plugin/SKILL_AUTHORING.md`** (D-SR2 — plugin root, NOT
  under `skills/`, so Claude Code's `skills/<name>/SKILL.md` auto-discovery never
  mistakes it for a skill), so future skills conform.

**Out:**

- Rewriting skill *methodology* / instructional content (the 8-layer behavior is
  current). Only stale references and demonstrably wrong content are touched.
- Changing any skill's `name:` or `description:` — these drive Claude Code
  auto-invocation; they are **frozen** except to fix an outright error.
- The Hermes platform and `framework/` spec (separate streams).
- The parked `legacy/claude-code-plugin/project-mngt/` skill (stays legacy).

## Approach

### Canonical frontmatter schema (the normalization target)

Derived from the migrated layer skills (e.g. `doc-brd`). Field order is fixed:

```yaml
---
name: <skill-name>                 # == directory name (conformance-relevant)
description: <one line; drives auto-invocation — DO NOT alter wording>
metadata:
  tags:
    - <tag>
  custom_fields:
    layer: <N | null>
    artifact_type: <TYPE | null>
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: <shared | …>
    development_status: <active | legacy>
    skill_category: <core-workflow | quality-assurance | utility | planning>
    upstream_artifacts: [...]
    downstream_artifacts: [...]
    version: "<x.y>"
    last_updated: "<YYYY-MM-DD>"
    versioning_policy: "<policy>"
---
```

### Flat → nested transform (the 22 skills)

`adr-roadmap, charts-flow, context-analyzer, contract-tester, doc-flow,
doc-iplan, doc-iplan-autopilot, doc-iplan-fixer, doc-iplan-reviewer,
doc-iplan-validator, doc-naming, doc-ref, doc-review, doc-validator,
mermaid-gen, project-init, quality-advisor, security-audit, skill-recommender,
test-automation, trace-check, workflow-optimizer`

Per file:

1. Delete the `title:` line (present in 14 of the 22).
2. Insert `metadata:` after `description:`; indent the existing `tags:` and
   `custom_fields:` blocks by two spaces under it.
3. Append the three missing `custom_fields` keys:
   - `version: "1.0"` — first tracked version (their body footers say `1.0.0`).
   - `last_updated: "<revision date>"`.
   - `versioning_policy:` — **decision (D-SR1):** skills that own a layer
     template track it (`"tracks <TYPE>-TEMPLATE schema_version"`); utility /
     orchestrator skills with no template use `"tracks skill behavior"`.
     Note: `doc-iplan` + its `-autopilot/-fixer/-reviewer/-validator` variants
     are in the flat group but **are Layer-8 artifact skills** (they own the
     IPLAN template) → template-tracking policy, `layer: 8`, `artifact_type:
     IPLAN` preserved from their existing `custom_fields`. The other ~17 are
     utility/orchestrator → behavior-tracking.

### Content-audit execution (workstream C)

124 bodies is too much for one linear pass. Run it as **parallel, READ-ONLY
general-purpose agents** (they audit and report; they do **not** edit), each given
a batch of ~15–20 skills and the fixed checklist above, returning a structured
findings table (skill → issue → suggested fix → severity). Main session triages:
mechanical fixes (dead link, stale label) applied directly; anything ambiguous or
content-level escalated to the user before editing. This keeps 124 long files out
of the main context while still reading them whole.

## Step sequence

1. **Lock decisions** (D-SR1 versioning_policy; D-SR2 schema-doc location; D-SR3
   footer removal vs. keep) → `plans/DECISIONS.md`.
2. **A — frontmatter normalization** of the 22 skills (per-file edits).
3. **B — footer/date cleanup** across the 99 skills.
4. **C — content audit** via parallel agents; triage + apply mechanical fixes;
   escalate content-level findings.
5. **D — write `SKILL_FRONTMATTER.md`** standard.
6. **Verify** (below).
7. **Land:** conventional commits grouped by workstream; CHANGELOG `[Unreleased]`
   entry; bump plugin `VERSION` → `0.2.1` (patch) at close; record SR completion
   in `plans/HANDOFF.md`.

## Verification

Runnable, all must pass (conformance is frontmatter-shape-agnostic — the suite
checks framework spec + version declarations + engine isolation + `plm_lint`, not
SKILL.md structure — so these are quality guards on top of a green suite):

- `python3 -m unittest discover -s tests/conformance` → **32/32**.
- `python3 tests/conformance/platforms/plm_lint.py --all` → clean.
- Every `SKILL.md` YAML frontmatter parses (`yaml.safe_load`) and has top-level
  `name` + `description`.
- `name:` value == directory name for all 124 (already true; must stay true).
- **Zero** skills with a top-level `custom_fields:` or `title:` key (i.e. flat
  form fully eliminated); all use `metadata.custom_fields`.
- No `last_updated: "YYYY-MM-DD…"` placeholder remains.
- **`name`/`description` freeze diff-guard** — the branch base is `origin/main`,
  so `git diff origin/main -- '**/SKILL.md' | grep -E '^[-+](name|description):'`
  must return **empty** (a changed line would show as a `-`/`+` pair; unchanged
  lines never appear). Any hit = an accidental auto-invocation change.
- No dead `../<skill>/` internal links — extract every **single-level**
  `../<name>/` reference (one `../`; exclude the multi-level `../../../../framework/…`
  spec paths) and assert each `<name>` directory exists under `skills/`.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Altering `description`/`name` breaks Claude Code auto-invocation | Freeze both; verification diff-guards `description`; `name`==dir asserted |
| R2 | YAML indentation error during flat→nested re-nest | `yaml.safe_load` every file in verification; per-file review |
| R3 | Footer removal (99 files) deletes substantive content, not just date cruft | Remove only the trailing metadata footer block; agent/diff review per file; never touch instructional sections |
| R4 | Content audit "fixes" drift into unwanted rewrites | Workstream C escalates anything beyond a dead link / stale label to the user; methodology content is out of scope |
| R5 | Large multi-file diff hard to review | Group commits by workstream (A, B, C, D) so each diff is coherent |

## Review log

> ≥2 passes before implementation. Each pass re-reads the whole plan, lists
> findings, folds fixes back above. Stop when a pass finds nothing.

### Pass 1 — 2026-05-23T00:00:00Z

- The `name`/`description` freeze was asserted but not made runnable → added a
  concrete `git diff origin/main … | grep '^[-+](name|description):'` diff-guard
  (must be empty), since `origin/main` is the branch base.
- `doc-iplan*` sit in the flat group but are real Layer-8 artifact skills →
  D-SR1 must give them template-tracking policy (not "skill behavior"); noted in
  the transform.
- Workstream-C agents could drift into editing → made them explicitly READ-ONLY
  (audit/report only; main session applies fixes).
- D-SR2 schema-doc location resolved to `platforms/claude-code-plugin/
  SKILL_AUTHORING.md` (plugin root, outside `skills/` so it isn't auto-discovered
  as a skill). D-SR3 (footer removal) made explicit, default = remove.
- Noted conformance is frontmatter-shape-agnostic (no test asserts SKILL.md
  structure), so the new guards sit on top of a green suite.

### Pass 2 — 2026-05-23T00:00:00Z

- Workstream B would have re-stamped `last_updated` on all 124 → churns the 95
  already-fresh files and makes the date lie; scoped re-stamp to modified skills
  only.
- Dead-link verification could false-positive on the multi-level
  `../../../../framework/…` spec paths → scoped the check to single-level
  `../<name>/` skill siblings.
- Remaining open items are **user decisions, not plan defects** — D-SR1/2/3
  defaults and the close-version (`0.2.1` patch, → `0.3.0` only if workstream C
  surfaces behavioral content changes) are surfaced for confirmation at
  presentation. No new structural findings.
