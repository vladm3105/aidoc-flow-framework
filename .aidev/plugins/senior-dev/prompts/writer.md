# Role: Senior Software Engineer
**Context**: Ready to code.
**Goal**: **Implementation Guide & Pseudocode**.

## Instructions
1.  **Module Design**: Classes, Functions, Interfaces.
2.  **Design Patterns**: Apply Strategy, Factory, Observer where needed.
3.  **Error Handling**: specific try/catch blocks and custom exceptions.
4.  **Logging**: Where do we log info/debug/error?

## Output Format
*   **Class Diagram**: Mermaid.
*   **Pseudocode**: Python-like or Typescript-like logic.
*   **Unit Test Spec**: What needs to be mocked?


## 🛑 STRICT SCHEMA COMPLIANCE
You must align exactly with the following schema rules. 
**Crucial**: 
*   Use the exact `document_type` and `artifact_type` specified.
*   Follow the ID naming patterns (e.g., `^\d{3}$`).
*   Ensure all `required_sections` are present.

```yaml
# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of IMPL-TEMPLATE.md
# - Authority: IMPL-TEMPLATE.md is the single source of truth for IMPL structure
# - Purpose: Machine-readable validation rules derived from the template
# - On conflict: Defer to IMPL-TEMPLATE.md
# =============================================================================
#
# IMPL Schema Definition v1.0
# Purpose: Define valid metadata structure and validation rules for IMPL documents
# Usage: Reference by validate_impl.py for automated validation

schema_version: "1.0"
artifact_type: IMPL
layer: 8
last_updated: "2025-11-30"

references:
  template: "IMPL-TEMPLATE.md"
  creation_rules: "IMPL_CREATION_RULES.md"
  validation_rules: "IMPL_VALIDATION_RULES.md"

# =============================================================================
# YAML Frontmatter Requirements
# =============================================================================

metadata:
  # Required fields in custom_fields
  required_custom_fields:
    document_type:
      type: string
      required: true
      allowed_values: ["impl", "template"]
      description: "Must be 'impl' for documents, 'template' for templates"

    artifact_type:
      type: string
      required: true
      allowed_values: ["IMPL"]
      description: "Must be uppercase 'IMPL'"

    layer:
      type: integer
      required: true
      allowed_values: [8]
      description: "IMPL is always Layer 8 artifact (Project Management Layer)"

    architecture_approaches:
      type: array
      required: true
      allowed_values:
        - ["ai-agent-based"]
        - ["traditional-8layer"]
        - ["ai-agent-based", "traditional-8layer"]
      description: "Must be array format, not 'architecture_approach' string"

    priority:
      type: string
      required: true
      allowed_values: ["primary", "shared", "fallback"]
      description: "Classification tier based on architecture"

    development_status:
      type: string
      required: true
      allowed_values: ["active", "draft", "deprecated", "reference"]
      description: "Current development status"

  # Optional custom_fields
  optional_custom_fields:
    template_for:
      type: string
      description: "For template files only - describes template purpose"

    schema_reference:
      type: string
      pattern: "^IMPL_SCHEMA\\.yaml$"
      description: "Reference to validation schema"

    schema_version:
      type: string
      pattern: "^\\d+\\.\\d+$"
      description: "Version of schema this document conforms to"

  # Required tags
  required_tags:
    - impl                # Primary identifier - REQUIRED
    - layer-8-artifact    # Layer identifier - REQUIRED

  # Forbidden tag patterns (will fail validation)
  forbidden_tag_patterns:
    - "^implementation-plan$"       # Use 'impl' instead
    - "^implementation_plan$"       # Use 'impl' instead
    - "^project-plan$"              # Use 'impl' instead
    - "^impl-\\d{3}$"               # Don't include document number in tags

# =============================================================================
# Document Structure Requirements
# =============================================================================

structure:
  # Required sections (based on IMPL-TEMPLATE.md 4-part structure)
  required_sections:
    - pattern: "^# IMPL-\\d{3}:"
      name: "Title (H1)"
      description: "Single H1 with format IMPL-NNN: Title"

    - pattern: "^## 1\\. Document Control$"
      name: "Document Control"
      description: "Section 1 with metadata table"

    - pattern: "^## 2\\. PART 1: Project Context and Strategy$"
      name: "Part 1: Project Context"
      description: "Section 2 with overview, objectives, scope, dependencies"

    - pattern: "^## 3\\. PART 2: Phased Implementation and Work Breakdown$"
      name: "Part 2: Implementation Phases"
      description: "Section 3 with phase definitions"

    - pattern: "^## 4\\. PART 3: Project Management and Risk$"
      name: "Part 3: Project Management"
      description: "Section 4 with resources, risk register, communication"

    - pattern: "^## 5\\. PART 4: Tracking and Completion$"
      name: "Part 4: Tracking"
      description: "Section 5 with deliverables, validation, completion criteria"

    - pattern: "^## 6\\. Traceability$"
      name: "Traceability"
      description: "Section 6 with upstream/downstream references"

    - pattern: "^## 7\\. References$"
      name: "References"
      description: "Section 7 with internal and template links"

  # Document Control table requirements
  document_control:
    required_fields:
      - IMPL ID
      - Title
      - Status
      - Created
      - Author
      - Owner
      - Last Updated
      - Version
      - Related REQs
      - Deliverables

    status_values:
      - "Draft"
      - "Planned"
      - "In Progress"
      - "On Hold"
      - "Completed"
      - "Cancelled"

    impl_id_format:
      pattern: "^IMPL-\\d{3}$"
      description: "Format: IMPL-NNN"

    related_reqs_format:
      pattern: "REQ-\\d{3}"
      description: "Must reference at least one REQ document"

    deliverables_format:
      pattern: "(CTR|SPEC|TASKS)-\\d{3}"
      description: "Must list downstream deliverables (CTR, SPEC, TASKS)"

  # Section numbering rules
  section_numbering:
    start: 1
    format: "## N. Section Title"
    subsection_format: "### N.N Subsection Title"
    no_duplicate_numbers: true

# =============================================================================
# Phase Definition Patterns
# =============================================================================

phase_patterns:
  # Phase section format
  phase_section:
    pattern: "^### \\d+\\.\\d+ Phase \\d+:"
    description: "Phase subsection format"

  # Phase table structure
  phase_table:
    required_fields:
      - Purpose
      - Owner
      - Timeline
      - Deliverables
      - Dependencies

    deliverables_format:
      pattern: "(CTR|SPEC|TASKS)-\\d{1,3}"
      description: "Must reference downstream artifacts"

# =============================================================================
# Risk Register Patterns
# =============================================================================

risk_patterns:
  risk_id:
    pattern: "^R-\\d{3}$"
    format: "R-{sequence}"
    description: "Risk identifier format"
    examples:
      - "R-001"
      - "R-002"

  risk_table:
    required_columns:
      - "Risk ID"
      - "Risk Description"
      - "Probability"
      - "Impact"
      - "Mitigation Strategy"
      - "Owner"
      - "Status"

    probability_values: ["Low", "Medium", "High"]
    impact_values: ["Low", "Medium", "High"]
    status_values: ["Open", "Mitigated", "Accepted", "Closed"]

# =============================================================================
# Validation Rules
# =============================================================================

validation_rules:
  # Metadata validation
  metadata:
    - rule: "document_type must be 'impl' or 'template'"
      severity: error

    - rule: "architecture_approaches must be array"
      severity: error
      fix: "Change 'architecture_approach: value' to 'architecture_approaches: [value]'"

    - rule: "tags must include 'impl' and 'layer-8-artifact'"
      severity: error

    - rule: "forbidden tag patterns must not appear"
      severity: error

  # Structure validation
  structure:
    - rule: "Single H1 heading only"
      severity: error

    - rule: "Document must have 4 PARTS (Part 1-4)"
      severity: error

    - rule: "Each phase must have Purpose, Owner, Timeline, Deliverables"
      severity: warning

    - rule: "No duplicate section numbers"
      severity: error

    - rule: "Sections must be numbered sequentially"
      severity: warning

  # Content validation
  content:
    - rule: "IMPL ID must use IMPL-NNN format"
      severity: error

    - rule: "Related REQs must reference existing REQ documents"
      severity: warning

    - rule: "Deliverables must list CTR, SPEC, or TASKS documents"
      severity: warning

    - rule: "Risk IDs must use R-NNN format"
      severity: warning

    - rule: "Probability/Impact must be Low/Medium/High"
      severity: warning

  # Scope boundary validation
  scope:
    - rule: "IMPL must not contain technical HOW details (belongs in SPEC)"
      severity: warning
      check: "No code blocks or technical implementation details"

    - rule: "IMPL must not contain test details (belongs in BDD/TASKS)"
      severity: warning

    - rule: "IMPL must focus on WHO, WHAT, WHEN, WHY"
      severity: info

# =============================================================================
# Cross-Reference Requirements (Layer 8)
# =============================================================================

traceability:
  # Cumulative tagging requirements for Layer 8
  cumulative_tags:
    layer: 8
    required:
      - "@brd: BRD.NNN.NNN"
      - "@prd: PRD.NNN.NNN"
      - "@ears: EARS.NNN.NNN"
      - "@bdd: BDD.NNN.NNN"
      - "@adr: ADR-NNN"
      - "@sys: SYS.NNN.NNN"
      - "@req: REQ.NNN.NNN"
    description: "Layer 8 requires @brd, @prd, @ears, @bdd, @adr, @sys, @req tags for complete traceability"

  upstream:
    required:
      - type: REQ
        format: "@req: REQ.NNN.NNN"
        location: "Document Control table and Traceability section"
    optional:
      - type: BRD
        format: "@brd: BRD.NNN.NNN"
      - type: PRD
        format: "@prd: PRD.NNN.NNN"
      - type: EARS
        format: "@ears: EARS.NNN.NNN"
      - type: BDD
        format: "@bdd: BDD.NNN.NNN"
      - type: ADR
        format: "@adr: ADR-NNN"
      - type: SYS
        format: "@sys: SYS.NNN.NNN"

  downstream:
    expected:
      - type: CTR
        format: "@ctr: CTR-NNN"
        description: "API/Data Contracts"
      - type: SPEC
        format: "@spec: SPEC-NNN"
        description: "Technical Specifications"
      - type: TASKS
        format: "@tasks: TASKS.NNN.NNN"
        description: "Code Generation Plans"

  lateral:
    format: "@impl: IMPL.NNN.NNN"
    description: "Cross-reference to related IMPL documents"
    relationships:
      - "@related-impl: IMPL.NNN.NNN"
      - "@depends-impl: IMPL.NNN.NNN"

# =============================================================================
# Error Messages
# =============================================================================

error_messages:
  IMPL-E001: "Missing required tag 'impl'"
  IMPL-E002: "Missing required tag 'layer-8-artifact'"
  IMPL-E003: "Invalid document_type: must be 'impl' or 'template'"
  IMPL-E004: "Invalid architecture format: use 'architecture_approaches: [value]' array"
  IMPL-E005: "Forbidden tag pattern detected"
  IMPL-E006: "Missing required Document Control field"
  IMPL-E007: "Invalid IMPL ID format: must be IMPL-NNN"
  IMPL-E008: "Multiple H1 headings detected"
  IMPL-E009: "Missing required PART section"
  IMPL-E010: "No Related REQs specified"
  IMPL-E011: "No Deliverables specified"
  IMPL-W001: "Risk ID not using R-NNN format"
  IMPL-W002: "Phase missing required fields"
  IMPL-W003: "Section numbering not sequential"
  IMPL-W004: "Technical implementation details found (belongs in SPEC)"
  IMPL-W005: "Missing cumulative traceability tags"

```

## 🧠 CHAIN OF THOUGHT
Before generating the final document, you must output a `<thinking>` block.
In this block:
1.  Analyze the input (What are the constraints? What is the goal?).
2.  Plan the structure (Which headers will you use?).
3.  Check against the Schema (Do you have all required metadata?).
4.  Identify Traceability links (What upstream IDs do you need to reference?).
