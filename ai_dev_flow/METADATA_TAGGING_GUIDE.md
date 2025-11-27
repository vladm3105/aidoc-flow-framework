# Metadata Tagging Guide

## Document Control

| Field | Value |
|-------|-------|
| **Document Type** | Framework Guide |
| **Version** | 1.0 |
| **Status** | Active |
| **Last Updated** | 2025-11-23 |
| **Purpose** | Define metadata tagging standards for dual-architecture documentation |

---

## 1. Purpose & Scope

### 1.1 Purpose

Define YAML frontmatter metadata standards for projects supporting multiple architectural approaches (e.g., AI Agent-Based vs Traditional implementations) within the AI Dev Flow framework.

### 1.2 Scope

**Applies To:**
- BRD (Business Requirements Documents)
- ADR (Architecture Decision Records)
- PRD (Product Requirements Documents)
- SPEC (Technical Specifications)
- IMPL (Implementation Plans)

**Does NOT Apply To:**
- Source code files (use language-specific conventions)
- Test files (use test framework conventions)
- Configuration files

### 1.3 When to Use Metadata Tagging

Use metadata tagging when:
- ✅ Project supports dual/multiple architectural approaches
- ✅ Need to indicate priority/recommendation between approaches
- ✅ Building documentation sites (Docusaurus, MkDocs, etc.)
- ✅ Require cross-referencing between equivalent implementations
- ✅ Need to filter/query documents by architecture approach

Do NOT use when:
- ❌ Project has single architecture only
- ❌ All documents apply equally to all approaches
- ❌ Metadata adds no value to documentation navigation

---

## 2. Metadata Structure Standards

### 2.1 YAML Frontmatter Format

All metadata must be placed at the start of the document in YAML frontmatter format:

```yaml
---
title: "DOC-XXX: Document Title"
tags:
  - tag1
  - tag2
custom_fields:
  field1: value1
  field2: value2
---
```

### 2.2 Required Fields

**All Documents:**
- `title`: Full document title including ID
- `tags`: Array of categorization tags

**Architecture-Specific Documents:**
- `custom_fields.architecture_approach`: Defines which architecture this document belongs to
- `custom_fields.priority`: Indicates recommendation level
- `custom_fields.development_status`: Current implementation status

### 2.3 Optional Fields

- `description`: Brief document summary (for SEO, navigation tooltips)
- `sidebar_label`: Abbreviated label for sidebar navigation
- `custom_fields.fallback_reference`: Link to fallback implementation
- `custom_fields.primary_alternative`: Link to recommended implementation
- `custom_fields.agent_id`: For AI Agent documents (AGENT-XXX)

---

## 2.4 How AI Assistants Use Metadata Tags

### Purpose

AI assistants (like Claude, Gemini, Copilot) use metadata tags to automatically:

1. **Recognize Document Type**: Determine if document is BRD, PRD, SPEC, ADR, etc.
2. **Understand Priority**: Identify recommended vs fallback approaches
3. **Follow Architecture Patterns**: Apply correct patterns for AI-agent vs traditional
4. **Validate Cross-References**: Check bidirectional links between primary/fallback
5. **Generate Appropriate Content**: Include correct admonitions and references
6. **Maintain Consistency**: Ensure metadata matches document content

### Tag-Specific AI Assistant Behavior

**When `ai-agent-primary` tag is present**, AI assistants will:
- ✅ Use AI/ML terminology and patterns
- ✅ Reference agent-to-agent communication (A2A Protocol)
- ✅ Include ML-specific requirements (training data, model endpoints, inference)
- ✅ Suggest AI-appropriate testing strategies (model validation, bias testing)
- ✅ Automatically add `:::recommended` admonition to key documents

**When `traditional-fallback` tag is present**, AI assistants will:
- ✅ Use traditional software architecture patterns
- ✅ Reference proven implementation approaches
- ✅ Include deterministic logic and rule-based systems
- ✅ Automatically add `:::fallback` admonition
- ✅ Link to primary (AI-agent) alternative

**When `priority: primary` field is set**, AI assistants will:
- ✅ Mark document as recommended approach
- ✅ Place higher in navigation hierarchy
- ✅ Set to expanded by default in documentation sites
- ✅ Include link to fallback alternative (if exists)

**When `priority: fallback` field is set**, AI assistants will:
- ✅ Mark document as reference implementation
- ✅ Set to collapsed by default in documentation sites
- ✅ Include prominent link to recommended alternative
- ✅ Add "use only if primary not viable" guidance

**When `agent_id: AGENT-XXX` field is present**, AI assistants will:
- ✅ Validate uniqueness across all documents
- ✅ Use agent ID in A2A Protocol references
- ✅ Include in traceability matrices
- ✅ Cross-reference with related agent documents

### Tag Processing Order

AI assistants process metadata in this order:

1. **Document Type Tags** (`feature-brd`, `platform-prd`, etc.)
   - Determine overall document structure
   - Select appropriate template
   - Identify required sections

2. **Architecture Tags** (`ai-agent-primary`, `traditional-fallback`, `shared-architecture`)
   - Select architectural patterns
   - Choose terminology (ML-based vs rule-based)
   - Determine technology recommendations

3. **Priority Tags** (`recommended-approach`, `reference-implementation`)
   - Apply visual hierarchy
   - Set default expansion state
   - Generate navigation metadata

4. **Feature Category Tags** (`fraud-detection`, `compliance`, etc.)
   - Enable cross-referencing
   - Support document filtering
   - Link related documents

### Validation Rules

AI assistants automatically validate:

| Check | Requirement | Error if Violated |
|-------|-------------|-------------------|
| Required Fields | `title`, `tags`, `priority`, `architecture_approach` present | ❌ Missing required field |
| Valid Priorities | Only `primary`, `fallback`, `shared`, `deprecated` | ❌ Invalid priority value |
| Tag Taxonomy | Tags follow standard categories | ⚠️ Non-standard tag (warning) |
| Bidirectional Refs | Primary ↔ fallback links exist | ❌ Orphan reference |
| Agent ID Format | `AGENT-XXX` (three digits) | ❌ Invalid format |
| Agent ID Unique | No duplicate agent IDs | ❌ Duplicate agent ID |

### Example: AI Assistant Workflow

**User Creates New Document:**
```markdown
---
title: "BRD-030: Payment Routing Agent"
tags:
  - feature-brd
  - ai-agent-primary
  - transaction-processing
  - recommended-approach
custom_fields:
  architecture_approach: ai-agent-based
  priority: primary
  development_status: active
  agent_id: AGENT-009
---
```

**AI Assistant Automatically:**
1. ✅ Recognizes this as a primary AI Agent BRD
2. ✅ Uses ML/AI terminology throughout
3. ✅ Adds `:::recommended` admonition
4. ✅ Validates AGENT-009 is unique
5. ✅ Checks if fallback reference needed
6. ✅ Suggests A2A Protocol integration points
7. ✅ Recommends ML-specific test strategies

---

## 3. Architecture Priority Taxonomy

### 3.1 Priority Levels

| Priority | Meaning | Visual Indicator | Use Case |
|----------|---------|------------------|----------|
| `primary` | Recommended approach | ✅ Green, expanded | AI Agent-based implementation (recommended) |
| `fallback` | secondary/reference option | ⚠️ Yellow, collapsed | Traditional implementation (use if primary not viable) |
| `shared` | Required by all approaches | ⚙️ Neutral | Platform requirements, shared infrastructure |
| `deprecated` | No longer recommended | ⛔ Red | Legacy documentation (archived) |

### 3.2 Development Status

| Status | Meaning | Indicator |
|--------|---------|-----------|
| `active` | Currently implemented/in development | ✅ |
| `reference` | Reference implementation only | 📖 |
| `planned` | Future implementation | 🔮 |
| `deprecated` | Legacy/archived | ⛔ |

---

## 4. Metadata Templates by Document Type

### 4.1 Primary (AI Agent) BRD

```yaml
---
title: "BRD-XXX: Feature Name (AI Agent-Based)"
tags:
  - feature-brd
  - ai-agent-primary
  - [feature-category]
  - recommended-approach
custom_fields:
  architecture_approach: ai-agent-based
  priority: primary
  development_status: active
  agent_id: AGENT-XXX
  fallback_reference: BRD-YYY
---
```

**Field Descriptions:**
- `agent_id`: Unique agent identifier (AGENT-001, AGENT-002, etc.)
- `fallback_reference`: Document ID of traditional equivalent (if exists)
- `feature-category`: Domain-specific tag (fraud-detection, compliance, customer-support, etc.)

### 4.2 Fallback (Traditional) BRD

```yaml
---
title: "BRD-XXX: Feature Name (Traditional)"
tags:
  - feature-brd
  - traditional-fallback
  - [feature-category]
  - reference-implementation
custom_fields:
  architecture_approach: traditional-8layer
  priority: fallback
  development_status: reference
  primary_alternative: BRD-YYY_descriptive_slug
---
```

**Field Descriptions:**
- `primary_alternative`: Full filename (without .md) of recommended AI Agent implementation

### 4.3 Shared Platform BRD

```yaml
---
title: "BRD-XXX: Platform Feature Name"
tags:
  - platform-brd
  - shared-architecture
  - required-both-approaches
custom_fields:
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  implementation_differs: false
  primary_implementation: ai-agent-based
---
```

**Field Descriptions:**
- `architecture_approaches`: Array of all applicable architectures
- `implementation_differs`: `true` if implementation varies by architecture, `false` if identical
- `primary_implementation`: Which architecture is preferred (even for shared docs)

### 4.4 Architecture Decision Record (ADR)

**Primary Architecture ADR:**
```yaml
---
title: "ADR-REF-XXX: Architecture Name"
tags:
  - architecture-adr
  - ai-agent-primary
  - recommended-approach
custom_fields:
  architecture_approach: ai-agent-based
  priority: primary
  development_status: active
  decision_status: recommended
---
```

**Fallback Architecture ADR:**
```yaml
---
title: "ADR-REF-XXX: Architecture Name"
tags:
  - architecture-adr
  - traditional-fallback
  - reference-implementation
custom_fields:
  architecture_approach: traditional-8layer
  priority: fallback
  development_status: reference
  decision_status: fallback
  primary_alternative: ADR-REF-YYY
---
```

**Comparison ADR:**
```yaml
---
title: "ADR-REF-XXX: Cost & Performance Analysis"
tags:
  - architecture-adr
  - comparison
  - cost-analysis
  - shared-architecture
custom_fields:
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  document_type: comparison
---
```

### 4.5 Product Requirements (PRD)

```yaml
---
title: "PRD-XXX: Feature Name"
tags:
  - product-requirements
  - [architecture-tag]
  - [feature-category]
custom_fields:
  architecture_approach: [approach-name]
  priority: [primary|fallback|shared]
  development_status: [active|reference|planned]
  source_brd: BRD-XXX
---
```

### 4.6 Technical Specifications (SPEC)

```yaml
---
title: "SPEC-XXX: Component Name"
tags:
  - technical-spec
  - [architecture-tag]
  - [component-category]
custom_fields:
  architecture_approach: [approach-name]
  priority: [primary|fallback|shared]
  development_status: [active|reference]
  source_req: REQ-XXX
  source_adr: ADR-XXX
---
```

---

## 5. Custom Admonitions

### 5.1 Recommended Approach Admonition

Use for primary/recommended implementations:

```markdown
:::recommended Primary Implementation (AI Agent-Based)
**Architecture**: AI Agent-Based Platform (@adr: ADR-REF-002)
**Priority**: ✅ Recommended approach
**Status**: Active development
**Agent ID**: AGENT-XXX

**Fallback Alternative**: If AI/ML capabilities not available, see [@brd: BRD-YYY](./BRD-YYY_name.md) for traditional implementation.

**Advantages of AI Agent Approach**:
- Advantage 1
- Advantage 2
- Advantage 3
:::
```

### 5.2 Fallback Approach Admonition

Use for fallback/reference implementations:

```markdown
:::fallback Fallback Implementation (Traditional 8-Layer)
**Architecture**: Traditional 8-Layer Platform (@adr: ADR-REF-001)
**Priority**: ⚠️ Fallback option (use only if AI approach not viable)
**Status**: Reference implementation

**Recommended Alternative**: [@brd: BRD-XXX - Feature Name](./BRD-XXX_name.md) (AI-powered, preferred approach)

**Use This Approach If**:
- AI/ML expertise not available on team
- Regulatory constraints prevent AI usage
- Budget constraints for AI infrastructure
- Risk-averse stakeholders require proven patterns
:::
```

### 5.3 Comparison Admonition

Use for comparative analysis documents:

```markdown
:::comparison Architecture Comparison
This document provides objective comparison between:
- **Primary**: AI Agent-Based Architecture (@adr: ADR-REF-002)
- **Fallback**: Traditional 8-Layer Architecture (@adr: ADR-REF-001)

**Decision Criteria**: [List key factors]
:::
```

---

## 6. Tag Taxonomy

### 6.1 Document Type Tags

| Tag | Purpose | Document Types |
|-----|---------|----------------|
| `feature-brd` | Feature-specific BRD | BRD-006 through BRD-029 |
| `platform-brd` | Platform/foundation BRD | BRD-001 through BRD-005 |
| `architecture-adr` | Architecture decision | ADR-REF-XXX |
| `product-requirements` | Product specs | PRD-XXX |
| `technical-spec` | Implementation specs | SPEC-XXX |

### 6.2 Architecture Approach Tags

| Tag | Meaning |
|-----|---------|
| `ai-agent-primary` | Primary AI Agent implementation |
| `traditional-fallback` | Traditional/fallback implementation |
| `shared-architecture` | Required by all approaches |
| `recommended-approach` | Recommended implementation path |
| `reference-implementation` | Reference/fallback only |

### 6.3 Feature Category Tags

Domain-specific tags for categorization:

**Financial Services:**
- `fraud-detection`
- `compliance`
- `kyc-kyb`
- `transaction-processing`
- `settlement-reconciliation`

**Operations:**
- `customer-support`
- `monitoring`
- `analytics-insights`
- `operations-monitoring`

**Infrastructure:**
- `fx-liquidity`
- `payment-orchestration`
- `notification-management`

### 6.4 Status Tags

| Tag | Meaning |
|-----|---------|
| `deprecated` | Document no longer recommended |
| `comparison` | Comparative analysis document |
| `required-both-approaches` | Needed by all architectures |

---

## 7. Cross-Referencing Standards

### 7.1 Bidirectional References

Primary and fallback implementations must cross-reference each other:

**Primary Document (BRD-022):**
```yaml
custom_fields:
  fallback_reference: BRD-016
```

**Fallback Document (BRD-016):**
```yaml
custom_fields:
  primary_alternative: BRD-022_fraud_detection_agent_ml_based_risk
```

### 7.2 Reference Format

**In Metadata:**
- Use document ID only: `BRD-016`
- Or full filename without extension: `BRD-022_fraud_detection_agent_ml_based_risk`

**In Admonitions:**
- Use full markdown link: `[@brd: BRD-022](./BRD-022_fraud_detection_agent_ml_based_risk.md)`

**In Document Body:**
- Use tag notation: `@brd: BRD-022`, `@adr: ADR-REF-002`

---

## 8. Documentation Site Integration

### 8.1 Docusaurus Configuration

**Custom Admonitions (`docusaurus.config.ts`):**

```typescript
docs: {
  admonitions: {
    keywords: ['recommended', 'fallback', 'comparison'],
    extendDefaults: true,
  },
}
```

**Custom Components (`src/theme/Admonition/Types.tsx`):**

```typescript
import DefaultAdmonitionTypes from '@theme-original/Admonition/Types';

function RecommendedAdmonition(props) {
  return (
    <div style={{
      border: '2px solid var(--ifm-color-success)',
      borderLeft: '6px solid var(--ifm-color-success)',
      padding: '1rem',
      backgroundColor: 'var(--ifm-alert-background-color)',
    }}>
      <h5 style={{ color: 'var(--ifm-color-success)' }}>
        ✅ {props.title || 'Recommended Approach'}
      </h5>
      <div>{props.children}</div>
    </div>
  );
}

const AdmonitionTypes = {
  ...DefaultAdmonitionTypes,
  'recommended': RecommendedAdmonition,
  'fallback': FallbackAdmonition,
};
```

### 8.2 Sidebar Visual Hierarchy

**Primary Architecture (Expanded):**
```typescript
{
  type: 'category',
  label: '🤖 AI Agent-Based Architecture (Recommended)',
  collapsed: false,  // Expanded by default
  className: 'primary-architecture',
  items: [...]
}
```

**Fallback Architecture (Collapsed):**
```typescript
{
  type: 'category',
  label: '🏗️ Traditional 8-Layer (Fallback/Reference)',
  collapsed: true,  // Collapsed by default
  className: 'fallback-architecture',
  items: [...]
}
```

**CSS Styling (`custom.css`):**
```css
.primary-architecture {
  border-left: 4px solid var(--ifm-color-success);
}

.primary-architecture > .menu__link {
  font-weight: 600;
}

.fallback-architecture {
  opacity: 0.85;
}
```

### 8.3 MkDocs Configuration

**Material Theme Tags:**
```yaml
# mkdocs.yml
plugins:
  - tags:
      tags_file: tags.md

markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences
```

**Custom Admonition CSS:**
```css
.admonition.recommended {
  border-left: 4px solid #00c851;
}

.admonition.fallback {
  border-left: 4px solid #ffbb33;
}
```

---

## 9. Validation & Quality Assurance

### 9.1 Metadata Validation Checklist

Before committing documents with metadata:

- [ ] YAML frontmatter valid syntax
- [ ] Required fields present (`title`, `tags`, `architecture_approach`, `priority`)
- [ ] Bidirectional cross-references correct (primary ↔ fallback)
- [ ] Tags follow taxonomy standards
- [ ] Agent IDs unique (for AI Agent documents)
- [ ] Custom admonitions present on key documents (BRD-022, BRD-016)
- [ ] Development status accurate
- [ ] Document ID in frontmatter matches filename

### 9.2 Automated Validation Script

```python
# scripts/validate_metadata.py
import yaml
import re
from pathlib import Path

def validate_metadata(file_path):
    """Validate YAML frontmatter metadata."""
    with open(file_path, 'r') as f:
        content = f.read()

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "No YAML frontmatter found"

    try:
        metadata = yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        return False, f"Invalid YAML: {e}"

    # Required fields
    required = ['title', 'tags']
    for field in required:
        if field not in metadata:
            return False, f"Missing required field: {field}"

    # Architecture-specific validation
    if 'custom_fields' in metadata:
        cf = metadata['custom_fields']

        if 'priority' in cf:
            valid_priorities = ['primary', 'fallback', 'shared', 'deprecated']
            if cf['priority'] not in valid_priorities:
                return False, f"Invalid priority: {cf['priority']}"

        # Check bidirectional references
        if cf.get('priority') == 'primary' and 'fallback_reference' not in cf:
            return False, "Primary document missing fallback_reference"

        if cf.get('priority') == 'fallback' and 'primary_alternative' not in cf:
            return False, "Fallback document missing primary_alternative"

    return True, "Valid"

# Usage
if __name__ == '__main__':
    import sys
    result, message = validate_metadata(sys.argv[1])
    print(f"{'✅' if result else '❌'} {message}")
    sys.exit(0 if result else 1)
```

### 9.3 Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validate metadata on BRD/ADR files
for file in $(git diff --cached --name-only | grep -E '(BRD|ADR)/.*\.md$'); do
  if [ -f "$file" ]; then
    python scripts/validate_metadata.py "$file"
    if [ $? -ne 0 ]; then
      echo "❌ Metadata validation failed for $file"
      exit 1
    fi
  fi
done

echo "✅ Metadata validation passed"
```

---

## 10. Migration Guide

### 10.1 Adding Metadata to Existing Documents

**Step 1: Identify Document Type**
- Is this a primary (recommended) implementation?
- Is this a fallback (reference) implementation?
- Is this shared across all architectures?

**Step 2: Select Template**
- Use templates from section 4

**Step 3: Add Frontmatter**
```markdown
---
[metadata here]
---

# Original Document Title
[rest of document]
```

**Step 4: Add Custom Admonition (if applicable)**
- Add after title for key documents
- Use templates from section 5

**Step 5: Update Cross-References**
- Ensure bidirectional references between primary/fallback

**Step 6: Validate**
- Run validation script
- Check document renders correctly

### 10.2 Bulk Migration Script

```bash
#!/bin/bash
# scripts/bulk_add_metadata.sh

# Add metadata to all AI Agent BRDs (BRD-022 to BRD-029)
for i in {022..029}; do
  file="docs/BRD/BRD-${i}_*.md"
  if [ -f $file ]; then
    # Insert frontmatter at beginning
    echo "Processing $file"
    # Implementation here
  fi
done
```

---

## 11. Best Practices

### 11.1 Do's

✅ **Do** use metadata for architectural differentiation
✅ **Do** maintain bidirectional cross-references
✅ **Do** keep metadata in sync between source and build locations
✅ **Do** validate metadata before committing
✅ **Do** use custom admonitions for visual clarity
✅ **Do** follow tag taxonomy consistently
✅ **Do** update metadata when document status changes

### 11.2 Don'ts

❌ **Don't** add metadata to source code files
❌ **Don't** use metadata when single architecture only
❌ **Don't** create orphan references (primary without fallback link)
❌ **Don't** mix architecture approaches in single document
❌ **Don't** use custom tag names outside taxonomy
❌ **Don't** skip validation steps

### 11.3 Common Pitfalls

**Pitfall 1: Inconsistent Frontmatter IDs**
- Problem: `id: ARCHITECTURE_GUIDE` but frontmatter has `id: architecture-guide`
- Solution: Use lowercase with hyphens consistently

**Pitfall 2: Missing Bidirectional References**
- Problem: BRD-022 references BRD-016, but BRD-016 doesn't reference BRD-022
- Solution: Always add both directions when creating pairs

**Pitfall 3: Invalid YAML Syntax**
- Problem: Tabs instead of spaces, unquoted special characters
- Solution: Use YAML validator, proper IDE settings

**Pitfall 4: Metadata Out of Sync**
- Problem: Source docs have metadata, docs-site doesn't (or vice versa)
- Solution: Maintain metadata in both locations, use sync scripts

---

## 12. Examples

### 12.1 Complete Example: AI Agent Fraud Detection BRD

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

**Fallback Alternative**: If AI/ML capabilities not available, see [@brd: BRD-016](./BRD-016_fraud_detection_risk_screening.md) for traditional implementation.

**Advantages of AI Agent Approach**:
- Adaptive ML-based fraud detection (vs static rules)
- Self-improving system with continuous learning
- 38.7% lower TCO compared to traditional approach
- Integrated via A2A Protocol with other agents
:::

## Document Control
[rest of document]
```

### 12.2 Complete Example: Traditional Fraud Detection BRD

```markdown
---
title: "BRD-016: Fraud Detection & Risk Screening (Traditional)"
tags:
  - feature-brd
  - traditional-fallback
  - fraud-detection
  - reference-implementation
custom_fields:
  architecture_approach: traditional-8layer
  priority: fallback
  development_status: reference
  primary_alternative: BRD-022_fraud_detection_agent_ml_based_risk
---

# BRD-016: Fraud Detection & Risk Screening

:::fallback Fallback Implementation (Traditional 8-Layer)
**Architecture**: Traditional 8-Layer Platform (@adr: ADR-REF-001)
**Priority**: ⚠️ Fallback option (use only if AI approach not viable)
**Status**: Reference implementation

**Recommended Alternative**: [@brd: BRD-022 - Fraud Detection Agent](./BRD-022_fraud_detection_agent_ml_based_risk.md) (AI-powered, preferred approach)

**Use This Approach If**:
- AI/ML expertise not available on team
- Regulatory constraints prevent AI usage
- Budget constraints for AI infrastructure
- Risk-averse stakeholders require proven patterns
:::

**Document ID**: BRD-016
[rest of document]
```

### 12.3 Complete Example: Shared Platform BRD

```markdown
---
title: "BRD-001: Platform Architecture & Technology Stack"
tags:
  - platform-brd
  - shared-architecture
  - required-both-approaches
custom_fields:
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  implementation_differs: false
  primary_implementation: ai-agent-based
---

# BRD-001: Platform Architecture & Technology Stack

## Document Control
[rest of document]
```

---

## 13. How to Define Metadata in Prompts to AI Assistants

### 13.1 Overview

When instructing AI assistants (Claude, Gemini, Copilot) to create or update documents, you can specify metadata tags using various prompt patterns. AI assistants understand both explicit YAML and natural language instructions.

### 13.2 Prompt Methods

#### Method 1: Direct Instruction (Recommended)

Explicitly specify metadata fields:

```
Create BRD-030: Payment Routing Agent using AI-agent metadata:
- priority: primary
- agent_id: AGENT-009
- architecture_approach: ai-agent-based
- category: transaction-processing
- development_status: active
- No traditional fallback exists
```

**AI Assistant Will Apply:**
```yaml
---
title: "BRD-030: Payment Routing Agent"
tags:
  - feature-brd
  - ai-agent-primary
  - transaction-processing
  - recommended-approach
custom_fields:
  architecture_approach: ai-agent-based
  priority: primary
  development_status: active
  agent_id: AGENT-009
  fallback_reference: null
---
```

#### Method 2: Shorthand Notation

AI assistants understand abbreviated instructions:

| Shorthand Phrase | AI Assistant Interprets As |
|------------------|----------------------------|
| "AI-agent primary" | `tags: [ai-agent-primary, recommended-approach]`<br>`priority: primary`<br>`architecture_approach: ai-agent-based` |
| "Traditional fallback" | `tags: [traditional-fallback, reference-implementation]`<br>`priority: fallback`<br>`architecture_approach: traditional-8layer` |
| "Shared platform" | `tags: [shared-architecture, required-both-approaches]`<br>`priority: shared`<br>`architecture_approaches: [ai-agent-based, traditional-8layer]` |
| "AGENT-009" | `agent_id: AGENT-009`<br>Validates uniqueness across documents |
| "Active development" | `development_status: active` |
| "Reference status" | `development_status: reference` |
| "Planned" | `development_status: planned` |

**Example Shorthand Prompt:**
```
Create an AI-agent primary BRD for risk scoring (AGENT-010, active)
```

**AI Assistant Applies Full Metadata:**
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

#### Method 3: Provide Complete YAML Frontmatter

Specify exact YAML structure in prompt:

```
Create BRD-030 with this metadata:

---
title: "BRD-030: Payment Routing Agent (Intelligent Optimization)"
tags:
  - feature-brd
  - ai-agent-primary
  - transaction-processing
  - recommended-approach
custom_fields:
  architecture_approach: ai-agent-based
  priority: primary
  development_status: active
  agent_id: AGENT-009
  fallback_reference: null
---
```

AI assistant will use this metadata exactly as specified.

#### Method 4: Reference Framework Templates

Point to specific template from this guide:

```
Use the "Primary (AI Agent) BRD" metadata template (section 4.1)
for BRD-030: Payment Routing Agent
```

AI assistant will look up template and apply appropriate metadata.

#### Method 5: Specify Cross-References

Define relationships to other documents:

```
Create BRD-030 as the AI-agent version with BRD-018 as its
traditional fallback alternative.
```

**AI Assistant Adds Bidirectional References:**
- BRD-030 (primary): `fallback_reference: BRD-018`
- BRD-018 (fallback): `primary_alternative: BRD-030_payment_routing_agent`

#### Method 6: Describe Document Characteristics

Use natural language description:

```
Create a new BRD for an AI agent that handles payment routing.
This should be:
- A primary/recommended implementation
- AI agent-based architecture
- Active development status
- Agent ID: AGENT-009
- No traditional fallback exists
- Category: transaction-processing
```

AI assistant translates to appropriate metadata tags.

#### Method 7: Bulk Operations

For multiple documents at once:

```
Apply AI-agent metadata to BRDs from BRD-030 to BRD-035:
- Use primary priority
- Agent IDs: AGENT-009 through AGENT-014
- All are transaction-processing category
- All active development status
- BRD-030 links to BRD-018 (fallback)
- Others have no fallback
```

#### Method 8: Update Existing Metadata

For modifying existing documents:

```
Update BRD-025 metadata:
- Change development_status from "planned" to "active"
- Add fallback_reference: BRD-020
- Update the recommended admonition to reflect active status
```

### 13.3 Keyword-Triggered Behaviors

AI assistants automatically apply specific behaviors when they detect certain keywords:

#### "AI-agent" or "ai-agent-primary" Keyword

**Triggers:**
- ✅ Add `ai-agent-primary` tag
- ✅ Add `recommended-approach` tag
- ✅ Set `priority: primary`
- ✅ Set `architecture_approach: ai-agent-based`
- ✅ Use ML/AI terminology throughout document
- ✅ Reference A2A Protocol for agent communication
- ✅ Include ML-specific requirements (training data, model endpoints)
- ✅ Add `:::recommended` admonition to key documents
- ✅ Suggest AI-appropriate testing strategies

#### "Traditional" or "fallback" Keyword

**Triggers:**
- ✅ Add `traditional-fallback` tag
- ✅ Add `reference-implementation` tag
- ✅ Set `priority: fallback`
- ✅ Set `architecture_approach: traditional-8layer`
- ✅ Use traditional software architecture patterns
- ✅ Reference proven implementation approaches
- ✅ Add `:::fallback` admonition
- ✅ Include link to primary (AI-agent) alternative
- ✅ Add "use only if primary not viable" guidance

#### "Shared" or "platform" Keyword

**Triggers:**
- ✅ Add `shared-architecture` tag
- ✅ Add `required-both-approaches` tag
- ✅ Set `priority: shared`
- ✅ Set `architecture_approaches: [ai-agent-based, traditional-8layer]`
- ✅ Note which approach is primary implementation
- ✅ Indicate if implementation differs between approaches

#### "Agent ID: AGENT-XXX" Pattern

**Triggers:**
- ✅ Add `agent_id: AGENT-XXX` field
- ✅ Validate format (AGENT-XXX with three digits)
- ✅ Check uniqueness across all documents
- ✅ Use agent ID in A2A Protocol references
- ✅ Include in traceability matrices
- ✅ Cross-reference with related agent documents

### 13.4 Common Prompt Patterns

#### Pattern 1: New AI Agent Feature (No Traditional Equivalent)

**Prompt:**
```
Create AI-agent BRD for fraud detection using ML-based risk scoring
(AGENT-011, active development, no traditional fallback)
```

**Applied Metadata:**
```yaml
tags:
  - feature-brd
  - ai-agent-primary
  - fraud-detection
  - recommended-approach
custom_fields:
  architecture_approach: ai-agent-based
  priority: primary
  development_status: active
  agent_id: AGENT-011
  fallback_reference: null
```

#### Pattern 2: Traditional Fallback Implementation

**Prompt:**
```
Create traditional fallback version of BRD-030 (reference implementation status)
```

**Applied Metadata:**
```yaml
tags:
  - feature-brd
  - traditional-fallback
  - transaction-processing
  - reference-implementation
custom_fields:
  architecture_approach: traditional-8layer
  priority: fallback
  development_status: reference
  primary_alternative: BRD-030_payment_routing_agent
```

#### Pattern 3: Shared Platform Requirement

**Prompt:**
```
Create shared platform BRD for API Gateway infrastructure
(applies to both AI-agent and traditional architectures, active)
```

**Applied Metadata:**
```yaml
tags:
  - platform-brd
  - shared-architecture
  - required-both-approaches
custom_fields:
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  implementation_differs: false
  primary_implementation: ai-agent-based
  development_status: active
```

#### Pattern 4: Update Existing Document

**Prompt:**
```
Update BRD-025:
- Change development_status to "active"
- Add fallback_reference: BRD-020
- Update admonition to reflect active development
```

**Applied Changes:**
```yaml
# Before
custom_fields:
  development_status: planned

# After
custom_fields:
  development_status: active
  fallback_reference: BRD-020
```

### 13.5 Template Reference Shortcuts

You can reference templates from section 4 directly in prompts:

| Prompt Reference | Template Applied |
|------------------|------------------|
| "Use Primary AI Agent BRD template" | section 4.1 template |
| "Use Fallback Traditional BRD template" | section 4.2 template |
| "Use Shared Platform BRD template" | section 4.3 template |
| "Use Primary ADR template" | section 4.4 template |
| "Use PRD template" | section 4.6 template |

**Example:**
```
Create BRD-031 using the Primary AI Agent BRD template from section 4.1
```

### 13.6 Validation in Prompts

You can request validation in your prompt:

```
Create BRD-030 as AI-agent primary (AGENT-009) and validate:
- Agent ID uniqueness
- Bidirectional references if fallback exists
- YAML syntax correctness
- Tag taxonomy compliance
```

AI assistant will automatically perform these checks after creating the document.

### 13.7 Best Practices for Prompts

1. **Be Explicit About Priority**: Always specify if it's primary, fallback, or shared
2. **Mention Agent ID Early**: For AI-agent docs, state the agent ID upfront
3. **Specify Cross-References**: Mention if there's a fallback or primary alternative
4. **State Development Status**: Indicate if active, planned, reference, or deprecated
5. **Use Category Tags**: Mention the functional domain (fraud-detection, compliance, etc.)
6. **Request Admonitions**: Ask for `:::recommended` or `:::fallback` admonitions explicitly
7. **Validate After Creation**: Request validation checks in the same prompt

### 13.8 Anti-Patterns (Avoid These)

**❌ Ambiguous Priority:**
```
Create a BRD for payment routing
```
*Problem: AI assistant doesn't know if this is primary, fallback, or shared*

**✅ Clear Priority:**
```
Create an AI-agent primary BRD for payment routing (AGENT-009)
```

---

**❌ Missing Agent ID:**
```
Create AI-agent BRD for fraud detection
```
*Problem: No agent ID specified for agent-specific document*

**✅ With Agent ID:**
```
Create AI-agent BRD for fraud detection (AGENT-011, active)
```

---

**❌ Incomplete Cross-Reference:**
```
Create BRD-030 with a fallback version
```
*Problem: Fallback version not identified*

**✅ Complete Cross-Reference:**
```
Create BRD-030 (AI-agent primary) with BRD-018 as traditional fallback
```

### 13.9 Examples: Complete Prompt Workflows

#### Example 1: Create AI Agent Document with Full Context

**Prompt:**
```
Create BRD-031: Risk Scoring Agent (Real-time Assessment)

Metadata requirements:
- AI-agent primary implementation
- Agent ID: AGENT-010
- Category: fraud-detection
- Active development status
- No traditional fallback exists

Content requirements:
- Include recommended admonition
- Explain ML-based risk scoring advantages
- Reference A2A Protocol integration with AGENT-001 (Fraud Detection)
- Include ML model requirements (training data, inference endpoints)
```

**AI Assistant Creates:**
- Complete YAML frontmatter with all metadata
- `:::recommended` admonition with advantages
- A2A Protocol references
- ML-specific requirements sections
- Validates agent ID uniqueness

#### Example 2: Create Document Pair (Primary + Fallback)

**Prompt:**
```
Create document pair for customer onboarding:

1. BRD-032: Customer Onboarding Agent (AI-agent primary, AGENT-011, active)
2. BRD-033: Customer Onboarding Workflow (traditional fallback, reference)

Establish bidirectional cross-references between them.
```

**AI Assistant Creates:**
- BRD-032 with `fallback_reference: BRD-033`
- BRD-033 with `primary_alternative: BRD-032_customer_onboarding_agent`
- Appropriate admonitions on both documents
- Validates cross-references are correct

#### Example 3: Bulk Metadata Update

**Prompt:**
```
Update all BRDs from BRD-022 to BRD-029:
- Change development_status from "planned" to "active"
- Ensure all have recommended admonitions
- Validate all agent IDs are unique
```

**AI Assistant:**
- Updates metadata for 8 documents
- Adds admonitions where missing
- Validates agent ID uniqueness
- Reports any conflicts or issues

---

## 14. Tool Integration

### 14.1 IDE Support

**VS Code Settings (`.vscode/settings.json`):**
```json
{
  "yaml.schemas": {
    "schemas/metadata-schema.json": "docs/**/*.md"
  },
  "yaml.validate": true,
  "yaml.format.enable": true
}
```

**JSON Schema (`schemas/metadata-schema.json`):**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["title", "tags"],
  "properties": {
    "title": { "type": "string" },
    "tags": {
      "type": "array",
      "items": { "type": "string" }
    },
    "custom_fields": {
      "type": "object",
      "properties": {
        "architecture_approach": {
          "enum": ["ai-agent-based", "traditional-8layer"]
        },
        "priority": {
          "enum": ["primary", "fallback", "shared", "deprecated"]
        },
        "development_status": {
          "enum": ["active", "reference", "planned", "deprecated"]
        }
      }
    }
  }
}
```

### 13.2 Query & Filtering

**List all primary (recommended) BRDs:**
```bash
grep -l "priority: primary" docs/BRD/*.md
```

**Find all AI Agent documents:**
```bash
grep -l "ai-agent-primary" docs/BRD/*.md
```

**Extract all agent IDs:**
```bash
grep "agent_id:" docs/BRD/*.md | sed 's/.*agent_id: //'
```

**Python query script:**
```python
import yaml
import re
from pathlib import Path

def query_metadata(docs_dir, filters):
    """Query documents by metadata filters."""
    results = []

    for md_file in Path(docs_dir).glob('**/*.md'):
        with open(md_file, 'r') as f:
            content = f.read()

        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            continue

        metadata = yaml.safe_load(match.group(1))

        # Check filters
        match = True
        for key, value in filters.items():
            if '.' in key:  # Nested field
                parts = key.split('.')
                val = metadata
                for part in parts:
                    val = val.get(part, {})
                if val != value:
                    match = False
            else:
                if metadata.get(key) != value:
                    match = False

        if match:
            results.append(md_file)

    return results

# Usage
primary_docs = query_metadata('docs/BRD', {
    'custom_fields.priority': 'primary'
})
```

---

## 14. Troubleshooting

### 14.1 Build Errors

**Error: "Invalid sidebar document ID"**
- Cause: Document ID in sidebar doesn't match frontmatter `id`
- Fix: Ensure frontmatter `id` matches sidebar reference (use lowercase with hyphens)

**Error: "YAML parsing error"**
- Cause: Invalid YAML syntax in frontmatter
- Fix: Check for tabs vs spaces, unquoted special characters, proper indentation

**Error: "Admonition not rendering"**
- Cause: Custom admonition not registered in config
- Fix: Add to `docusaurus.config.ts` admonitions keywords

### 14.2 Reference Issues

**Broken cross-references**
- Cause: Referenced document ID doesn't exist
- Fix: Verify document exists, check filename matches reference

**One-way references**
- Cause: Primary references fallback, but fallback doesn't reference primary
- Fix: Add bidirectional references in both documents

### 14.3 Sync Issues

**Metadata out of sync between source and docs-site**
- Cause: Changes made to one location but not the other
- Fix: Use sync script, maintain both locations, verify with diff

---

## 15. References

### 15.1 Related Documentation

- `ID_NAMING_STANDARDS.md` - Document naming conventions
- `AI_ASSISTANT_RULES.md` - AI assistant guidelines
- `TOOL_OPTIMIZATION_GUIDE.md` - Tool-specific optimization
- `COMPLETE_TAGGING_EXAMPLE.md` - Traceability tagging examples

### 15.2 External Resources

- [YAML Specification](https://yaml.org/spec/1.2/spec.html)
- [Docusaurus Frontmatter](https://docusaurus.io/docs/api/plugins/@docusaurus/plugin-content-docs#markdown-front-matter)
- [MkDocs Material Tags](https://squidfunk.github.io/mkdocs-material/setup/setting-up-tags/)
- [JSON Schema](https://json-schema.org/)

### 15.3 Changelog

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-23 | AI Agent | Initial metadata tagging guide creation |

---

**Questions or Issues?** Open an issue or contact the framework maintainers.
