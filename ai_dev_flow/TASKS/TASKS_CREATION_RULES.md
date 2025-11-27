---
title: "TASKS Creation Rules"
tags:
  - creation-rules
  - layer-11-artifact
  - shared-architecture
custom_fields:
  document_type: creation_rules
  artifact_type: TASKS
  layer: 11
  priority: shared
  development_status: active
---

# TASKS Creation Rules

Rules for creating AI Tasks (TASKS) documents in the SDD framework.

## Document Control

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Created** | 2025-11-27 |
| **Last Updated** | 2025-11-27 |
| **Status** | Active |

---

## 1. When to Create a TASKS Document

### Create TASKS When

- [ ] SPEC (YAML specification) is complete and approved
- [ ] Code generation plan needed for a single SPEC
- [ ] AI code generator requires structured implementation instructions
- [ ] Clear acceptance criteria needed before implementation
- [ ] Traceability from SPEC to code is required

### Do NOT Create TASKS When

- [ ] No SPEC exists yet (create SPEC first)
- [ ] Need project management plan (use IMPL instead)
- [ ] Simple configuration changes only
- [ ] Documentation-only updates

---

## 2. File Naming Convention

### Format

```
TASKS-NNN_{descriptive_component}_tasks.md
```

### Rules

1. **TASKS-NNN**: Sequential numbering starting from 001
2. **descriptive_component**: Lowercase with underscores
3. **_tasks**: Required suffix
4. **Extension**: Always `.md`

### Examples

- `TASKS-001_gateway_connection_service_tasks.md`
- `TASKS-002_market_data_integration_tasks.md`
- `TASKS-003_order_execution_service_tasks.md`

---

## 3. Required Sections

### 3.1 Frontmatter

```yaml
---
title: "TASKS-NNN: [Component Name] Implementation Tasks"
tags:
  - tasks-document
  - layer-11-artifact
  - code-generation
custom_fields:
  document_type: tasks
  artifact_type: TASKS
  layer: 11
  parent_spec: SPEC-NNN
---
```

### 3.2 Document Control Table

| Field | Required | Description |
|-------|----------|-------------|
| TASKS ID | Yes | TASKS-NNN format |
| Title | Yes | Descriptive task name |
| Status | Yes | Draft/Ready/In Progress/Completed |
| Version | Yes | Semantic version (X.Y.Z) |
| Created | Yes | YYYY-MM-DD |
| Author | Yes | Creator name |
| Parent SPEC | Yes | SPEC-NNN reference |
| Complexity | Yes | 1-5 scale |

### 3.3 Mandatory Sections

| Section | Purpose |
|---------|---------|
| 1. Scope | Define implementation boundaries |
| 2. Plan | Numbered implementation steps |
| 3. Constraints | Technical and development limitations |
| 4. Acceptance | Verification requirements |
| 5. Dependencies | Upstream/downstream artifacts |
| 6. Traceability Tags | Links to all upstream artifacts |
| 7. File Structure | Output file organization |
| 8. Implementation Contracts | ICON integration (mandatory) |

---

## 4. Scope Section Rules

### Requirements

- Clear statement of what component/functionality will be implemented
- Explicit boundaries (what IS included)
- Explicit exclusions (what is NOT included)
- Single SPEC focus (one TASKS per SPEC)

### Good Example

```markdown
## 1. Scope

Implement a minimal `gateway_connection_service` that:
- Establishes async TCP connections to IB Gateway
- Manages connection state with 5-state machine
- Provides retry logic with exponential backoff
- Includes circuit breaker pattern

**Exclusions**:
- Market data subscription (TASKS-002)
- Order execution (TASKS-003)
```

### Bad Example

```markdown
## 1. Scope

Build the whole gateway system.
```

---

## 5. Plan Section Rules

### Requirements

- Numbered sequential steps (1, 2, 3...)
- Each step is a specific coding task
- Steps reference SPEC line numbers where applicable
- Time estimates optional but recommended
- Verification step for each major component

### Good Example

```markdown
## 2. Plan

1. **Create module structure** (2 hours)
   - Create `src/gateway/__init__.py`
   - Create `src/gateway/models.py` (SPEC-001:15-45)
   - Create `src/gateway/errors.py` (SPEC-001:47-82)

2. **Implement connection protocol** (4 hours)
   - Create `src/gateway/connector.py`
   - Implement `GatewayConnector` protocol (SPEC-001:84-120)
   - Add type hints per SPEC-001:122-135

3. **Add retry handler** (3 hours)
   - Create `src/gateway/retry.py`
   - Implement exponential backoff (SPEC-001:137-165)
   - Verify: Unit tests pass with 85% coverage
```

### Bad Example

```markdown
## 2. Plan

1. Write the code.
2. Test it.
3. Deploy it.
```

---

## 6. Constraints Section Rules

### Required Constraint Categories

| Category | Description |
|----------|-------------|
| Technical | Language, framework, platform requirements |
| Coding Standards | Style guides, naming conventions |
| Interface | API compatibility, contract compliance |
| Performance | Latency, throughput targets |
| Quality | Test coverage, documentation requirements |

### Example

```markdown
## 3. Constraints

- **Technical**: Python 3.11+, asyncio, ib_async library
- **Coding Standards**: PEP 8, snake_case naming
- **Interface**: Match SPEC-001 exactly, no additions
- **Performance**: p95 latency < 50ms for validations
- **Quality**: 85% unit test coverage minimum
- **Dependencies**: No new runtime dependencies without approval
```

---

## 7. Acceptance Section Rules

### Requirements

- Measurable, verifiable criteria
- Link to BDD scenarios
- Specific test requirements
- Performance validation
- Documentation requirements

### Example

```markdown
## 4. Acceptance

- [ ] All BDD scenarios in BDD-001 pass
- [ ] Unit test coverage ≥85%
- [ ] Integration test coverage ≥75%
- [ ] mypy type checking passes (--strict)
- [ ] p95 latency < 50ms (benchmark tests)
- [ ] All traceability links valid
- [ ] Code review approved
```

---

## 8. Implementation Contracts Section (MANDATORY)

### Section 8 Requirements

Every TASKS document MUST include "## 8. Implementation Contracts":

```markdown
## 8. Implementation Contracts

### 8.1 Contracts Provided (if provider)

@icon: ICON-001:ContractName
@icon-role: provider

This TASKS implements the following contract:
- [ICON-001](../ICON/ICON-001.md): [Contract description]

### 8.2 Contracts Consumed (if consumer)

@icon: ICON-001:ContractName
@icon-role: consumer

This TASKS depends on:
- [ICON-001](../ICON/ICON-001.md): [Usage description]

### 8.3 No Contracts (if neither)

No implementation contracts for this TASKS.
```

### Validation

```bash
# Section 8 must exist
grep -q "## 8. Implementation Contracts" TASKS-NNN.md
```

---

## 9. Traceability Tag Requirements

### Required Tags (Layer 11)

```markdown
## Traceability Tags

@brd: BRD-001:REQ-NNN
@prd: PRD-001:REQ-NNN
@ears: EARS-001:REQ-NNN
@bdd: BDD-001:SCENARIO-NNN
@adr: ADR-NNN
@sys: SYS-001:REQ-NNN
@req: REQ-NNN
@spec: SPEC-NNN:section
```

### Optional Tags

```markdown
@impl: IMPL-NNN (if project uses IMPL)
@ctr: CTR-NNN (if contracts defined)
@icon: ICON-NNN:ContractName (if implementation contracts)
```

---

## 10. Quality Checklist

### Before Creating

- [ ] SPEC document exists and is approved
- [ ] REQ documents are complete
- [ ] BDD scenarios are defined
- [ ] Architecture decisions (ADR) documented

### During Creation

- [ ] Use TASKS-TEMPLATE.md as starting point
- [ ] Follow all section rules above
- [ ] Include specific SPEC line references
- [ ] Define measurable acceptance criteria
- [ ] Include Section 8 (Implementation Contracts)

### After Creation

- [ ] All traceability tags valid
- [ ] Links resolve to existing documents
- [ ] Update TASKS-000_index.md
- [ ] Run validation script
- [ ] Notify downstream IPLAN creators

---

## 11. Common Anti-Patterns

### Avoid

1. **Vague scope** - Be specific about boundaries
2. **Generic steps** - Each step should be actionable
3. **Missing SPEC references** - Always link to SPEC lines
4. **No acceptance criteria** - Must be verifiable
5. **Missing Section 8** - ALWAYS include contracts section
6. **Orphaned contracts** - ICON references must exist

---

## 12. Validation

### Automated Validation

```bash
./scripts/validate_tasks.sh /path/to/TASKS-NNN_name.md
```

### Manual Checklist

- [ ] Filename follows convention
- [ ] All 8 required sections present
- [ ] Traceability tags complete
- [ ] Section 8 Implementation Contracts included
- [ ] SPEC references valid
- [ ] BDD scenario links valid

---

## References

- [TASKS-TEMPLATE.md](./TASKS-TEMPLATE.md) - Tasks template
- [TASKS-000_index.md](./TASKS-000_index.md) - Tasks registry
- [README.md](./README.md) - Directory overview
- [IMPLEMENTATION_CONTRACTS_GUIDE.md](./IMPLEMENTATION_CONTRACTS_GUIDE.md) - Contracts guide
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Workflow guide

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-27
