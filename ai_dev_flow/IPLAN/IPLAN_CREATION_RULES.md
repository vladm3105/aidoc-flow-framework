---
title: "IPLAN Creation Rules"
tags:
  - creation-rules
  - layer-12-artifact
  - shared-architecture
custom_fields:
  document_type: creation_rules
  artifact_type: IPLAN
  layer: 12
  priority: shared
  development_status: active
---

# IPLAN Creation Rules

Rules for creating Implementation Plans (IPLAN) documents in the SDD framework.

## Document Control

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Created** | 2025-11-27 |
| **Last Updated** | 2025-11-27 |
| **Status** | Active |

---

## 1. When to Create an IPLAN Document

### Create IPLAN When

- [ ] Starting implementation of a TASKS document in a new session
- [ ] Complex setup requiring specific environment configuration
- [ ] Multi-phase work spanning multiple sessions
- [ ] Team handoff requiring context documentation
- [ ] Session-specific decisions need preservation
- [ ] Step-by-step verification checkpoints required

### Do NOT Create IPLAN When

- [ ] Simple, one-file implementation (<100 lines)
- [ ] No environment setup needed
- [ ] Work completed in single session without interruption
- [ ] TASKS document already provides sufficient execution detail

---

## 2. File Naming Convention

### Format

```
IPLAN-NNN_{descriptive_slug}_YYYYMMDD_HHMMSS.md
```

### Rules

1. **IPLAN-NNN**: Sequential numbering starting from 001
2. **descriptive_slug**: Lowercase with underscores
3. **Timestamp**: YYYYMMDD_HHMMSS format (EST/EDT timezone)
4. **Extension**: Always `.md`

### Examples

- `IPLAN-001_implement_gateway_connection_20251127_092843.md`
- `IPLAN-002_add_retry_logic_20251127_143022.md`
- `IPLAN-003_deploy_authentication_service_20251128_095500.md`

### Naming Rules

1. Always use `IPLAN` (not `IPLAN_S`, `IMPLPLAN`, or `iplan`)
2. Sequence numbers must be zero-padded (001, not 1)
3. Descriptive slug uses underscores, not hyphens or camelCase
4. Timestamp required for session tracking
5. Always use EST/EDT timezone for consistency

---

## 3. Required Sections

### 3.1 Frontmatter

```yaml
---
title: "IPLAN-NNN: [Descriptive Task/Feature Name]"
tags:
  - iplan-document
  - layer-12-artifact
  - session-execution
custom_fields:
  document_type: iplan
  artifact_type: IPLAN
  layer: 12
  parent_tasks: TASKS-NNN
  complexity: [1-5]
---
```

### 3.2 Document Control Table

| Field | Required | Description |
|-------|----------|-------------|
| ID | Yes | IPLAN-NNN format |
| Status | Yes | Draft/Ready/In Progress/Completed/Blocked |
| Version | Yes | Semantic version (X.Y.Z) |
| Created | Yes | YYYY-MM-DD HH:MM:SS TZ |
| Last Updated | Yes | YYYY-MM-DD HH:MM:SS TZ |
| Author | Yes | AI Assistant/Developer Name |
| Estimated Effort | Yes | Hours or hour range |
| Complexity | Yes | 1-5 scale |
| Parent TASKS | Yes | TASKS-NNN reference |
| IPLAN-Ready Score | Recommended | Percentage (target: ≥90%) |

### 3.3 Mandatory Sections

| Section | Purpose |
|---------|---------|
| Position in Workflow | Layer 12 context |
| Objective | Goal and deliverables |
| Context | Current state and technical decisions |
| Task List | Phase-based checklist |
| Implementation Guide | Bash commands and verification |
| Technical Details | Module specifications |
| Traceability Tags | Complete tag chain (9-11 tags) |
| Traceability | Upstream/downstream references |
| Risk Mitigation | Implementation risks |
| Success Criteria | Measurable completion metrics |
| References | Framework and artifact links |

---

## 4. Objective Section Rules

### Requirements

- 1-2 sentence goal statement
- Specific deliverables list
- Measurable outcomes

### Good Example

```markdown
## Objective

Implement TASKS-001 Gateway Connection Service from scratch, creating async TCP
connection management with retry logic, circuit breaker, and 100% BDD coverage.

**Deliverables**:
- 6 Python modules (connector, service, models, errors, retry, circuit breaker)
- Complete test suite (unit 85%, integration 75%, BDD 100%)
- Project structure, dependencies, configuration
- All BDD scenarios validated
```

### Bad Example

```markdown
## Objective

Build the gateway connection stuff.
```

---

## 5. Context Section Rules

### Required Subsections

1. **Current State Analysis**
   - Documentation status with percentage
   - Code status with percentage
   - Previous work completed

2. **Key Technical Decisions**
   - Architecture (from ADR)
   - Error handling (from SPEC)
   - Resilience patterns (from SPEC)
   - Performance targets (from SPEC)

### Good Example

```markdown
## Context

### Current State Analysis

**Documentation Status**: ✅ 100% Complete
- SPEC-001: Gateway Connection Service specification
- REQ-001 through REQ-010: All requirements documented
- BDD-001: 18 scenarios defined

**Code Status**: ❌ 0% - Starting from Scratch
- No /src directory exists
- Test infrastructure not configured

### Key Technical Decisions

**Architecture** (from ADR-002):
- Async TCP with ib_async library
- Protocol-based interfaces for testability

**Error Handling** (from SPEC-001):
- 6 typed exceptions with error codes
- Exponential backoff retry strategy
```

---

## 6. Task List Section Rules

### Requirements

- Organize tasks into numbered phases
- Use checkboxes for trackable progress
- Include time estimates per phase
- Mark phase status (COMPLETED/PENDING/IN PROGRESS)
- Include verification for each task

### Phase Structure

```markdown
### Phase 0: Documentation Review (COMPLETED ✅)
- [x] Read templates and standards
- [x] Analyze SPEC and upstream artifacts
- [x] Review TASKS document

### Phase 1: Project Foundation (8 hours) - PENDING
- [ ] **TASK-1.1**: Create directory structure
  - Create src/module/ directory
  - Verify: `ls -R src/`

- [ ] **TASK-1.2**: Install dependencies
  - Run `poetry add ib_async pydantic`
  - Verify: `poetry show | grep ib_async`
```

### Phase Guidelines

- **Phase 0**: Documentation review (prerequisite)
- **Phase 1**: Setup and foundation (4-8 hours)
- **Phase 2**: Core implementation (split into 2.1, 2.2, etc.)
- **Phase 3**: Testing (split by test type)
- **Phase 4**: Quality assurance and deployment

---

## 7. Implementation Guide Section Rules

### Required Subsections

1. **Prerequisites**
   - Required tools
   - Required file access
   - Knowledge requirements
   - Environment setup

2. **Execution Steps**
   - Numbered steps
   - Bash code blocks
   - Verification commands
   - Expected outcomes

3. **Verification Checklist**
   - After each phase validation

### Bash Command Rules

**CRITICAL**: All bash commands must be:
- **Executable**: Copy-paste ready
- **Absolute paths**: No relative paths (ambiguous in new session)
- **Verified**: Include verification command after each step
- **Documented**: Include expected output

### Good Example

```markdown
### Execution Steps

**Step 1: Create Project Structure**

```bash
# Create directory structure
cd /opt/data/project
mkdir -p src/module/{models,errors,service}
touch src/module/__init__.py
```

Verification:
```bash
ls -R src/module/
# Expected: __init__.py, models/, errors/, service/
```

**Step 2: Install Dependencies**

```bash
poetry add ib_async>=0.9.86 pydantic>=2.0
```

Verification:
```bash
poetry show | grep -E "(ib_async|pydantic)"
# Expected:
# ib_async    0.9.86  ...
# pydantic    2.5.0   ...
```
```

### Bad Example

```markdown
### Steps

1. Create directories
2. Install stuff
3. Write code
```

---

## 8. Traceability Tags Section (MANDATORY)

### Required Tags (Layer 12 - All 9 mandatory)

| Tag | Format | Description |
|-----|--------|-------------|
| @brd | BRD-NNN:REQ-NNN | Business Requirements (Layer 1) |
| @prd | PRD-NNN:REQ-NNN | Product Requirements (Layer 2) |
| @ears | EARS-NNN:REQ-NNN | EARS Requirements (Layer 3) |
| @bdd | BDD-NNN:SCENARIO-NNN | BDD Scenarios (Layer 4) |
| @adr | ADR-NNN | Architecture Decisions (Layer 5) |
| @sys | SYS-NNN:REQ-NNN | System Requirements (Layer 6) |
| @req | REQ-NNN | Atomic Requirements (Layer 7) |
| @spec | SPEC-NNN:section | Technical Specifications (Layer 10) |
| @tasks | TASKS-NNN:PHASE-X.Y | Code Generation Plan (Layer 11) |

### Optional Tags (If present in project)

| Tag | Format | Description |
|-----|--------|-------------|
| @impl | IMPL-NNN | Implementation Plan (Layer 8) |
| @ctr | CTR-NNN:section | Interface Contracts (Layer 9) |

### Example

```markdown
## Traceability Tags

**Layer 12 Position**: IPLAN inherits tags from all upstream artifacts

### Required Tags (Mandatory)

- `@brd: BRD-001:REQ-042` - Business Requirements (Layer 1)
- `@prd: PRD-001:REQ-015` - Product Requirements (Layer 2)
- `@ears: EARS-001:REQ-003` - EARS Requirements (Layer 3)
- `@bdd: BDD-001:SCENARIO-005` - BDD Scenarios (Layer 4)
- `@adr: ADR-002` - Architecture Decisions (Layer 5)
- `@sys: SYS-002:REQ-001` - System Requirements (Layer 6)
- `@req: REQ-001` - Atomic Requirements (Layer 7)
- `@spec: SPEC-001:connection_service` - Technical Specifications (Layer 10)
- `@tasks: TASKS-001:PHASE-2.1` - Code Generation Plan (Layer 11)

### Optional Tags

- `@impl: IMPL-001` - Implementation Plan (Layer 8)
- `@ctr: CTR-001:IBGatewayConnector` - Interface Contract (Layer 9)
```

---

## 9. Quality Checklist

### Before Creating

- [ ] TASKS document exists and is complete
- [ ] Implementation requires session context documentation
- [ ] Environment setup is non-trivial
- [ ] Work spans multiple sessions or phases

### During Creation

- [ ] Use IPLAN-TEMPLATE.md as starting point
- [ ] Complete all required sections
- [ ] Write executable bash commands with absolute paths
- [ ] Include verification after each step
- [ ] Add all 9 required traceability tags
- [ ] Document current state and decisions

### After Creation

- [ ] All bash commands tested/valid
- [ ] All traceability tags reference existing documents
- [ ] Update IPLAN-000_index.md
- [ ] Validate with validation script
- [ ] Token count within limits (25-40KB optimal)

---

## 10. Session Context Rules

### DO Include

- ✅ Absolute file paths: `/opt/data/project/src/module.py`
- ✅ Exact commands: `poetry add ib_async>=0.9.86`
- ✅ Environment details: Python 3.11+, PostgreSQL 14
- ✅ Verification steps after each command
- ✅ Current state: "Code Status: 35% complete"
- ✅ Resume markers: "RESUME HERE 👈"

### DO NOT Include

- ❌ Relative paths: `../src/module.py` (ambiguous)
- ❌ Vague instructions: "Install dependencies"
- ❌ Assumed environment: "Run the tests"
- ❌ Skipped verification
- ❌ Missing state information

---

## 11. Token Efficiency Guidelines

### Target Sizes

| Tool | Optimal | Maximum |
|------|---------|---------|
| Claude Code | 25-40KB | 100KB |
| Gemini CLI | 10KB inline | Use file read tool |

### When to Split

- IPLAN exceeds 100,000 tokens
- Logical phase boundaries exist
- Multiple independent workstreams

### Splitting Pattern

```
IPLAN-001_feature_part1_20251127_092843.md (Phase 0-2)
IPLAN-001_feature_part2_20251127_092843.md (Phase 3-4)
```

### Efficiency Techniques

1. **Use tables** for repetitive data
2. **Reference** external docs instead of duplicating
3. **Summarize** long bash output
4. **Abbreviate** with codes (IB_CONN_001)

---

## 12. Common Anti-Patterns

### Avoid

1. **No verification steps** - Every command needs verification
2. **Relative paths** - Use absolute paths always
3. **Vague commands** - Be specific with versions, flags
4. **Missing timestamps** - Include in filename
5. **Incomplete tags** - All 9 required tags mandatory
6. **Technical design** - HOW belongs in SPEC, not IPLAN
7. **No resume markers** - Mark where to continue

---

## 13. Validation

### Automated Validation

```bash
./scripts/validate_iplan.sh /path/to/IPLAN-NNN_name_timestamp.md
```

### Manual Checklist

- [ ] Filename follows convention with timestamp
- [ ] All required sections present
- [ ] Bash commands are executable
- [ ] Verification after each step
- [ ] All 9+ traceability tags complete
- [ ] Registered in IPLAN-000_index.md
- [ ] Token count < 100KB

---

## References

- [IPLAN-TEMPLATE.md](./IPLAN-TEMPLATE.md) - Implementation plan template
- [IPLAN-000_index.md](./IPLAN-000_index.md) - Plan registry
- [README.md](./README.md) - Directory overview
- [BDD_SCENARIO_MAPPING.md](./BDD_SCENARIO_MAPPING.md) - Scenario mapping guide
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Workflow guide
- [TRACEABILITY.md](../TRACEABILITY.md) - Cumulative tagging hierarchy
- [TASKS/README.md](../TASKS/README.md) - Parent artifact guidance

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-27
