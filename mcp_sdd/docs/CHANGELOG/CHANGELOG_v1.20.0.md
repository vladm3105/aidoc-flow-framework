# CHANGELOG — UCX v1.20.0

**Release Date**: 2026-04-06
**Plan**: PLAN-029 (Review/Remediation Pipeline Quality)

## Summary

Improve review accuracy and remediation fix quality across the sdd_review, sdd_remediate, and sdd_remediate_fix pipeline. Addresses false-positive findings from generic persona behavior, thin executor prompts producing cosmetic-only fixes, and missing post-fix validation feedback loops.

## Changed

### Remediate-Fix Prompt Enrichment (A1.1, A2.2, A2.3)

The `_build_remediate_fix_prompt()` function in `remediation/runner.py` now produces a detailed executor prompt:

| Before | After |
|--------|-------|
| 4-line generic instruction ("Fix findings... apply targeted edits") | 6-step fix strategy with FWDREF handling, section ordering, substantive content rules |
| Findings listed flat, no priority grouping | Findings grouped by Phase 1 (P0), Phase 2 (P1), Phase 3 (P2) |
| No document content in prompt | Derived copy content embedded (capped at 50K chars) |

New fix strategy instructions:
1. Read derived file first to understand existing structure
2. FWDREF-DEFERRED: do not rename without adding substantive content
3. New sections must contain minimum 3 paragraphs or detailed table
4. Preserve section ordering
5. Confirm each fix addresses the exact gap
6. Do not introduce new validation errors

### Review Finding Truncation Fix (A2.1)

`review_parser.py`: `_clean_text` `max_len` for `recommended_action` fields increased from 300 to 2000 characters. Executor now receives full remediation guidance instead of truncated fragments.

### Priority-Aware Finding Cap (A2.4)

`runner.py`: Review findings are now sorted by priority (P0 first, then P1, then P2) before the 50-finding cap is applied. Previously a flat `[:50]` slice could drop P0 findings when many P1/P2 findings existed. Overflow message now reports total count and recommends re-running after fixes.

### BRD Review Persona Flow (A1.2)

`persona_mappings.yaml`: `fact_checker` persona added to default BRD review sequence:

```yaml
# Before
personas: [architect, auditor, business_analyst, chaos_engineer, chairperson]
# After
personas: [architect, auditor, business_analyst, chaos_engineer, fact_checker, chairperson]
```

The `fact_checker` persona (already defined in framework) detects scope misunderstandings and false positives before the chairperson synthesis phase.

### Auditor Applicability Guard (A1.4)

`auditor.md`: New APPLICABILITY CHECK instruction at top of Compliance section. Auditor must verify regulation is relevant to document's stated domain before flagging as P0. Out-of-scope regulations classified as P1 "Scope Gap" instead of P0 "Compliance Blocker".

### Chairperson Applicability Veto (A1.3)

`chairperson.md`: New 4th synthesis principle — Applicability Veto. Chairperson excludes out-of-scope findings from score calculation and lists them separately in the manifest under `out_of_scope_findings`.

## Added

### Post-Fix Validation in Pipeline (A3.1)

`tool_registry.py`: The lifecycle pipeline (`sdd_run_lifecycle`) now auto-runs `sdd_validate` on the remediated derived copy after `remediate_fix` completes. Result available under `post_remediation_verify` key. Catches regressions introduced by the executor (broken YAML, section ordering errors, new placeholder introductions).

### Substantive Change Detection (A3.2)

New function `verify_remediation_quality()` in `remediation/runner.py`. Deterministic quality check comparing original vs remediated document — no LLM call needed.

Detects:
- Cosmetic FWDREF-DEFERRED to FWDREF renames without new content
- Stub sections (new headers with <50 words of content)
- Suspiciously low content delta for the number of findings

Returns `quality_pass: true/false` with specific issue descriptions.

Automatically called after `sdd_remediate_fix` executor completes. Result available under `remediation_quality` key in tool output.

## Files Changed

| File | Change |
|------|--------|
| `mcp_sdd/src/mcp_server/remediation/runner.py` | Enriched `_build_remediate_fix_prompt`, added phased finding groups, priority-sorted cap, new `verify_remediation_quality()` |
| `mcp_sdd/src/mcp_server/remediation/review_parser.py` | `recommended_action` truncation 300 to 2000 chars |
| `mcp_sdd/src/mcp_server/tool_registry.py` | Post-fix validation in pipeline, quality check in remediate_fix handler |
| `mcp_sdd/skills/persona_mappings.yaml` | `fact_checker` added to BRD review sequence |
| `mcp_sdd/skills/personas/chairperson.md` | Applicability Veto (principle #4) |
| `mcp_sdd/skills/personas/auditor.md` | APPLICABILITY CHECK guard in Compliance section |

## Backward Compatibility

- Existing projects retain their scaffolded `persona_mappings.yaml` (no automatic override). New projects and `sdd_init --update-mappings` receive the updated defaults.
- `verify_remediation_quality()` is additive — returned as extra field in tool output, does not affect existing response structure.
- Post-fix validation is pipeline-only (triggered by `sdd_run_lifecycle`). Standalone `sdd_remediate_fix` calls receive quality check but not auto-validation.
- All existing CLI commands and MCP tool signatures unchanged.

## Test Coverage

Verified: `verify_remediation_quality()` correctly flags the BRD-05 remediation issues (39 FWDREF renames, 3 stub sections, `quality_pass: false`). All existing imports pass.
