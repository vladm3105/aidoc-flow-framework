@brd: BRD.01 @prd: PRD.01.01.01 @ears: EARS.01.01.01
# =============================================================================
# BDD-MVP-TEMPLATE: Streamlined Behavior Driven Development (MVP)
# =============================================================================

# MVP Note: Use a single .feature file; do not split into multiple files in MVP.

@brd: BRD.01.EE.SS
@prd: PRD.01.01.01
# TEMPLATE_SOURCE: BDD-TEMPLATE.feature
# SCHEMA_REFERENCE: BDD_SCHEMA.yaml
# CREATION_RULES: BDD_CREATION_RULES.md
# VALIDATION_RULES: BDD_VALIDATION_RULES.md
# MATRIX_TEMPLATE: BDD-00_TRACEABILITY_MATRIX-TEMPLATE.md
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