# =============================================================================
# BDD Section Template
# =============================================================================
#
# File: BDD-NN.SS_{slug}.feature
# Pattern: ^BDD-\d{2,}\.\d+_[a-z0-9_]+\.feature$
# Use when: Standard section file (≤500 lines, ≤12 scenarios)
#
# =============================================================================

# Traceability Tags
@section: N.S
@parent_doc: BDD-NN
@index: BDD-NN.0_index.md
@brd:BRD.XX.YY.ZZ
@prd:PRD.AA.BB.CC
@ears:EARS.NN.SS.RR
@sys:SYS.NN.SS

Feature: BDD-NN.SS: [Feature Name]
  As a [user role/persona]
  I want [capability/functionality]
  So that [business value/benefit]

  # Business Context
  #
  # [1-2 sentences explaining the business context and why this feature exists]
  #
  # Acceptance Criteria Summary:
  # - Primary path: [Brief description]
  # - Negative cases: [Brief description]
  # - Edge cases: [Brief description]
  # - Quality attributes: [Performance, security, etc.]

Background:
  # Common preconditions for ALL scenarios in this section
  Given the system timezone is "America/New_York"
  And the current time is "09:30:00" in "America/New_York"
  And the system is in "active" state

# =============================================================================
# PRIMARY SCENARIOS (Happy Path)
# =============================================================================

@primary
@scenario_id:BDD.NN.S.01
Scenario: [Primary scenario 1 name]
  # Purpose: [Brief description of what this scenario validates]
  # Upstream: @ears:EARS.NN.SS.01
  
  Given [precondition 1]
  And [precondition 2]
  When [action/event occurs]
  Then [expected outcome 1]
  And [expected outcome 2]
  And it SHALL complete WITHIN @threshold:PRD.NN.category.timeout_key

@primary
@scenario_id:BDD.NN.S.02
Scenario: [Primary scenario 2 name]
  Given [precondition]
  When [action occurs]
  Then [expected result]

# =============================================================================
# NEGATIVE SCENARIOS (Error Handling)
# =============================================================================

@negative
@scenario_id:BDD.NN.S.03
Scenario: [Invalid input scenario]
  # Purpose: Validate error handling for invalid inputs
  
  Given [valid precondition]
  When [invalid action occurs]
  Then [appropriate error response]
  And error code "ERR_XXX" SHALL be returned
  And error message SHALL contain "expected text"

@negative
@scenario_id:BDD.NN.S.04
Scenario: [Authorization failure scenario]
  Given [user without required permissions]
  When [restricted action attempted]
  Then [access denied response]
  And error code "AUTH_ERR_XXX" SHALL be returned

# =============================================================================
# EDGE CASE SCENARIOS
# =============================================================================

@edge_case
@boundary
@scenario_id:BDD.NN.S.05
Scenario: [Boundary condition scenario]
  # Purpose: Test behavior at limits
  
  Given [system at capacity/limit]
  When [action at boundary]
  Then [graceful handling]
  And system SHALL remain stable

@edge_case
@scenario_id:BDD.NN.S.06
Scenario: [Empty/null input scenario]
  Given [minimal/empty state]
  When [action with null/empty input]
  Then [appropriate handling]

# =============================================================================
# DATA-DRIVEN SCENARIOS (Scenario Outline)
# =============================================================================

@data_driven
@scenario_id:BDD.NN.S.07
Scenario Outline: [Parameterized scenario name]
  # Purpose: Validate multiple input variations
  
  Given the system receives <input>
  When processing with <parameter>
  Then result SHALL be <expected_output>
  And status SHALL be "<status>"

  Examples:
    | input       | parameter | expected_output | status  |
    | value1      | param1    | output1         | success |
    | value2      | param2    | output2         | success |
    | invalid_val | param3    | error           | failed  |

# =============================================================================
# QUALITY ATTRIBUTE SCENARIOS
# =============================================================================

@quality_attribute
@performance
@scenario_id:BDD.NN.S.08
Scenario: [Performance scenario]
  # Purpose: Validate performance requirements
  # Upstream: @ears:EARS.NN.SS.PERF
  
  Given [baseline conditions]
  When [performance-critical operation]
  Then response time SHALL be WITHIN @threshold:PRD.NN.perf.response_time
  And CPU usage SHALL NOT exceed @threshold:PRD.NN.perf.max_cpu
  And memory usage SHALL NOT exceed @threshold:PRD.NN.perf.max_memory

@quality_attribute
@security
@scenario_id:BDD.NN.S.09
Scenario: [Security scenario]
  Given [security context]
  When [security-relevant action]
  Then [secure outcome]
  And sensitive data SHALL NOT be exposed
  And audit log SHALL contain action record

@quality_attribute
@reliability
@scenario_id:BDD.NN.S.10
Scenario: [Reliability scenario]
  Given [normal operation]
  When [transient failure occurs]
  Then [system recovers gracefully]
  And no data loss occurs
  And service resumes WITHIN @threshold:PRD.NN.reliability.recovery_time

# =============================================================================
# INTEGRATION SCENARIOS
# =============================================================================

@integration
@scenario_id:BDD.NN.S.11
Scenario: [External system integration]
  Given [external system available]
  When [integration point triggered]
  Then [successful integration]
  And external system receives correct payload
  And response is processed correctly

# =============================================================================
# SCENARIO GUIDELINES
# =============================================================================
#
# **File Size & Scenario Limits**:
# - Target: 300–500 lines per file
# - Maximum: 600 lines per file (absolute)
# - Maximum 12 scenarios per Feature block
# - If limits exceeded → Create subsections (BDD-NN.SS.mm format)
#
# **Canonical Step Phrases**:
# - Time: "the current time is \"HH:MM:SS\" in \"America/New_York\""
# - State: "the system is in \"state_name\" state"
# - Transitions: "the system attempts to transition to \"state_name\" state"
# - Validation: "the validation result SHALL be \"result\""
# - Thresholds: "SHALL complete WITHIN @threshold:PRD.NN.category.key"
# - Errors: "error code \"ERR_XXX\" SHALL be returned"
#
# **Threshold References**:
# - Always use @threshold: prefix for quantitative values
# - Format: @threshold:PRD.NN.category.key
# - Never hardcode numbers in scenarios (use threshold registry)
#
# **Traceability**:
# - Link to upstream: @ears, @brd, @prd, @sys tags
# - Reference in steps: "# Upstream: @ears:EARS.NN.SS.RR"
# - Scenario IDs: @scenario_id:BDD.NN.S.SEQ
#
# **Timezone Policy**:
# - Always use IANA timezone names (e.g., "America/New_York")
# - Never use abbreviations (EST, EDT, PST, etc.)
# - Always include seconds in time format (HH:MM:SS)
#
# =============================================================================

# Document Path: 04_BDD/BDD-NN.SS_{slug}.feature
# Framework: AI Dev Flow SDD
# Layer: 4 (BDD - Behavior-Driven Development)
# Template Version: 1.0
# Last Updated: 2025-12-27
