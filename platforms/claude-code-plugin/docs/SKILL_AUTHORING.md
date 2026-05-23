# SKILL_AUTHORING.md — Canonical SKILL.md standard (aidoc-flow plugin)

Authoring contract for every skill shipped by the **aidoc-flow** Claude Code
plugin. It is the single pattern the skill set is recreated against (P3-T6).
The framework spec is the source of truth for *content*; this file governs
*form*.

## 1. Scope — the canonical skill set (54)

- **Layer families (8 × 4 = 32):** `doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}`
  in four variants — base (`doc-X`), `-autopilot`, `-audit`, `-fixer`.
- **Change-management family (4):** `doc-chg` + `-autopilot`/`-audit`/`-fixer`
  — the CHG governance overlay (governs edits to existing artifacts; not a layer).
- **Utilities (18):** doc-flow, doc-naming, doc-ref, doc-review, doc-validator,
  project-init, project-adopt, project-profile, knowledge-extractor, gate-check,
  trace-check, charts-flow, adr-roadmap, context-analyzer, quality-advisor,
  skill-recommender, workflow-optimizer, security-audit.

Removed and **never reintroduced**: `-reviewer`/`-validator` variants (merged
into `-audit`); test-type families (utest/itest/ftest/ptest/stest/sectest);
SPEC-subtype families (cspec/dspec/uxspec/riskspec/procspec); contract-tester,
test-automation, mermaid-gen; loose `*.md` files at `skills/` root.

## 2. Frontmatter (mandatory)

Claude Code requires `name` + `description`; the rest is metadata.

```yaml
---
name: <skill-name>            # FROZEN — must equal the directory name
description: <one sentence: what it does + when to use it>
metadata:
  tags: [sdd-workflow, <layer-N-artifact | utility>, <quality-assurance | automation-workflow>?]
  custom_fields:
    layer: <1-8>              # layer skills only; omit for utilities
    artifact_type: <BRD|PRD|EARS|BDD|ADR|SPEC|TDD|IPLAN>   # layer skills only
    skill_category: core-workflow | automation-workflow | quality-assurance | utility
    upstream_artifacts: [<...>]      # cumulative chain; [] for BRD
    downstream_artifacts: [<...>]
    version: "0.2.0"                  # DEFAULT = plugin VERSION (see §3)
    framework_spec_version: "0.1.0"   # = FRAMEWORK_SPEC_VERSION
    last_updated: "YYYY-MM-DD"
---
```

Dropped legacy fields: `architecture_approaches`, `priority`,
`development_status`, `versioning_policy` (superseded by §3).

## 3. Versioning rule

- A skill's `version` **defaults to the plugin `VERSION`** (currently `0.2.0`)
  and moves with it. There is no per-skill version stream.
- `framework_spec_version` records the spec the skill targets (the value in
  `platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION`).
- **No `## Version History` section.** History lives in git and the plugin
  `CHANGELOG.md`. Skill bodies carry no changelog/footer block.

## 4. Reference & content conventions

- Template / README / governance links point into the framework spec using the
  **`framework/layers/NN_<X>/`** form (e.g. `framework/layers/01_BRD/README.md`).
  Never `framework/NN_X/` (legacy; tripped by the conformance lint).
- Sibling skills are linked as `../<skill>/SKILL.md`.
- Diagrams: reference the **`charts-flow`** skill — never `mermaid-gen`.
- Element IDs (hierarchical artifacts BRD/PRD/EARS/BDD/TDD): 4-segment
  `TYPE.NN.SS.xxxx` (`xxxx` = 4-hex content hash). Document-level refs
  (ADR/SPEC/IPLAN and `@adr:` etc.): dash form `TYPE-NN`. Authority:
  `framework/governance/ID_NAMING_STANDARDS.md`.
- No legacy fingerprints (enforced by `tests/conformance/platforms/plm_lint.py`):
  no `layer: 9-12`, no `SYS/REQ/CTR/TSPEC/TASKS`, no 3-segment IDs presented as
  valid, no legacy paths.
- "The skill is the validator": the framework ships no runtime code — skills
  describe declarative checks against the spec, not scripts to execute.

## 5. Body structure by variant

Common: open with `# <skill-name>` then `## Purpose` (state layer +
upstream/downstream). Close with `## Related Resources`. No footer.

**base (`doc-X`)** — *create the layer artifact*
`Purpose · When to Use · Prerequisites · Layer Guidance (distilled from
framework/layers/NN_X/*-TEMPLATE.yaml + README) · Creation Process ·
Validation (checklist + codes + quality gate) · Next Skill · Related Resources ·
Quick Reference`

**`-autopilot`** — *generate end-to-end*
`Purpose · Skill Dependencies · Input Contract · Smart Document Detection ·
Workflow (Phase 1 input analysis → 2 type/scope → 3 generation → 4 validation →
5 audit↔fix cycle) · Execution Modes (single · batch (chunks of 3) · dry-run) ·
Quality Gates · Error Handling · Related Resources`

**`-audit`** — *quality gate, produces a report for the fixer*
`Purpose · When to Use · Execution Contract · Structural Checklist (Tier 1
blocking / Tier 2 advisory) · Metadata Checks · Combined Report Format ·
Hand-off to -fixer · Related Resources`

**`-fixer`** — *apply fixes from an audit report*
`Purpose · Input Contract (consumes the latest -audit report) · Fix Phases /
Categories · Auto-Fix Actions · Confidence Classification (auto-safe /
auto-assisted / manual-required) · Content-Preservation Rules · Fix Report
Format · Related Resources`

**utility** — `Purpose · When to Use · Behavior · Related Resources`
(add what the specific utility needs; keep it minimal).

## 6. Acceptance checklist (per skill)

- [ ] `name` equals the directory name.
- [ ] `version: "0.2.0"`, `framework_spec_version: "0.1.0"` present.
- [ ] No `## Version History`; no `mermaid-gen`; no `-reviewer`/`-validator`
      references; no removed-family references.
- [ ] Template/README/governance links use `framework/layers/NN_X/`.
- [ ] Frontmatter parses as YAML; body follows the variant structure above.
- [ ] `python3 tests/conformance/platforms/plm_lint.py --all` clean.
