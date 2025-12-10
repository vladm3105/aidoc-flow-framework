# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of IPLAN-TEMPLATE.md
# - Authority: IPLAN-TEMPLATE.md is the single source of truth for IPLAN structure
# - Purpose: AI guidance for document creation (derived from template)
# - On conflict: Defer to IPLAN-TEMPLATE.md
# =============================================================================
---
title: "IPLAN Creation Rules"
tags:
  - creation-rules
  - layer-12-artifact
  - shared-architecture
custom_fields:
  document_type: creation-rules
  artifact_type: IPLAN
  layer: 12
  priority: shared
  development_status: active
---

> **📋 Document Role**: This is a **CREATION HELPER** for IPLAN-TEMPLATE.md.
> - **Authority**: `IPLAN-TEMPLATE.md` is the single source of truth for IPLAN structure
> - **Validation**: Use `IPLAN_VALIDATION_RULES.md` after IPLAN creation/changes

# IPLAN Creation Rules

Rules for creating Implementation Plans (IPLAN) documents in the SDD framework.

## Document Control

| Field | Value |
|-------|-------|
| **Version** | 1.1.0 |
| **Created** | 2025-11-27 |
| **Last Updated** | 2025-11-29 |
| **Status** | Active |

---

## Table of Contents

1. [When to Create an IPLAN Document](#1-when-to-create-an-iplan-document)
2. [File Naming Convention](#2-file-naming-convention)
3. [Required Sections](#3-required-sections)
4. [Objective Section Rules](#4-objective-section-rules)
5. [Context Section Rules](#5-context-section-rules)
6. [Task List Section Rules](#6-task-list-section-rules)
7. [Implementation Guide Section Rules](#7-implementation-guide-section-rules)
8. [Traceability Tags Section](#8-traceability-tags-section-mandatory)
9. [Quality Checklist](#9-quality-checklist)
10. [Session Context Rules](#10-session-context-rules)
11. [Token Efficiency Guidelines](#11-token-efficiency-guidelines)
12. [Common Anti-Patterns](#12-common-anti-patterns)
13. [Validation](#13-validation)
14. [Upstream Artifact Verification Process](#14-upstream-artifact-verification-process)
15. [Required Implementation Patterns](#15-required-implementation-patterns)
16. [Cross-Document Validation](#16-cross-document-validation-mandatory)

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
IPLAN-NNN_{descriptive_slug}.md
```

### Rules

1. **IPLAN-NNN**: Sequential numbering starting from 001
2. **descriptive_slug**: Lowercase with underscores
3. **Extension**: Always `.md`

### Examples

- `IPLAN-001_implement_gateway_connection.md`
- `IPLAN-002_add_retry_logic.md`
- `IPLAN-003_deploy_authentication_service.md`

### Naming Rules

1. Always use `IPLAN` (not `IPLAN_S`, `IMPLPLAN`, or `iplan`)
2. Sequence numbers must be zero-padded (001, not 1)
3. Descriptive slug uses underscores, not hyphens or camelCase
4. Do NOT include timestamps in filename (use Document Control for versioning)

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

### 3.1.1 Immediate Validation After Creation

**MANDATORY**: Run validation immediately after creating each IPLAN file.

```bash
# Validate immediately after creation
./ai_dev_flow/scripts/validate_iplan.sh docs/IPLAN/IPLAN-NNN_*.md

# Quick check for required tag
grep -q "layer-12-artifact" docs/IPLAN/IPLAN-NNN_*.md || echo "ERROR: Missing layer-12-artifact tag"

# Quick check for tags section
grep -q "^tags:" docs/IPLAN/IPLAN-NNN_*.md || echo "ERROR: Missing tags: section"
```

**CRITICAL**: Do NOT proceed to next IPLAN until validation passes. Files missing `layer-12-artifact` tag will fail validation.

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

Implement TASKS-001 Service Connector from scratch, creating async TCP
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
- SPEC-001: Service Connector specification
- REQ-001 through REQ-010: All requirements documented
- BDD-001: 18 scenarios defined

**Code Status**: ❌ 0% - Starting from Scratch
- No /src directory exists
- Test infrastructure not configured

### Key Technical Decisions

**Architecture** (from ADR-002):
- Async TCP with async_client library
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
  - Run `poetry add async_client pydantic`
  - Verify: `poetry show | grep async_client`
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
poetry add async_client>=1.0.0 pydantic>=2.0
```

Verification:
```bash
poetry show | grep -E "(async_client|pydantic)"
# Expected:
# async_client    1.0.0  ...
# pydantic        2.5.0  ...
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
| @ears | EARS.NNN.NNN | EARS Requirements (Layer 3) |
| @bdd | BDD-NNN:SCENARIO-NNN | BDD Scenarios (Layer 4) |
| @adr | ADR-NNN | Architecture Decisions (Layer 5) |
| @sys | SYS-NNN:REQ-NNN | System Requirements (Layer 6) |
| @req | REQ-NNN | Atomic Requirements (Layer 7) |
| @spec | SPEC-NNN | Technical Specifications (Layer 10) |
| @tasks | TASKS-NNN | Code Generation Plan (Layer 11) |

### Optional Tags (If present in project)

| Tag | Format | Description |
|-----|--------|-------------|
| @impl | IMPL-NNN | Implementation Plan (Layer 8) |
| @ctr | CTR-NNN | Interface Contracts (Layer 9) |

### Example

```markdown
## Traceability Tags

**Layer 12 Position**: IPLAN inherits tags from all upstream artifacts

### Required Tags (Mandatory)

- `@brd: BRD.001.042` - Business Requirements (Layer 1)
- `@prd: PRD.001.015` - Product Requirements (Layer 2)
- `@ears: EARS.001.003` - EARS Requirements (Layer 3)
- `@bdd: BDD.001.005` - BDD Scenarios (Layer 4)
- `@adr: ADR-002` - Architecture Decisions (Layer 5)
- `@sys: SYS.002.001` - System Requirements (Layer 6)
- `@req: REQ.001.001` - Atomic Requirements (Layer 7)
- `@spec: SPEC-001` - Technical Specifications (Layer 10)
- `@tasks: TASKS.001.001` - Code Generation Plan (Layer 11)

### Optional Tags

- `@impl: IMPL.001.001` - Implementation Plan (Layer 8)
- `@ctr: CTR-001` - Interface Contract (Layer 9)
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
- ✅ Exact commands: `poetry add async_client>=1.0.0`
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
IPLAN-001_feature_part1.md (Phase 0-2)
IPLAN-001_feature_part2.md (Phase 3-4)
```

### Efficiency Techniques

1. **Use tables** for repetitive data
2. **Reference** external docs instead of duplicating
3. **Summarize** long bash output
4. **Abbreviate** with codes (SVC_ERR_001)

---

## 12. Common Anti-Patterns

### Avoid

1. **No verification steps** - Every command needs verification
2. **Relative paths** - Use absolute paths always
3. **Vague commands** - Be specific with versions, flags
4. **Wrong filename format** - Use IPLAN-NNN_{slug}.md (no timestamps)
5. **Incomplete tags** - All 9 required tags mandatory
6. **Technical design** - HOW belongs in SPEC, not IPLAN
7. **No resume markers** - Mark where to continue

---

## 13. Validation

### Automated Validation

```bash
./scripts/validate_iplan.sh /path/to/IPLAN-NNN_{slug}.md
```

### Manual Checklist

- [ ] Filename follows convention (IPLAN-NNN_{slug}.md)
- [ ] All required sections present
- [ ] Bash commands are executable
- [ ] Verification after each step
- [ ] All 9+ traceability tags complete
- [ ] Registered in IPLAN-000_index.md
- [ ] Token count < 100KB

---

## 14. Upstream Artifact Verification Process

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

| Tag | Required for This Layer | Existing Document | Action |
|-----|------------------------|-------------------|--------|
| @brd | Yes/No | BRD-001 or null | Reference/Create/Skip |
| @prd | Yes/No | PRD-001 or null | Reference/Create/Skip |
| ... | ... | ... | ... |

**Step 3: Decision Rules**

| Situation | Action |
|-----------|--------|
| Upstream exists | Reference with exact document ID |
| Upstream required but missing | Skip that functionality - do NOT implement |
| Upstream optional and missing | Use `null` in traceability tag |
| Upstream not applicable | Omit tag entirely |

### Traceability Tag Rules

- **NEVER** use placeholder IDs like `BRD-XXX` or `TBD`
- **NEVER** reference documents that don't exist
- **ALWAYS** verify document exists before adding reference
- **USE** `null` only when artifact type is genuinely not applicable

### Same-Type References (Conditional)

Include ONLY if relationships exist between IPLAN documents sharing session context or execution dependencies.

| Relationship | Document ID | Document Title | Purpose |
|--------------|-------------|----------------|---------|
| Related | IPLAN-NNN | [Related IPLAN title] | Shared session context |
| Depends | IPLAN-NNN | [Prerequisite IPLAN title] | Must complete before this |

**Tags**:
```markdown
@related-iplan: IPLAN-NNN
@depends-iplan: IPLAN-NNN
```


## 15. Required Implementation Patterns

### Error Handling Pattern

All error handling must follow this pattern:

```python
try:
    result = await operation()
except SpecificError as e:
    logger.error("Context: %s", e, exc_info=True)
    raise DomainError("User-friendly message") from e
except Exception as e:
    logger.exception("Unexpected error in operation")
    raise
```

**Rules**:
- NEVER use bare `except:` or `except Exception:` without re-raise
- Always use exception chaining: `raise NewError() from original`
- Log before handling: `logger.error("msg", exc_info=True)`

### Resource Management Pattern

Classes managing external resources must implement:

```python
class Service:
    async def __aenter__(self) -> "Service":
        return self

    async def __aexit__(self, *args) -> None:
        await self.cleanup()

    async def cleanup(self) -> None:
        """Release resources. Safe to call multiple times."""
        if self._cache:
            self._cache.clear()
        if self._tasks:
            for task in self._tasks:
                task.cancel()
```

**Rules**:
- Implement `__aenter__` and `__aexit__` for async resources
- Add explicit `cleanup()` method callable outside context manager
- Make cleanup idempotent (safe to call multiple times)

### Validation Pattern

Input validation must use Pydantic or explicit checks:

```python
# Pydantic approach (preferred)
class Config(BaseModel):
    timeout: float = Field(ge=1.0, le=300.0)
    name: str = Field(min_length=1, max_length=100)

# Manual approach (when Pydantic not suitable)
def validate_input(value: str) -> str:
    if not value or not value.strip():
        raise ValueError("Value cannot be empty")
    if len(value) > MAX_LENGTH:
        raise ValueError(f"Value exceeds {MAX_LENGTH} characters")
    return value.strip()
```

**Rules**:
- Validate at system boundaries (user input, external APIs)
- Use Pydantic `Field()` constraints for model validation
- Return cleaned/normalized values from validation functions

### Async Cache Pattern

Caches in async code must use async locks:

```python
class CachedService:
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._lock = asyncio.Lock()  # NOT threading.Lock

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            return self._cache.get(key)

    async def set(self, key: str, value: Any) -> None:
        async with self._lock:
            self._cache[key] = value

    def clear(self) -> int:
        """Clear cache. Returns count of items cleared."""
        count = len(self._cache)
        self._cache.clear()
        return count
```

**Rules**:
- Use `asyncio.Lock()` for async code, NOT `threading.Lock`
- Always provide cache clearing method
- Document TTL and eviction strategy if applicable

### Type Hint Quality Pattern

Minimize `Any` type usage:

```python
# AVOID: Overly permissive
def process(data: Optional[Any]) -> Any:
    pass

# PREFERRED: Specific types
def process(data: Optional[ContractData]) -> ProcessedResult:
    pass

# If Any required, document why
def handle_external(data: Any) -> None:  # Any: third-party API response
    pass
```

**Rules**:
- Use specific types: `Optional[SpecificType]` not `Optional[Any]`
- Use `Protocol` for duck typing instead of `Any`
- Document justification when `Any` is unavoidable

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

**Document Version**: 1.1.0
**Last Updated**: 2025-11-29

---

## 16. Cross-Document Validation (MANDATORY)

**CRITICAL**: Execute cross-document validation IMMEDIATELY after creating any IPLAN document. Do NOT proceed to implementation until validation passes.

### Automatic Validation Loop

```
LOOP:
  1. Run: python scripts/validate_cross_document.py --document {doc_path} --auto-fix
  2. IF errors fixed: GOTO LOOP (re-validate)
  3. IF warnings fixed: GOTO LOOP (re-validate)
  4. IF unfixable issues: Log for manual review, continue
  5. IF clean: Mark VALIDATED, proceed to implementation
```

### Validation Command

```bash
# Per-document validation (Phase 1)
python scripts/validate_cross_document.py --document docs/IPLAN/IPLAN-NNN_slug.md --auto-fix

# Layer validation (Phase 2) - run when all IPLAN documents complete
python scripts/validate_cross_document.py --layer IPLAN --auto-fix
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Tag Count |
|------------|------------------------|-----------|
| IPLAN (Layer 12) | @brd through @tasks (+ optional @impl, @ctr) | 9-11 |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing @brd through @tasks tag | Add with upstream document reference |
| Invalid tag format | Correct to TYPE.NNN.NNN or TYPE-NNN format |
| Broken link | Recalculate path from current location |
| Missing traceability section | Insert from template |

### Validation Codes Reference

| Code | Description | Severity |
|------|-------------|----------|
| XDOC-001 | Referenced requirement ID not found | ERROR |
| XDOC-002 | Missing cumulative tag | ERROR |
| XDOC-003 | Upstream document not found | ERROR |
| XDOC-006 | Tag format invalid | ERROR |
| XDOC-007 | Gap in cumulative tag chain | ERROR |
| XDOC-009 | Missing traceability section | ERROR |

### Quality Gate

**Blocking**: YES - Cannot proceed to implementation until Phase 1 validation passes with 0 errors.
