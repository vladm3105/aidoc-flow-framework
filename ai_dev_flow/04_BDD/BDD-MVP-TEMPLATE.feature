# =============================================================================
# BDD-MVP-TEMPLATE: Behavior Driven Development (MVP v2.0)
# =============================================================================

# MVP Note: Use a single .feature file per module; split into multiple files only when >500 lines.

# TEMPLATE_SOURCE: BDD-TEMPLATE.feature
# SCHEMA_VERSION: 2.0
# SCHEMA_REFERENCE: BDD_MVP_SCHEMA.yaml
# CREATION_RULES: BDD_CREATION_RULES.md
# VALIDATION_RULES: BDD_VALIDATION_RULES.md
# MATRIX_TEMPLATE: BDD-00_TRACEABILITY_MATRIX-TEMPLATE.md
#
# ID Format for Scenarios: BDD.NN.14.SS
#   - NN = Document number (e.g., 01, 02)
#   - 14 = Element type code for Scenario
#   - SS = Sequence number (01, 02, 03, ...)
# Example: BDD.01.14.01 = BDD doc 01, Scenario type, sequence 01
#
# v2.0 REQUIRED TAGS:
#   - @scenario-type:{success|optional|recovery|parameterized|error}
#   - Priority: @p0-critical | @p1-high | @p2-medium | @p3-low
#   - @scenario-id:BDD.NN.14.SS

# ===================
# TRACEABILITY TAGS (Cumulative - Layer 4)
# ===================
@brd:BRD.NN.TT.SS
@prd:PRD.NN.TT.SS
@ears:EARS.NN.25.SS

Feature: BDD-NN.SS: [Feature Name]
  As a [User Role]
  I want [Capability]
  So that [Benefit]

  # ===================
  # BACKGROUND (Optional - shared preconditions)
  # ===================

  Background:
    Given the system is in a ready state
    And the current time is "09:30:00" in "America/New_York"

  # ===================
  # SUCCESS SCENARIOS (@scenario-type:success)
  # Primary happy path - Required for all EARS event-driven statements
  # ===================

  @scenario-type:success @p0-critical @scenario-id:BDD.NN.14.01
  Scenario: [Primary success path description]
    Given [precondition from EARS WHEN clause]
    When [action from EARS trigger]
    Then the system SHALL [outcome from EARS SHALL clause]
    And the response SHALL be returned WITHIN @threshold:PRD.NN.perf.api.p95_latency

  @scenario-type:success @p0-critical @scenario-id:BDD.NN.14.02
  Scenario: [Secondary success path description]
    Given [precondition]
    When [action]
    Then the system SHALL [expected result]

  # ===================
  # ERROR SCENARIOS (@scenario-type:error)
  # Negative cases - Required for all EARS unwanted behavior statements
  # ===================

  @scenario-type:error @p1-high @scenario-id:BDD.NN.14.10
  Scenario: [Error condition] results in [expected behavior]
    Given [error precondition from EARS IF clause]
    When [action that triggers error]
    Then the system SHALL NOT [prevented behavior]
    And error code "[ERROR_CODE]" SHALL be returned WITHIN @threshold:PRD.NN.timeout.error.response

  @scenario-type:error @p1-high @scenario-id:BDD.NN.14.11
  Scenario: Invalid input is rejected with appropriate error
    Given [invalid input condition]
    When [action with invalid input]
    Then the system SHALL return error "[ERROR_CODE]"
    And the error message SHALL describe the validation failure

  # ===================
  # RECOVERY SCENARIOS (@scenario-type:recovery)
  # Failure recovery - Required for each circuit breaker/resilience pattern
  # ===================

  @scenario-type:recovery @p1-high @scenario-id:BDD.NN.14.20
  Scenario: System recovers from [failure type]
    Given [failure condition - e.g., external service unavailable]
    When [recovery trigger - e.g., service becomes available]
    Then the system SHALL recover WITHIN @threshold:PRD.NN.recovery.max_time
    And circuit breaker state SHALL transition to "half-open"

  @scenario-type:recovery @p1-high @scenario-id:BDD.NN.14.21
  Scenario: Circuit breaker prevents cascade failure
    Given the error threshold has been exceeded
    When additional requests arrive
    Then the circuit breaker SHALL be in "open" state
    And requests SHALL be rejected with "SERVICE_UNAVAILABLE"
    And fallback behavior SHALL be activated

  # ===================
  # PARAMETERIZED SCENARIOS (@scenario-type:parameterized)
  # Data-driven tests - Required for multi-value validation
  # ===================

  @scenario-type:parameterized @p2-medium @scenario-id:BDD.NN.14.30
  Scenario Outline: [Parameterized test description]
    Given [context with <variable>]
    When [action with <input>]
    Then the system SHALL return <expected>

    Examples:
      | variable | input   | expected |
      | value1   | input1  | result1  |
      | value2   | input2  | result2  |
      | value3   | input3  | result3  |

  @scenario-type:parameterized @p1-high @scenario-id:BDD.NN.14.31
  Scenario Outline: Validation accepts valid <input_type>
    Given a valid <input_type> value "<value>"
    When the value is validated
    Then validation SHALL pass
    And no error SHALL be returned

    Examples:
      | input_type | value           |
      | email      | user@example.com|
      | phone      | +1-555-123-4567 |
      | date       | 2026-02-09      |

  # ===================
  # OPTIONAL SCENARIOS (@scenario-type:optional)
  # Alternative paths with optional parameters
  # ===================

  @scenario-type:optional @p2-medium @scenario-id:BDD.NN.14.40
  Scenario: [Alternative path with optional parameter]
    Given [optional context - e.g., optional flag is set]
    When [alternative action]
    Then the system SHALL [alternative outcome]

  @scenario-type:optional @p3-low @scenario-id:BDD.NN.14.41
  Scenario: [Feature with default behavior when optional field omitted]
    Given [context without optional field]
    When [action]
    Then the system SHALL use default value "[DEFAULT]"

  # ===================
  # 5-CATEGORY COVERAGE MATRIX
  # ===================
  # | Category      | Min Scenarios | Priority Distribution            |
  # |---------------|---------------|-----------------------------------|
  # | success       | 1 per EARS    | 100% @p0-critical or @p1-high     |
  # | error         | 1 per unwanted| 80% @p1-high, 20% @p2-medium      |
  # | recovery      | 1 per CB      | 100% @p1-high                     |
  # | parameterized | 1 per multi   | 50% @p1-high, 50% @p2-medium      |
  # | optional      | 1 per optional| 100% @p2-medium or @p3-low        |
  # ===================

  # ===================
  # MIGRATION NOTE (MVP → Full)
  # ===================
  # This is an MVP BDD file. For full enterprise validation:
  # 1. Expand to include all 8 scenario categories
  # 2. Add complete traceability tags (@adr, @sys, etc.)
  # 3. Add performance scenarios with @threshold references
  # 4. Add security scenarios for authentication/authorization
  # 5. Split into multiple .feature files if >500 lines
  # 6. Validate ADR-Ready score >= 90%
