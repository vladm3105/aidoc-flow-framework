# PLAN-029: Improve Review/Remediation Pipeline Quality

> **Historical Context**: This document records release/implementation history across the `mcp_ucx` -> `ucx_hermes` transition. Any `mcp_ucx` paths or tool-surface references are legacy snapshots, not active runtime guidance.

## Context

The sdd_review → sdd_remediate → sdd_remediate_fix pipeline produced low-quality results when executed via codex against BRD-05 (Multi-Agent AI System). Root cause analysis revealed three systemic issues:

1. **Review false positives** — Auditor persona flags regulations (PCI-DSS, KYC/AML) without checking if they apply to the document's domain. fact_checker persona (which has scope-mismatch detection) is NOT in the standard BRD review flow. Result: 3 of 8 P1 findings were false positives; true PRD-Ready score was ~65-70, not 42.

2. **Thin remediate-fix prompt** — `_build_remediate_fix_prompt()` gives the executor only 4 lines of generic instructions ("Fix the findings... apply targeted edits"). Compare: `_build_validate_fix_prompt()` has a detailed 5-step fix strategy. No document content embedded. Findings truncated to 300 chars. No FWDREF handling guidance. Result: codex renamed FWDREF-DEFERRED → FWDREF (39 cells) without adding content, produced shallow sections, introduced section ordering regression.

3. **No feedback loop** — No post-fix validation, no quality scoring, no check that findings were actually addressed vs cosmetically renamed. prd_ready_score left at stale '93'.

---

## Part A: Framework Fixes (mcp_ucx codebase — applies to ALL projects)

These fix the pipeline engine, prompt construction, and finding extraction logic. Changes here benefit every project that uses sdd_review/sdd_remediate.

### A-Tier 1: Quick Wins

**A1.1 Enrich Remediate-Fix Prompt Instructions**
- File: `mcp_ucx/src/mcp_server/remediation/runner.py` (lines 341-348)
- Replace 4-line generic instructions with detailed fix strategy:
  1. Read derived file FIRST to understand structure and existing content
  2. FWDREF-DEFERRED: do NOT rename without adding substantive content — renaming is not a fix
  3. New sections MUST have substantive content (≥3 paragraphs with specific details)
  4. Preserve existing section ordering — do NOT insert sections out of sequence
  5. Verify no new validation errors introduced
  6. For each finding, confirm the fix addresses the EXACT gap, not a symptom
- Impact: HIGH — directly prevents FWDREF renaming, shallow sections, ordering regressions
- Effort: 30min

**A1.2 Add fact_checker to Default BRD Review Persona Mapping**
- File: `mcp_ucx/skills/persona_mappings.yaml` (line 50)
- Change: `personas: [architect, auditor, business_analyst, chaos_engineer, fact_checker, chairperson]`
- Rationale: fact_checker persona already exists in framework (`mcp_ucx/skills/personas/fact_checker.md`) with "Scope Misunderstanding" detection — just not wired into BRD review flow
- Impact: HIGH — catches false positives before chairperson synthesis
- Effort: 5min (1-line YAML change)
- Note: Projects that already ran `sdd_init` keep their current mapping. New projects and `sdd_init --update-mappings` get the fix.

**A1.3 Add Applicability Veto to Chairperson Persona**
- File: `mcp_ucx/skills/personas/chairperson.md`
- Add 4th synthesis principle: verify findings are within document's declared scope; exclude out-of-scope findings from score calculation; list separately in manifest under `out_of_scope_findings`
- Impact: MED — safety net for false positives missed by fact_checker
- Effort: 15min

**A1.4 Add Scope Guard to Auditor Persona**
- File: `mcp_ucx/skills/personas/auditor.md`
- Add APPLICABILITY CHECK instruction at top of Compliance section: verify regulation is relevant to document's stated domain before flagging. Out-of-scope items → P1 "Scope Gap" not P0 "Compliance Blocker"
- Impact: MED — source-level false positive prevention
- Effort: 10min

### A-Tier 2: Code Changes

**A2.1 Increase recommended_action Truncation Limit**
- File: `mcp_ucx/src/mcp_server/remediation/review_parser.py` (line 71: `_clean_text`)
- Change default `max_len` from 300 to 2000 for recommended_action fields
- Impact: HIGH — executor receives full remediation guidance instead of truncated fragments
- Effort: 30min (2-line change + test update)

**A2.2 Embed Document Content in Remediate-Fix Prompt**
- File: `mcp_ucx/src/mcp_server/remediation/runner.py` (`_build_remediate_fix_prompt`, lines 287-351)
- After findings section, read derived copy file(s) and embed content (capped at 50K chars) in prompt under `## Current Document Content`
- Impact: HIGH — executor sees full document in context, makes targeted edits instead of blind insertions
- Effort: 1hr

**A2.3 Phased Execution in Remediate-Fix Prompt**
- File: `mcp_ucx/src/mcp_server/remediation/runner.py` (`_build_remediate_fix_prompt`)
- Group findings by priority: Phase 1 (P0 — fix first), Phase 2 (P1), Phase 3 (P2 — only if time)
- Impact: MED — executor focuses attention on critical fixes first
- Effort: 1hr

**A2.4 Priority-Aware Finding Cap**
- File: `mcp_ucx/src/mcp_server/remediation/runner.py` (finding cap logic, ~line 520)
- Include ALL P0s first, then P1s, then P2s up to 50 limit (currently flat `[:50]` slice)
- Add header: "N total findings; top 50 by priority shown; re-run after fixing"
- Impact: MED — P0 findings never silently dropped
- Effort: 45min

### A-Tier 3: Pipeline Changes

**A3.1 Post-Fix Validation Step**
- File: `mcp_ucx/src/mcp_server/tool_registry.py` (`_handle_lifecycle_pipeline`)
- Auto-run sdd_validate on remediated derived copy after remediate_fix stage completes
- Impact: HIGH — catches regressions (section ordering errors, broken YAML, new placeholder introductions)
- Effort: 2-3hr

**A3.2 Substantive Change Detection**
- File: `mcp_ucx/src/mcp_server/remediation/runner.py` (new function `verify_remediation_quality`)
- Compare original vs modified derived copy:
  - Count content delta (words/chars) — flag if suspiciously low for number of findings
  - Detect cosmetic-only changes (FWDREF-DEFERRED → FWDREF without new surrounding content)
  - Flag stub sections (header + <50 words)
  - Report findings that appear un-addressed
- Impact: HIGH — deterministic quality check, no LLM call needed
- Effort: 4-6hr

**A3.3 Quality Score Comparison (Before vs After)**
- File: `mcp_ucx/src/mcp_server/tool_registry.py`
- Extract original prd_ready_score from review report, compare with post-remediation re-score
- Output: `{ original_score, post_score, delta, target, meets_target }`
- Impact: MED — prevents stale scores; clear signal on whether another pass needed
- Effort: 2hr

---

## Part B: Project Fixes (b-local UCX templates — applies to b-local only)

These fix the project-specific review template and persona customizations that were scaffolded into `/opt/data/b-local/b-local-docs/UCX/`. Changes here only affect b-local's review quality.

**B1.1 Add Applicability Guard to b-local BRD Review Template**
- File: `/opt/data/b-local/b-local-docs/UCX/prompts/templates/review/UCR_PROMPT_BRD.md`
- Add `## APPLICABILITY PRE-SCREEN` section before persona reviews:
  1. Read BRD scope and domain sections (Sections 1-3) first
  2. Build explicit "Applicable Regulations" list from document's stated compliance scope
  3. Each persona must check this list before flagging regulatory gaps
- Modify "LAYER-APPROPRIATE FINDING CLASSIFICATION" table: regulations not in declared scope → P2 max with "verify applicability" note
- Impact: HIGH — eliminates false P0s from inapplicable regulations for b-local BRDs
- Effort: 30min

**B1.2 Add fact_checker to b-local BRD Review Persona Mapping**
- File: `/opt/data/b-local/b-local-docs/UCX/skills/persona_mappings.yaml` (line 50)
- Change: `personas: [architect, auditor, business_analyst, chaos_engineer, fact_checker, chairperson]`
- Impact: HIGH — immediate effect on next b-local review run
- Effort: 5min

**B1.3 Update b-local Chairperson with Applicability Veto**
- File: `/opt/data/b-local/b-local-docs/UCX/skills/personas/chairperson.md`
- Mirror the framework fix (A1.3) into the project copy
- Impact: MED
- Effort: 15min

**B1.4 Update b-local Auditor with Scope Guard**
- File: `/opt/data/b-local/b-local-docs/UCX/skills/personas/auditor.md`
- Mirror the framework fix (A1.4) into the project copy
- Impact: MED
- Effort: 10min

**B1.5 Add Output Template Applicability Field**
- File: `/opt/data/b-local/b-local-docs/UCX/prompts/templates/review/UCR_OUTPUT_TEMPLATE.md`
- Add `applicable_regulations` field to YAML frontmatter schema
- Add `Applicable` column (YES/NO/CONDITIONAL) to findings tables
- Add "Applicability Matrix" section between Document Control and Executive Summary
- Impact: LOW — structural improvement for future reviews
- Effort: 1hr

---

## Implementation Priority (Combined)

| # | Item | Scope | Impact | Effort | Key File |
|---|------|-------|--------|--------|----------|
| 1 | A1.1 Enrich remediate-fix prompt | Framework | HIGH | 30min | runner.py:341 |
| 2 | A1.2 + B1.2 fact_checker in persona mapping | Both | HIGH | 10min | persona_mappings.yaml |
| 3 | A2.1 Increase action truncation | Framework | HIGH | 30min | review_parser.py:71 |
| 4 | B1.1 Applicability guard in b-local template | Project | HIGH | 30min | UCR_PROMPT_BRD.md |
| 5 | A2.2 Embed document in remediate-fix | Framework | HIGH | 1hr | runner.py:287 |
| 6 | A1.3 + B1.3 Chairperson veto | Both | MED | 30min | chairperson.md |
| 7 | A1.4 + B1.4 Auditor scope guard | Both | MED | 20min | auditor.md |
| 8 | A2.4 Priority-aware finding cap | Framework | MED | 45min | runner.py |
| 9 | A2.3 Phased execution in prompt | Framework | MED | 1hr | runner.py |
| 10 | A3.1 Post-fix validation step | Framework | HIGH | 2-3hr | tool_registry.py |
| 11 | A3.2 Substantive change detection | Framework | HIGH | 4-6hr | runner.py (new) |
| 12 | A3.3 Quality score comparison | Framework | MED | 2hr | tool_registry.py |
| 13 | B1.5 Output template applicability field | Project | LOW | 1hr | UCR_OUTPUT_TEMPLATE.md |

Items 1-5 address ~80% of the quality problems observed in BRD-05.

## Verification

After implementation, re-run the BRD-05 pipeline:
1. `sdd_review` with codex → confirm false positives reduced (≤1 false P0)
2. `sdd_remediate` → confirm findings have full recommended_action text (>300 chars)
3. `sdd_remediate_fix` with codex → confirm:
   - FWDREF-DEFERRED not renamed without content
   - New sections have ≥3 substantive paragraphs
   - Section ordering preserved
   - Post-fix validation passes
4. Compare PRD-Ready scores: review score vs post-remediation score
