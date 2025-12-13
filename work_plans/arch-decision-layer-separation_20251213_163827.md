# Implementation Plan - Architecture Decision Layer Separation

**Created**: 2025-12-13 16:38:27 EST
**Status**: Ready for Implementation

## Objective

Establish proper layer separation for architecture decision topics across ALL projects using the SDD framework:
- **BRD (Layer 1)**: Business drivers and constraints only
- **PRD (Layer 2)**: Technical options and evaluation criteria
- **ADR (Layer 5)**: Final decisions and consequences

**Key Simplification**: No new "ADT" terminology. Use:
- **BRD subsection IDs** (`BRD.001.01`) - numbered topics in Section 7.2
- **ADR** - the only decision artifact (existing)

## Context

### Problem Statement
Current BRD Section 7.2 blends Layer 1 (business) content with Layer 5 (technical) content, creating:
- Technical noise for non-technical stakeholders
- Difficulty tracing architecture decisions to business justification
- BRD updates required for technical exploration changes

### Core Principle
**Each layer contains only what its audience needs to make decisions at that layer.**

| Content Type | BRD (Layer 1) | PRD (Layer 2) | ADR (Layer 5) |
|--------------|---------------|---------------|---------------|
| Business driver | Yes | Reference | Reference |
| Technical options | No | Yes | Selected + rejected |
| Evaluation criteria | No | Yes | Applied criteria |
| Final decision | No | No | Yes |
| Trade-off analysis | No | Constraints only | Full analysis |
| Consequences | Business impact only | Product impact | Technical consequences |

### Decision: No "ADT" Terminology
- **ADT** (Architecture Decision Topic) sounds too similar to **ADR** (Architecture Decision Record)
- Use simple subsection IDs (`BRD.001.01`) within existing document sections
- ADR remains the only decision artifact type

### Flow
```
BRD Section 7.2        →   PRD Section 18           →   ADR
(subsection BRD.001.01)    (technical requirements)     (decides)
"Topic Name"               "Topic Name"                 "Decision for Topic"
```

## Task List

### Pending
- [ ] 1. Document subsection ID format for Section 7.2 (`ai_dev_flow/ID_NAMING_STANDARDS.md`)
- [ ] 2. Update BRD section 7.2 template - business-focused (`ai_dev_flow/BRD/BRD-TEMPLATE.md`)
- [ ] 3. Add BRD Section 7.2 content guidance (`ai_dev_flow/BRD/BRD_CREATION_RULES.md`)
- [ ] 4. Add PRD Section 18 template structure (`ai_dev_flow/PRD/PRD-TEMPLATE.md`)
- [ ] 5. Add PRD elaboration guidance (`ai_dev_flow/PRD/PRD_CREATION_RULES.md`)
- [ ] 6. Update ADR Section 4.1 - originating topic reference (`ai_dev_flow/ADR/ADR-TEMPLATE.md`)
- [ ] 7. Update doc-brd skill - business-only content (`.claude/skills/doc-brd/SKILL.md`)
- [ ] 8. Update doc-prd skill - elaboration workflow (`.claude/skills/doc-prd/SKILL.md`)
- [ ] 9. Update doc-adr skill - originating topic reference (`.claude/skills/doc-adr/SKILL.md`)
- [ ] 10. Add architecture topic validation rules (`.claude/skills/trace-check/SKILL.md`)

## Implementation Guide

### Prerequisites
- Access to `/opt/data/docs_flow_framework/` directory
- Understanding of SDD framework layer structure

### Template Structures

#### BRD Section 7.2 Template (Business-Focused)
```markdown
### BRD.NNN.NN: [Topic Name]

**Business Driver**: [Why this decision matters to business - reference upstream requirements]
**Business Constraints**:
- [Non-negotiable business rule 1]
- [Non-negotiable business rule 2]
**ADR Reference**: ADR-NNN (pending)
**PRD Elaboration**: PRD-NNN §X.X
```

**Remove from BRD**: Options Under Evaluation, Key Considerations (technical), Evaluation criteria, Technical timelines

#### PRD Section 18 Template (Architecture Decision Requirements)
```markdown
### BRD.NNN.NN: [Topic Name]

**Upstream**: BRD-NNN §7.2.X
**Technical Options**:
1. [Option A] (description)
2. [Option B] (description)
3. [Option C] (description)
**Evaluation Criteria**:
- [Criterion 1]: [measurable target]
- [Criterion 2]: [measurable target]
**Product Constraints**:
- [Integration constraint 1]
- [Integration constraint 2]
**Decision Timeline**: [Milestone reference]
**ADR Reference**: ADR-NNN (pending)
```

#### ADR Section 4.1 Template (Originating Topic)
```markdown
## 4. Context

### 4.1 Problem Statement

**Originating Topic**: BRD.NNN.NN - [Topic Name]
**Business Driver**: [From BRD Section 7.2]
**Business Constraints**: [From BRD Section 7.2]
**Technical Options Evaluated**: [From PRD Section 18]
```

### Validation Rules (trace-check Skill)
```yaml
ARCHITECTURE_TOPIC_VALIDATION:
  - rule: "BRD Section 7.2 subsections use format BRD.NNN.NN"
  - rule: "BRD subsections include ADR Reference field"
  - rule: "PRD Section 18 topics reference valid BRD subsection ID in Upstream field"
  - rule: "ADR Section 4.1 references originating BRD/PRD subsection ID"
```

### Content Guidelines

| Layer | Include | Exclude |
|-------|---------|---------|
| BRD Section 7.2 | Business objectives, Regulatory constraints, Non-negotiable rules, Business impact | Technology options, Performance specs, Evaluation criteria, Implementation patterns |
| PRD Section 18 | Technology options, Measurable criteria, Product constraints | Final decision, Full trade-off analysis, Technical consequences |
| ADR | Selected + rejected options, Applied criteria, Full trade-offs, Technical consequences | - |

### Verification
- Each BRD Section 7.2 subsection has `BRD.NNN.NN` format
- BRD subsections contain only business drivers and constraints
- PRD Section 18 topics reference valid BRD subsection IDs
- ADR Section 4.1 references originating topic

## Practical Example

### BEFORE: BRD with Technical Noise
```markdown
### BRD.001.03: Ledger System Selection

**Decision Required**: Core ledger system for double-entry accounting
**Options Under Evaluation**: Modern Treasury, Custom PostgreSQL, TigerBeetle
**Key Considerations**:
- Real-time position tracking capability
- Multi-currency support with sub-ledger isolation
**Timeline**: Decision required before Q1 2026 development phase
```

### AFTER: Layer-Separated

**BRD Section 7.2**:
```markdown
### BRD.001.03: Ledger System Selection

**Business Driver**: Real-time financial position visibility required for
treasury management (FR BRD.001.004) and regulatory reporting (BRD-003 §4.8).
**Business Constraints**:
- Must support multi-currency operations (USD, UZS, USDC)
- Audit trail retention per BSA requirements (5 years)
**ADR Reference**: ADR-003 (pending)
**PRD Elaboration**: PRD-001 §18.3
```

**PRD Section 18**:
```markdown
### BRD.001.03: Ledger System Selection

**Upstream**: BRD-001 §7.2.3
**Technical Options**:
1. Modern Treasury (managed SaaS)
2. Custom PostgreSQL with double-entry schema
3. TigerBeetle (high-performance financial DB)
**Evaluation Criteria**:
- Throughput: ≥10,000 TPS sustained
- Latency: <100ms P99 for balance queries
**ADR Reference**: ADR-003 (pending)
```

## References

### Files to Modify
```
/opt/data/docs_flow_framework/
├── ai_dev_flow/
│   ├── ID_NAMING_STANDARDS.md
│   ├── BRD/
│   │   ├── BRD-TEMPLATE.md
│   │   └── BRD_CREATION_RULES.md
│   ├── PRD/
│   │   ├── PRD-TEMPLATE.md
│   │   └── PRD_CREATION_RULES.md
│   └── ADR/
│       └── ADR-TEMPLATE.md
└── .claude/skills/
    ├── doc-brd/SKILL.md
    ├── doc-prd/SKILL.md
    ├── doc-adr/SKILL.md
    └── trace-check/SKILL.md
```

### Source Plan
- Plan file: `/home/ya/.claude/plans/sorted-purring-tiger.md`
