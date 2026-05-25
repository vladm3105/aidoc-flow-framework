---
name: quality-advisor
description: Provide real-time quality guidance during artifact creation - section completion, anti-pattern detection, cumulative-tag and naming checks - before an artifact is finished. Use while authoring or reviewing a single SDD document.
metadata:
  tags:
    - sdd-workflow
    - utility
    - quality-assurance
  custom_fields:
    skill_category: utility
    version: "0.2.0"
    framework_spec_version: "0.6.0"
    last_updated: "2026-05-23"
---

# quality-advisor

## Purpose

Give proactive, in-the-moment quality guidance while an SDD artifact is being
written, so issues are caught during creation instead of at post-creation
validation. It scores section completion, detects documentation anti-patterns,
checks cumulative tagging, and validates naming — then returns actionable
recommendations.

## When to Use

Use `quality-advisor` when:

- Authoring a new artifact and wanting live feedback.
- Reviewing an artifact before submission.
- Checking template-requirement, tag, or naming compliance for one document.

Do **not** use it for full bidirectional traceability validation (use
`../trace-check/SKILL.md`), whole-project validation (use
`../doc-validator/SKILL.md`), or non-SDD documentation.

## Behavior

Given the artifact content, its type, and an optional check level (quick /
standard / strict), the skill:

1. **Loads template requirements** for the artifact's layer from
   `framework/registry/LAYER_REGISTRY.yaml` — required sections, minimum tag
   count, and special rules (e.g. PRD KPIs must be quantitative, EARS
   WHEN-THE-SHALL syntax, SPEC YAML form). Code is the downstream execution
   target of IPLAN, not a documentation artifact.
2. **Scores section completion** — detects required sections, flags
   missing/partial ones, and reports a completion score with specific issues.
3. **Detects anti-patterns** — missing Document Control, placeholder text, vague
   acceptance criteria, missing traceability tags, broken links, ID-format
   violations, empty sections, orphan artifacts, count/cross-reference
   mismatches, undefined acronyms, mixed ID notation, forward references to
   non-existent documents — each with severity and a fix suggestion.
4. **Validates cumulative tagging** — confirms the artifact carries exactly the
   upstream tag families its layer requires (BRD 0 → … → IPLAN 7), with no gaps
   and no downstream tags.
5. **Checks naming** — document IDs `TYPE-NN`, element IDs `TYPE.NN.SS.xxxx`,
   threshold tags, and filename slugs, deferring to `../doc-naming/SKILL.md` and
   `framework/governance/ID_NAMING_STANDARDS.md`; flags legacy patterns.
6. **Generates a quality report** — overall status and score, error/warning/info
   counts, per-area results, and prioritized recommendations plus next steps
   (typically: fix errors, then run `../trace-check/SKILL.md`).

The framework ships no runtime code — this skill IS the checker, applying the
declarative checks above against the spec.

## Related Resources

- Layer registry & tag rules: `framework/registry/LAYER_REGISTRY.yaml`
- ID & tag standards: `framework/governance/ID_NAMING_STANDARDS.md`
- Layer READMEs: `framework/layers/02_PRD/README.md` ·
  `framework/layers/05_ADR/README.md`
- Naming: `../doc-naming/SKILL.md`
- Post-creation validation: `../doc-validator/SKILL.md` ·
  `../doc-review/SKILL.md` · layer `-audit` skills (e.g. `../doc-prd-audit/SKILL.md`)
- Traceability: `../trace-check/SKILL.md` · Context: `../context-analyzer/SKILL.md`
