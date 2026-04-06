# CHANGELOG — UCX v1.15.0

**Release Date**: 2026-04-03
**Plan**: PLAN-024 (Review persona optimization), PLAN-025 (Creation/remediation persona optimization)

## Summary

Optimize persona mappings across all three UCX phases (creation, review, remediation). Max 5 personas per layer for review and remediation (PRD creation exception at 6). Fix category coverage gaps across creation phase. Remove deprecated legacy review prompts. Update all coupled template files.

## Changed

### Review Phase (PLAN-024)

Reduce bloated review persona lists to max 5 per layer. Update 5 review prompt templates with hardcoded persona sections.

| Layer | Before | After | Key Change |
|-------|--------|-------|------------|
| BRD | 11 | 5 | Keep architect, auditor, business_analyst, chaos_engineer, chairperson |
| PRD | 10 | 5 | Keep architect, auditor, tech_lead, product_owner, chaos_engineer |
| ADR | 7 | 5 | Keep architect, tech_lead, operator, auditor, chaos_engineer |
| SYS | 6 | 5 | Add auditor (fixes compliance gap), drop qa_lead, integration_lead |
| BDD | 6 | 5 | Drop integration_lead |
| EARS/REQ/SPEC/CTR/TSPEC | 5 | 5 | No change |

Review prompt templates updated: `UCR_PROMPT_BRD.md` (11→5 sections), `UCR_PROMPT_PRD.md` (10→5), `UCR_PROMPT_ADR.md` (7→5), `UCR_PROMPT_SYS.md` (6→5, added auditor section), `UCR_PROMPT_BDD.md` (6→5).

### Creation Phase (PLAN-025)

Fix coverage gaps in creation phase. All 7 PERSONA_CATEGORY_MAP categories (functional, quality, technical, integration, compliance, risk, operations) must be covered per layer.

| Layer | Before | After | Change |
|-------|--------|-------|--------|
| PRD | 7 | 6 | Drop qa_lead (testability covered by requirements_specialist) |
| ADR | 5 | 5 | Swap strategist → auditor (compliance coverage) |
| BDD | 4 | 5 | Add auditor (compliance) |
| SYS | 4 | 5 | Add auditor (compliance) |
| REQ | 4 | 5 | Add chaos_engineer (operations, risk) |
| SPEC | 4 | 5 | Add auditor (compliance) |
| CTR | 4 | 5 | Add chaos_engineer (operations) |
| TSPEC | 4 | 5 | Add auditor (compliance) |

### Remediation Phase (PLAN-025)

- `_default`: 6→5 personas — drop integration_lead (architect covers integration category)
- Removed Integration Fixer from all remediation templates (framework and b-local)
- Updated `UCRem_PERSONAS.md`: 6→5 fixer personas, removed Integration Fixer section, renumbered
- Updated `UCRem_REPORT_SCHEMA.md` and `UCRem_REPORT_TEMPLATE.md`

### Template Updates

All review, creation, and remediation prompt templates updated to match new persona mappings:

- Review: 5 `UCR_PROMPT_*.md` files rewritten (BRD, PRD, ADR, SYS, BDD)
- Creation: `UCC_OUTPUT_SCHEMA.md` PRD example updated
- Remediation: 8 `UCRem_PROMPT_*.md` + `UCRem_REPORT_TEMPLATE.md` + `UCRem_REPORT_SCHEMA.md` + `UCRem_PERSONAS.md`

### Documentation Updates

- `b-local UCX/README.md`: Updated persona counts, file tree, deprecated review/ references
- Architecture docs: Verified clean (no stale persona counts)

## Removed

- Deprecated legacy review files: `UCR_PROMPT_BRD_PROJECT.md`, `UCR_FORMAT_BRD_PROJECT.md`, `UCR_PROMPT_PRD_PROJECT.md` from `UCX/review/`
- Integration Fixer persona from remediation phase (architect absorbs cross-reference duties)
- Strategist from ADR creation (auditor replaces for compliance coverage)
- 6 review persona sections from BRD template (Tech Lead, Strategist, Operator, Integration Lead, Product Owner, Fact Checker)

## Accepted Coverage Gaps (by design)

| Phase | Layer | Missing Category | Rationale |
|-------|-------|-----------------|-----------|
| Creation | BRD | operations | Business doc; operational concerns caught in review |
| Creation | PRD | operations, risk | Already at 6 personas; both covered in review |
| Review | SPEC | compliance | integration_lead provides more value than auditor at this layer |
| Review | TSPEC | compliance | Same trade-off as SPEC |

## Persona Slot Totals

| Phase | Before | After |
|-------|--------|-------|
| Creation | 42 | 50 |
| Review | 65 | 50 |
| Remediation | 6 | 5 |
| **Grand Total** | **113** | **105** |

## Backward Compatibility

- `persona_mappings.yaml` format unchanged — only persona list values changed
- Projects with existing `sdd_init` copies must manually update their `UCX/skills/persona_mappings.yaml`
- Review prompt templates with hardcoded sections were fully rewritten — downstream projects using customized templates should regenerate via `sdd_init`

## Validation

- 214 unit tests passed
- All persona names resolve to `.md` files across all 3 phases
- BRD review prompt assembles correctly with 5 core personas
- Category coverage verified: 8/10 creation layers at 7/7, 8/10 review layers at 7/7, remediation at 7/7

## Files Changed

### Persona Mappings
- `mcp_sdd/skills/persona_mappings.yaml` — all three phases updated

### Review Templates (b-local)
- `UCX/prompts/templates/review/UCR_PROMPT_BRD.md` — rewritten (11→5 sections)
- `UCX/prompts/templates/review/UCR_PROMPT_PRD.md` — rewritten (10→5 sections)
- `UCX/prompts/templates/review/UCR_PROMPT_ADR.md` — rewritten (7→5 sections)
- `UCX/prompts/templates/review/UCR_PROMPT_SYS.md` — rewritten (6→5 sections, added auditor)
- `UCX/prompts/templates/review/UCR_PROMPT_BDD.md` — updated (6→5 sections)

### Creation Templates (b-local)
- `UCX/prompts/templates/creation/UCC_OUTPUT_SCHEMA.md` — PRD example updated

### Remediation Templates (framework + b-local)
- `UCRem_PROMPT_{BRD,PRD,EARS,BDD,ADR,REQ,TSPEC}.md` — removed Integration Fixer
- `UCRem_REPORT_TEMPLATE.md` — removed Integration Fixer
- `UCRem_REPORT_SCHEMA.md` — removed Integration Fixer
- `UCRem_PERSONAS.md` — rewritten (6→5 fixers, removed section 4)

### Documentation
- `b-local UCX/README.md` — updated persona counts, file tree
- Deleted: `UCX/review/UCR_PROMPT_BRD_PROJECT.md`, `UCR_FORMAT_BRD_PROJECT.md`, `UCR_PROMPT_PRD_PROJECT.md`
