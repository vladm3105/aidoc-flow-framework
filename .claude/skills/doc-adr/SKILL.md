---
title: "doc-adr: Create Architecture Decision Records (Layer 5)"
name: doc-adr
description: Create Architecture Decision Records (ADR) - Layer 5 artifact documenting architectural decisions with Context-Decision-Consequences format
tags:
  - sdd-workflow
  - layer-5-artifact
  - shared-architecture
custom_fields:
  layer: 5
  artifact_type: ADR
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: core-workflow
  upstream_artifacts: [BDD,EARS]
  downstream_artifacts: [SYS,REQ]
---

# doc-adr

## Purpose

Create **Architecture Decision Records (ADR)** - Layer 5 artifact in the SDD workflow that documents architectural decisions with rationale, alternatives, and consequences.

**Layer**: 5

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3), BDD (Layer 4)

**Downstream Artifacts**: SYS (Layer 6), REQ (Layer 7), Code (Layer 13)

## Prerequisites

### Upstream Artifact Verification (CRITICAL)

**Before creating this document, you MUST:**

1. **List existing upstream artifacts**:
   ```bash
   ls docs/BRD/ docs/PRD/ docs/EARS/ docs/BDD/ docs/ADR/ docs/SYS/ docs/REQ/ 2>/dev/null
   ```

2. **Reference only existing documents** in traceability tags
3. **Use `null`** only when upstream artifact type genuinely doesn't exist
4. **NEVER use placeholders** like `BRD-XXX` or `TBD`
5. **Do NOT create missing upstream artifacts** - skip functionality instead


Before creating ADR, read:

1. **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`
2. **Technology Stack**: `docs/ADR/ADR-000_technology_stack.md` (approved technologies)
3. **Upstream BRD, PRD**: Read Architecture Decision Requirements sections
4. **Template**: `ai_dev_flow/ADR/ADR-TEMPLATE.md`
5. **Creation Rules**: `ai_dev_flow/ADR/ADR_CREATION_RULES.md`
6. **Validation Rules**: `ai_dev_flow/ADR/ADR_VALIDATION_RULES.md`

## When to Use This Skill

Use `doc-adr` when:
- Have identified architectural topics in BRD/PRD Architecture Decision Requirements sections
- Need to document technology choices with rationale
- Evaluating alternatives for architectural patterns
- Making decisions with long-term impact
- You are at Layer 5 of the SDD workflow

## ADR-Specific Guidance

### 1. Context-Decision-Consequences Format

**Template Structure**:

```markdown
# ADR-NNN: [Decision Title]

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

## Context
[What is the issue we're addressing? What factors are in play?]

## Decision
[What is the change we're proposing or have agreed to implement?]

## Consequences
[What becomes easier or more difficult because of this decision?]

### Positive Consequences
- [Benefit 1]
- [Benefit 2]

### Negative Consequences
- [Drawback 1]
- [Drawback 2]

### Risks
- [Risk 1 and mitigation]

## Alternatives Considered
### Alternative 1: [Name]
- **Pros**: [...]
- **Cons**: [...]
- **Why Rejected**: [...]

## Verification
[How will we verify this decision was correct?]

## Relations
- Supersedes: [ADR-XXX]
- Related to: [ADR-YYY]
- Influences: [SYS-NNN, REQ-MMM]
```

### 2. ADR Lifecycle States

**Proposed**: Decision under consideration
- Still evaluating alternatives
- Seeking stakeholder feedback
- Not yet implemented

**Accepted**: Decision approved and active
- Chosen as the path forward
- Implementation can proceed
- Should be followed by all

**Deprecated**: Decision no longer recommended
- Better alternative found
- Context changed
- Not deleted (historical record)

**Superseded by ADR-XXX**: Replaced by newer decision
- Links to replacing ADR
- Explains why replaced
- Maintains audit trail

### 3. Technology Stack Reference (ADR-000)

**CRITICAL**: Before proposing new technology:

1. Read `docs/ADR/ADR-000_technology_stack.md`
2. Check if technology already approved
3. If approved: Reference ADR-000 and explain use
4. If new: Justify addition and update ADR-000

**Example**:
```markdown
## Context
This service requires a message queue for asynchronous processing.

Per ADR-000 Technology Stack, the approved message queue is **Google Cloud Pub/Sub**.
This ADR documents the specific implementation approach for our use case.
```

**If proposing new technology NOT in ADR-000**:
```markdown
## Context
This feature requires real-time bidirectional communication (WebSocket).

**Note**: WebSocket technology is not currently in ADR-000 Technology Stack.
This ADR proposes adding Socket.IO to the approved stack.

## Decision
Add Socket.IO to technology stack for real-time communication.
[Justify why existing stack insufficient]

**Action**: Update ADR-000 Technology Stack if this ADR is accepted.
```

### 4. Platform BRD Critical Decisions First

**Priority Order**:

1. **Platform BRD ADRs** (create first)
   - Foundation decisions
   - Technology stack
   - Cross-cutting concerns
   - Referenced by all Feature BRDs

2. **Feature BRD ADRs** (create after Platform ADRs)
   - Feature-specific decisions
   - References Platform ADR decisions
   - Implementation details

**Example Flow**:
```
BRD-001 (Platform) identifies: "Database technology decision needed"
  ↓
ADR-033: Choose PostgreSQL (Platform ADR - CREATED FIRST)
  ↓
BRD-002 (Feature) references: "Use database per ADR-033"
  ↓
ADR-045: User data schema design (Feature ADR - references ADR-033)
```

## Tag Format Convention (By Design)

The SDD framework uses two distinct notation systems for cross-references:

| Notation | Format       | Artifacts                               | Purpose                                                             |
|----------|--------------|----------------------------------------|---------------------------------------------------------------------|
| Dash     | TYPE-NNN     | ADR, SPEC, CTR, IPLAN, ICON            | Technical artifacts - references to files/documents                 |
| Dot      | TYPE.NNN.NNN | BRD, PRD, EARS, BDD, SYS, REQ, IMPL, TASKS | Hierarchical artifacts - references to features inside documents |

**Key Distinction**:
- `@adr: ADR-033` → Points to the document `ADR-033_risk_limit_enforcement.md`
- `@brd: BRD.017.001` → Points to feature 001 inside document `BRD-017.md`

## Unified Feature ID Format (MANDATORY)

**For hierarchical requirements (BRD, PRD, EARS, BDD, SYS, REQ)**:
- **Always use**: `TYPE.NNN.NNN` (dot separator)
- **Never use**: `TYPE-NNN:NNN` (colon separator - DEPRECATED)

Examples:
- `@brd: BRD.017.001` ✅
- `@brd: BRD-017:001` ❌


## Cumulative Tagging Requirements

**Layer 5 (ADR)**: Must include tags from Layers 1-4 (BRD, PRD, EARS, BDD)

**Tag Count**: 4 tags (@brd, @prd, @ears, @bdd)

**Format**:
```markdown
## Traceability

**Required Tags** (Cumulative Tagging Hierarchy - Layer 5):
```markdown
@brd: BRD.001.030
@prd: PRD.001.002
@ears: EARS.001.001
@bdd: BDD.001.001
```

**Upstream Sources**:
- [BRD-001](../BRD/BRD-001_platform.md#BRD-001) - Architecture Decision Requirements
- [PRD-001](../PRD/PRD-001_integration.md#PRD-001) - Product requirements
- [EARS-001](../EARS/EARS-001_risk.md#EARS-001) - Formal requirements
- [BDD-001](../BDD/BDD-001_limits.feature) - Test scenarios

**Downstream Artifacts**:
- SYS-NNN (to be created) - System requirements
- REQ-NNN (to be created) - Atomic requirements
```

## Upstream/Downstream Artifacts

**Upstream Sources**:
- **BRD** (Layer 1) - Architecture Decision Requirements section
- **PRD** (Layer 2) - Architecture Decision Requirements section
- **EARS** (Layer 3) - Formal requirements constraints
- **BDD** (Layer 4) - Test scenarios validating decision

**Downstream Artifacts**:
- **SYS** (Layer 6) - System requirements implementing decision
- **REQ** (Layer 7) - Atomic requirements following decision
- **Code** (Layer 13) - Implementation per decision

**Same-Type Document Relationships** (conditional):
- `@related-adr: ADR-NNN` - ADRs sharing architectural context
- `@depends-adr: ADR-NNN` - ADR that must be decided first

## Creation Process

### Step 1: Identify Decision Topic

From BRD/PRD Architecture Decision Requirements sections, identify topic needing decision.

### Step 2: Read Technology Stack

Check `docs/ADR/ADR-000_technology_stack.md` for approved technologies.

### Step 3: Reserve ID Number

Check `docs/ADR/` for next available ID number (e.g., ADR-001, ADR-033).

**Special IDs**:
- **ADR-000**: Reserved for Technology Stack reference
- **ADR-001 onwards**: Regular decision records

### Step 4: Create ADR File

**File naming**: `docs/ADR/ADR-NNN_{slug}.md`

**Example**: `docs/ADR/ADR-033_risk_limit_architecture.md`

### Step 5: Fill Document Control Section

Complete all required metadata fields and initialize Document Revision History table.

### Step 6: Document Context

**Context Section**: Explain the problem and factors:
- What issue are we addressing?
- What constraints exist?
- What requirements drive this decision?
- Reference upstream BRD/PRD sections

### Step 7: State Decision

**Decision Section**: Clear, concise statement:
- What are we choosing to do?
- How will it be implemented?
- Reference technology stack (ADR-000) if applicable

### Step 8: Analyze Consequences

**Consequences Section**:
- **Positive**: Benefits and advantages
- **Negative**: Drawbacks and limitations
- **Risks**: Potential issues and mitigations

### Step 9: Document Alternatives

**Alternatives Considered**: For each alternative:
- Name and description
- Pros and cons
- Why rejected

### Step 10: Define Verification

**Verification Section**: How to validate decision:
- Success metrics
- BDD scenarios that test it
- Performance benchmarks

### Step 11: Add Relations

**Relations Section**:
- Supersedes: Which ADR this replaces
- Related to: Connected ADRs
- Influences: Which SYS/REQ depend on this

### Step 12: Add Cumulative Tags

Include @brd, @prd, @ears, @bdd tags (Layers 1-4).

### Step 13: Create/Update Traceability Matrix

**MANDATORY**: Update `docs/ADR/ADR-000_TRACEABILITY_MATRIX.md`

### Step 14: Commit Changes

Commit ADR and traceability matrix.

## Validation

### Automated Validation

```bash
# ADR validation
./ai_dev_flow/scripts/validate_adr_template.sh docs/ADR/ADR-033_*.md

# Cumulative tagging validation
python ai_dev_flow/scripts/validate_tags_against_docs.py --artifact ADR-033 --expected-layers brd,prd,ears,bdd --strict
```

### Manual Checklist

- [ ] Document Control section at top
- [ ] Status field completed (Proposed/Accepted/Deprecated/Superseded)
- [ ] Context explains problem and constraints
- [ ] Decision clearly stated
- [ ] Consequences analyzed (positive, negative, risks)
- [ ] Alternatives considered and documented
- [ ] Verification approach defined
- [ ] Relations to other ADRs documented
- [ ] Technology Stack (ADR-000) referenced if applicable
- [ ] Cumulative tags: @brd, @prd, @ears, @bdd included
- [ ] Traceability matrix updated

## Common Pitfalls

1. **No alternatives**: Must document why other options rejected
2. **Missing technology stack check**: Always check ADR-000 first
3. **Vague consequences**: Be specific about impacts
4. **No verification**: Must define how to validate decision
5. **Missing cumulative tags**: Layer 5 must include Layers 1-4 tags

## Post-Creation Validation (MANDATORY - NO CONFIRMATION)

**CRITICAL**: Execute this validation loop IMMEDIATELY after document creation. Do NOT proceed to next document until validation passes.

### Automatic Validation Loop

```
LOOP:
  1. Run: python scripts/validate_cross_document.py --document {doc_path} --auto-fix
  2. IF errors fixed: GOTO LOOP (re-validate)
  3. IF warnings fixed: GOTO LOOP (re-validate)
  4. IF unfixable issues: Log for manual review, continue
  5. IF clean: Mark VALIDATED, proceed
```

### Validation Command

```bash
# Per-document validation (Phase 1)
python scripts/validate_cross_document.py --document docs/ADR/ADR-NNN_slug.md --auto-fix

# Layer validation (Phase 2) - run when all ADR documents complete
python scripts/validate_cross_document.py --layer ADR --auto-fix
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Count |
|------------|------------------------|-------|
| ADR (Layer 5) | @brd, @prd, @ears, @bdd | 4 tags |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing @brd/@prd/@ears/@bdd tag | Add with upstream document reference |
| Invalid tag format | Correct to TYPE.NNN.NNN format |
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

**Blocking**: YES - Cannot proceed to next document until Phase 1 validation passes with 0 errors.

---

## Next Skill

After creating ADR, use:

**`doc-sys`** - Create System Requirements (Layer 6)

The SYS will:
- Implement ADR architectural decisions
- Include `@brd`, `@prd`, `@ears`, `@bdd`, `@adr` tags (cumulative)
- Define functional requirements and quality attributes
- Translate ADR decisions into technical requirements

## Related Resources

- **Technology Stack**: `docs/ADR/ADR-000_technology_stack.md`
- **ADR Creation Rules**: `ai_dev_flow/ADR/ADR_CREATION_RULES.md`
- **ADR Validation Rules**: `ai_dev_flow/ADR/ADR_VALIDATION_RULES.md`
- **ADR README**: `ai_dev_flow/ADR/README.md`
- **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`

## Quick Reference

**ADR Purpose**: Document architectural decisions with rationale

**Layer**: 5

**Tags Required**: @brd, @prd, @ears, @bdd (4 tags)

**Format**: Context-Decision-Consequences

**Lifecycle States**: Proposed → Accepted → Deprecated/Superseded

**Critical**: Always check ADR-000 Technology Stack first

**Next**: doc-sys
