# Metadata Tagging Quick Reference

**Version**: 1.0
**Purpose**: Quick reference card for metadata tagging standards
**Full Guide**: [METADATA_TAGGING_GUIDE.md](./METADATA_TAGGING_GUIDE.md)

---

## When to Use

✅ **Use metadata tagging when:**
- Project supports dual/multiple architectural approaches
- Building documentation sites (Docusaurus, MkDocs)
- Need to indicate priority between approaches

❌ **Do NOT use when:**
- Project has single architecture only
- All documents apply equally to all approaches

---

## Three-Tier Template System

### 1️⃣ Primary (Recommended) Implementation

```yaml
---
title: "DOC-XXX: Feature Name"
tags:
  - feature-doc
  - ai-agent-primary
  - recommended-approach
custom_fields:
  architecture_approach: ai-agent-based
  priority: primary
  development_status: active
  agent_id: AGENT-XXX
  fallback_reference: DOC-YYY
---
```

**Custom Admonition:**
```markdown
:::recommended Primary Implementation (AI Agent-Based)
**Architecture**: AI Agent-Based Platform (@adr: ADR-REF-002)
**Priority**: ✅ Recommended approach
**Status**: Active development

**Fallback Alternative**: [@doc: DOC-YYY](./DOC-YYY_name.md)
:::
```

---

### 2️⃣ Fallback (Reference) Implementation

```yaml
---
title: "DOC-XXX: Feature Name"
tags:
  - feature-doc
  - traditional-fallback
  - reference-implementation
custom_fields:
  architecture_approach: traditional-8layer
  priority: fallback
  development_status: reference
  primary_alternative: DOC-YYY_name
---
```

**Custom Admonition:**
```markdown
:::fallback Fallback Implementation (Traditional)
**Architecture**: Traditional Platform (@adr: ADR-REF-001)
**Priority**: ⚠️ Fallback option (use only if primary not viable)
**Status**: Reference implementation

**Recommended Alternative**: [@doc: DOC-YYY](./DOC-YYY_name.md)
:::
```

---

### 3️⃣ Shared Platform Requirements

```yaml
---
title: "DOC-XXX: Platform Feature"
tags:
  - platform-doc
  - shared-architecture
  - required-both-approaches
custom_fields:
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  implementation_differs: false
  primary_implementation: ai-agent-based
---
```

---

## Priority Levels

| Priority | Indicator | Meaning | Visual |
|----------|-----------|---------|--------|
| `primary` | ✅ | Recommended approach | Green, expanded |
| `fallback` | ⚠️ | Secondary option | Yellow, collapsed |
| `shared` | ⚙️ | Required by all | Neutral |
| `deprecated` | ⛔ | Legacy/archived | Red |

---

## Development Status

| Status | Meaning |
|--------|---------|
| `active` | Currently implemented/in development |
| `reference` | Reference implementation only |
| `planned` | Future implementation |
| `deprecated` | Legacy/archived |

---

## Tag Taxonomy

### Document Type Tags
- `feature-brd` / `feature-prd` / `feature-spec`
- `platform-brd` / `platform-prd`
- `architecture-adr`

### Architecture Tags
- `ai-agent-primary`
- `traditional-fallback`
- `shared-architecture`
- `recommended-approach`
- `reference-implementation`

### Feature Category Tags
- `fraud-detection`
- `compliance`
- `customer-support`
- `transaction-processing`
- `monitoring`
- `analytics-insights`
- etc.

---

## How to Define Metadata Tags (For AI Assistants)

### Basic YAML Frontmatter Structure

Metadata tags are defined in **YAML frontmatter** at the top of markdown documents:

```yaml
---
title: "Document Title"
tags:
  - tag1
  - tag2
  - tag3
custom_fields:
  field1: value1
  field2: value2
---

# Your Document Content Starts Here
```

### What AI Assistants Use Tags For

When you add metadata tags, AI assistants automatically:

1. **Recognize Document Type**: Know whether it's a BRD, PRD, SPEC, etc.
2. **Understand Priority**: Identify recommended vs fallback approaches
3. **Follow Architecture**: Apply correct patterns for AI-agent vs traditional
4. **Validate Cross-References**: Check bidirectional links between primary/fallback
5. **Generate Appropriate Content**: Include correct admonitions and references
6. **Maintain Consistency**: Ensure metadata matches document content

### Tag Behavior by Type

**`ai-agent-primary` tag** → AI assistants will:
- ✅ Use AI/ML terminology and patterns
- ✅ Reference agent-to-agent communication (A2A Protocol)
- ✅ Include ML-specific requirements (training data, models)
- ✅ Add `:::recommended` admonition

**`priority: primary` field** → AI assistants will:
- ✅ Mark as recommended approach
- ✅ Place higher in navigation hierarchy
- ✅ Expand by default in documentation sites
- ✅ Link to fallback alternatives

**`agent_id: AGENT-XXX` field** → AI assistants will:
- ✅ Validate uniqueness across documents
- ✅ Use in A2A Protocol references
- ✅ Include in traceability matrices

### Required vs Optional Fields

**Required Fields** (all documents):
```yaml
title: "DOC-XXX: Document Title"
tags: [array of classification tags]
custom_fields:
  architecture_approach: ai-agent-based  # or traditional-8layer
  priority: primary                      # or fallback, shared, deprecated
  development_status: active             # or reference, planned, deprecated
```

**Optional Fields** (context-dependent):
```yaml
custom_fields:
  agent_id: AGENT-009                    # For AI agent documents only
  fallback_reference: BRD-016            # For primary docs with traditional equivalent
  primary_alternative: BRD-022_name      # For fallback docs linking to primary
  implementation_differs: false          # For shared docs
  architecture_approaches: [...]         # For shared docs (instead of architecture_approach)
```

### Tag Inheritance Rules

AI assistants process documents in this order:

1. **Document Type Tags** → Determine template and structure
2. **Architecture Tags** → Select appropriate patterns and examples
3. **Priority Tags** → Apply visual hierarchy and recommendations
4. **Feature Tags** → Cross-reference related documents

### Quick Validation by AI Assistants

AI assistants automatically check:

- ✅ Required fields present: `title`, `tags`, `priority`, `architecture_approach`
- ✅ Valid priority values: Only `primary`, `fallback`, `shared`, `deprecated`
- ✅ Tag taxonomy compliance: Tags follow standard categories
- ✅ Bidirectional references: Primary ↔ fallback links exist
- ✅ Agent ID format: `AGENT-XXX` (three digits)
- ✅ Agent ID uniqueness: No duplicate agent IDs

---

## How to Define Metadata in Prompts

When instructing AI assistants to create or update documents, use these prompt patterns:

### Method 1: Direct Instruction (Recommended)

```
Create BRD-030 for Payment Routing Agent using AI-agent metadata:
- priority: primary
- agent_id: AGENT-009
- architecture_approach: ai-agent-based
- category: transaction-processing
```

### Method 2: Shorthand Notation

AI assistants understand abbreviated instructions:

| Shorthand | AI Understands As |
|-----------|-------------------|
| "AI-agent primary" | `ai-agent-primary` tag, `priority: primary`, `recommended-approach` tag |
| "Traditional fallback" | `traditional-fallback` tag, `priority: fallback`, `reference-implementation` tag |
| "Shared platform" | `shared-architecture` tag, `priority: shared`, applies to both architectures |
| "AGENT-009" | `agent_id: AGENT-009`, validates uniqueness |
| "Active development" | `development_status: active` |

**Example:**
```
Create an AI-agent primary BRD for risk scoring (AGENT-010, active)
```

AI assistant applies:
```yaml
tags:
  - feature-brd
  - ai-agent-primary
  - recommended-approach
custom_fields:
  architecture_approach: ai-agent-based
  priority: primary
  development_status: active
  agent_id: AGENT-010
```

### Method 3: Provide Complete Frontmatter

```
Create BRD-030 with this metadata:

---
title: "BRD-030: Payment Routing Agent"
tags:
  - feature-brd
  - ai-agent-primary
  - transaction-processing
custom_fields:
  architecture_approach: ai-agent-based
  priority: primary
  agent_id: AGENT-009
---
```

### Method 4: Reference Template

```
Use the "Primary (AI Agent) BRD" metadata template for BRD-030
```

### Method 5: Specify Cross-References

```
Create BRD-030 as AI-agent version with BRD-018 as fallback
```

AI assistant adds:
- BRD-030: `fallback_reference: BRD-018`
- BRD-018: `primary_alternative: BRD-030_payment_routing_agent`

### Common Prompt Patterns

**New AI Agent Document:**
```
Create AI-agent BRD for fraud detection (AGENT-011, active, no fallback)
```

**Traditional Fallback:**
```
Create traditional fallback version of BRD-030 (reference status)
```

**Shared Platform:**
```
Create shared platform BRD for API gateway (applies to both architectures)
```

**Update Existing:**
```
Update BRD-025: change status to "active", add fallback_reference: BRD-020
```

### What AI Assistants Automatically Apply

**From "AI-agent" keyword:**
- ✅ `ai-agent-primary` tag
- ✅ `priority: primary`
- ✅ `recommended-approach` tag
- ✅ ML/AI terminology
- ✅ `:::recommended` admonition

**From "Traditional" or "fallback" keyword:**
- ✅ `traditional-fallback` tag
- ✅ `priority: fallback`
- ✅ `reference-implementation` tag
- ✅ `:::fallback` admonition
- ✅ Link to primary alternative

**From "Shared" or "platform" keyword:**
- ✅ `shared-architecture` tag
- ✅ `priority: shared`
- ✅ `architecture_approaches: [ai-agent-based, traditional-8layer]`

---

## Validation Checklist

Before committing documents with metadata:

- [ ] YAML frontmatter valid syntax
- [ ] Required fields present (`title`, `tags`, `architecture_approach`, `priority`)
- [ ] Bidirectional cross-references correct (primary ↔ fallback)
- [ ] Tags follow taxonomy standards
- [ ] Agent IDs unique (for AI Agent documents)
- [ ] Custom admonitions present on key documents
- [ ] Development status accurate
- [ ] Document ID in frontmatter matches filename

---

## Quick Validation Script

```bash
# Validate single file
python scripts/validate_metadata.py docs/BRD/BRD-022_name.md

# Validate all BRDs
for file in docs/BRD/*.md; do
  python scripts/validate_metadata.py "$file"
done

# Check bidirectional references
grep -l "fallback_reference: BRD-016" docs/BRD/*.md  # Should find BRD-022
grep -l "primary_alternative: BRD-022" docs/BRD/*.md  # Should find BRD-016
```

---

## Common Patterns

### BRD Pattern (Business Requirements)

**AI Agent BRDs (BRD-022 to BRD-029):**
- `priority: primary`
- `architecture_approach: ai-agent-based`
- `agent_id: AGENT-001` through `AGENT-008`
- `fallback_reference:` (if traditional equivalent exists)

**Traditional BRDs (BRD-016, BRD-017, BRD-019):**
- `priority: fallback`
- `architecture_approach: traditional-8layer`
- `primary_alternative:` (link to AI Agent equivalent)

**Shared BRDs (BRD-001 to BRD-005):**
- `priority: shared`
- `architecture_approaches: [ai-agent-based, traditional-8layer]`

### ADR Pattern (Architecture Decisions)

**Primary Architecture ADR:**
- `priority: primary`
- `decision_status: recommended`
- `architecture_approach: ai-agent-based`

**Fallback Architecture ADR:**
- `priority: fallback`
- `decision_status: fallback`
- `primary_alternative:` (link to recommended ADR)

**Comparison ADR:**
- `priority: shared`
- `document_type: comparison`
- `architecture_approaches:` (array of both)

---

## Tool-Specific Notes

### Claude Code
- ✅ Optimal for bulk metadata migration (20-50 files)
- ✅ Validates YAML syntax automatically
- ✅ Can handle 100KB files easily

### Gemini CLI
- ✅ Good for single-file updates
- ⚠️ Use file read tool (not `@`) for files >10K tokens

### GitHub Copilot
- ✅ Good for individual file metadata
- ⚠️ Limited context for bulk operations

---

## Example: Complete BRD with Metadata

```markdown
---
title: "BRD-022: Fraud Detection Agent (ML-based Risk)"
tags:
  - feature-brd
  - ai-agent-primary
  - fraud-detection
  - recommended-approach
custom_fields:
  architecture_approach: ai-agent-based
  priority: primary
  development_status: active
  agent_id: AGENT-001
  fallback_reference: BRD-016
---

# BRD-022: Fraud Detection Agent (ML-based Risk)

:::recommended Primary Implementation (AI Agent-Based)
**Architecture**: AI Agent-Based Platform (@adr: ADR-REF-002)
**Priority**: ✅ Recommended approach
**Status**: Active development
**Agent ID**: AGENT-001

**Fallback Alternative**: [@brd: BRD-016](./BRD-016_fraud_detection_risk_screening.md)

**Advantages of AI Agent Approach**:
- Adaptive ML-based fraud detection
- Self-improving system
- 38.7% lower TCO
:::

## Document Control
[rest of document]
```

---

## Resources

- **Full Guide**: [METADATA_TAGGING_GUIDE.md](./METADATA_TAGGING_GUIDE.md)
- **AI Rules**: [AI_ASSISTANT_RULES.md](./AI_ASSISTANT_RULES.md) - Rule 10
- **Tool Guide**: [TOOL_OPTIMIZATION_GUIDE.md](./TOOL_OPTIMIZATION_GUIDE.md)
- **ID Standards**: [ID_NAMING_STANDARDS.md](./ID_NAMING_STANDARDS.md)

---

**Need Help?** See full guide or open framework issue.
