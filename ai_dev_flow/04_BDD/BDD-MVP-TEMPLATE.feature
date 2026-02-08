# =============================================================================
# BDD-MVP-TEMPLATE: Streamlined Behavior Driven Development (MVP)
# =============================================================================

# MVP Note: Use a single .feature file; do not split into multiple files in MVP.

@brd: BRD.NN.EE.SS
@prd: PRD.NN.EE.SS
# TEMPLATE_SOURCE: BDD-TEMPLATE.feature
# SCHEMA_VERSION: 1.1
# SCHEMA_REFERENCE: BDD_MVP_SCHEMA.yaml
# CREATION_RULES: BDD_CREATION_RULES.md
# VALIDATION_RULES: BDD_VALIDATION_RULES.md
# MATRIX_TEMPLATE: BDD-00_TRACEABILITY_MATRIX-TEMPLATE.md
#
# ID Format for Scenarios: BDD.NN.13.SS
#   - NN = Document number (e.g., 01, 02)
#   - 13 = Element type code for Scenario
#   - SS = Sequence number (01, 02, 03, ...)
# Example: BDD.01.13.01 = BDD doc 01, Scenario type, sequence 01
#
Feature: [Feature Name]
  As a [User Role]
  I want [Capability]
  So that [Benefit]

  # ===================
  # CRITICAL PATHS
  # ===================

  @primary @acceptance
  Scenario: [Happy Path Scenario]
    Given [Precondition]
    When [Action]
    Then [Expected Result]

  @negative @error
  Scenario: [Critical Error Path]
    Given [Precondition]
    When [Invalid Action]
    Then [Error Handled Gracefully]

  # ===================
  # MIGRATION NOTE
  # ===================
  # This is an MVP BDD file. For full enterprise validation:
  # 1. Expand to BDD-TEMPLATE.feature
  # 2. Add complete traceability tags (@ears, @adr, etc)
  # 3. Add Scenario Outlines for data-driven testing
