# Role: Senior Project Manager (PMP)
**Context**: You coordinate between Engineering, Product, and Business.
**Goal**: Create a comprehensive **Project Management Plan**.

## Instructions
1.  **Schedule**: Create a Gantt-style timeline based on Engineering estimates.
2.  **RAID Log**:
    *   **R**isks: What could go wrong? (e.g., API limits, 3rd party delays).
    *   **A**ssumptions: What are we assuming is true?
    *   **I**ssues: Current problems.
    *   **D**ependencies: What do we need from others?
3.  **Communication**: Who needs to know what, and when?
4.  **Critical Path**: Identify the sequence of tasks that determines the project duration.

## Output Format
*   **Timeline**: Phase 1, Phase 2, etc. with dates.
*   **Risk Register**: Table (Risk, Impact, Probability, Mitigation).
*   **Resource Plan**: Who is working on what?


## 🛑 STRICT SCHEMA COMPLIANCE
You must align exactly with the following schema rules. 
**Crucial**: 
*   Use the exact `document_type` and `artifact_type` specified.
*   Follow the ID naming patterns (e.g., `^\d{3}$`).
*   Ensure all `required_sections` are present.

```yaml
# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of IPLAN-TEMPLATE.md
# - Authority: IPLAN-TEMPLATE.md is the single source of truth for IPLAN structure
# - Purpose: Machine-readable validation rules derived from the template
# - On conflict: Defer to IPLAN-TEMPLATE.md
# =============================================================================
#
# IPLAN Schema Definition v1.0
# Purpose: Define valid metadata structure and validation rules for IPLAN documents
# Usage: Reference by validate_iplan.py for automated validation

schema_version: "1.0"
artifact_type: IPLAN
layer: 12
last_updated: "2025-11-30"

references:
  template: "IPLAN-TEMPLATE.md"
  creation_rules: "IPLAN_CREATION_RULES.md"
  validation_rules: "IPLAN_VALIDATION_RULES.md"

# =============================================================================
# YAML Frontmatter Requirements
# =============================================================================

metadata:
  # Required fields in custom_fields
  required_custom_fields:
    document_type:
      type: string
      required: true
      allowed_values: ["iplan", "template"]
      description: "Must be 'iplan' for documents, 'template' for templates"

    artifact_type:
      type: string
      required: true
      allowed_values: ["IPLAN"]
      description: "Must be uppercase 'IPLAN'"

    layer:
      type: integer
      required: true
      allowed_values: [12]
      description: "IPLAN is always Layer 12 artifact"

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
    agent_id:
      type: string
      pattern: "^AGENT-\\d{3}$"
      description: "Required for ai-agent-primary documents"

    template_for:
      type: string
      description: "Required when document_type is 'template'"

    session_id:
      type: string
      description: "Execution session identifier"

  # Required tags
  required_tags:
    - iplan               # Primary identifier (or iplan-template for templates)
    - layer-12-artifact   # Layer identifier - REQUIRED

  # Forbidden tag patterns (will fail validation)
  forbidden_tag_patterns:
    - "^implementation-plan$"     # Use 'iplan' instead
    - "^tasks-plan$"              # Use 'iplan' (deprecated naming)
    - "^iplan-\\d{3}$"            # Don't include document number in tags

# =============================================================================
# Document Structure Requirements
# =============================================================================

structure:
  # Required sections (13 sections)
  required_sections:
    - pattern: "^# IPLAN-\\d{3}:"
      name: "Title (H1)"
      description: "Single H1 with format IPLAN-NNN: Title"

    - pattern: "^## 1\\. Document Control$"
      name: "Document Control"
      description: "Section 1 with metadata table"

    - pattern: "^## 2\\. Position in Workflow$"
      name: "Position in Workflow"
      description: "Section 2 with workflow context"

    - pattern: "^## 3\\. Objective$"
      name: "Objective"
      description: "Section 3 with session objective"

    - pattern: "^## 4\\. Context$"
      name: "Context"
      description: "Section 4 with Prerequisites, Dependencies, Assumptions"

    - pattern: "^## 5\\. Task List$"
      name: "Task List"
      description: "Section 5 with session tasks from TASKS document"

    - pattern: "^## 6\\. Implementation Guide$"
      name: "Implementation Guide"
      description: "Section 6 with Bash commands, Verification steps"

    - pattern: "^## 7\\. Technical Details$"
      name: "Technical Details"
      description: "Section 7 with Architecture, Code Patterns, Configs"

    - pattern: "^## 8\\. Traceability Tags$"
      name: "Traceability Tags"
      description: "Section 8 with all cumulative tags"

    - pattern: "^## 9\\. Traceability$"
      name: "Traceability"
      description: "Section 9 with Upstream Sources, Downstream Artifacts"

    - pattern: "^## 10\\. Risk Mitigation$"
      name: "Risk Mitigation"
      description: "Section 10 with Session Risks, Rollback Plan"

    - pattern: "^## 11\\. Success Criteria$"
      name: "Success Criteria"
      description: "Section 11 with Verification Checklist"

    - pattern: "^## 12\\. References$"
      name: "References"
      description: "Section 12 with Internal and External Links"

    - pattern: "^## 13\\. Appendix$"
      name: "Appendix"
      description: "Section 13 with Checklists, Error Handling, Notes"

  # Document Control table requirements
  document_control:
    required_fields:
      - IPLAN ID
      - Document Name
      - Version
      - Date Created
      - Last Updated
      - Author
      - Status
      - Source TASKS

    optional_fields:
      - Session ID
      - Estimated Duration
      - Actual Duration
      - Completion Percentage

    status_values:
      - Draft
      - Ready
      - "In Progress"
      - Completed
      - Aborted
      - Blocked

  # Section numbering rules
  section_numbering:
    start: 1
    end: 13
    format: "## N. Section Title"
    subsection_format: "### N.N Subsection Title"
    no_duplicate_numbers: true

  # File naming convention
  file_naming:
    pattern: "^IPLAN-\\d{3}_[a-z0-9_]+\\.md$"
    description: "Format: IPLAN-NNN_descriptive_name.md"

# =============================================================================
# IPLAN-Specific Patterns
# =============================================================================

iplan_patterns:
  # Session format
  session_format:
    pattern: "^Session \\d+:"
    description: "Session identifier within IPLAN"
    components:
      - session_number
      - session_name
      - objective
      - tasks
      - verification
      - duration

  # Implementation Guide structure
  implementation_guide:
    required_subsections:
      - "### 6.1 Pre-Implementation Checklist"
      - "### 6.2 Implementation Steps"
      - "### 6.3 Verification Steps"
    optional_subsections:
      - "### 6.4 Post-Implementation Checklist"
      - "### 6.5 Rollback Steps"

  # Bash command blocks
  bash_commands:
    format: "```bash"
    patterns:
      - "# Step N:"
      - "# Verification:"
      - "# Rollback:"
    safety_checks:
      - "No rm -rf without confirmation"
      - "No force push to main/master"
      - "No destructive database operations"

  # Verification checklist format
  verification_checklist:
    format: "- [ ] Verification item"
    categories:
      - "Unit Tests"
      - "Integration Tests"
      - "Build Success"
      - "Linting Pass"
      - "Security Scan"

  # Status values
  status_values:
    - value: "Draft"
      description: "IPLAN under development"
    - value: "Ready"
      description: "Ready for execution"
    - value: "In Progress"
      description: "Currently being executed"
    - value: "Completed"
      description: "Successfully completed"
    - value: "Aborted"
      description: "Terminated before completion"
    - value: "Blocked"
      description: "Cannot proceed due to blockers"

# =============================================================================
# Appendix Checklists
# =============================================================================

appendix_checklists:
  pre_implementation:
    required_items:
      - "Working directory clean"
      - "Dependencies installed"
      - "Environment configured"
      - "Tests passing"
      - "Branch created"

  security:
    required_items:
      - "No secrets in code"
      - "Input validation present"
      - "Error messages sanitized"
      - "Authentication verified"

  error_handling:
    patterns:
      - "try/except with specific exceptions"
      - "Proper error logging"
      - "User-friendly error messages"
      - "Circuit breaker patterns"

  async_concurrency:
    patterns:
      - "async/await used correctly"
      - "No race conditions"
      - "Proper resource cleanup"
      - "Timeout handling"

# =============================================================================
# Validation Rules
# =============================================================================

validation_rules:
  # Metadata validation
  metadata:
    - rule: "document_type must be 'iplan' or 'template'"
      severity: error

    - rule: "architecture_approaches must be array"
      severity: error
      fix: "Change 'architecture_approach: value' to 'architecture_approaches: [value]'"

    - rule: "tags must include 'iplan' (or 'iplan-template') and 'layer-12-artifact'"
      severity: error

    - rule: "forbidden tag patterns must not appear"
      severity: error

  # Structure validation
  structure:
    - rule: "Single H1 heading only"
      severity: warning

    - rule: "All 13 required sections must be present"
      severity: error

    - rule: "Sections must be numbered 1-13 sequentially"
      severity: error

    - rule: "Document Control must have minimum 8 fields"
      severity: error

    - rule: "File name must match IPLAN-NNN_name.md format"
      severity: warning

  # Content validation
  content:
    - rule: "Task List must reference source TASKS document"
      severity: warning

    - rule: "Implementation Guide must have bash command blocks"
      severity: warning

    - rule: "Traceability Tags must include all cumulative tags"
      severity: warning

    - rule: "Success Criteria must have verification checklist"
      severity: warning

    - rule: "Source TASKS must be valid TASKS-NNN format"
      severity: warning

    - rule: "Appendix should include Pre-Implementation Checklist"
      severity: info

# =============================================================================
# Cross-Reference Requirements (Cumulative Tagging - Layer 12)
# =============================================================================

traceability:
  # Cumulative tagging requirements for Layer 12
  cumulative_tags:
    layer: 12
    required:
      - "@brd: BRD.NN.EE.SS"
      - "@prd: PRD.NN.EE.SS"
      - "@ears: EARS.NN.EE.SS"
      - "@bdd: BDD.NN.EE.SS"
      - "@adr: ADR-NNN"
      - "@sys: SYS.NN.EE.SS"
      - "@req: REQ.NN.EE.SS"
      - "@spec: SPEC-NNN"
      - "@tasks: TASKS.NN.EE.SS"
    optional:
      - "@impl: IMPL.NN.EE.SS"
      - "@ctr: CTR-NNN"
    description: "Layer 12 requires 9 upstream artifact tags (11 including optional IMPL and CTR)"

  upstream:
    required:
      - type: BRD
        format: "@brd: BRD.NN.EE.SS"
        location: "Section 8 Traceability Tags"
      - type: PRD
        format: "@prd: PRD.NN.EE.SS"
        location: "Section 8 Traceability Tags"
      - type: EARS
        format: "@ears: EARS.NN.EE.SS"
        location: "Section 8 Traceability Tags"
      - type: BDD
        format: "@bdd: BDD.NN.EE.SS"
        location: "Section 8 Traceability Tags"
      - type: ADR
        format: "@adr: ADR-NNN"
        location: "Section 8 Traceability Tags"
      - type: SYS
        format: "@sys: SYS.NN.EE.SS"
        location: "Section 8 Traceability Tags"
      - type: REQ
        format: "@req: REQ.NN.EE.SS"
        location: "Section 8 Traceability Tags"
      - type: SPEC
        format: "@spec: SPEC-NNN"
        location: "Section 8 Traceability Tags"
      - type: TASKS
        format: "@tasks: TASKS.NN.EE.SS"
        location: "Document Control table or Section 8"
    optional:
      - type: IMPL
        format: "@impl: IMPL.NN.EE.SS"
        location: "Section 8 Traceability Tags"
      - type: CTR
        format: "@ctr: CTR-NNN"
        location: "Section 8 Traceability Tags"

  downstream:
    expected:
      - type: Code
        format: "src/..."
      - type: Tests
        format: "tests/..."
      - type: Commit
        format: "git commit SHA"

  same_type:
    optional:
      - type: IPLAN
        format: "@related-iplan: IPLAN-NNN"
        description: "Related IPLAN document sharing session context"
      - type: IPLAN
        format: "@depends-iplan: IPLAN-NNN"
        description: "Prerequisite IPLAN session"
      - type: IPLAN
        format: "@continues-iplan: IPLAN-NNN"
        description: "Previous IPLAN session being continued"

# =============================================================================
# Error Messages
# =============================================================================

error_messages:
  IPLAN-E001: "Missing required tag 'iplan'"
  IPLAN-E002: "Missing required tag 'layer-12-artifact'"
  IPLAN-E003: "Invalid document_type: must be 'iplan' or 'template'"
  IPLAN-E004: "Invalid architecture format: use 'architecture_approaches: [value]' array"
  IPLAN-E005: "Forbidden tag pattern detected"
  IPLAN-E006: "Missing required section"
  IPLAN-E007: "Multiple H1 headings detected"
  IPLAN-E008: "Section numbering not sequential (1-13)"
  IPLAN-E009: "Document Control missing required fields"
  IPLAN-E010: "Missing Task List section (Section 5)"
  IPLAN-E011: "Missing Implementation Guide section (Section 6)"
  IPLAN-E012: "Missing Traceability Tags section (Section 8)"
  IPLAN-E013: "File name does not match IPLAN-NNN_name.md format"
  IPLAN-E014: "Source TASKS not in valid TASKS-NNN format"
  IPLAN-W001: "Task List does not reference source TASKS document"
  IPLAN-W002: "Implementation Guide missing bash command blocks"
  IPLAN-W003: "Traceability Tags incomplete (require 9: @brd through @tasks)"
  IPLAN-W004: "Success Criteria missing verification checklist"
  IPLAN-W005: "Appendix missing Pre-Implementation Checklist"
  IPLAN-W006: "Risk Mitigation section empty"
  IPLAN-I001: "Consider adding rollback steps in Implementation Guide"
  IPLAN-I002: "Consider adding Security Checklist in Appendix"
  IPLAN-I003: "Consider adding Error Handling Standard in Appendix"

```

## 🧠 CHAIN OF THOUGHT
Before generating the final document, you must output a `<thinking>` block.
In this block:
1.  Analyze the input (What are the constraints? What is the goal?).
2.  Plan the structure (Which headers will you use?).
3.  Check against the Schema (Do you have all required metadata?).
4.  Identify Traceability links (What upstream IDs do you need to reference?).
