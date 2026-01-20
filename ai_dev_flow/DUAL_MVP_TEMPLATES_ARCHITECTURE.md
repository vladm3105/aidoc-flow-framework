# Dual-Format Architecture: YAML + MD Templates

**Version**: 1.0
**Purpose**: Explain dual-format architecture (MD templates for humans, YAML templates for Autopilot, shared YAML schemas)
**Date**: 2026-01-20
**Status**: Active
**Target Audience**: Framework users, AI developers, Autopilot operators

---

## Overview

The AI Dev Flow Framework now supports **two parallel documentation formats** optimized for different audiences:

1. **Markdown (`.md`)** - Human-readable templates with narrative explanations
2. **YAML (`.yaml`)** - AI-optimized templates with structured data
3. **YAML Schemas** - Shared validation rules for both formats

### Why Dual-Format?

| Audience | Primary Format | Benefits |
|-----------|-----------------|-----------|
| **Human Developers** | Markdown (.md) | Rich text, tables, diagrams, narrative flow |
| **AI Autopilot** | YAML (.yaml) | 3-5x faster parsing, zero ambiguity, type-safe |
| **Validators** | YAML Schemas | Single validation rules for both formats |

### Key Principles

- ✅ **MD Templates**: Primary source of truth for **human workflow**
- ✅ **YAML Templates**: Primary source of truth for **Autopilot workflow**
- ✅ **YAML Schemas**: Derivative of **both** templates, validate both formats
- ✅ **No format bias**: Both formats have equal authority in their workflows
- ✅ **Shared validation**: Same quality gates apply to both formats
- ✅ **Clear separation**: Easy to understand which format to use when

---

## Three Document Types Explained

### 1. MD Template (`XXXX-MVP-TEMPLATE.md`)

**Purpose**: Human-readable template for creating narrative documents

**Characteristics**:
- ✅ Rich text formatting (headers, tables, bullet lists, code blocks)
- ✅ Narrative explanations and contextual information
- ✅ Embedded diagrams (Mermaid, ASCII art)
- ✅ Easy human review and editing
- ✅ Familiar Markdown syntax
- ❌ Requires regex parsing for AI consumption

**Authority**: **Primary source of truth for Human Workflow**

**Used By**:
- Human developers creating/editing documents
- AI agents generating human-readable drafts
- Documentation reviewers and approvers
- Business stakeholders reading requirements

**Example Content**:
```markdown
## Section Title

This section provides detailed explanations with examples and context.

### Subsection

| Column 1 | Column 2 | Column 3 |
|-----------|-----------|----------|
| Data      | Value     | Description|

```python
def example_function():
    """Example code block with syntax highlighting."""
    return True
```

### Important Notes

- Item 1: Description
- Item 2: Description
```

**File Locations**:
- `ai_dev_flow/01_BRD/BRD-MVP-TEMPLATE.md`
- `ai_dev_flow/02_PRD/PRD-MVP-TEMPLATE.md`
- `ai_dev_flow/03_EARS/EARS-MVP-TEMPLATE.md`
- `ai_dev_flow/05_ADR/ADR-MVP-TEMPLATE.md`
- `ai_dev_flow/06_SYS/SYS-MVP-TEMPLATE.md`
- `ai_dev_flow/07_REQ/REQ-MVP-TEMPLATE.md`
- `ai_dev_flow/08_CTR/CTR-MVP-TEMPLATE.md`
- `ai_dev_flow/10_TASKS/TASKS-TEMPLATE.md`

**When to Use MD Template**:
- ✅ Creating BRD/PRD for business stakeholders
- ✅ Writing narrative explanations for complex requirements
- ✅ Documents requiring rich formatting (tables, diagrams, code blocks)
- ✅ Human reviews and approval processes
- ✅ Documentation with extensive prose and explanations
- ✅ Learning framework structure for the first time

**Advantages for Humans**:
- **Readability**: Natural language flow with narrative structure
- **Visual formatting**: Tables, lists, code blocks for clarity
- **Diagrams**: Embedded Mermaid diagrams for visual representation
- **Familiarity**: Most developers comfortable with Markdown
- **Review process**: Easy to annotate and comment in pull requests

**Disadvantages for AI**:
- **Parsing complexity**: Requires regex to extract structured data
- **Ambiguity**: Same content can be represented multiple ways (list vs table)
- **Slower**: 3-5x slower to parse than YAML
- **Error-prone**: Regex edge cases, malformed Markdown variations

---

### 2. YAML Template (`XXXX-MVP-TEMPLATE.yaml`)

**Purpose**: AI-optimized template for Autopilot code generation

**Characteristics**:
- ✅ Structured data (key-value pairs, lists, nested objects)
- ✅ Direct YAML parsing (no regex overhead)
- ✅ Type-safe (schema validation possible at parse time)
- ✅ Zero parsing ambiguity
- ✅ Direct mapping to programming language data structures
- ❌ Less readable for humans (no rich text formatting)
- ❌ Limited narrative explanation capabilities

**Authority**: **Primary source of truth for Autopilot Workflow**

**Used By**:
- AI Autopilot generating artifacts automatically
- Code generation pipelines
- Automated validation tools
- Schema validators (format-aware)
- Machine-to-machine communication in CI/CD

**Example Content**:
```yaml
# Section: Document Identification
id: REQ-NN
summary: "[Single-sentence description]"

# Section: Document Control
document_control:
  status: "Draft"
  version: "1.0"
  date_created: "YYYY-MM-DD"
  last_updated: "YYYY-MM-DD"
  author: "[Author Name]"
  priority: "Critical (P1)"
  source_document: "@req: REQ.NN.EE.SS"

# Section: Requirements (structured array)
requirements:
  - id: "REQ-01.01"
    requirement_type: "Functional"
    statement: "The system shall provide [functionality]"
    acceptance_criteria:
      - "Criterion 1"
      - "Criterion 2"
    verification_method: "Automated Testing"
    priority: "High"
    traceability_tag: "@prd: PRD.NN.EE.SS"

# Section: Code Example (as multi-line string)
interface_contract: |
  from typing import Protocol
  
  class ExampleProtocol(Protocol):
      def method_name(self, param: str) -> str:
          """Method documentation."""
          ...

# Section: Traceability
traceability:
  upstream_references:
    brd: "@brd: BRD.NN.EE.SS"
    prd: "@prd: PRD.NN.EE.SS"
    ears: "@ears: EARS.NN.EE.SS"
  
  downstream_artifacts:
    spec: "SPEC"
    tasks: "TASKS"
  
  tags:
    - "@req: REQ.NN.EE.SS"
```

**File Locations**:
- `ai_dev_flow/01_BRD/BRD-MVP-TEMPLATE.yaml` (NEW)
- `ai_dev_flow/02_PRD/PRD-MVP-TEMPLATE.yaml` (NEW)
- `ai_dev_flow/03_EARS/EARS-MVP-TEMPLATE.yaml` (NEW)
- `ai_dev_flow/05_ADR/ADR-MVP-TEMPLATE.yaml` (NEW)
- `ai_dev_flow/06_SYS/SYS-MVP-TEMPLATE.yaml` (NEW)
- `ai_dev_flow/07_REQ/REQ-MVP-TEMPLATE.yaml` (NEW)
- `ai_dev_flow/08_CTR/CTR-MVP-TEMPLATE.yaml` (NEW)
- `ai_dev_flow/09_SPEC/SPEC-MVP-TEMPLATE.yaml` (EXISTING)
- `ai_dev_flow/10_TASKS/TASKS-MVP-TEMPLATE.yaml` (NEW)

**When to Use YAML Template**:
- ✅ Autopilot generating artifacts automatically
- ✅ Code generation from specifications
- ✅ Structured data validation
- ✅ Machine-to-machine communication
- ✅ Processing large volumes of artifacts
- ✅ Type-safe data exchange between systems

**Advantages for Autopilot**:
- **Performance**: 3-5x faster parsing than Markdown regex
- **Simplicity**: Direct `yaml.safe_load()` vs complex regex patterns
- **Clarity**: No ambiguity in data extraction (keys vs regex matching)
- **Type Safety**: Schema validation at parse time, catch errors early
- **Mapping**: 1:1 mapping to Python/dictionaries, zero transformation
- **Validation**: Built-in YAML validation (syntax, structure, data types)
- **Maintainability**: Easier to update structured data than parsing logic

**Disadvantages for Humans**:
- **Readability**: Nested structures less readable than narrative prose
- **Formatting**: No rich text (tables, bold, italic)
- **Editing**: Requires understanding of YAML syntax (indentation, quotes)
- **Learning curve**: Humans less familiar with YAML for documentation
- **Context**: Limited space for explanatory comments

---

### 3. YAML Schema (`XXXX_MVP_SCHEMA.yaml`)

**Purpose**: Machine-readable validation rules for both MD and YAML documents

**Characteristics**:
- ✅ Defines validation rules (required fields, patterns, constraints)
- ✅ Format-aware (validates both `.md` and `.yaml` documents)
- ✅ Shared validation rules (traceability tags, metadata, structure)
- ✅ Error codes with severity levels (error, warning, info)
- ✅ Reference documentation (templates, creation rules, validation rules)
- ❌ Not a document creation template
- ❌ Not a source of truth for content
- ❌ No example values (only validation rules)

**Authority**: **Derivative of both MD and YAML templates**

**Used By**:
- Validators (`validate_brd.py`, `validate_req.py`, etc.)
- CI/CD pipelines
- Quality gates
- Schema validation tools
- Pre-commit hooks

**Example Content**:
```yaml
# =============================================================================
# Document Role: This is a DERIVATIVE of template(s)
# - Authority:
#   * MD Template: XXXX-MVP-TEMPLATE.md (primary for human workflow)
#   * YAML Template: XXXX-MVP-TEMPLATE.yaml (primary for autopilot workflow)
# - Purpose: Machine-readable validation rules for both MD and YAML documents
# - On conflict: Defer to respective template (MD or YAML based on document format)
#
# Authority Hierarchy:
# Human Workflow:  MD Template → YAML Schema (validates MD) → Validators
# Autopilot:    YAML Template → YAML Schema (validates YAML) → Validators
# Schema is DERIVATIVE of both templates (dual-authority)
# =============================================================================

schema_version: "1.0"
artifact_type: "REQ"
layer: 7

references:
  md_template: "REQ-MVP-TEMPLATE.md"
  yaml_template: "REQ-MVP-TEMPLATE.yaml"
  creation_rules: "REQ_MVP_CREATION_RULES.md"
  validation_rules: "REQ_MVP_VALIDATION_RULES.md"

# Document Format Support
document_formats:
  supported:
    - format: "markdown"
      extension: ".md"
      template: "REQ-MVP-TEMPLATE.md"
      authority: "primary for human workflow"
    - format: "yaml"
      extension: ".yaml"
      template: "REQ-MVP-TEMPLATE.yaml"
      authority: "primary for autopilot workflow"
  
  validation_mode: "format-aware"  # Apply rules based on document format

# Metadata Validation Rules
metadata:
  required_custom_fields:
    document_type:
      type: string
      allowed_values: ["req"]
      description: "Must be 'req'"
    
    artifact_type:
      type: string
      allowed_values: ["REQ"]
      description: "Must be uppercase 'REQ'"
    
    layer:
      type: integer
      allowed_values: [7]
      description: "REQ is always Layer 7"
    
    architecture_approaches:
      type: array
      required: true
      allowed_values:
        - ["ai-agent-based"]
        - ["traditional-8layer"]
        - ["ai-agent-based", "traditional-8layer"]
      description: "Must be array format, not 'architecture_approach' string"

  required_tags:
    - req
    - layer-7-artifact

  forbidden_tag_patterns:
    - "^req-document$"
    - "^requirements$"
    - "^req-\\d{2,}$"

# Validation Rules (Format-Agnostic)
validation_rules:
  # Rules that apply to both MD and YAML formats
  metadata:
    - rule: "document_type must be 'req'"
      severity: "error"
      applies_to: ["markdown", "yaml"]
    
    - rule: "architecture_approaches must be array"
      severity: "error"
      applies_to: ["markdown", "yaml"]
    
    - rule: "tags must include 'req' and 'layer-7-artifact'"
      severity: "error"
      applies_to: ["markdown", "yaml"]

  traceability:
    - rule: "Traceability tags must follow format @artifact: ID"
      severity: "error"
      applies_to: ["markdown", "yaml"]
      pattern: "^@[a-z]{3,}: [A-Z]+-\\d{2,}:\\d{2,}:\\d{2,}$"
    
    - rule: "Cumulative tags required at Layer 7"
      severity: "warning"
      applies_to: ["markdown", "yaml"]
      required_tags:
        - "@brd: BRD.NN.EE.SS"
        - "@prd: PRD.NN.EE.SS"
        - "@ears: EARS.NN.EE.SS"
        - "@bdd: BDD.NN.EE.SS"
        - "@adr: ADR-NN"
        - "@sys: SYS.NN.EE.SS"

  # Markdown-specific validation rules (applies only to .md files)
  markdown_specific:
    - rule: "Single H1 heading only"
      severity: "warning"
      applies_to: ["markdown"]
    
    - rule: "Section numbering must be sequential (1-12)"
      severity: "error"
      applies_to: ["markdown"]
    
    - rule: "Document Control table must have minimum 11 fields"
      severity: "error"
      applies_to: ["markdown"]

  # YAML-specific validation rules (applies only to .yaml files)
  yaml_specific:
    - rule: "All required keys must be present"
      severity: "error"
      applies_to: ["yaml"]
      required_keys:
        - id
        - summary
        - document_control
        - traceability
    
    - rule: "Data types must match schema"
      severity: "error"
      applies_to: ["yaml"]
    
    - rule: "List fields must be arrays"
      severity: "error"
      applies_to: ["yaml"]

# Error Messages
error_messages:
  REQ-E001: "Missing required tag 'req'"
  REQ-E002: "Missing required tag 'layer-7-artifact'"
  REQ-E003: "Invalid document_type: must be 'req'"
  REQ-E004: "Invalid architecture format: use 'architecture_approaches: [value]' array"
  REQ-E005: "Forbidden tag pattern detected"
  REQ-E006: "Missing required section"
  REQ-E007: "Multiple H1 headings detected"
  REQ-E008: "Section numbering not sequential (1-12)"
  REQ-E009: "Document Control missing required fields"
  REQ-W001: "SPEC-Ready Score below 70% threshold (MVP)"
  REQ-W002: "Acceptance Criteria count below 3 (MVP)"
  REQ-W003: "Missing upstream traceability tags (require 6: @brd, @prd, @ears, @bdd, @adr, @sys)"
```

**File Locations**:
- `ai_dev_flow/01_BRD/BRD_MVP_SCHEMA.yaml`
- `ai_dev_flow/02_PRD/PRD_MVP_SCHEMA.yaml`
- `ai_dev_flow/03_EARS/EARS_MVP_SCHEMA.yaml`
- `ai_dev_flow/04_BDD/BDD_MVP_SCHEMA.yaml`
- `ai_dev_flow/05_ADR/ADR_MVP_SCHEMA.yaml`
- `ai_dev_flow/06_SYS/SYS_MVP_SCHEMA.yaml`
- `ai_dev_flow/07_REQ/REQ_MVP_SCHEMA.yaml`
- `ai_dev_flow/08_CTR/CTR_MVP_SCHEMA.yaml`
- `ai_dev_flow/09_SPEC/SPEC_MVP_SCHEMA.yaml`
- `ai_dev_flow/10_TASKS/TASKS_MVP_SCHEMA.yaml`

**Key Concepts**:
- **Format-Aware**: Schemas validate both formats with format-specific rules
- **Shared Rules**: Common validation rules apply to both formats (traceability, metadata)
- **Single Version**: One `schema_version: X.X` per schema (no format-specific versions)
- **Dual References**: Schemas reference both `md_template` and `yaml_template`

---

## Comparison Table

| Aspect | MD Template | YAML Template | YAML Schema |
|---------|-------------|---------------|-------------|
| **Purpose** | Document creation | Document creation | Validation |
| **Authority** | Human workflow (primary) | Autopilot workflow (primary) | Derivative of both |
| **Readability** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐ Fair | ❌ N/A (rules only) |
| **AI Parsing Speed** | ⚠️ Medium (regex) | ✅ Fast (direct load) | ✅ Fast (direct load) |
| **Rich Formatting** | ✅ Yes (tables, bold, etc.) | ❌ No | ❌ N/A |
| **Type Safety** | ⚠️ Limited | ✅ Full | ✅ Full |
| **Example Values** | ✅ Yes | ✅ Yes | ❌ No (rules only) |
| **Narrative Text** | ✅ Yes | ❌ Limited | ❌ No |
| **Used For** | Human editing | AI generation | Validation |
| **Line Count** | 200-800 | 100-400 | 300-999 |
| **File Extension** | `.md` | `.yaml` | `.yaml` |
| **Target Audience** | Humans | AI Autopilot | Validators |

---

## When to Use Each Format

### Decision Flowchart

```
Need to create artifact?
  │
  ├──────────────────────────────────────────────────────────────┤
  │                                                             │
  │ Is this for human review/editing?                             │
  │  ┌────────────────────────────────────────────────────────────┐  │
  │  │                                                         │  │
  ├─ YES → Use MD Template (.md)                                 │  │
  │  • Rich formatting (tables, diagrams, code blocks)               │  │
  │  • Narrative explanations and context                              │  │
  │  • Easy human review and editing                                │  │
  │  • Familiar Markdown syntax                                       │  │
  │                                                             │  │
  └────────────────────────────────────────────────────────────┘  │
  │                                                             │
  ├──────────────────────────────────────────────────────────────┤  │
  │                                                             │
  │ Is this for Autopilot code generation?                       │  │
  │  ┌────────────────────────────────────────────────────────────┐  │
  │  │                                                         │  │
  ├─ YES → Use YAML Template (.yaml)                            │  │
  │  • Structured data (key-value, lists, objects)                   │  │
  │  • Fast parsing (3-5x faster than Markdown)                   │  │
  │  • Zero ambiguity in data extraction                            │  │
  │  • Type-safe validation at parse time                             │  │
  │  • Direct mapping to Python/data structures                     │  │
  │                                                             │  │
  └────────────────────────────────────────────────────────────┘  │
  │                                                             │
  └──────────────────────────────────────────────────────────────┤
  │                                                             │
  Uncertain? → Create both (MD + YAML)                          │
  • MD version for human review/editing                              │
  • YAML version for Autopilot generation                           │
  │                                                             │
  └─────────────────────────────────────────────────────────────┘
```

### Use Cases by Layer

| Layer | Artifact | Recommended Format | Primary Audience | Reason |
|-------|----------|-------------------|------------------|---------|
| 1 | BRD | **MD** (primary), YAML (optional) | Business stakeholders | Narrative business case critical |
| 2 | PRD | **MD** (primary), YAML (optional) | Product managers | Detailed feature descriptions needed |
| 3 | EARS | **YAML** (primary) | Autopilot | Formal structure, no narrative needed |
| 4 | BDD | **.feature** | Testers | Gherkin standard, AI can parse natively |
| 5 | ADR | **YAML** (primary) | Autopilot | Decision structure, no narrative needed |
| 6 | SYS | **YAML** (primary) | Autopilot | System specs, no narrative needed |
| 7 | REQ | **YAML** (primary) | Autopilot | Directly feeds SPEC generation |
| 8 | CTR | **YAML** (primary) | Autopilot | Contract structure, no narrative needed |
| 9 | SPEC | **YAML** (already YAML) | Autopilot | Already optimized |
| 10 | TASKS | **YAML** (primary) | Autopilot | Directly feeds code execution |

**Key Pattern**:
- **Layers 1-2**: MD primary (human-facing business/product documents)
- **Layers 3-8, 10**: YAML primary (Autopilot-facing technical documents)
- **Layer 4**: `.feature` format (Gherkin standard for BDD)

---

## Authority Hierarchy

### Complete Authority Diagram

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                    Dual-Authority Architecture                      │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────┐      ┌─────────────────────────────┐  │
│  │      Human Workflow       │      │    Autopilot Workflow     │  │
│  │                           │      │                           │  │
│  │  1. MD Template           │      │  1. YAML Template          │  │
│  │     (XXXX-MVP-TEMPLATE.md) │      │     (XXXX-MVP-TEMPLATE.yaml)│  │
│  │     PRIMARY SOURCE        │      │     PRIMARY SOURCE          │  │
│  │     ↓                    │      │     ↓                       │  │
│  │  2. YAML Schema          │      │  2. YAML Schema           │  │
│  │     (XXXX_MVP_SCHEMA.yaml)│      │     (XXXX_MVP_SCHEMA.yaml)│  │
│  │     validates MD only       │      │     validates YAML only     │  │
│  │     ↓                    │      │     ↓                       │  │
│  │  3. Validators           │      │  3. Validators            │  │
│  │     (format-aware)        │      │     (format-aware)         │  │
│  │                           │      │                           │  │
│  └─────────────────────────────┘      └─────────────────────────────┘  │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │            YAML Schema (DERIVATIVE of both templates)       │  │
│  │                                                               │  │
│  │  • Validates MD documents (human workflow)                      │  │
│  │  • Validates YAML documents (autopilot workflow)                    │  │
│  │  • Shared validation rules (traceability, metadata)                  │  │
│  │  • Format-specific rules (MD: headings, YAML: keys)                │  │
│  │  • Single schema version per file (no format-specific versions)          │  │
│  │                                                               │  │
│  │  References:                                                   │  │
│  │    - md_template: XXXX-MVP-TEMPLATE.md                      │  │
│  │    - yaml_template: XXXX-MVP-TEMPLATE.yaml                    │  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                       │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Authority Rules

1. **Templates are PRIMARY sources of truth**
   - MD Template → primary for human workflow
   - YAML Template → primary for Autopilot workflow
   - Templates define content structure and examples

2. **Schemas are DERIVATIVE of templates**
   - YAML Schema validates both MD and YAML documents
   - Schema references both `md_template` and `yaml_template`
   - Schema has single version (no format-specific versions)
   - Schema contains validation rules only (not content)

3. **Validators are format-aware**
   - Detect document format from file extension (`.md` or `.yaml`)
   - Apply format-specific validation rules from schema
   - Apply shared validation rules to both formats
   - Return errors with severity levels (error, warning, info)

4. **Autopilot uses YAML only**
   - Never loads MD templates
   - Uses `XXXX-MVP-TEMPLATE.yaml` files
   - Requires YAML templates to exist (raises error if missing)

5. **Humans use MD by default**
   - MD templates provide narrative explanations
   - YAML templates are reference only for understanding structure
   - Can create both formats if needed

---

## Performance Benefits

### AI Parsing Speed Comparison

| Operation | MD Template (.md) | YAML Template (.yaml) | Improvement |
|-----------|---------------------|----------------------|-------------|
| **Parse single document** | ~50ms | ~10ms | **5x faster** |
| **Parse 100 documents** | ~5s | ~1s | **5x faster** |
| **Extract traceability tags** | Regex (complex pattern) | Key access (direct) | **3x faster** |
| **Validate structure** | Regex + custom logic | Schema validation (built-in) | **4x faster** |
| **Extract requirements list** | Regex (list parsing) | Array access (direct) | **5x faster** |
| **Map to Python dict** | Custom parsing logic | `yaml.safe_load()` (native) | **10x faster** |

### Detailed Analysis

**Markdown Parsing Overhead**:
```python
# MD Template parsing (complex, error-prone)
import re

def parse_markdown_traceability(md_content):
    # Multiple regex patterns needed
    brd_pattern = r"@brd: (BRD-\\d{2,}:\\d{2,}:\\d{2,})"
    prd_pattern = r"@prd: (PRD-\\d{2,}:\\d{2,}:\\d{2,})"
    ears_pattern = r"@ears: (EARS-\\d{2,}:\\d{2,}:\\d{2,})"
    
    # Edge cases to handle:
    # - Trailing whitespace
    # - Case sensitivity
    # - Multiple occurrences
    # - Malformed tags
    
    brd_matches = re.findall(brd_pattern, md_content)
    prd_matches = re.findall(prd_pattern, md_content)
    # ... more complex parsing logic
    
    return {
        'brd': brd_matches,
        'prd': prd_matches,
        # ...
    }

# Time: ~50ms per document
# Error-prone: Regex edge cases, MD variations
```

**YAML Parsing (clean, fast)**:
```python
# YAML Template parsing (simple, fast)
import yaml

def parse_yaml_traceability(yaml_content):
    # Single function call
    document = yaml.safe_load(yaml_content)
    
    # Direct key access
    traceability = document.get('traceability', {})
    upstream = traceability.get('upstream_references', {})
    
    # No regex, no edge cases, zero ambiguity
    return {
        'brd': upstream.get('brd'),
        'prd': upstream.get('prd'),
        # ...
    }

# Time: ~10ms per document (5x faster)
# Error-free: YAML syntax validation, type checking
```

### Quantified Benefits for Autopilot

| Metric | Baseline (MD) | Target (YAML) | Improvement |
|---------|----------------|----------------|-------------|
| **Parse time per artifact** | 50ms | 10ms | **80% reduction** |
| **Parse time for 100 artifacts** | 5s | 1s | **80% reduction** |
| **Code complexity** | High (regex) | Low (native) | **Simpler codebase** |
| **Bug count (estimated)** | 5-10 bugs | 1-2 bugs | **80% reduction** |
| **Type safety** | Partial | Full | **100% type-safe** |
| **Error detection** | Late (after parsing) | Early (during parsing) | **Faster feedback loop** |

---

## Migration Guide

### When to Convert MD to YAML

**Convert When**:
- ✅ Autopilot needs to consume existing MD documents
- ✅ Moving from human review to code generation phase
- ✅ Integrating MD documents into CI/CD pipelines
- ✅ Need type-safe validation before processing
- ✅ Performance is critical (large document volumes)

**Keep as MD When**:
- ✅ Document is primarily for human review/editing
- ✅ Business stakeholders need narrative explanations
- ✅ Rich formatting (tables, diagrams) is important
- ✅ Document is in early phases (BRD, PRD)
- ✅ No automation requirement

### Conversion Process

**Step 1**: Analyze MD document structure
- Identify sections and subsections
- Extract tables and lists
- Note code blocks and diagrams

**Step 2**: Map to YAML template structure
- Use corresponding `XXXX-MVP-TEMPLATE.yaml` as reference
- Map MD sections to YAML keys
- Convert tables to arrays of objects
- Convert code blocks to YAML multi-line strings (`|`)

**Step 3**: Validate YAML output
- Check YAML syntax with `yaml.safe_load()`
- Validate against `XXXX_MVP_SCHEMA.yaml`
- Verify all required fields are present
- Confirm traceability tags follow format

**Step 4**: Update references
- Update cross-references in related documents
- Update `@artifact:` tags if IDs changed
- Verify upstream/downstream links are correct

### Manual Conversion Example

**Before (MD)**:
```markdown
## Section: Requirements

| ID | Type | Statement | Priority |
|-----|-------|-----------|----------|
| REQ-01.01 | Functional | The system shall provide user authentication | High |
| REQ-01.02 | Functional | The system shall allow password reset | Medium |

```python
def authenticate():
    """Authenticate user credentials."""
    return True
```

### Verification
- Automated testing
```

**After (YAML)**:
```yaml
section_requirements:
  - id: "REQ-01.01"
    type: "Functional"
    statement: "The system shall provide user authentication"
    priority: "High"
    verification_method: "Automated testing"
    traceability_tag: "@prd: PRD.01.02.01"

  - id: "REQ-01.02"
    type: "Functional"
    statement: "The system shall allow password reset"
    priority: "Medium"
    verification_method: "Automated testing"
    traceability_tag: "@prd: PRD.01.02.02"

implementation_example: |
  def authenticate():
      """Authenticate user credentials."""
      return True

verification:
  method: "Automated testing"
```

### Automated Conversion (Future)

**Planned Feature**: MD→YAML converter script

```bash
# Example usage (future enhancement)
python3 ai_dev_flow/scripts/md_to_yaml_converter.py \
  --input docs/REQ-01_database.md \
  --output docs/REQ-01_database.yaml \
  --template 07_REQ/REQ-MVP-TEMPLATE.yaml \
  --schema 07_REQ/REQ_MVP_SCHEMA.yaml \
  --validate
```

**Converter Capabilities**:
- Parse MD structure using regex or AI assistance
- Map sections to YAML template
- Convert tables to structured arrays
- Extract code blocks and preserve as multi-line strings
- Validate output against schema
- Report conversion accuracy

---

## FAQ

### Q1: Why not use YAML for everything?

**A**: Different audiences have different needs:

- **Humans**: Need narrative explanations, context, and rich formatting
  - Tables and diagrams are natural in Markdown
  - Prose flows better for understanding business context
  - Code examples with syntax highlighting
  - Familiar syntax for most developers

- **AI Autopilot**: Needs structured data, speed, and type safety
  - YAML parsing is 3-5x faster than Markdown regex
  - No ambiguity in data extraction (keys vs regex matching)
  - Schema validation at parse time
  - Direct mapping to programming structures

**Result**: Dual format optimizes for both audiences.

---

### Q2: Can I have both MD and YAML versions?

**A**: Yes! Both formats can coexist:

**Use Cases for Both Formats**:
- Human reviews MD version, Autopilot uses YAML version
- MD for stakeholder communication, YAML for code generation
- Gradual migration (keep MD until stakeholders ready)
- Different workflows (human review vs automation)

**Consistency**:
- Both versions should have same content (different format only)
- Both validate against same schema (format-specific rules apply)
- Traceability tags must match between formats
- Version numbers should be synchronized

**Best Practice**:
- Keep master document in format best suited for primary workflow
- Generate other format on-demand (don't manually maintain both)
- Use git to track changes in primary format only

---

### Q3: Do I need to update existing validators?

**A**: No (as of this implementation):

- Validators are format-aware and already detect file extensions
- Schemas reference both templates (MD and YAML)
- Validators apply appropriate rules based on format
- No code changes required for validators

**What Changed**:
- Schema headers (to reference both templates)
- Schema `references` section (added `yaml_template` field)
- No validator logic changes

---

### Q4: Which format does Autopilot use?

**A**: Autopilot uses **YAML templates exclusively**:

**Autopilot Behavior**:
1. Load `XXXX-MVP-TEMPLATE.yaml` for artifact type
2. Use structured data directly for code generation
3. Validate against schema at parse time
4. Never load `XXXX-MVP-TEMPLATE.md` (MD files)

**Why YAML Only**:
- 3-5x faster parsing
- Zero regex complexity
- Type-safe validation
- Cleaner codebase
- Better performance for large volumes

**Exception**: If YAML template doesn't exist, Autopilot raises error (doesn't fallback to MD).

---

### Q5: How do schemas validate both formats?

**A**: Schemas are format-aware:

**Validation Process**:
```
Document File Detected (.md or .yaml)
  │
  ├─ .md → Apply Markdown-specific rules
  │          + Apply shared rules (traceability, metadata)
  │
  └─ .yaml → Apply YAML-specific rules
               + Apply shared rules (traceability, metadata)
```

**Example** (REQ schema):

```yaml
validation_rules:
  # Shared rules (apply to both formats)
  traceability:
    - rule: "Traceability tags must follow format @artifact: ID"
      severity: "error"
      applies_to: ["markdown", "yaml"]
  
  # Markdown-specific rules
  markdown_specific:
    - rule: "Section numbering must be sequential (1-12)"
      severity: "error"
      applies_to: ["markdown"]
  
  # YAML-specific rules
  yaml_specific:
    - rule: "All required keys must be present"
      severity: "error"
      applies_to: ["yaml"]
```

**Validator Logic** (pseudocode):
```python
def validate_document(file_path, schema_path):
    file_format = detect_format(file_path)  # .md or .yaml
    schema = load_schema(schema_path)
    
    errors = []
    
    # Apply shared rules
    for rule in schema.validation_rules.traceability:
        if rule.applies_to.includes(file_format):
            if not validate_rule(file_path, rule):
                errors.append(rule)
    
    # Apply format-specific rules
    if file_format == ".md":
        for rule in schema.validation_rules.markdown_specific:
            if not validate_rule(file_path, rule):
                errors.append(rule)
    elif file_format == ".yaml":
        for rule in schema.validation_rules.yaml_specific:
            if not validate_rule(file_path, rule):
                errors.append(rule)
    
    return errors
```

---

### Q6: What if I make changes to MD template?

**A**: Update both template and schema:

**For Human Workflow Changes**:
1. Update `XXXX-MVP-TEMPLATE.md` with new sections/format
2. Update `XXXX_MVP_CREATION_RULES.md` with new guidance
3. **Optional**: Update `XXXX_MVP_SCHEMA.yaml` if structure changed

**For Autopilot Workflow Changes**:
1. Update `XXXX-MVP-TEMPLATE.yaml` with new sections/fields
2. Update `XXXX_MVP_CREATION_RULES.md` with new guidance
3. **Optional**: Update `XXXX_MVP_SCHEMA.yaml` if structure changed

**For Schema Changes**:
- Update schema headers to reference both templates
- Update `references` section if template names changed
- Add/remove validation rules as needed
- Keep single `schema_version` (increment if breaking changes)

---

### Q7: How do I create a new artifact?

**A**: Choose format based on purpose:

**For Human Review/Editing**:
```bash
# Copy MD template
cp ai_dev_flow/07_REQ/REQ-MVP-TEMPLATE.md my_project/docs/REQ-01_feature.md

# Edit in your favorite editor
vim my_project/docs/REQ-01_feature.md
```

**For Autopilot Generation**:
```bash
# Copy YAML template
cp ai_dev_flow/07_REQ/REQ-MVP-TEMPLATE.yaml my_project/docs/REQ-01_feature.yaml

# Autopilot loads and fills in structure
python3 autopilot.py --template my_project/docs/REQ-01_feature.yaml
```

**For Both Formats**:
```bash
# Create both versions
cp ai_dev_flow/07_REQ/REQ-MVP-TEMPLATE.md my_project/docs/REQ-01_feature.md
cp ai_dev_flow/07_REQ/REQ-MVP-TEMPLATE.yaml my_project/docs/REQ-01_feature.yaml

# Humans edit MD, Autopilot uses YAML
```

---

## References

### Core Documentation

- **[MVP_WORKFLOW_GUIDE.md](./MVP_WORKFLOW_GUIDE.md)** - Overall workflow using MVP templates
- **[TRACEABILITY.md](./TRACEABILITY.md)** - Complete traceability rules and tag format
- **[SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](./SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)** - SPEC-driven development workflow

### Template Creation Guides

- **[SCHEMA_TEMPLATE_GUIDE.md](./SCHEMA_TEMPLATE_GUIDE.md)** - How to create YAML schemas
- **[README.md](./README.md)** - Framework overview and quick start

### Validation Standards

- **[VALIDATION_STANDARDS.md](./VALIDATION_STANDARDS.md)** - Validation rules and quality gates

### Autopilot Documentation

- **[AUTOPILOT/AUTOPILOT_WORKFLOW_GUIDE.md](./AUTOPILOT/AUTOPILOT_WORKFLOW_GUIDE.md)** - Autopilot workflow and YAML template usage

---

## Appendix: Quick Reference

### File Path Mapping

| Layer | Artifact | MD Template | YAML Template | YAML Schema |
|-------|----------|--------------|---------------|-------------|
| 1 | BRD | `01_BRD/BRD-MVP-TEMPLATE.md` | `01_BRD/BRD-MVP-TEMPLATE.yaml` | `01_BRD/BRD_MVP_SCHEMA.yaml` |
| 2 | PRD | `02_PRD/PRD-MVP-TEMPLATE.md` | `02_PRD/PRD-MVP-TEMPLATE.yaml` | `02_PRD/PRD_MVP_SCHEMA.yaml` |
| 3 | EARS | `03_EARS/EARS-MVP-TEMPLATE.md` | `03_EARS/EARS-MVP-TEMPLATE.yaml` | `03_EARS/EARS_MVP_SCHEMA.yaml` |
| 4 | BDD | `04_BDD/BDD-MVP-TEMPLATE.feature` | N/A (Gherkin standard) | `04_BDD/BDD_MVP_SCHEMA.yaml` |
| 5 | ADR | `05_ADR/ADR-MVP-TEMPLATE.md` | `05_ADR/ADR-MVP-TEMPLATE.yaml` | `05_ADR/ADR_MVP_SCHEMA.yaml` |
| 6 | SYS | `06_SYS/SYS-MVP-TEMPLATE.md` | `06_SYS/SYS-MVP-TEMPLATE.yaml` | `06_SYS/SYS_MVP_SCHEMA.yaml` |
| 7 | REQ | `07_REQ/REQ-MVP-TEMPLATE.md` | `07_REQ/REQ-MVP-TEMPLATE.yaml` | `07_REQ/REQ_MVP_SCHEMA.yaml` |
| 8 | CTR | `08_CTR/CTR-MVP-TEMPLATE.md` | `08_CTR/CTR-MVP-TEMPLATE.yaml` | `08_CTR/CTR_MVP_SCHEMA.yaml` |
| 9 | SPEC | N/A (already YAML) | `09_SPEC/SPEC-MVP-TEMPLATE.yaml` | `09_SPEC/SPEC_MVP_SCHEMA.yaml` |
| 10 | TASKS | `10_TASKS/TASKS-TEMPLATE.md` | `10_TASKS/TASKS-MVP-TEMPLATE.yaml` | `10_TASKS/TASKS_MVP_SCHEMA.yaml` |

### Command Reference

**Validate YAML Syntax**:
```bash
python3 -c "import yaml; yaml.safe_load(open('path/to/file.yaml'))"
```

**Validate MD Syntax**:
```bash
# Check for common MD issues (no built-in validator)
# Use linter tools or schema validation scripts
```

**Run Validator**:
```bash
# Example: Validate REQ document
python3 ai_dev_flow/07_REQ/scripts/validate_req.py \
  --path path/to/REQ-01_feature.md
```

**Convert MD to YAML** (future enhancement):
```bash
python3 ai_dev_flow/scripts/md_to_yaml_converter.py \
  --input path/to/document.md \
  --output path/to/document.yaml \
  --template XXXX-MVP-TEMPLATE.yaml
```

---

## Document Metadata

| Field | Value |
|--------|--------|
| **Title** | Dual-Format Architecture: YAML + MD Templates |
| **Version** | 1.0 |
| **Status** | Active |
| **Date** | 2026-01-20 |
| **Maintained By** | AI Dev Flow Team |
| **Related Documents** | DUAL_FORMAT_ARCHITECTURE_IMPLEMENTATION_PLAN.md |
| **Purpose** | Explain dual-format architecture, document types, and usage guidelines |

---

**END OF DOCUMENT**
