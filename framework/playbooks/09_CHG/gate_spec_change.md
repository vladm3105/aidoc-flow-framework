---
layer: 09_CHG
lens: gate_spec_process
weight: 0
agent: framework-maintainer
framework_spec_version: "0.53.0"
type: process-playbook
---
# GATE-SPEC Framework Self-Change Process

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-09-07 |
| Author | Framework Maintainer |
| Framework Version | 0.53.0 |

## Purpose

Step-by-step process playbook for modifying `framework/` itself (templates,
governance, registry, VERSION). This is NOT a review lens — it is an execution
guide for the agent or human performing the change. For review lenses, see the
existing 09_CHG playbooks (architect, auditor, security_engineer, etc.).

## When to use

- Editing any file under `framework/` (templates, governance, registry, VERSION)
- Adding or modifying layer templates
- Changing governance rules or lint rules
- Updating the registry or C4 mapping
- Bumping `framework/VERSION`

## Prerequisites

- Change classified as C2 or C3 (spec changes are NEVER C1 per GATE-SPEC-E003)
- SemVer impact determined (major/minor/patch)
- Both platform owners identified (for C3 approval)

## Process Steps

### Phase 1: Classify and Plan

1. **Classify the change**
   - C2: additive changes, new optional fields, new governance rules (minor/patch)
   - C3: breaking changes to schemas, removing fields, changing required sections (major)
   - Never C1 for spec changes

2. **Determine SemVer impact**
   - `major`: breaking change to layer schema, registry model, or governance rule
   - `minor`: backward-compatible additions (new optional keys, new gates, new playbook roles)
   - `patch`: clarifications, typo fixes, documentation-only changes

3. **Create CHG record**
   - Use `layers/09_CHG/CHG-TEMPLATE.yaml` as the template
   - Set `change_source: spec`
   - Set `entry_gate: GATE-SPEC`
   - Set `semver_impact` to the determined value
   - Set `change_level` to C2 or C3

### Phase 2: Archive Originals

4. **Create archive directory**
   ```sh
   mkdir -p archive/CHG-{NN}/{category}
   ```

5. **Archive ALL files before modification**
   ```sh
   # Governance docs
   cp governance/*.md archive/CHG-{NN}/governance/
   
   # Gate definitions
   cp layers/09_CHG/gates/*.md archive/CHG-{NN}/layers/09_CHG/gates/
   
   # Layer READMEs
   for d in layers/*/; do
     [ -f "$d/README.md" ] && cp "$d/README.md" "archive/CHG-{NN}/$d"
   done
   
   # Root docs
   cp README.md AI_ASSISTANT_RULES.md archive/CHG-{NN}/root/
   
   # YAML files
   cp registry/LAYER_REGISTRY.yaml archive/CHG-{NN}/registry/
   ```

6. **Verify archive completeness**
   ```sh
   find archive/CHG-{NN} -type f | wc -l
   ```

### Phase 3: Update Artifacts

7. **Add/Update Document Control blocks** (per GD-24)
   - MD files: Add `## Document Control` table after first heading
   - YAML files: Add `last_updated` and `framework_version` to `metadata:`
   - Required fields: Version, Status, Last Updated, Author, Framework Version

8. **Make the actual changes**
   - Edit templates, governance rules, registry as needed
   - Follow existing patterns and conventions
   - Ensure changes are consistent across all affected files

9. **Update CHG record**
   - Mark implementation steps as `Completed`
   - Update `supersedes` with full file paths to archive locations
   - Update `artifacts_modified` with accurate file counts

### Phase 4: Version and Record

10. **Bump `framework/VERSION`**
    - Follow SemVer: major/minor/patch per classification
    - Update `LAYER_REGISTRY.yaml` `metadata.framework_version` to match

11. **Create or update `CHANGELOG.md`** (GATE-SPEC-E008)
    - Add entry with version number, date, and change summary
    - Follow existing format (Added/Changed/Fixed sections)

12. **Add GD entry to `DECISIONS.md`** (if significant decision)
    - Follow existing format (Status, Context, Decision, Consequences, Authority)
    - Place before existing entries (newest first)

13. **Security assessment** (GATE-SPEC-W003)
    - Review against SECURITY_REVIEW.md threats T1-T4
    - Record findings in CHG `security_assessment` section
    - For informational metadata changes: typically no blocking findings

### Phase 5: Verify

14. **Run verification checks**
    - All modified files have Document Control block
    - No duplicate Document Control sections
    - `framework_version` matches `VERSION` in all files
    - Archive contains all originals
    - YAML files parse without errors

15. **Update CHG status**
    - Set `change_control.status: Implemented`
    - Set `document_control.status: Completed`
    - Set all verification `result: Pass`

## GATE-SPEC Entry Criteria Checklist

```markdown
- [ ] Change edits framework/ (templates / governance / registry / VERSION)
- [ ] change_description.why and .trigger populated
- [ ] semver_impact set (major | minor | patch)
- [ ] change_level proposed (>= C2; major => C3)
- [ ] CHANGELOG.md entry drafted
- [ ] For C3: both platform owners notified
```

## GATE-SPEC Exit Criteria Checklist

```markdown
- [ ] GATE-SPEC-E001..E004 pass (record-level)
- [ ] GATE-SPEC-E005..E008 pass (VERSION bump, FSV match, suite green, CHANGELOG)
- [ ] GATE-SPEC-W001..W003 reviewed
- [ ] CHG document created (>= C2)
- [ ] Human approval obtained per matrix (branch protection)
- [ ] Both platforms re-declare FRAMEWORK_SPEC_VERSION; conformance green
- [ ] Ready to merge
```

## Common Pitfalls

1. **Forgetting subdirectories** — `governance/*.md` misses `governance/chg/README.md`
2. **Duplicate metadata keys** — Adding a new `metadata:` block when one already exists causes silent field loss
3. **Wrong framework_version** — Must match current VERSION, not the previous one
4. **Missing CHANGELOG** — GATE-SPEC-E008 requires it; create if absent
5. **Stale step statuses** — Implementation steps must be Updated to Completed

## Cross-references

- `layers/09_CHG/README.md` — CHG overlay documentation
- `layers/09_CHG/gates/GATE-SPEC_FRAMEWORK.md` — Full gate definition
- `governance/DOC_GOVERNANCE_CORE.md` — §Principle 10 (Document lifecycle tracking)
- `governance/SECURITY_REVIEW.md` — Security review checklist (W003)
- `governance/DECISIONS.md` — GD-24 (Document control convention)
