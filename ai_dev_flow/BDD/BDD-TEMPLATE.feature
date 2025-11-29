# ⚠️ CRITICAL: Always reference SPEC_DRIVEN_DEVELOPMENT_GUIDE.md as the single source of truth
#              for workflow steps, artifact definitions, and quality gates.
#              Location: ../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md
#
# QUICK SELF-CHECK BEFORE WRITING BDD SCENARIOS:
# Use these questions to verify your requirements are at the appropriate abstraction level:
#
# 1. Could this requirement be implemented in multiple ways? (✅ Good abstraction)
#    vs. Does this prescribe a specific implementation? (❌ Too technical for BDD)
#
# 2. Does this describe a business capability or outcome? (✅ Business-level)
#    vs. Does this describe HOW to build it technically? (❌ Implementation-level)
#
# 3. Would a solution architect understand the intent without implementation details? (✅ Appropriate)
#    vs. Does this require reading code or API docs to understand? (❌ Too specific)
#
# 4. Does this reference business rules, regulations, or SLAs? (✅ Business-level)
#    vs. Does this reference APIs, databases, or code? (❌ Technical-level)
#
# 5. Is this testable through BDD scenarios without knowing implementation? (✅ Good BDD)
#    vs. Does testing require knowing internal system architecture? (❌ Too coupled)
#
# For detailed guidance on requirements boundaries, see:
#   - ../EARS/EARS-TEMPLATE.md#5.6 (Business vs Technical Requirements Boundary)
#   - ../BRD/BRD-TEMPLATE.md#appendix-b (PRD-Level Content Exclusions)
#
# 📋 Document Authority: This is the PRIMARY STANDARD for BDD structure.
# - All BDD feature files must conform to this template
# - BDD_CREATION_RULES.md - Helper guidance for template usage
# - BDD_VALIDATION_RULES.md - Post-creation validation checks

## Document Control

| Item | Details |
|------|---------|
| **Project Name** | [Enter project name] |
| **Document Version** | [e.g., 1.0] |
| **Date** | [Current date] |
| **Document Owner** | [Name and title] |
| **Prepared By** | [Business Analyst name] |
| **Status** | [Draft / In Review / Approved] |
| **ADR-Ready Score** | ✅ 95% (Target: ≥90%) |

### Document Revision History

| Version | Date | Author | Changes Made | Approver |
|---------|------|--------|--------------|----------|
| 1.0 | [Date] | [Name] | Initial draft | |
| | | | | |

---

> **⚠️ UPSTREAM ARTIFACT REQUIREMENT**: Before completing traceability tags:
> 1. **Check existing artifacts**: List what upstream documents actually exist in `docs/`
> 2. **Reference only existing documents**: Use actual document IDs, not placeholders
> 3. **Use `null` appropriately**: Only when upstream artifact type genuinely doesn't exist for this feature
> 4. **Do NOT create phantom references**: Never reference documents that don't exist
> 5. **Do NOT create missing upstream artifacts**: If upstream artifacts are missing, skip that functionality. Only create functionality for existing upstream artifacts.

# 

POSITION: BDD is in Layer 4 (Testing Layer) - defines acceptance criteria from EARS requirements
#
# REQUIREMENTS VERIFIED:
#   - REQ-NNN: [Brief description of primary requirement being verified]
#   - REQ-NNN: [Additional requirements if multiple are covered]
# TRACEABILITY:
#   Upstream: [REQ-NNN](../reqs/.../REQ-NNN_...md#REQ-NNN), [ADR-NNN](../../../adrs/ADR-NNN_...md#ADR-NNN)
#   Downstream: Spec(../specs/.../SPEC-NNN_...yaml), Code(`component.module`), Tasks([TASKS-NNN](../ai_tasks/TASKS-NNN_....md))
#
# SAME-TYPE REFERENCES (Conditional):
#   Include only if same-type relationships exist between BDD features.
#   @related-bdd: BDD-NNN  # Related BDD feature sharing domain context
#   @depends-bdd: BDD-NNN  # Prerequisite BDD feature that must be implemented first
#
# CUMULATIVE TAGGING REQUIREMENTS (Layer 4):
# Required Tags: @brd, @prd, @ears (plus standard @requirement, @adr, @bdd tags)
# Format: @artifact-type: DOCUMENT-ID:REQUIREMENT-ID
# Example:
#   @brd: BRD-001:FR-030
#   @prd: PRD-003:FEATURE-002
#   @ears: EARS-001:EVENT-003
# Purpose: Complete traceability chain from business requirements through tests
# See: ../TRACEABILITY.md#cumulative-tagging-hierarchy

@brd: BRD-NNN:REQUIREMENT-ID
@prd: PRD-NNN:REQUIREMENT-ID
@ears: EARS-NNN:STATEMENT-ID
@requirement:[REQ-NNN](../reqs/.../REQ-NNN_...md#REQ-NNN)
@adr:[ADR-NNN](../adrs/ADR-NNN_...md#ADR-NNN)
@bdd:[BDD-NNN:scenarios](BDD-NNN_descriptive_requirements.feature#scenarios)
Feature: [Feature Title]
  [Additional context about business value and importance]
  As a [user/stakeholder role: e.g., trader, risk manager, system administrator]
  I want [specific capability: e.g., to place orders with risk validation]
  So that [business benefit: e.g., trading losses are prevented through automatic risk controls]

  Background:
    Given [initial context that applies to all scenarios: e.g., the system is operational]
    And [additional shared setup: e.g., valid user credentials are configured]
    And [more context as needed: e.g., required external services are available]

  # ===================
  # SUCCESS PATH SCENARIOS
  # ===================

  @positive @functional @acceptance
  Scenario: [Descriptive scenario name for primary success case]
    Given [initial state: verified precondition for the scenario]
    And [additional context: any other required setup]
    When [primary action: the main behavior being tested]
    And [additional actions: supplementary steps if needed]
    Then [primary outcome: expected successful result]
    And [verification steps: additional success validations]
    And [business impact: measurable business outcome]

  @positive @functional
  Scenario: [Another success scenario with different valid conditions]
    Given [different valid initial state]
    When [valid action with different parameters]
    Then [expected result for this scenario]
    And [appropriate outcome validations]

  # ===================
  # ALTERNATIVE PATH SCENARIOS
  # ===================

  @alternative @functional
  Scenario: [Handle optional parameters correctly]
    Given [base setup with optional elements]
    When [action with optional parameters included]
    Then [standard behavior still occurs]
    And [optional parameters are utilized appropriately]

  @alternative @functional
  Scenario: [Process data in different valid formats]
    Given [same capability with different input format]
    When [processing occurs with alternate format]
    Then [results are equivalent to primary format]
    And [data integrity is maintained]

  # ===================
  # ERROR PATH SCENARIOS
  # ===================

  @negative @error_handling @robustness
  Scenario: [Reject invalid input gracefully]
    Given [invalid input data is provided]
    When [the system attempts to process the request]
    Then [an appropriate error response is returned]
    And [error details are properly logged]
    And [system state remains consistent]

  @negative @regulatoryurity
  Scenario: [Handle unauthorized access attempts]
    Given [user lacks required permissions]
    When [attempting a restricted operation]
    Then [access is denied with clear error message]
    And [regulatoryurity event is logged appropriately]

  @negative @boundary
  Scenario: [Enforce required field validations]
    Given [request is missing mandatory fields]
    When [validation is performed]
    Then [specific field-level errors are returned]
    And [helpful error messages guide correction]

  # ===================
  # EDGE CASE SCENARIOS
  # ===================

  @edge_case @boundary @performance
  Scenario: [Handle maximum input size limits]
    Given [input data at maximum allowed size]
    When [processing occurs]
    Then [operation completes successfully]
    And [performance requirements are met]
    And [no resource exhaustion occurs]

  @edge_case @boundary
  Scenario: [Process concurrent operations correctly]
    Given [multiple valid requests arrive simultaneously]
    When [concurrent processing occurs]
    Then [all requests are handled correctly]
    And [race conditions are prevented]
    And [results are consistent with sequential processing]

  @edge_case @recovery
  Scenario: [Recover from temporary service interruptions]
    Given [external dependency becomes temporarily unavailable]
    When [service recovers after interruption]
    Then [processing resumes normally]
    And [any in-flight operations complete appropriately]
    And [system health indicators return to normal]

  # ===================
  # DATA-DRIVEN SCENARIOS
  # ===================

  @data_driven @functional
  Scenario Outline: [Validate input ranges and boundaries comprehensively]
    Given input parameter "<parameter>" has value <value>
    When validation occurs
    Then result status is "<expected_status>"
    And response includes message "<expected_message>"

    Examples: Valid Range Inputs
      | parameter | value | expected_status | expected_message |
      | quantity  | 1     | valid          | accepted         |
      | quantity  | 100   | valid          | accepted         |
      | quantity  | 1000  | valid          | accepted         |

    Examples: Invalid Range Inputs
      | parameter | value | expected_status | expected_message       |
      | quantity  | 0     | invalid        | quantity must be > 0   |
      | quantity  | -1    | invalid        | quantity must be > 0   |

  @data_driven @performance
  Scenario Outline: [Validate performance under different load conditions]
    Given system load is at <load_percentage> capacity
    When <concurrent_requests> simultaneous requests are processed
    Then average response time is less than <max_response_time> milliregulatoryonds
    And success rate is greater than <min_success_rate> percent

    Examples: Performance Benchmarks
      | load_percentage | concurrent_requests | max_response_time | min_success_rate |
      | 25%             | 10                  | 50               | 99.9            |
      | 50%             | 50                  | 100              | 99.5            |
      | 75%             | 100                 | 200              | 99.0            |

  # ===================
  # INTEGRATION SCENARIOS
  # ===================

  @integration @end_to_end
  Scenario: [Complete business workflow integration]
    Given [full business context with all prerequisites]
    When [complete business process executes]
    Then [end-to-end business outcome is achieved]
    And [all integrated components function correctly]
    And [audit trail captures the complete workflow]

  @integration @data_flow
  Scenario: [Validate data transformation across system boundaries]
    Given [source data in external format]
    When [transformation layers process the data]
    Then [target format matches specifications]
    And [data integrity is preserved]
    And [business rules are applied correctly]

  # ===================
  # NON-FUNCTIONAL SCENARIOS
  # ===================

  @non_functional @regulatoryurity
  Scenario: [Data protection and privacy compliance]
    Given [sensitive data is processed]
    When [operations involve personal information]
    Then [data is encrypted in transit and at rest]
    And [access controls are enforced]
    And [audit logs capture data access appropriately]

  @non_functional @reliability
  Scenario: [Maintain availability during peak load]
    Given [system under peak usage conditions]
    When [high-volume requests arrive]
    Then [service remains available above 99.9% uptime]
    And [degradation occurs gracefully if needed]
    And [monitoring alerts are triggered appropriately]

  @non_functional @performance @latency
  Scenario: [Response time meets user expectations]
    Given [normal system operating conditions]
    When [typical user requests are made]
    Then [response time is under 500ms for 95% of requests]
    And [response time is under 2000ms for 99% of requests]
    And [latency is consistent across similar operations]

  # ===================
  # FAILURE RECOVERY SCENARIOS
  # ===================

  @failure_recovery @resilience
  Scenario: [Handle external service failures gracefully]
    Given [external dependency becomes unavailable]
    When [requests requiring that dependency arrive]
    Then [graceful degradation behavior occurs]
    And [users receive appropriate messaging]
    And [incidents are logged for monitoring]
    And [automatic retry mechanisms are triggered]

  @failure_recovery @data_integrity
  Scenario: [Preserve data consistency during failures]
    Given [operation is in progress]
    When [unexpected failure occurs mid-operation]
    Then [transaction is rolled back completely]
    And [system state is consistent]
    And [no partial or corrupt data persists]

  @failure_recovery @monitoring
  Scenario: [Detection and alerting for critical failures]
    Given [critical component failure occurs]
    When [monitoring systems detect the issue]
    Then [appropriate alerts are triggered]
    And [runbook procedures are accessible]
    And [incident response processes begin automatically]
