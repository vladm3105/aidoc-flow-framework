---
title: "Metadata vs. Traceability Quick Reference"
tags:
  - quick-reference
  - metadata-guide
  - traceability-guide
  - shared-architecture
custom_fields:
  document_type: quick-reference
  purpose: clarify-metadata-traceability-distinction
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
---

# Metadata vs. Traceability Quick Reference

## Critical Distinction

AI Dev Flow uses **TWO SEPARATE SYSTEMS** for document information:

1. **YAML Frontmatter (Metadata)**: Document classification and tooling integration
2. **Traceability Tags (`@artifact: ID`)**: Audit trail and compliance tracking

**These are NOT the same and serve different purposes.**

---

## Side-by-Side Comparison

| Aspect | YAML Frontmatter | Traceability Tags |
|--------|------------------|-------------------|
| **Primary Purpose** | Document classification, search, tooling | Audit trail, compliance, dependency tracking |
| **Location** | Top of file (lines 1-20) | section 7 (Traceability) in document body |
| **Format** | YAML key-value pairs | Markdown inline: `@artifact: ID (Description)` |
| **Audience** | Documentation systems (Docusaurus), validation tools | Auditors, reviewers, QA, AI assistants |
| **Validation** | Schema-based (`scripts/validate_metadata.py`) | Bidirectional link checking (`scripts/validate_tags_against_docs.py`) |
| **Changeability** | Can be updated as needed | Immutable after document approval |
| **Content** | Classification tags, layer info, architecture approach | Specific document IDs with descriptions |
| **Machine-Readable** | Yes (YAML parsers) | Yes (regex: `@[a-z]+: [A-Z]+-\d+`) |
| **Human-Readable** | Moderate (structured data) | High (prose with inline references) |
| **Required In** | Templates, index files, published docs | All production documents (BRD → IPLAN) |
| **Quality Gate** | `validate_metadata.py` must pass | `validate_tags_against_docs.py` must pass |
| **Git Conflicts** | Low risk (top of file) | Low risk (section 7 only) |

---

## When to Use Each System

### Use YAML Frontmatter When:

- ✅ Classifying document type (BRD, PRD, REQ, etc.)
- ✅ Marking document status (draft, approved, deprecated)
- ✅ Organizing documentation site structure
- ✅ Enabling automated validation
- ✅ Filtering/searching documents by attributes
- ✅ Specifying architecture approach (ai-agent vs traditional)

### Use Traceability Tags When:

- ✅ Linking specific upstream requirements
- ✅ Tracking downstream implementations
- ✅ Creating audit trail for compliance
- ✅ Enabling impact analysis (what depends on this?)
- ✅ Supporting regulatory documentation
- ✅ Providing context for reviewers
- ✅ AI assistants need to follow dependency chains

---

## Examples: REQ-NN (Atomic Requirement)

### YAML Frontmatter Example

```yaml
---
title: "REQ-NN: WebSocket Reconnection Logic"
tags:
  - atomic-requirement
  - layer-7-artifact
  - websocket-connectivity
  - error-handling
custom_fields:
  document_type: requirement
  artifact_type: REQ
  layer: 7
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: primary
  development_status: active
  upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SYS]
  downstream_artifacts: [IMPL, CTR, SPEC]
---
```

**What This Tells Us**:
- This is a Layer 7 artifact (Atomic Requirements)
- Related to WebSocket connectivity and error handling
- Active document, primary priority
- Has upstream dependencies (6 layers) and downstream targets (3 layers)
- **Does NOT tell us which specific documents it links to**

### Traceability Tags Example (Same Document)

```markdown
## 7. Traceability

### Upstream References

#### Business Requirements (@brd)
- @brd: BRD.01.01.01 (Platform Architecture & Technology Stack)
  - section 5.2.3: Real-time data streaming requirements
  - Establishes need for persistent connections

#### Product Requirements (@prd)
- @prd: PRD.03.01.01 (Unified [PRODUCT_NAME] Product Definition)
  - section 4.1: Live quote updates with <500ms latency
  - Drives WebSocket choice over polling

#### EARS (@ears) — Event-Action-Response-State (Engineering Requirements)
- @ears: EARS.02.24.01 (Exchange Integration Requirements)
  - EARS.02.24.03: WHEN connection lost THEN system SHALL reconnect WITHIN 5 seconds
  - Direct source for this requirement

#### Acceptance Criteria (@bdd)
- @bdd: BDD.01.13.01 (Quote Display Acceptance Criteria)
  - Scenario: Reconnection after network interruption
  - Defines expected user experience

#### Architecture Decisions (@adr)
- @adr: ADR-NN (WebSocket Connection Architecture)
  - Decision: Exponential backoff reconnection strategy
  - Provides architectural context

#### System Requirements (@sys)
- @sys: SYS.01.25.01 ([PRODUCT_NAME] System Requirements)
  - SYS.01.25.12: Connection resilience requirements
  - System-level performance constraints

### Downstream References

#### Implementation Approach (@impl)
- @impl: IMPL.01.28.01 ([PRODUCT_NAME] Implementation Approach)
  - section 3.2: Connection management strategy

#### Technical Specifications (@spec)
- @spec: SPEC-NN (WebSocket Quote Ingestion Technical Spec)
  - section 4: Reconnection algorithm implementation
  - section 5: Error handling and logging
```

**What This Tells Us**:
- Exact 01_BRD/02_PRD/03_EARS/04_BDD/05_ADR/SYS document IDs this requirement traces to
- Specific sections within each upstream document
- Why each upstream artifact matters (rationale)
- Which downstream documents implement this requirement
- **Provides complete audit trail for compliance**

---

## Traceability Rules (REQUIRED vs OPTIONAL)

| Document Type | Upstream Traceability | Downstream Traceability |
|---------------|----------------------|------------------------|
| **BRD** | OPTIONAL (to other BRDs) | OPTIONAL |
| **All Other Documents** | REQUIRED | OPTIONAL |

**Key Rules**:
- **Upstream REQUIRED** (except BRD): Document MUST reference its upstream sources
- **Downstream OPTIONAL**: Only link to documents that already exist
- **No-TBD Rule**: NEVER use placeholder IDs (TBD, XXX, NNN) - leave empty or omit section

---

## Cumulative Tagging Hierarchy

Each SDD layer inherits ALL upstream traceability tags:

| Layer | Required Tags | Example Count | Purpose |
|-------|---------------|---------------|---------|
| Layer 1 (BRD) | None | 0 | Source document (no upstream) |
| Layer 2 (PRD) | @brd | 1 | Business context |
| Layer 3 (EARS) | @brd, @prd | 2 | Product + business context |
| Layer 4 (BDD) | @brd, @prd, @ears | 3 | Add acceptance criteria |
| Layer 5 (ADR) | @brd, @prd, @ears, @bdd | 4 | Add architecture decisions |
| Layer 6 (SYS) | @brd, @prd, @ears, @bdd, @adr | 5 | Add system requirements |
| Layer 7 (REQ) | @brd, @prd, @ears, @bdd, @adr, @sys | 6 | Full upstream chain |
| Layer 8 (IMPL) | All Layer 7 + new tags | 7+ | Add implementation approach |
| Layer 9 (CTR) | All Layer 8 + new tags | 8+ | Add contracts (if applicable) |
| Layer 10 (SPEC) | All previous + new tags | 9+ | Add technical spec |
| Layer 11 (TASKS) | All previous + new tags | 10+ | Add task breakdown |
| Layer 12 (IPLAN) | All previous + new tags | 11+ | Complete audit trail |

**Rule**: Each layer MUST include ALL upstream tags from previous layers.

---

## Validation Commands

### YAML Frontmatter Validation

```bash
# Validate all markdown files
python3 scripts/validate_metadata.py .

# Validate specific directory
python3 scripts/validate_metadata.py ai_dev_flow

# Strict mode (warnings as errors)
python3 scripts/validate_metadata.py --strict .
```

**Checks**:
- YAML syntax correctness
- Required fields present
- Tag taxonomy compliance
- Layer consistency
- Architecture approach validity

### Traceability Tags Validation

```bash
# Run a traceability check with your AI assistant (or local scripts)
# Checks bidirectional links between documents
```

**Checks**:
- All upstream tags present
- Cumulative tagging hierarchy correct
- Bidirectional references valid
- Document IDs exist
- No orphaned references

---

## Common Mistakes to Avoid

### ❌ Wrong: Using YAML for Audit Trail

```yaml
# DON'T DO THIS - Too generic, no audit trail
custom_fields:
  references: [BRD-NN, PRD-NN, ADR-NN]
```

**Problem**: No context, no descriptions, no compliance value

### ✅ Right: Use Traceability Tags

```markdown
## 7. Traceability

### Upstream References
- @brd: BRD.NN.NN.NN (Platform Architecture)
  - section 3.5: Technology stack requirements
- @prd: PRD.NN.NN.NN (Product)
  - section 4: Real-time data requirements
```

**Benefit**: Full context, audit-ready, human-readable

---

### ❌ Wrong: Putting Traceability in YAML

```yaml
custom_fields:
  upstream:
    brd: "BRD-NN"
    prd: "PRD-NN"
```

**Problems**:
- Audit trail in metadata (wrong location)
- No descriptions or section references
- Hard to review inline with document
- Violates separation of concerns

---

### ❌ Wrong: Omitting YAML Frontmatter

```markdown
# REQ-NN: WebSocket Reconnection Logic

## 1. Requirement Statement
...
```

**Problems**:
- Document not discoverable by tooling
- No classification metadata
- Can't generate documentation sites
- Validation tools can't check compliance

---

## Quick Decision Tree

```
Need to classify document type/status?
  → Use YAML Frontmatter

Need to link specific upstream documents?
  → Use Traceability Tags (@artifact: ID)

Need to show which documents depend on this one?
  → Use Traceability Tags (@artifact: ID)

Need to enable documentation site generation?
  → Use YAML Frontmatter

Need audit trail for compliance?
  → Use Traceability Tags (@artifact: ID)

Need to filter/search documents?
  → Use YAML Frontmatter

Need AI assistant to follow dependency chains?
  → Use Traceability Tags (@artifact: ID)
```

---

## Summary

| System | Primary Value | Key Use Case |
|--------|---------------|--------------|
| **YAML Frontmatter** | Classification & tooling | "What type of document is this?" |
| **Traceability Tags** | Audit trail & compliance | "What documents does this depend on?" |

**Both systems are required.** They complement each other:

- **YAML Frontmatter**: Enables discovery, organization, validation
- **Traceability Tags**: Enables impact analysis, compliance, review

---

## See Also

- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](./SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - section "Metadata Management Approaches"
<!-- VALIDATOR:IGNORE-LINKS-START -->
- See `scripts/validate_metadata.py` and `scripts/validate_tags_against_docs.py` for local validation tooling.
<!-- VALIDATOR:IGNORE-LINKS-END -->
- [scripts/validate_metadata.py](../scripts/validate_metadata.py) - YAML validation tool
- Local validation: `scripts/validate_tags_against_docs.py` for cumulative tag compliance and bidirectional checks
