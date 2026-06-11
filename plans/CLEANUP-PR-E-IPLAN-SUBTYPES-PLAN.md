# CLEANUP-PR-E — IPLAN Sub-types (code-build vs deploy)

> Child PR of `FRAMEWORK-CLEANUP-001` (master plan PR #128, merged
> `528d6f23`). **Smallest child PR** — 1 item; framework PATCH floor.

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | CLEANUP-PR-E                                |
| Type           | combined plan + impl (small, template-additive) |
| Worktree       | `feat/cleanup-pr-e-iplan-subtypes` at `/opt/data/aidoc-flow/framework-cleanup-pr-e/` |
| Depends on     | FRAMEWORK-CLEANUP-001 master plan (PR #128); PR-A (#129); PR-C (#130); PR-B (#131) — all merged |
| Closes         | `plans/FRAMEWORK-TODO.md` Open item #17 |
| Version impact | Framework PATCH `0.19.0 → 0.19.1` (template subtype field is additive; existing IPLANs default to `combined` so backward-compat preserved) + plugin PATCH `0.16.0 → 0.16.1` (audit SKILL reads subtype) |
| Status         | DRAFT — 2026-06-11 |

## Item closed

| # | Tag | Title |
|---|---|---|
| 17 | `[template]` | IPLAN sub-types — code-build vs deploy |

## Problem

Per the 2026-06-11 url-shortener review, IPLAN-01 covers Red/Green/Refactor
with pytest gates but has **no canary, no smoke endpoint, no observability
dashboard, no rollback procedure** (§5 explicitly defers runbook/dashboard
to "first to-production session"). It scored 100, but it's a code-build
plan, not a deploy plan. The crew (operator + chaos + integration_lead
lenses) is calibrated for deploy concerns; if the artifact silently
scopes out those concerns, the crew can't catch it.

## Fix shape

1. **Template** — `IPLAN-TEMPLATE.yaml` `document_control` gains a
   new field `subtype: <code_build | deploy | combined>`:

   ```yaml
   document_control:
     iplan_id: "IPLAN-NN"
     subtype: combined  # code_build | deploy | combined
     # code_build: file manifest + Red/Green/Refactor; deploy concerns
     #   (rollback, smoke, canary, observability) NOT required
     # deploy: deploy concerns required; file manifest + R/G/R optional
     # combined (default): both required
     ...
   ```

2. **`doc-iplan-audit/SKILL.md`** — Structural Checklist becomes
   subtype-aware. The auditor reads `subtype` from artifact
   frontmatter and selects the required-section set:

   - `code_build`: `document_control`, `file_manifest`,
     `execution_commands`, `implementation_contracts`,
     `session_handoff`, `traceability` (current 6 sections).
   - `deploy`: `document_control`, `rollback_procedure`,
     `smoke_tests`, `canary_metrics`, `observability_hooks`,
     `runbook_reference`, `traceability` (7 sections — deploy-focused).
   - `combined` (default): all sections from both sets.

   Missing `subtype` field defaults to `combined` for backward
   compat with pre-0.19.1 IPLANs.

3. **`doc-iplan` author SKILL** — at creation time, the author SKILL
   prompts for `subtype` (default `combined`); writes the chosen
   subtype into `document_control.subtype`.

4. **Playbooks** — `operator.md`, `chaos_engineer.md`, and
   `integration_lead.md` for the IPLAN layer gain a subtype-aware
   intro:

   - At `code_build` subtype, these lenses MAY return
     `lens_score: 100` with the rationale "subtype: code_build —
     deploy concerns out of scope for this IPLAN" (the rationale
     pattern from CLEANUP-PR-B item 8).
   - At `deploy` or `combined`, the existing checks apply unchanged.

5. **Backward compat** — IPLANs that pre-date this PR have no
   `subtype` field. Auditor defaults missing field to `combined`.
   url-shortener's `examples/url-shortener/docs/08_IPLAN/IPLAN-01.md`
   stays untouched (don't hand-edit example artifacts); when a
   future cascade re-runs IPLAN, it will gain the field via the
   updated author SKILL.

## File structure

### Modified

| Path | Change |
|---|---|
| `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` | Add `subtype:` field with the 3-value enum + section-set notes; ~10 lines |
| `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` § file_manifest, execution_commands, implementation_contracts, session_handoff | Add `_required_when_subtype: [code_build, combined]` marker |
| Template new sections: `rollback_procedure`, `smoke_tests`, `canary_metrics`, `observability_hooks`, `runbook_reference` | Mark `_required_when_subtype: [deploy, combined]` |
| `platforms/claude-code-plugin/skills/doc-iplan/SKILL.md` | Add "Subtype selection" prompt step at draft time |
| `platforms/claude-code-plugin/skills/doc-iplan-audit/SKILL.md` | Structural Checklist gains subtype-aware section dispatch (read subtype, select section set, default to `combined` if absent) |
| `framework/playbooks/08_IPLAN/operator.md` | Subtype-aware intro paragraph + rationale-pattern note |
| `framework/playbooks/08_IPLAN/chaos_engineer.md` | Same |
| `framework/playbooks/08_IPLAN/integration_lead.md` | Same |
| `framework/VERSION` | `0.19.0 → 0.19.1` PATCH |
| `platforms/claude-code-plugin/VERSION` | `0.16.0 → 0.16.1` PATCH |
| Both `FRAMEWORK_SPEC_VERSION` | `0.19.0 → 0.19.1` |
| `CHANGELOG.md`, `docs/TAGGING.md` (2 new rows), `plans/HANDOFF.md`, `plans/FRAMEWORK-TODO.md` (item 17 Open → Closed) | Docs-of-record discipline |
| `tests/conformance/platforms/test_plugin_release_metadata.py` | Hardcoded `"0.19.0"` → `"0.19.1"` |

### Out of scope

- Hand-editing url-shortener IPLAN-01 to add the subtype field
  (per never-hand-edit example artifacts; a future cascade re-run
  picks up the new field via the author SKILL change).
- New conformance test for the subtype dispatch logic (the existing
  structural-checklist conformance tests will catch malformed
  subtypes once a cascade produces one).
- Deploy-specific template sections (rollback_procedure / smoke_tests
  / etc.) — added as named sub-objects in IPLAN-TEMPLATE.yaml but
  their content shape is intentionally minimal (just `_size_target` +
  `_guidance`); a future cascade fills them in for the first deploy
  IPLAN authored.
- Hermes mirror — plugin-first per HERMES-CATCHUP-001.

## Implementation sequence

### Task 1 — Plan iterative review

### Task 2 — Template update

Edit `IPLAN-TEMPLATE.yaml`:

- Add `subtype` field in `document_control`
- Mark existing 6 sections with `_required_when_subtype: [code_build, combined]`
- Add 5 new sections (rollback_procedure, smoke_tests, canary_metrics,
  observability_hooks, runbook_reference) marked
  `_required_when_subtype: [deploy, combined]`

### Task 3 — doc-iplan author SKILL update

Add a "Subtype selection" step to the Draft phase: prompt user (or
default to `combined`); set the value in `document_control.subtype`.

### Task 4 — doc-iplan-audit SKILL update

Extend Structural Checklist with subtype-aware section dispatch.
Default missing subtype to `combined`.

### Task 5 — Playbook updates (operator, chaos_engineer, integration_lead)

Each gains a one-paragraph "Subtype awareness" intro:

- code_build subtype: lens MAY return 100 with rationale
  "subtype: code_build — deploy concerns out of scope"
- deploy / combined: existing checks apply unchanged

### Task 6 — Version + sync + docs of record

### Task 7 — Conformance + lint cheap checks

- `python3 -m unittest discover -s tests/conformance` — 120/120 PASS
- `python3 -m unittest discover -s tests/unit` — 43/43 PASS
- `python3 -m sdd_doc_lint examples/url-shortener/docs/` — 0 unexpected findings
  (url-shortener IPLAN-01 has no subtype; auditor defaults to `combined`
  which makes existing sections required — should pass)

### Task 8 — Open PR

## Verification

| # | Check | Expected |
|---|---|---|
| 1 | `IPLAN-TEMPLATE.yaml` has `subtype` field with 3-value enum | PASS — yaml parse |
| 2 | 6 existing sections marked `_required_when_subtype: [code_build, combined]` | PASS — grep |
| 3 | 5 new deploy sections marked `_required_when_subtype: [deploy, combined]` | PASS — grep |
| 4 | `doc-iplan/SKILL.md` has Subtype selection step | PASS — manual review |
| 5 | `doc-iplan-audit/SKILL.md` has subtype-aware dispatch | PASS — manual review |
| 6 | 3 IPLAN playbooks (operator, chaos_engineer, integration_lead) have subtype awareness | PASS — grep |
| 7 | Conformance: 120/120 PASS | PASS |
| 8 | Unit: 43/43 PASS | PASS |
| 9 | url-shortener lint clean (backward compat: missing subtype → combined) | PASS |

## Risks & rollback

| Risk | Mitigation |
|---|---|
| Existing IPLANs (url-shortener IPLAN-01) lack subtype → auditor breaks | Default missing → `combined`; backward compat preserved |
| Template `_required_when_subtype` field is non-standard | Treat as guidance metadata (similar to existing `_size_target`); auditor reads but doesn't validate at template-parse time |
| Playbook subtype-aware rationale pattern conflicts with PR-B no-findings-rationale rule | Compatible: code_build subtype IS the rationale; lens emits `no_findings_rationale: "subtype: code_build — deploy concerns out of scope"` per PR-B's structure |

**Rollback:** Single PR. `git revert <merge-sha>` restores. Template
additions are backward-compat (missing field defaults to combined).

## Review log

### Pass 0 — initial draft

- **Date:** 2026-06-11T23:30:00Z
- **Status:** SUPERSEDED by Pass 1.

### Pass 1 — self-review against codebase

- **Date:** 2026-06-11T23:35:00Z
- **Findings (1 MED):**
  - **P1-1 (MEDIUM):** `_required_when_subtype:` is a NEW convention —
    no existing template uses `_required_when_*` metadata. Need to
    explicitly document this convention in the template's `_guidance`
    field so future readers know it's a marker, not a validated field.
    *Patch:* Plan text already says "Treat as guidance metadata
    (similar to existing `_size_target`)"; impl will include an inline
    `_guidance` paragraph explaining the convention.
- **Cross-checks clean:**
  - IPLAN-TEMPLATE has 7 top-level sections ✓
  - doc-iplan/SKILL.md has `## Creation Process` at line 123 (insertion point for Subtype selection step) ✓
  - doc-iplan-audit has Structural Checklist + Metadata Checks ✓
  - All 3 target playbooks exist ✓

### Pass 2 — re-review

- **Date:** 2026-06-11T23:40:00Z
- **Method:** verify Pass 1 patch propagation; verify no contradictions
  in scope.
- **Findings:** 0 substantive.
- **Verdict:** self-converged. Per FRAMEWORK-CLEANUP-001 Pass 4 lesson,
  user-driven review on the PR is the real convergence gate.
