# Implementation Plan - Add Upstream Verification to SDD Framework

**Created**: 2025-11-28 16:05:58 EST
**Status**: Ready for Implementation

## Objective

Add guidance to all templates, creation rules, and skills emphasizing:
1. Check what upstream artifacts actually exist before creating traceability tags
2. Use `null` or omit tags only when upstream artifacts genuinely don't exist
3. Do NOT create placeholder references to non-existent documents
4. Create missing upstream artifacts only if required by SDD workflow

## User Decisions

- **Callout placement**: After Document Control section (top of document)
- **Skills update**: Yes, update all doc-* skills too

## Scope

### Files to Update

**Templates (13 files)**:
- `ai_dev_flow/BRD/BRD-TEMPLATE.md`
- `ai_dev_flow/PRD/PRD-TEMPLATE.md`
- `ai_dev_flow/EARS/EARS-TEMPLATE.md`
- `ai_dev_flow/BDD/BDD-TEMPLATE.md`
- `ai_dev_flow/ADR/ADR-TEMPLATE.md`
- `ai_dev_flow/SYS/SYS-TEMPLATE.md`
- `ai_dev_flow/REQ/REQ-TEMPLATE.md`
- `ai_dev_flow/IMPL/IMPL-TEMPLATE.md`
- `ai_dev_flow/CTR/CTR-TEMPLATE.md`
- `ai_dev_flow/SPEC/SPEC-TEMPLATE.md`
- `ai_dev_flow/TASKS/TASKS-TEMPLATE.md`
- `ai_dev_flow/IPLAN/IPLAN-TEMPLATE.md`
- `ai_dev_flow/ICON/ICON-TEMPLATE.md`

**Creation Rules (13 files)**:
- `ai_dev_flow/BRD/BRD_CREATION_RULES.md`
- `ai_dev_flow/PRD/PRD_CREATION_RULES.md`
- `ai_dev_flow/EARS/EARS_CREATION_RULES.md`
- `ai_dev_flow/BDD/BDD_CREATION_RULES.md`
- `ai_dev_flow/ADR/ADR_CREATION_RULES.md`
- `ai_dev_flow/SYS/SYS_CREATION_RULES.md`
- `ai_dev_flow/REQ/REQ_CREATION_RULES.md`
- `ai_dev_flow/IMPL/IMPL_CREATION_RULES.md`
- `ai_dev_flow/CTR/CTR_CREATION_RULES.md`
- `ai_dev_flow/SPEC/SPEC_CREATION_RULES.md`
- `ai_dev_flow/TASKS/TASKS_CREATION_RULES.md`
- `ai_dev_flow/IPLAN/IPLAN_CREATION_RULES.md`
- `ai_dev_flow/ICON/ICON_CREATION_RULES.md`

**Skills (12 files)**:
- `.claude/skills/doc-brd/SKILL.md`
- `.claude/skills/doc-prd/SKILL.md`
- `.claude/skills/doc-ears/SKILL.md`
- `.claude/skills/doc-bdd/SKILL.md`
- `.claude/skills/doc-adr/SKILL.md`
- `.claude/skills/doc-sys/SKILL.md`
- `.claude/skills/doc-req/SKILL.md`
- `.claude/skills/doc-impl/SKILL.md`
- `.claude/skills/doc-ctr/SKILL.md`
- `.claude/skills/doc-spec/SKILL.md`
- `.claude/skills/doc-tasks/SKILL.md`
- `.claude/skills/doc-iplan/SKILL.md`

## Changes to Make

### 1. Add Callout Box to Each Template

Add after Document Control section in each template:

```markdown
> **⚠️ UPSTREAM ARTIFACT REQUIREMENT**: Before completing traceability tags:
> 1. **Check existing artifacts**: List what upstream documents actually exist in `docs/`
> 2. **Reference only existing documents**: Use actual document IDs, not placeholders
> 3. **Use `null` appropriately**: Only when upstream artifact type genuinely doesn't exist for this feature
> 4. **Do NOT create phantom references**: Never reference documents that don't exist
> 5. **Create missing artifacts if required**: If SDD workflow requires an upstream artifact that's missing, create it first
```

### 2. Add Section to Each Creation Rules File

Add new section "Upstream Artifact Verification Process":

```markdown
## N. Upstream Artifact Verification Process

### Before Creating This Document

**Step 1: Inventory Existing Upstream Artifacts**

```bash
# List existing upstream artifacts for this layer
ls -la docs/BRD/    # Layer 1
ls -la docs/PRD/    # Layer 2
ls -la docs/EARS/   # Layer 3
ls -la docs/BDD/    # Layer 4
ls -la docs/ADR/    # Layer 5
ls -la docs/SYS/    # Layer 6
ls -la docs/REQ/    # Layer 7
# ... continue for applicable layers
```

**Step 2: Map Existing Documents to Traceability Tags**

| Tag | Required for Layer N | Existing Document | Action |
|-----|---------------------|-------------------|--------|
| @brd | Yes/No | BRD-001 or null | Reference/Create/Skip |
| @prd | Yes/No | PRD-001 or null | Reference/Create/Skip |
| ... | ... | ... | ... |

**Step 3: Decision Rules**

| Situation | Action |
|-----------|--------|
| Upstream exists | Reference with exact document ID |
| Upstream required but missing | Create upstream artifact FIRST, then reference |
| Upstream optional and missing | Use `null` in traceability tag |
| Upstream not applicable | Omit tag entirely |

### Traceability Tag Rules

- **NEVER** use placeholder IDs like `BRD-XXX` or `TBD`
- **NEVER** reference documents that don't exist
- **ALWAYS** verify document exists before adding reference
- **USE** `null` only when artifact type is genuinely not applicable
```

### 3. Update Frontmatter Traceability Section in Templates

Change from:
```yaml
traceability:
  brd: "BRD-NNN"
  prd: "PRD-NNN"
  # ...
```

To:
```yaml
traceability:
  # INSTRUCTION: Replace with actual document IDs or null if not applicable
  # Run: ls docs/TYPE/ to find existing documents before filling
  brd: "BRD-NNN" # or null if no BRD exists for this feature
  prd: "PRD-NNN" # or null if no PRD exists for this feature
  # ...
```

### 4. Add Section to Each doc-* Skill

Add to Prerequisites section:

```markdown
### Upstream Artifact Verification (CRITICAL)

**Before creating this document, you MUST:**

1. **List existing upstream artifacts**:
   ```bash
   ls docs/BRD/ docs/PRD/ docs/EARS/ # ... applicable upstream types
   ```

2. **Reference only existing documents** in traceability tags
3. **Use `null`** only when upstream artifact type genuinely doesn't exist
4. **NEVER use placeholders** like `BRD-XXX` or `TBD`
5. **Create missing required upstream first** if SDD workflow mandates it
```

## Execution Order

1. Update all 13 templates with callout box after Document Control
2. Update all 13 creation rules with verification process section
3. Update all 12 doc-* skills with upstream verification guidance
4. Update TRACEABILITY.md with global upstream verification rules

## Validation

After updates, verify:
```bash
# Check all templates have the callout
grep -l "UPSTREAM ARTIFACT REQUIREMENT" ai_dev_flow/*/*.md | grep TEMPLATE

# Check all creation rules have verification section
grep -l "Upstream Artifact Verification" ai_dev_flow/*/*_CREATION_RULES.md

# Check all skills have verification guidance
grep -l "Upstream Artifact Verification" .claude/skills/doc-*/SKILL.md
```

## Total Files to Update

| Category | Count |
|----------|-------|
| Templates | 13 |
| Creation Rules | 13 |
| Skills | 12 |
| **Total** | **38** |
