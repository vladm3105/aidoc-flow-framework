# P3-T6 Plan — Skill set revision (remove stale, recreate retained at plugin version)

| Field      | Value                          |
|------------|--------------------------------|
| Task       | P3-T6                          |
| Depends on | P3-T0..T5 (plugin build); LAYER_REGISTRY.yaml (8-layer contract) |
| Status     | VERIFIED — 2026-05-23T16:12:01Z |
| Feeds      | Conformance suite; plugin v0.2.0 |

## Objective

The Claude Code plugin ships 140 skill entries (124 dirs + 16 loose `.md`)
inherited from the legacy `ucx_framework`, including families that no longer
exist in the 8-layer SDD contract (`framework/registry/LAYER_REGISTRY.yaml`).
This task prunes the set to the canonical skills and recreates the survivors to
one consistent standard, with each skill's `version` defaulting to the plugin
version (`0.2.0`).

## Scope

**In:**
- Remove stale skills/files (manifest below).
- Author a canonical SKILL.md spec: `platforms/claude-code-plugin/docs/SKILL_AUTHORING.md`.
- Recreate the 46 retained skills against that spec, sourced from
  `framework/layers/NN_<X>/` templates + READMEs + `framework/governance/`.
- Set every retained skill `version: "0.2.0"`; drop `## Version History`
  footers (history lives in git + plugin `CHANGELOG.md`).
- Repair references broken by deletions (mermaid-gen → charts-flow; `agents/`
  delegations; orchestrator skill lists).

**Out:**
- Platform A (Hermes) skills/templates — untouched.
- `framework/` spec content — untouched (it is the source of truth, not a target).
- Adding brand-new skills — tracked separately (user's "new skills" note).
- Hermes/framework version streams.

## Manifest

**Retain (46):**
- Layer skills (32): `doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}` × {base, `-autopilot`, `-audit`, `-fixer`}.
- Utilities (14): doc-flow, doc-naming, doc-ref, doc-review, doc-validator,
  project-init, trace-check, charts-flow, adr-roadmap, context-analyzer,
  quality-advisor, skill-recommender, workflow-optimizer, security-audit.

**Remove (94):**
- Deprecated variants (14): `-reviewer` + `-validator` for prd, ears, bdd, adr,
  spec, tdd, iplan (brd already has none).
- Test-type families (36): doc-{utest,itest,ftest,ptest,stest,sectest}×6.
- SPEC-subtype families (25): doc-{cspec,dspec,uxspec,riskspec,procspec}×5.
- Legacy utilities (3): contract-tester, test-automation, mermaid-gen.
- Loose `.md` (16): all non-dir files at `skills/` root (quickrefs, readmes,
  REVIEW_DOCUMENT_STANDARDS.md).

## Approach

### Canonical SKILL.md (defined fully in SKILL_AUTHORING.md)

Frontmatter (Claude Code requires `name` + `description`; rest is metadata):
```yaml
name: <unchanged — equals dir name>
description: <one line: what it does + when to use>
metadata:
  tags: [sdd-workflow, layer-<N>-artifact, ...]
  custom_fields:
    layer: <N>                 # layer skills only
    artifact_type: <BRD..IPLAN># layer skills only
    skill_category: core-workflow|automation-workflow|quality-assurance|utility
    upstream_artifacts: [...]
    downstream_artifacts: [...]
    version: "0.2.0"           # DEFAULT = plugin version
    framework_spec_version: "0.1.0"
    last_updated: "2026-05-23"
```
Rules: `name` is frozen (it is the identifier). `version` defaults to the
plugin VERSION. No `## Version History` section. Sibling links use `../<skill>/`.
All template/README/governance links point into `framework/`. No `mermaid-gen`.

Per-variant body structure:
- **base** (`doc-X`): Purpose · When to Use · Prerequisites · Layer Guidance
  (distilled from `framework/layers/NN_X/*-TEMPLATE.yaml` + README) · Creation
  Process · Validation (checklist + codes + quality gate) · Next Skill ·
  Related Resources · Quick Reference.
- **`-autopilot`**: Purpose · Input Contract · Skill Dependencies · Phases
  (detect → generate → audit gate → fix loop) · Execution Modes (single/batch/
  dry-run) · Quality Gates · Error Handling · Related Resources.
- **`-audit`**: Purpose · When to Use · Execution Contract · Structural
  Checklist · Metadata Checks · Report Format · Hand-off to `-fixer` ·
  Related Resources.
- **`-fixer`**: Purpose · Input Contract (consumes audit report) · Fix
  Categories · Auto-Fix Actions · Content-Preservation Rules · Related Resources.
- **utility**: Purpose · When to Use · Behavior · Related Resources.

### Reference repairs (apply with deletions)
- `mermaid-gen` → `charts-flow` everywhere it is referenced (e.g.
  `doc-flow/SKILL.md`, `doc-brd/SKILL.md:641`).
- `agents/*.md` delegating to removed skills → repoint to a retained skill or
  drop the delegation (audit all 10 agent files).
- Orchestrators (doc-flow, skill-recommender, doc-ref, doc-validator,
  project-init) that enumerate skills → regenerate lists to the 46-skill set.

## Step sequence

1. **Pattern first:** write `docs/SKILL_AUTHORING.md`; recreate the BRD family
   (doc-brd, doc-brd-autopilot, doc-brd-audit, doc-brd-fixer) to it. **Pause for
   user sign-off on the pattern.**
2. Delete the 94 stale entries (`git rm`).
3. Recreate the remaining 7 layer families to the pattern.
4. Recreate the 14 utilities to the pattern.
5. Repair all broken references; sweep for dangling `mermaid-gen`/removed-skill
   mentions.
6. **Verify** (see below).
7. **Land:** commits per logical group, conventional prefixes; update plugin
   `CHANGELOG.md`; refresh `plans/HANDOFF.md`; tick `MIGRATION_TODO.md`.

## Verification

- `grep -rIl "mermaid-gen\|doc-utest\|doc-cspec\|doc-uxspec\|doc-riskspec\|doc-procspec\|contract-tester\|test-automation\|-reviewer/\|-validator/" platforms/claude-code-plugin` → **0 hits** outside this plan.
- Every retained `SKILL.md` parses as YAML frontmatter and contains
  `version: "0.2.0"`; **no** `## Version History` heading remains.
- `skills/` has exactly 46 dirs and **0** loose `.md`.
- Run `tests/conformance/` + any plugin self-tests → green.
- `name:` for each retained skill equals its directory name (identifier frozen).

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | "Recreate" drops valuable embedded guidance | Source from the framework TEMPLATE.yaml (the SoT, which carries the guidance); pattern-first review on BRD before rollout. |
| R2 | Deleting skills orphans agents/commands | Step 5 audits all `agents/` + the 1 command and repairs refs in the same change. |
| R3 | Conformance encodes the old skill list | Inspect conformance checks before deleting; if it pins names, update the check (don't weaken it). |
| R4 | Pushing to wrong branch | Confirm target branch with user before push (task setup says `multi-platform-migration-AamWB`; working tree is on `skill-revision`). |
| R5 | Frozen `name` accidentally changed | Verification asserts `name == dirname` for all 46. |

## Review log

### Pass 1 — 2026-05-23T15:40:40Z

- **Finding:** initial draft removed `-validator` globally, but `doc-validator`
  (a kept utility) and per-layer `doc-X-validator` are different things → manifest
  now scopes removal to the 7 layers with `-reviewer`/`-validator` and the
  verification grep uses `-validator/` (trailing slash, dir-scoped) to avoid
  matching the utility `doc-validator`.
- **Finding:** verification grep for `mermaid-gen` would trip on this plan file
  and SKILL_AUTHORING.md → scope greps to `platforms/claude-code-plugin` and
  exclude doc files; "outside this plan" qualifier added.
- **Finding:** conformance may pin the skill inventory (R3) → added a step-0
  inspection before deletion.

### Pass 2 — 2026-05-23T15:42:00Z

- **Finding:** `framework_spec_version` added to frontmatter so each skill
  records the spec it targets (0.1.0), distinct from its own version (0.2.0) —
  keeps the two version streams (docs/PROJECT.md §2) legible at skill level.
- **Finding:** loose-file count must be asserted (=0) separately from dir count
  (=46); folded both into Verification.
- No further findings.

## Progress — 2026-05-23T16:12:01Z (IMPLEMENTED + VERIFIED)

- Authored `platforms/claude-code-plugin/docs/SKILL_AUTHORING.md` (the standard).
- Recreated the BRD family as the approved exemplar; rolled the pattern out to
  the other 7 layers (28 skills, via per-layer agents) and the 14 utilities.
- Deleted the 94 stale entries (`git rm`); also removed the orphaned
  `doc-flow/SHARED_CONTENT.md` and a stray `.code-workspace` (cruft).
- Reference repairs: `mermaid-gen`→`charts-flow`; `-reviewer`/`-validator`
  refs → `-audit` in `agents/README.md`, `doc-validator`, `doc-review`; plugin
  `README.md` inventory updated to 46; `CHANGELOG.md [Unreleased]` entry added.
- Aligned `tests/conformance/platforms/plm_lint.py` `MIGRATED` to the 46-set.
- **Verification — all green:** 46 skill dirs / 46 `SKILL.md` / 0 loose files;
  every `SKILL.md` has `version: "0.2.0"`, `framework_spec_version: "0.1.0"`,
  `name == dirname`, no `## Version History`; zero removed-skill references
  across `skills/` + `agents/` + `commands/` (CHANGELOG history excepted);
  full conformance suite **32 passed, 103 subtests**.
- **Open (not landed):** push-branch confirmation (R4); optional plugin
  version bump 0.2.0→0.3.0 given scope; the user's separate "new skills" idea.
