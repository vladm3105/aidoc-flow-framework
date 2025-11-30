# Implementation Plan - Framework Fixes for New Project Setup

**Created**: 2025-11-30 15:34:20 EST
**Status**: Ready for Implementation

## Objective

Prepare the docs_flow_framework for setting up a new project (`/opt/data/gcp_nlp_analysis`) by fixing critical issues, creating missing schema files, properly documenting ICON in the framework, and adding ICON to traceability documents.

## Context

Framework review identified several issues that should be fixed before creating new projects:
- Missing gitignore entry for custom_agents in setup script
- Hardcoded paths in skills that break portability
- Missing ICON_SCHEMA.yaml
- BRD schema exception needs documentation (by design - no schema)
- ICON not documented in main README.md
- ICON missing from traceability documents
- Broken IMPL example link

## Task List

### Pending
- [ ] Task 1: Document BRD schema exception (no BRD_SCHEMA.yaml by design)
- [ ] Task 2: Create ICON_SCHEMA.yaml
- [ ] Task 3: Implement ICON into framework documentation (4 README.md sections)
- [ ] Task 4: Fix broken IMPL example link in README.md
- [ ] Task 5: Fix Critical Issues (setup script + 3 skill files)
- [ ] Task 6: Add ICON to traceability documents (2 files, 3 locations)

### Notes
- ICON is Layer 11 artifact (shares with TASKS), optional - use only when criteria met
- BRD has no schema by design - business requirements are flexible and domain-specific
- After fixes, proceed with `/opt/data/gcp_nlp_analysis` project setup

## Implementation Guide

### Prerequisites
- Access to `/opt/data/docs_flow_framework/`
- Understanding of ICON purpose: type-safe interfaces for parallel development

### Task 1: Document BRD Schema Exception

**File**: `/opt/data/docs_flow_framework/ai_dev_flow/BRD/README.md`
Add after file listing:
```markdown
> **Note**: BRD does not have a schema file (`BRD_SCHEMA.yaml`) by design. Business requirements
> are inherently flexible and domain-specific; rigid schema validation would be counterproductive
> for capturing diverse business needs across different project types.
```

### Task 2: Create ICON_SCHEMA.yaml

**File**: `/opt/data/docs_flow_framework/ai_dev_flow/ICON/ICON_SCHEMA.yaml`

Create with structure based on TASKS_SCHEMA.yaml pattern:
- schema_version: "1.0"
- artifact_type: ICON
- layer: 11
- Required metadata fields: document_type, artifact_type, layer, contract_type, provider_tasks, consumer_count
- Contract types: protocol, exception, state-machine, data-model, di-interface
- Creation criteria: 5+ consumers, >500 lines, platform-level, cross-project
- Traceability: cumulative tags through Layer 11

### Task 3: Implement ICON into README.md

**File**: `/opt/data/docs_flow_framework/ai_dev_flow/README.md`

**3.1** Add after "8. Code Generation Layer" (TASKS), before "9. Session Planning Layer":
```markdown
### 8b. Implementation Contracts Layer (Optional)

**ICON/** - Implementation Contracts (Layer 11)
- Type-safe interface definitions for parallel development coordination
- Protocol interfaces, exception hierarchies, state machines, data models
- **When to use**: 5+ consumer TASKS, >500 lines, platform-level, cross-project
- **Default**: Embed contracts in TASKS section 8 unless criteria met
- **Files**: [ICON-000_index.md](./ICON/ICON-000_index.md) | [Template](./ICON/ICON-TEMPLATE.md)
- **Guide**: [IMPLEMENTATION_CONTRACTS_GUIDE.md](./TASKS/IMPLEMENTATION_CONTRACTS_GUIDE.md)
```

**3.2** Update 16-Layer Architecture Table - add ICON row after TASKS:
```markdown
| **11** | ICON | Implementation contracts (optional) | @brd→@spec (8-10) | Interface definitions |
```

**3.3** Update Document ID Standards - add ICON to list:
```markdown
- Documents in `docs/` directories: BRD, PRD, EARS, BDD, ADR, SYS, REQ, IMPL, CTR, SPEC, TASKS, ICON
```

**3.4** Add Schema File Reference Table (after Document ID Standards):
```markdown
## Schema File Reference

| Artifact | Schema File | Layer | Notes |
|----------|-------------|-------|-------|
| BRD | N/A¹ | 1 | No schema by design |
| PRD | PRD_SCHEMA.yaml | 2 | |
| EARS | EARS_SCHEMA.yaml | 3 | |
| BDD | BDD_SCHEMA.yaml | 4 | |
| ADR | ADR_SCHEMA.yaml | 5 | |
| SYS | SYS_SCHEMA.yaml | 6 | |
| REQ | REQ_SCHEMA.yaml | 7 | |
| IMPL | IMPL_SCHEMA.yaml | 8 | |
| CTR | CTR_SCHEMA.yaml | 9 | |
| SPEC | SPEC_SCHEMA.yaml | 10 | |
| TASKS | TASKS_SCHEMA.yaml | 11 | |
| ICON | ICON_SCHEMA.yaml | 11 | Optional artifact |
| IPLAN | IPLAN_SCHEMA.yaml | 12 | |

¹ BRD has no schema by design - business requirements are inherently flexible and domain-specific.
```

### Task 4: Fix IMPL Example Link

**File**: `/opt/data/docs_flow_framework/ai_dev_flow/README.md`
**Line**: ~293

Change:
```markdown
[IMPL-001_feature_implementation_example.md](./IMPL/IMPL-001_feature_implementation_example.md)
```
To:
```markdown
[IMPL-001_feature_implementation_example.md](./IMPL/examples/IMPL-001_feature_implementation_example.md)
```

### Task 5: Fix Critical Issues

**5.1** `/opt/data/docs_flow_framework/scripts/setup_project_hybrid.sh`
Add after existing gitignore entries (~line 127):
```bash
add_gitignore_entry "!.claude/custom_agents/"
```

**5.2** `/opt/data/docs_flow_framework/.claude/skills/project-init/SKILL.md`
Lines 145-146 - Replace:
```bash
mkdir -p /opt/data/project_name
cd /opt/data/project_name
```
With:
```bash
mkdir -p {project_root}
cd {project_root}
```
Add note: "Replace `{project_root}` with your actual project path"

**5.3** `/opt/data/docs_flow_framework/.claude/skills/adr-roadmap/SKILL.md`
Line 63 - Replace `/opt/data/project/docs/ADR/` with `{project_root}/docs/ADR/`

**5.4** `/opt/data/docs_flow_framework/.claude/skills/adr-roadmap_quickref.md`
Replace all 3 instances of `/opt/data/project/docs/ADR/` with `{project_root}/docs/ADR/`

### Task 6: Add ICON to Traceability Documents

**6.1** `/opt/data/docs_flow_framework/ai_dev_flow/TRACEABILITY.md`
**Location**: Lines 35-47 (Schema Authority Principle table)
**Add after TASKS row**:
```markdown
| ICON | `ai_dev_flow/ICON/ICON_SCHEMA.yaml` | 11 |
```

**6.2** `/opt/data/docs_flow_framework/ai_dev_flow/TRACEABILITY_MATRIX_COMPLETE-TEMPLATE.md`
**Location**: Lines 73-98 (Coverage Summary table)
**Add after TASKS row**:
```markdown
| ICON | [X]/[Y] | XX% | [Status] |
```

**6.3** `/opt/data/docs_flow_framework/ai_dev_flow/TRACEABILITY_MATRIX_COMPLETE-TEMPLATE.md`
**Location**: Lines 139-156 (Cumulative Tagging Table)
**Add after TASKS row**:
```markdown
| 11 | **ICON** | All upstream through `@spec` + `@tasks` | 9-11 | Formal Template (Markdown) | Optional - standalone when 5+ consumers |
```

### Verification

```bash
# Verify ICON_SCHEMA.yaml created
ls -la ai_dev_flow/ICON/ICON_SCHEMA.yaml

# Verify no hardcoded /opt/data/project paths in skills
grep -r "/opt/data/project" .claude/skills/

# Verify gitignore entry added
grep "custom_agents" scripts/setup_project_hybrid.sh

# Verify IMPL link fixed
grep "IMPL-001_feature_implementation_example" ai_dev_flow/README.md

# Verify ICON in traceability Schema Authority table
grep "ICON.*ICON_SCHEMA.yaml" ai_dev_flow/TRACEABILITY.md

# Verify ICON in TRACEABILITY_MATRIX_COMPLETE-TEMPLATE.md
grep -c "ICON" ai_dev_flow/TRACEABILITY_MATRIX_COMPLETE-TEMPLATE.md
```

## Files to Modify Summary

| File | Task | Action |
|------|------|--------|
| `ai_dev_flow/BRD/README.md` | 1 | Add schema exception note |
| `ai_dev_flow/ICON/ICON_SCHEMA.yaml` | 2 | Create new file |
| `ai_dev_flow/README.md` | 3,4 | Add ICON docs (4 sections), fix IMPL link |
| `ai_dev_flow/TRACEABILITY.md` | 6.1 | Add ICON to Schema Authority table |
| `ai_dev_flow/TRACEABILITY_MATRIX_COMPLETE-TEMPLATE.md` | 6.2,6.3 | Add ICON to Coverage Summary + Cumulative Tagging tables |
| `scripts/setup_project_hybrid.sh` | 5.1 | Add gitignore entry |
| `.claude/skills/project-init/SKILL.md` | 5.2 | Fix hardcoded path |
| `.claude/skills/adr-roadmap/SKILL.md` | 5.3 | Fix hardcoded path |
| `.claude/skills/adr-roadmap_quickref.md` | 5.4 | Fix 3 hardcoded paths |

## Post-Implementation: New Project Setup

After completing all fixes, create the new project:

```bash
# Create project directory
mkdir -p /opt/data/gcp_nlp_analysis

# Run hybrid setup script
/opt/data/docs_flow_framework/scripts/setup_project_hybrid.sh /opt/data/gcp_nlp_analysis

# Create documentation structure
mkdir -p /opt/data/gcp_nlp_analysis/docs/{BRD,PRD,EARS,BDD,ADR,SYS,REQ,IMPL,CTR,SPEC,TASKS,IPLAN,generated/matrices}
mkdir -p /opt/data/gcp_nlp_analysis/{work_plans,src,tests,tmp,scripts}

# Initialize git
cd /opt/data/gcp_nlp_analysis && git init

# Update global CLAUDE.md with new project work_plans path
```

## References

- Related files:
  - `/opt/data/docs_flow_framework/ai_dev_flow/ICON/ICON-TEMPLATE.md`
  - `/opt/data/docs_flow_framework/ai_dev_flow/ICON/ICON_CREATION_RULES.md`
  - `/opt/data/docs_flow_framework/ai_dev_flow/ICON/ICON_VALIDATION_RULES.md`
  - `/opt/data/docs_flow_framework/ai_dev_flow/TASKS/TASKS_SCHEMA.yaml` (pattern reference)
  - `/opt/data/docs_flow_framework/ai_dev_flow/TASKS/IMPLEMENTATION_CONTRACTS_GUIDE.md`
- Documentation:
  - `/opt/data/docs_flow_framework/MULTI_PROJECT_SETUP_GUIDE.md`
  - `/opt/data/docs_flow_framework/MULTI_PROJECT_QUICK_REFERENCE.md`
