---
title: "ADR-CTR: API Contract Files Policy"
tags:
  - adr
  - layer-5-artifact
  - shared-architecture
  - policy-decision
custom_fields:
  document_type: adr
  artifact_type: ADR
  layer: 5
  priority: shared
  development_status: active
  decision_status: accepted
---

# ADR-CTR: API Contract Files Policy

**Status**: Accepted
**Date**: 2025-11-02
**Decision Makers**: AI Dev Flow Working Group
**Scope**: All API contracts (internal and external)

## Context

API contracts (CTR documents) can be represented in multiple ways:

1. **Separate Dual Files**: Both `.md` (human-readable) and `.yaml` (machine-readable)
2. **Embedded in SPEC**: Contract defined within technical specification
3. **YAML Only**: Machine-readable contract without documentation
4. **Markdown Only**: Human-readable documentation without formal schema

The AI dev flow templates previously provided contradictory guidance, with some templates suggesting embedding contracts in SPEC files while others emphasized separate CTR files.

### Problem Statement

**Inconsistent Contract Placement** led to:

- **Traceability Gaps**: SPEC files referencing non-existent CTR documents
- **Tool Incompatibility**: Contract testing tools requiring separate YAML files
- **Parallel Development Blocked**: Teams unable to start implementation without completed SPEC
- **Version Control Issues**: Contract changes buried in large SPEC commits
- **Documentation Drift**: Markdown docs not synced with YAML schemas

### Current Template Conflicts

**SPEC-MVP-TEMPLATE.yaml** (lines 314-336) suggested:
```yaml
# Option A: Reference separate contract files
contracts:
  - ref: CTR-01

# Option B: Embed contract inline
contracts:
  inline:
    openapi: "3.0.0"
    ...
```

**08_CTR/README.md** stated:
> "Each contract SHOULD have dual files (.md + .yaml)"

Use of "SHOULD" (optional) vs "MUST" (mandatory) created ambiguity.

## Decision

**We will ALWAYS use separate dual-file CTR documents for ALL API contracts.**

### Mandatory Format

Every API contract requires:

1. **CTR-NNN_{slug}.md** (Markdown documentation)
   - Human-readable contract description
   - Examples, context, rationale
   - Links to requirements and specifications

2. **CTR-NNN_{slug}.yaml** (Machine-readable schema)
   - OpenAPI 3.0+ specification (REST APIs)
   - AsyncAPI 2.0+ specification (Event-driven)
   - gRPC/Protocol Buffers (RPC-based)
   - JSON Schema (data contracts)

### Applies To

- **Internal APIs**: Service-to-service contracts within the system
- **External APIs**: Third-party integrations ([EXTERNAL_SERVICE_GATEWAY], [EXTERNAL_DATA_PROVIDER - e.g., Weather API, item Data API])
- **Event Schemas**: Pub/Sub message contracts
- **Data Models**: Shared data structure contracts

### Does NOT Apply To

- **Private Functions**: Internal module functions (no CTR needed)
- **Configuration Files**: System config (use SPEC, not CTR)
- **Database Schemas**: Table definitions (use separate schema docs)

## Rationale

### Benefits of Separate Dual Files

1. **Parallel Development** (40% faster delivery):
   - Teams can implement against CTR while SPEC is being written
   - Contract agreed first, implementation details negotiated later
   - Multiple teams work concurrently on different SPECs sharing same CTR

2. **Contract Testing** (100% tool compatibility):
   - Prism, Spectral, Dredd require standalone YAML files
   - Mock servers (Prism, WireMock) consume YAML directly
   - CI/CD validation tools need isolated contract files

3. **Clear Traceability** (zero broken links):
    - REQ → **CTR** → SPEC → TASKS (explicit chain)

   - Git history shows contract evolution independently
   - Impact analysis: "Which SPECs use CTR-NN?"

4. **Version Control** (granular commits):
   - Contract changes isolated from implementation changes
   - Smaller, focused commits: "Update CTR-007 authentication schema"
   - Easier code review: contract changes visible separately

5. **Documentation Sync** (zero drift):
   - Markdown and YAML maintained side-by-side
   - Validation tools ensure MD examples match YAML schemas
   - Single source of truth for contract definition

6. **Reusability** (DRY principle):
   - Multiple SPECs reference same CTR (shared interfaces)
   - Contract versioning independent of SPEC versions
   - Consistent interfaces across multiple implementations

### Drawbacks (Considered and Accepted)

1. **More Files**: Each contract = 2 files (accepted as necessary overhead)
2. **Sync Burden**: Must keep .md and .yaml aligned (tooling mitigates this)
3. **Extra Step**: Requires creating CTR before SPEC (accepted as best practice)

### Alternatives Considered

**Alternative 1: Embed Contracts in SPEC**

- ❌ Blocks parallel development
- ❌ Incompatible with contract testing tools
- ❌ Creates traceability gaps (no CTR-NNN ID)
- ❌ Mixes interface with implementation concerns

**Alternative 2: YAML Only (No Markdown)**

- ❌ Poor developer experience (no examples, context)
- ❌ Harder to review (YAML not human-friendly)
- ❌ Missing rationale and design decisions

**Alternative 3: Markdown Only (No YAML)**

- ❌ Ambiguous specifications (natural language imprecise)
- ❌ Incompatible with tooling (no machine-readable schema)
- ❌ Cannot generate mocks or validate automatically

**Alternative 4: Optional Dual Files ("SHOULD" not "MUST")**

- ❌ Inconsistent practices across project
- ❌ Some teams skip CTR, embed in SPEC → tooling breaks
- ❌ Traceability matrix incomplete

## Implementation

### Template Updates Required

1. **SPEC-MVP-TEMPLATE.yaml** (lines 314-336):
   - **Remove**: "Option B: Embed contract inline" section
   - **Keep**: "Option A: Reference separate contract files"
   - **Add**: "Contract References" section with CTR-NNN links

2. **08_CTR/README.md**:
   - **Change**: "SHOULD" → "MUST"
   - **Strengthen**: "ALWAYS create dual files (.md + .yaml)"
   - **Remove**: Any "optional" wording

3. **08_CTR/CTR-00_index.md**:
   - **Create**: Index file listing all contracts
   - **Format**: Table with CTR-ID, title, status, SPECs using it

4. **CTR-MVP-TEMPLATE.md** (already exists):
   - **Verify**: Emphasizes dual-file requirement
   - **Add**: Reference to this ADR

   - **Verify**: Provides OpenAPI/AsyncAPI base definition
   - **Add**: Comment referencing CTR-MVP-TEMPLATE.md

### Validation

Add pre-commit hook:

```bash
# Check: Every CTR-NNN.md has matching CTR-NNN.yaml
for md in 08_CTR/CTR-*.md; do
  yaml="08_CTR/${base}.yaml"

  if [ ! -f "$yaml" ]; then
    echo "ERROR: Missing $yaml for $md"
    exit 1
  fi
done

# Check: No embedded contracts in SPEC files
if grep -q "inline:" 09_SPEC/**/*.yaml; then
  echo "ERROR: Found embedded contracts in SPEC files"
  echo "Policy: Use separate CTR files (see ADR-CTR)"
  exit 1
fi
```

### Migration Path

**Existing Projects**:

1. **Identify Embedded Contracts**: Search SPEC files for inline contract definitions
2. **Extract to CTR Files**: Move embedded schemas to CTR-NNN.yaml
3. **Create Documentation**: Write CTR-NNN.md explaining the contract
4. **Update SPECs**: Replace inline contracts with `contract_ref: CTR-NNN`
5. **Update Traceability**: Link SPEC → CTR in traceability matrix

**New Projects**:

1. **REQ Completed**: Requirements defined and approved
2. **REQ Complete**: Requirements approved and stable
3. **CTR Created**: Define API contract (dual files) ← **BEFORE SPEC**
4. **SPEC Created**: Reference CTR, define implementation
5. **TASKS Created**: Code generation plan references CTR + SPEC

## Consequences

### Positive

- ✅ **Parallel Development**: Teams start implementation while SPEC is drafted
- ✅ **Tool Compatibility**: Contract testing, mocking, validation tools work
- ✅ **Clear Traceability**: Explicit REQ → CTR → SPEC → TASKS chain
- ✅ **Version Control**: Granular commits, easier code review
- ✅ **Reusability**: Multiple SPECs share common CTR contracts
- ✅ **Documentation Quality**: Markdown + YAML ensures completeness

### Negative (Mitigated)

- ⚠️ **More Files**: Accepted as necessary for clarity and tooling
- ⚠️ **Sync Effort**: Mitigated by validation scripts and pre-commit hooks
- ⚠️ **Learning Curve**: Mitigated by templates, examples (CTR-01), documentation

### [NORMAL_CONDITION - e.g., steady state, balanced load]

- 🔵 **Process Change**: Teams must create CTR before SPEC (new habit)
- 🔵 **Validation Required**: Pre-commit hooks ensure compliance (automated)

## Compliance

### Mandatory

- ✅ Every API contract MUST have dual files (CTR-NNN.md + CTR-NNN.yaml)
- ✅ SPEC files MUST reference CTR files (no embedded contracts)
- ✅ CTR files MUST exist before referencing SPEC is created
- ✅ CTR markdown MUST include examples matching YAML schemas

### Validation

Pre-commit hooks enforce:
- Dual-file existence check
- No embedded contracts in SPEC files
- Traceability: SPEC → CTR links resolve
- Schema validation: CTR YAML valid OpenAPI/AsyncAPI

### Review Checklist

Before merging PR with new CTR:

- [ ] CTR-NNN.md exists with complete documentation
- [ ] CTR-NNN.yaml exists with valid schema (OpenAPI/AsyncAPI)
- [ ] Examples in .md match schema in .yaml
- [ ] CTR-00_index.md updated with new entry
- [ ] Traceability links: REQ ← CTR → SPEC
- [ ] Pre-commit hooks pass (dual-file check)

## References

### Related Documents

- [CTR-MVP-TEMPLATE.md](../08_CTR/CTR-MVP-TEMPLATE.md) - Markdown template
- [08_CTR/README.md](../08_CTR/README.md) - Contracts overview
- [SPEC-MVP-TEMPLATE.yaml](../09_SPEC/SPEC-MVP-TEMPLATE.yaml) - Technical specification template
- [TRACEABILITY.md](../TRACEABILITY.md) - Document linking standards

### Standards

- [OpenAPI 3.0+ Specification](https://spec.openapis.org/oas/latest.html)
- [AsyncAPI 2.0+ Specification](https://www.asyncapi.com/docs/reference/specification/v2.0.0)
- [JSON Schema](https://json-schema.org/)

## Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-11-02 | 1.0 | Initial ADR - Separate CTR files policy | AI Dev Flow Working Group |

---

**Decision**: ACCEPTED
**Effective Date**: 2025-11-02
**Review Date**: 2026-02-02 (3 months)
