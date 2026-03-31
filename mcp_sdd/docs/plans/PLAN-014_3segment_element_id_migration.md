# PLAN-014: 3-Segment Element ID Migration

**Status**: Draft
**Created**: 2026-03-30
**Updated**: 2026-03-31
**Scope**: Migrate element IDs from 4-segment `TYPE.NN.TT.hash` to 3-segment `TYPE.NN.hash` for YAML documents
**Risk**: Medium — breaking change for element IDs; all downstream project docs (b-local etc.) will be re-created

---

## Context

In the old MD-based sectioned format, element IDs used 4 segments: `BRD.02.01.8cf7` where `.01` is the element type code (Functional Requirement). This was necessary because markdown headings (`### BRD.02.01.8cf7: Feature Name`) needed self-documenting type context.

In unified YAML templates, the parent key already provides type context:

```yaml
functional_requirements:    # ← type context is HERE
  - id: "BRD.02.8cf7"      # ← type code in ID is redundant
    title: "Feature Name"
```

The type code segment is redundant noise that creates confusion (all-digit hashes like `2616` look like sequential IDs).

**New format**: `TYPE.NN.hash` (3 segments)
- `BRD.02.8cf7` — element in BRD-02
- `PRD.01.a3b2` — element in PRD-01
- Hash: SHA256 4-char hex, input: `"{doc_id}:{yaml_key}:{title}"`

**No backward compatibility with b-local**: All b-local project documents will be re-created from scratch with 3-segment IDs.

---

## Decisions

1. **Hash input**: `"{doc_id}:{yaml_key}:{title}"` — YAML parent key replaces type code as semantic differentiator
2. **Hash length**: 4-char hex (65,536 values per document). Collision: extend to 5-8 chars for the colliding element only. Detection happens at document generation time (mcp_sdd `sdd_create` or manual authoring). Duplicate `{yaml_key}:{title}` pairs within a document are invalid — each element must have a unique title within its parent key.
3. **No dual-format transition**: 3-segment is the only valid format. 4-segment is deprecated immediately. All project docs re-created.
4. **Element type code table (01-99)**: Deprecated for ID purposes. Retained in `ID_NAMING_STANDARDS.md` as historical reference only. YAML key names replace type codes for semantic meaning.
5. **BRD Section-to-Element-Code Mapping**: Deprecated. Replace with "YAML key validation" — each template defines valid section keys.
6. **Pattern-based search trade-off**: `grep -r "\.96\."` (find all Security requirements) no longer works. Replacement: `grep -r "security"` on YAML keys. Documented as accepted trade-off.
7. **Validation regex**: `^[A-Z]{2,8}\.\d{2,}\.[0-9a-f]{4,8}$` — 3-segment only, no dual-format

---

## Phase 1: Standards Authority (3 files)

Update the primary authority documents.

| File | Changes |
|------|---------|
| `ai_dev_ssd_flow/ID_NAMING_STANDARDS.md` | Replace 4-segment format with 3-segment. Remove element type code from format spec. Update regex to `^[A-Z]{2,8}\.\d{2,}\.[0-9a-f]{4,8}$`. Deprecate type code table (mark as historical). Remove Section-to-Element-Code Mapping. Update all examples. Update IDPAT-E002, IDPAT-E003 messages. |
| `ai_dev_ssd_flow/VALIDATION_STANDARDS.md` | Update IDPAT-E002 format to 3-segment. Update IDPAT-E003 "normalize to dot notation (TYPE.NN.hash)". Update IDPAT-W001. Deprecate ELEM-E001/W001 (type codes no longer in IDs). |
| `ai_dev_ssd_flow/LAYER_REGISTRY.yaml` | Change `id_patterns.element` to `^[A-Z]{2,8}\.\d{2,}\.[0-9a-f]{4,8}$`. Remove `id_patterns.document` (unchanged). |

---

## Phase 1.5: Archive AUTOPILOT (prerequisite)

The `ai_dev_ssd_flow/AUTOPILOT/` directory (14 files, 49 element ID occurrences) is deprecated infrastructure. Archive to `ai_dev_ssd_flow/archived/AUTOPILOT_v1_archive/` before proceeding. This eliminates Python scripts with hardcoded ID-parsing logic that would need code changes otherwise.

---

## Phase 2: Template Updates (22 files)

### Phase 2a: Primary templates (11 files in `mcp_sdd/templates/`)

For each template:
- `id_standard.format:` → `"{doc_type}.{doc_id}.{hash}"`
- `id_standard._guidance:` → hash input: `"{doc_id}:{yaml_key}:{title}"`
- All inline examples: `TYPE.NN.TT.xxxx` → `TYPE.NN.xxxx`
- Remove `{section_id}` from format definition

Files: `BRD-TEMPLATE.yaml`, `PRD-TEMPLATE.yaml`, `EARS-TEMPLATE.yaml`, `BDD-TEMPLATE.yaml`, `ADR-TEMPLATE.yaml`, `SYS-TEMPLATE.yaml`, `REQ-TEMPLATE.yaml`, `CTR-TEMPLATE.yaml`, `SPEC-TEMPLATE.yaml`, `TSPEC-TEMPLATE.yaml`, `TASKS-TEMPLATE.yaml`

**SPEC-TEMPLATE.yaml special**: Also update `element_ids:` section examples from `SPEC.01.16.01` to `SPEC.01.xxxx` format.

### Phase 2b: Mirror templates (11 files in `ai_dev_ssd_flow/{NN}_{TYPE}/`)

Copy-sync from `mcp_sdd/templates/` to layer directories.

### Phase 2c: Layer READMEs (11 files in `ai_dev_ssd_flow/{NN}_{TYPE}/README.md`)

Each README contains element ID examples (e.g., `BRD.01.07.a7f3`). Update all to 3-segment format.

---

## Phase 3: SPEC Subtype Files (10 files)

| File | Changes |
|------|---------|
| `09_SPEC/CSPEC/CSPEC_MVP_SCHEMA.yaml` | `element_id_format` → `"CSPEC.{DOC}.{hash}"` |
| `09_SPEC/CSPEC/CSPEC-MVP-TEMPLATE.yaml` | Update ID examples |
| `09_SPEC/DSPEC/DSPEC_MVP_SCHEMA.yaml` | Same |
| `09_SPEC/DSPEC/DSPEC-MVP-TEMPLATE.yaml` | Same |
| `09_SPEC/UXSPEC/UXSPEC_MVP_SCHEMA.yaml` | Same |
| `09_SPEC/UXSPEC/UXSPEC-MVP-TEMPLATE.yaml` | Same |
| `09_SPEC/RISKSPEC/RISKSPEC_MVP_SCHEMA.yaml` | Same |
| `09_SPEC/RISKSPEC/RISKSPEC-MVP-TEMPLATE.yaml` | Same |
| `09_SPEC/PROCSPEC/PROCSPEC_MVP_SCHEMA.yaml` | Same |
| `09_SPEC/PROCSPEC/PROCSPEC-MVP-TEMPLATE.yaml` | Same |

---

## Phase 4: mcp_sdd Prompt Templates (11 files)

**Critical** — these instruct AI agents on ID format during document creation/review.

### Creation prompts (6 files in `mcp_sdd/prompts/templates/creation/`)

| File | Key change |
|------|------------|
| `UCC_PROMPT_BRD.md` | Update element ID format instructions |
| `UCC_PROMPT_PRD.md` | **HIGH** — has explicit "Use ONLY the unified 4-segment format" instruction. Replace with 3-segment. |
| `UCC_PROMPT_EARS.md` | Update element ID examples |
| `UCC_PROMPT_BDD.md` | Update element ID examples |
| `UCC_PROMPT_TSPEC.md` | Update element ID examples |
| `UCC_OUTPUT_SCHEMA.md` | Update output ID format |

### Review prompts (1 file)

| File | Key change |
|------|------------|
| `UCR_PROMPT_BRD.md` | Update ID format references |

### Remediation prompts (4 files)

| File | Key change |
|------|------------|
| `UCRem_PROMPT_BRD.md` | Update ID format references |
| `UCRem_PROMPT_PRD.md` | Update ID format references |
| `UCRem_PROMPT_EARS.md` | Update ID format references |
| `UCRem_PROMPT_ADR.md` | Update ID format references |

---

## Phase 5: Framework Documentation (~25 files)

| File | Key changes |
|------|-------------|
| `ai_dev_ssd_flow/README.md` | Element reference table |
| `ai_dev_ssd_flow/QUICK_REFERENCE.md` | Element format row |
| `ai_dev_ssd_flow/TRACEABILITY.md` | Tag format, cross-ref examples |
| `ai_dev_ssd_flow/METADATA_TAGGING_GUIDE.md` | Dot notation explanation |
| `ai_dev_ssd_flow/COMPLETE_TAGGING_EXAMPLE.md` | Usage examples |
| `ai_dev_ssd_flow/CUMULATIVE_TAG_REFERENCE.md` | Validation logic |
| `ai_dev_ssd_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` | `@artifact-type` format |
| `ai_dev_ssd_flow/AI_ASSISTANT_RULES.md` | XDOC-006, inline examples |
| `ai_dev_ssd_flow/TRACEABILITY_MATRIX_COMPLETE-TEMPLATE.md` | Feature ID format |
| `ai_dev_ssd_flow/TRACEABILITY_SETUP.md` | Format references |
| `ai_dev_ssd_flow/TESTING_STRATEGY_TDD.md` | 9x `BRD.01.01.01` references |
| `ai_dev_ssd_flow/METADATA_VS_TRACEABILITY.md` | 6 mixed IDs |
| `ai_dev_ssd_flow/THRESHOLD_NAMING_RULES.md` | `@threshold:` tag format |
| `ai_dev_ssd_flow/01_BRD/BRD-00_GLOSSARY.md` | 1 ID reference |
| `ai_dev_ssd_flow/METADATA_CORE_MATRIX.md` | If any ID refs |
| `ai_dev_ssd_flow/AI_TOOL_OPTIMIZATION_GUIDE.md` | 1 ID ref |
| `ai_dev_ssd_flow/PROJECT_SETUP_GUIDE.md` | 1 ID ref |
| `ai_dev_ssd_flow/PROJECT/PROJECT_MODEL.md` | 23 ID refs |
| `ai_dev_ssd_flow/FINANCIAL_DOMAIN_CONFIG.md` | 9 ID refs |
| `ai_dev_ssd_flow/10_TSPEC/TSPEC-00_index.md` | 6 ID refs |
| `ai_dev_ssd_flow/09_SPEC/CSPEC/CSPEC-00_index.md` | 5 ID refs |
| `ai_dev_ssd_flow/09_SPEC/CSPEC/CSPEC_MVP_CREATION_RULES.md` | 5 ID refs |
| `ai_dev_ssd_flow/05_ADR/ADR-00_ai_powered_documentation_assistant_architecture.md` | 5 ID refs |
| `ai_dev_ssd_flow/09_SPEC/DSPEC/DSPEC-00_index.md` | 4 ID refs |
| `ai_dev_ssd_flow/09_SPEC/DSPEC/DSPEC_MVP_CREATION_RULES.md` | 4 ID refs |

---

## Phase 6: Claude Code Skills (~41 files with element IDs)

Location: `/opt/data/docs_flow_framework/.claude/skills/`

**High priority** (most occurrences):
- `doc-naming/SKILL.md` (24 occurrences) — primary ID authority for AI
- `doc-naming_quickref.md` (20 occurrences)
- `doc-brd/SKILL.md`, `doc-brd-autopilot/SKILL.md` (~15 combined)
- `doc-spec/SKILL.md`, `doc-spec-autopilot/SKILL.md` (~13 combined)
- `doc-tasks/SKILL.md`, `doc-tasks-autopilot/SKILL.md` (~17 combined)
- `doc-sys/SKILL.md`, `doc-sys-autopilot/SKILL.md` (~13 combined)
- `doc-tspec/SKILL.md`, `doc-tspec-autopilot/SKILL.md` (~14 combined)
- `doc-ctr/SKILL.md` (~4)

**Medium priority** (2-3 each):
- `trace-check/SKILL.md`, `doc-flow/SKILL.md`, `doc-flow/SHARED_CONTENT.md`
- `doc-req/SKILL.md`, `doc-adr/SKILL.md`

**All other** doc-* and doc-*-autopilot skills: 1-2 occurrences each

Total: ~41 files, ~227 occurrences

---

## Phase 7: mcp_sdd Persona Skills (15 files)

Location: `/opt/data/docs_flow_framework/mcp_sdd/skills/personas/`

Check and update if any persona files reference element ID format. These files define expert personas used in creation/review prompts.

Files: `architect.md`, `auditor.md`, `business_analyst.md`, `chairperson.md`, `chaos_engineer.md`, `fact_checker.md`, `integration_lead.md`, `operator.md`, `product_owner.md`, `qa_lead.md`, `requirements_specialist.md`, `strategist.md`, `tech_lead.md`, `ux_strategist.md`

---

## Phase 8: mcp_sdd Source & Tests

| File | Changes |
|------|---------|
| `mcp_sdd/src/mcp_server/validation/runner.py` | Update element ID regex if present |
| `mcp_sdd/src/mcp_server/tool_registry.py` | Check for ID format references |
| `mcp_sdd/tests/unit/test_auth_example.py` | Update `@brd: BRD.01.01.01` → 3-segment |
| Other test files | Check for element ID patterns |

---

## Phase 9: Governance & Root Docs

| File | Changes |
|------|---------|
| `README.md` (root) | Update element ID format if referenced |
| `README_AIAGENT.md` | Check for ID format refs |
| `governance/` files | Check for element ID references |

---

## Phase 10: Documentation, Changelog & Roadmap

### SDD Framework Docs (updated in earlier phases, verified here)

| File | Phase Updated | Verify |
|------|---------------|--------|
| `ai_dev_ssd_flow/README.md` | Phase 5 | Element ID table uses 3-segment |
| `README.md` (root) | Phase 9 | Element ID section uses 3-segment |

### SDD Framework Changelog & Roadmap

| File | Action |
|------|--------|
| `changelog/CHANGELOG_v0.13.0.md` | CREATE — minor release: 3-segment element IDs, AUTOPILOT archived |
| `roadmap/ROADMAP.md` | Update: v0.12.1 → v0.13.0, add completed release entry |

### mcp_sdd Documentation

| File | Action |
|------|--------|
| `mcp_sdd/docs/README.md` | Update changelog index, add v1.6.0 entry |
| `mcp_sdd/docs/architecture/MCP_CLI_REFERENCE.md` | Update element ID examples if present |
| `mcp_sdd/docs/specs/SPEC-003_mcp_creation_validation_profile_contracts.md` | Update element ID format in contracts |
| `mcp_sdd/skills/README.md` | Update element ID format if referenced |

### mcp_sdd Changelog & Roadmap

| File | Action |
|------|--------|
| `mcp_sdd/docs/ROADMAP.md` | Update: v1.5.0 → v1.6.0, add v1.6.0 release entry |
| `mcp_sdd/docs/CHANGELOG/CHANGELOG_v1.6.0.md` | CREATE — 3-segment IDs, template updates, regex, prompt template fixes |

---

## Phase 11: Final Review

1. `grep -rP '[A-Z]{2,8}\.\d{2,}\.\d{2,}\.[0-9a-f]{2,}' ai_dev_ssd_flow/ mcp_sdd/ .claude/ --include='*.md' --include='*.yaml' | grep -v archive | grep -v v1_archive` — verify 0 active 4-segment refs remain
2. Validate all 11 template YAML files
3. Run `python -m pytest tests/` — all tests pass
4. Dry-run `sdd_create` for BRD — verify 3-segment IDs in output
5. Run `sdd_validate_links` on `ai_dev_ssd_flow/` — no broken links

---

## Traceability: Cascade Rule

**When a document is re-created with 3-segment IDs, ALL downstream documents referencing its old IDs must also be re-created.** This is by design — b-local and all project docs will be re-created from scratch.

No migration tooling for existing cross-references. Clean break.

---

## Trade-offs (Documented)

| Lost Capability | Replacement |
|----------------|-------------|
| `grep "\.96\."` finds all Security requirements | `grep "security"` on YAML keys |
| Element type visible in ID at a glance | YAML parent key provides context |
| Section-to-Code validation via ID | Template schema defines valid keys |
| All-digit hashes look like sequential numbers | Accepted — hash is deterministic, context is in YAML structure |

---

## Phase Dependencies

```
Phase 1 (Standards) → Phase 1.5 (Archive AUTOPILOT)
                    → Phase 2 (Templates: 2a primary + 2b mirrors + 2c READMEs)
                    → Phase 3 (SPEC subtypes)
                    → Phase 4 (Prompt templates)
                    → Phase 5 (Framework docs ~26 files)
                    → Phase 6 (Claude Code skills ~41 files)
                    → Phase 7 (mcp_sdd personas)
                    → Phase 8 (Source & tests)
                    → Phase 9 (Governance)
Phase 2-9 complete → Phase 10 (Changelog)
Phase 10 complete  → Phase 11 (Final review)
```

Note: Template examples using non-hex chars (e.g., `g7k2`) must be corrected to valid hex (`a7f3`, `8cf7`, etc.) during Phase 2.

Phases 3-9 can run in parallel after Phase 2.

---

## Verification Checklist

- [ ] Regex `^[A-Z]{2,8}\.\d{2,}\.[0-9a-f]{4,8}$` validates `BRD.02.8cf7` → PASS
- [ ] Regex rejects `BRD.02.01.8cf7` (4-segment) → PASS
- [ ] All 11 templates use `format: "{doc_type}.{doc_id}.{hash}"`
- [ ] `UCC_PROMPT_PRD.md` no longer says "4-segment"
- [ ] `doc-naming/SKILL.md` teaches 3-segment format
- [ ] `python -m pytest tests/` — all pass
- [ ] Dry-run `sdd_create` → 3-segment IDs in output
- [ ] Zero 4-segment refs in active files (excluding archives)
