---
layer: 09_CHG
lens: document_control_lifecycle
weight: 0
agent: framework-maintainer
framework_spec_version: "0.53.0"
type: process-playbook
---
# Document Control Lifecycle Management

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-09-07 |
| Author | Framework Maintainer |
| Framework Version | 0.53.0 |

## Purpose

Process playbook for managing `document_control` blocks across all framework
documents (GD-24). Covers adding, updating, verifying, and auditing document
lifecycle metadata. This is NOT a review lens — it is an execution guide.

## When to use

- Adding document_control to a new or existing document
- Updating version/status/last_updated after a change
- Verifying document_control consistency across the framework
- Auditing framework documents for missing or stale metadata

## Document Control Formats

### MD files (governance docs, gates, READMEs, root docs)

```markdown
## Document Control

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Approved |
| Last Updated | YYYY-MM-DD |
| Author | [Name or Role] |
| Framework Version | X.Y.Z |
```

**Placement:** After the first `#` heading, before the main content.

### YAML layer templates (BRD, PRD, EARS, etc.)

```yaml
document_control:
  _size_target: 100
  version: "1.0"
  status: Approved
  last_updated: "YYYY-MM-DDTHH:MM:SS"
  author: "[Author]"
  framework_version: "X.Y.Z"
```

**Placement:** After the `metadata:` block, as a top-level key.

### YAML data files (LAYER_REGISTRY, ADAPTATION_SURFACE, etc.)

```yaml
metadata:
  schema_version: "1.0.0"
  # ... existing fields ...
  last_updated: "YYYY-MM-DD"
  framework_version: "X.Y.Z"
```

**Placement:** Added to the existing `metadata:` block. NEVER create a
duplicate `metadata:` key — YAML parsers silently drop fields from earlier
duplicate keys.

## Required Fields

| Field | Format | Description |
|-------|--------|-------------|
| Version | Sequential (1.0, 2.0, ...) | Bumped on each rewrite via CHG |
| Status | Draft / Approved / Deprecated | Lifecycle state |
| Last Updated | ISO 8601 date | Date of last modification |
| Author | Name or role | Who last modified the document |
| Framework Version | SemVer (X.Y.Z) | `framework/VERSION` at creation/update time |

## Operations

### Adding Document Control to a New Document

1. Determine the document type (MD governance, MD gate, MD README, YAML data)
2. Apply the correct format from the templates above
3. Set `Version: 1.0`, `Status: Draft`
4. Set `Framework Version` to current `framework/VERSION`
5. Set `Last Updated` to current date
6. Place after the first heading (MD) or in metadata block (YAML)

### Updating Document Control on Change

1. Bump `Version` (1.0 → 2.0 → 3.0, etc.)
2. Update `Last Updated` to current date
3. Set `Framework Version` to current `framework/VERSION`
4. Update `Status` if applicable (Draft → Approved, etc.)
5. Archive the previous version per CHG process

### Verifying Document Control Consistency

Run these checks after any framework change:

```bash
# Check all MD files have Document Control
find . -name "*.md" -not -path "./archive/*" | while read f; do
  grep -q "^## Document Control" "$f" || echo "MISSING: $f"
done

# Check no duplicate Document Control sections
grep -rc "^## Document Control" --include="*.md" . | grep -v archive | awk -F: '{if($2>1) print}'

# Check framework_version matches VERSION
VERSION=$(cat framework/VERSION)
grep -r "Framework Version | " --include="*.md" . | grep -v archive | grep -v "$VERSION" | head -5

# Check YAML files have last_updated
for f in registry/LAYER_REGISTRY.yaml governance/*.yaml; do
  grep -q "last_updated" "$f" || echo "MISSING: $f"
done

# Verify YAML parses correctly
python3 -c "import yaml; yaml.safe_load(open('governance/PROFILE-TEMPLATE.yaml'))"
```

### Auditing Framework Documents

Full audit checklist:

```markdown
- [ ] Every .md file in framework/ (excl. archive, templates, playbook roles) has ## Document Control
- [ ] Every YAML data file has last_updated + framework_version in metadata
- [ ] No duplicate metadata: keys in any YAML file
- [ ] All Framework Version values match framework/VERSION
- [ ] All Last Updated dates are ISO 8601 format
- [ ] All Version fields are bumped after CHG rewrites
- [ ] No stale document_control (Status: Draft on old documents)
- [ ] Archive contains originals for all modified documents
```

## Common Pitfalls

1. **Duplicate `metadata:` key in YAML** — Adding a new `metadata:` block when
   one already exists causes YAML parsers to silently drop the earlier fields.
   ALWAYS merge into the existing block.

2. **Wrong Framework Version** — Must be the current `framework/VERSION`, not the
   previous version. After a VERSION bump, all newly-created/updated document
   control blocks must use the new version.

3. **Missing from subdirectories** — `governance/*.md` glob misses
   `governance/chg/README.md`. Use recursive find or explicit enumeration.

4. **Stale Last Updated** — The date must reflect when the document was actually
   modified, not when document_control was first added.

5. **Inconsistent Status values** — Use the exact enum: Draft, Approved,
   Deprecated. Do not use "Complete", "Done", "Active", etc.

## Cross-references

- `governance/DECISIONS.md` — GD-24 (Document control convention)
- `governance/DOC_GOVERNANCE_CORE.md` — §Principle 10 (Document lifecycle tracking)
- `governance/DOC_GOVERNANCE_CORE.md` — §Governance document lifecycle tracking
- `layers/09_CHG/README.md` — §Framework Self-Changes
- `layers/09_CHG/gates/GATE-SPEC_FRAMEWORK.md` — GATE-SPEC-E005 (VERSION bump)
- `governance/SECURITY_REVIEW.md` — T1-T4 threat review for metadata changes
