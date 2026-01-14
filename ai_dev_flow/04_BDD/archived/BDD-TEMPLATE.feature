# =============================================================================
# 📋 Document Authority: This is the PRIMARY STANDARD for BDD structure.
# All other documents (Schema, Creation Rules, Validation Rules) DERIVE from this template.
# - In case of conflict, this template is the single source of truth
# - Schema: BDD_SCHEMA.yaml - Machine-readable validation (derivative)
# - Creation Rules: BDD_CREATION_RULES.md - AI guidance for document creation (derivative)
# - Validation Rules: BDD_VALIDATION_RULES.md - AI checklist after document creation (derivative)
#   NOTE: VALIDATION_RULES includes all CREATION_RULES and may be extended for validation
# =============================================================================
#
# ⚠️ CRITICAL: Always reference SPEC_DRIVEN_DEVELOPMENT_GUIDE.md as the single source of truth
#              for workflow steps, artifact definitions, and quality gates.
#              Location: ../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md
#
# SCHEMA_REFERENCE: BDD_SCHEMA.yaml
# SCHEMA_VERSION: 1.1
#
# =============================================================================
# 🚨 COMMON ANTI-PATTERNS TO AVOID (Read Before Generating)
# =============================================================================
#
# ❌ WRONG: Tags in comments (Gherkin frameworks cannot parse these)
#    # @brd: BRD.001.FR001
#    # @prd: PRD.001.001
#    Feature: My Feature
#
# ✅ CORRECT: Tags as Gherkin-native on separate lines before Feature
#    @brd: BRD.01.01.01
#    @brd: BRD.01.01.02
#    @prd: PRD.01.07.01
#    @ears: EARS.01.24.01
#    Feature: My Feature
#
# ❌ WRONG: ADR-Ready Score without checkmark or ≥ symbol
#    | **ADR-Ready Score** | 75% (Target: 90%) |
#
# ✅ CORRECT: ADR-Ready Score with checkmark and ≥ symbol
#    | **ADR-Ready Score** | ✅ 75% (Target: ≥90%) |
#
# ❌ WRONG: Hardcoded magic numbers in scenarios
#    Then response time is less than 200ms
#
# ✅ CORRECT: Threshold registry reference
#    Then response time is less than @threshold: PRD.035.perf.api.p95_latency
#
# =============================================================================
# 📁 FILE ORGANIZATION: Section-Based Structure (MANDATORY)
# =============================================================================
#
# BDD uses section-based numbering aligned with 02_PRD/BRD standards.
# All .feature files use dot notation inside the suite folder: docs/04_BDD/BDD-NN_{slug}/
#
# **Three Valid Patterns**:
#
# 1. **Section-Only Format** (primary pattern):
#    - Pattern: ^BDD-\d{2,}\.\d+_[a-z0-9_]+\.feature$
#    - Example: docs/04_BDD/BDD-02_knowledge_engine/BDD-02.14_query_result_filtering.feature
#    - Use when: Standard section file (≤500 lines, ≤12 scenarios)
#    - Metadata:
#      @section: 2.14
#      @parent_doc: BDD-02
#      @index: BDD-02.0_index.md
#    - Feature title: Feature: BDD-02.14: Query Result Filtering
#
# 2. **Subsection Format** (when section >500 lines):
#    - Pattern: ^BDD-\d{2,}\.\d+\.\d{2}_[a-z0-9_]+\.feature$
#    - Example: BDD-02.24.01_quality_performance.feature
#    - Use when: Section requires splitting (each subsection ≤500 lines)
#    - Metadata:
#      @section: 2.24.01
#      @parent_section: 2.24
#      @parent_doc: BDD-02
#      @index: BDD-02.0_index.md
#    - Feature title: Feature: BDD-02.24.01: Performance Quality Attributes
#
# 3. **Aggregator Format** (optional redirect stub):
#    - Pattern: ^BDD-\d{2,}\.\d+\.00_[a-z0-9_]+\.feature$
#    - Example: BDD-02.12.00_query_graph_traversal.feature
#    - Use when: Organizing multiple subsections under one section
#    - Requirements: @redirect tag, 0 scenarios, references to subsections
#    - Metadata:
#      @redirect
#      @section: 2.12.00
#      @parent_doc: BDD-02
#      @index: BDD-02.0_index.md
#
# **Numbering Scheme**:
# - .0 suffix: Index file (e.g., BDD-02.0_index.md) - MANDATORY for each suite
# - .1, .2, .3: Content sections (e.g., docs/04_BDD/BDD-02_knowledge_engine/BDD-02.1_ingest.feature)
# - .SS.01, .SS.02: Subsections (e.g., BDD-02.3.01_learning_path.feature)
# - .SS.00: Aggregator/redirect stub (e.g., BDD-02.2.00_query.feature)
#
# **File Organization**:
# - All .feature files live inside the suite folder: docs/04_BDD/BDD-NN_{slug}/
# - NO features/ subdirectory (prohibited - legacy format)
# - Index file required: BDD-NN.0_index.md
# - Optional companions: BDD-NN_README.md, BDD-NN_TRACEABILITY.md
#
# **File Size & Scenario Limits**:
# - Target: 300–500 lines per .feature file
# - Maximum: 600 lines per file (absolute)
# - Maximum 12 scenarios per Feature block
# - If section approaches/exceeds limits → Split into subsections (.SS.mm format)
# - If many subsections → Add aggregator (.SS.00 format)
#
# **Prohibited Patterns** (cause validation ERROR):
# - ❌ _partN suffix (e.g., BDD-02_query_part1.feature)
# - ❌ Single-file format: BDD-NN_slug.feature (legacy)
# - ❌ Directory-based: BDD-NN_{slug}/features/ (legacy)
#
# **Reference**: BDD_SPLITTING_RULES.md, ID_NAMING_STANDARDS.md
#
# =============================================================================
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
#   - ../03_EARS/EARS-TEMPLATE.md#5.6 (Business vs Technical Requirements Boundary)
#   - ../01_BRD/BRD-TEMPLATE.md#appendix-b (PRD-Level Content Exclusions)
#
# =============================================================================

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
#   - REQ-NN: [Brief description of primary requirement being verified]
#   - REQ-NN: [Additional requirements if multiple are covered]
# TRACEABILITY:
#   Upstream: [REQ-NN](../07_REQ/.../REQ-NN_...md#REQ-NN), [ADR-NN](../../../05_ADR/ADR-NN_...md#ADR-NN)
#   Downstream: Spec(../specs/.../SPEC-NN_...yaml), Code(`component.module`), Tasks([TASKS-NN](../11_TASKS/TASKS-NN_....md))
#
# SAME-TYPE REFERENCES (Conditional):
#   Include only if same-type relationships exist between BDD features.
#   @related-bdd: BDD-NN  # Related BDD feature sharing domain context
#   @depends-bdd: BDD-NN  # Prerequisite BDD feature that must be implemented first
#
# CUMULATIVE TAGGING REQUIREMENTS (Layer 4):
# MANDATORY Tags: @brd, @prd, @ears (plus standard @requirement, @adr, @bdd tags)
# Format: @artifact-type: TYPE.NN.TT.SS (Unified Element ID format: DOC_TYPE.DOC_NUM.ELEM_TYPE.SEQ)
# Examples:
#   @brd: BRD.01.01.30   (REQUIRED - business requirements)
#   @prd: PRD.03.07.02   (REQUIRED - product requirements)
#   @ears: EARS.01.24.03 (REQUIRED - engineering requirements)
# Purpose: Complete traceability chain from business requirements through tests
# See: ../TRACEABILITY.md#cumulative-tagging-hierarchy
#
# THRESHOLD REGISTRY INTEGRATION:
# Use @threshold tags for ALL quantitative values (performance, SLA, limits)
# Format: @threshold: PRD.NN.category.subcategory.key
# Examples:
#   @threshold: PRD.035.perf.api.p95_latency
#   @threshold: PRD.035.sla.uptime.target
#   @threshold: PRD.035.limit.api.requests_per_second
# Purpose: Prevent magic numbers by referencing centralized threshold registry
# See: ../02_PRD/PRD-00_threshold_registry_template.md
#
# THRESHOLDS REFERENCED IN THIS BDD FILE:
# BDD scenarios REFERENCE thresholds defined in the PRD threshold registry.
# All quantitative assertions must use @threshold: tags for traceability.
#
# Threshold Naming Convention: @threshold: PRD.NN.category.subcategory.key
# See: ../THRESHOLD_NAMING_RULES.md for complete naming standards.
#
# Thresholds typically used in BDD scenarios:
#
#   performance:
#     - "@threshold: PRD.NN.perf.api.p50_latency"     # 50th percentile response time
#     - "@threshold: PRD.NN.perf.api.p95_latency"     # 95th percentile response time
#     - "@threshold: PRD.NN.perf.api.p99_latency"     # 99th percentile response time
#
#   sla:
#     - "@threshold: PRD.NN.sla.uptime.target"        # Uptime availability target
#     - "@threshold: PRD.NN.sla.success_rate.target"  # Success rate target
#     - "@threshold: PRD.NN.sla.error_rate.max"       # Maximum acceptable error rate
#
#   timeout:
#     - "@threshold: PRD.NN.timeout.request.sync"     # Synchronous request timeout
#     - "@threshold: PRD.NN.timeout.request.async"    # Asynchronous request timeout
#
#   limit:
#     - "@threshold: PRD.NN.limit.api.requests_per_second"  # Rate limiting
#     - "@threshold: PRD.NN.limit.batch.max_size"           # Batch size limits
#     - "@threshold: PRD.NN.limit.payload.max_bytes"        # Payload size limits
#
#   capacity:
#     - "@threshold: PRD.NN.capacity.concurrent.max"  # Max concurrent connections
#     - "@threshold: PRD.NN.capacity.queue.max_depth" # Queue depth limits
#
# Example Usage in Scenarios:
#   Then response time is less than @threshold: PRD.NN.perf.api.p95_latency
#   And success rate is above @threshold: PRD.NN.sla.success_rate.target
#   And service maintains @threshold: PRD.NN.sla.uptime.target uptime
#

@brd: BRD.NN.EE.SS      # REQUIRED - business requirements traceability
@prd: PRD.NN.EE.SS      # REQUIRED - product requirements traceability
@ears: EARS.NN.24.SS    # REQUIRED - engineering requirements traceability
@requirement:[REQ-NN](../07_REQ/.../REQ-NN_...md#REQ-NN)
@adr:[ADR-NN](../05_ADR/ADR-NN_...md#ADR-NN)
@bdd:[BDD-NN.SS:scenarios](BDD-NN.SS_{slug}.feature#scenarios)
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

  @primary @functional @acceptance
  Scenario: [Descriptive scenario name for primary success case]
    Given [initial state: verified precondition for the scenario]
    And [additional context: any other required setup]
    When [primary action: the main behavior being tested]
    And [additional actions: supplementary steps if needed]
    Then [primary outcome: expected successful result]
    And [verification steps: additional success validations]
    And [business impact: measurable business outcome]

  @primary @functional
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

  @negative @security
  Scenario: [Handle unauthorized access attempts]
    Given [user lacks required permissions]
    When [attempting a restricted operation]
    Then [access is denied with clear error message]
    And [security event is logged appropriately]

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

  # NOTE: Performance thresholds should use @threshold registry references
  # @threshold: PRD.NN.perf.api.p50_latency
  # @threshold: PRD.NN.perf.api.p95_latency
  # @threshold: PRD.NN.perf.api.p99_latency
  @data_driven @performance
  Scenario Outline: [Validate performance under different load conditions]
    Given system load is at <load_percentage> capacity
    When <concurrent_requests> simultaneous requests are processed
    Then average response time is less than @threshold: PRD.NN.perf.api.<percentile>_latency
    And success rate is greater than @threshold: PRD.NN.sla.success_rate.<load_level>

    Examples: Performance Benchmarks (replace with actual threshold keys)
      | load_percentage | concurrent_requests | percentile | load_level |
      | 25%             | 10                  | p50        | low        |
      | 50%             | 50                  | p95        | medium     |
      | 75%             | 100                 | p99        | high       |

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
  # QUALITY ATTRIBUTE SCENARIOS
  # ===================

  @quality_attribute @security
  Scenario: [Data protection and privacy compliance]
    Given [sensitive data is processed]
    When [operations involve personal information]
    Then [data is encrypted in transit and at rest]
    And [access controls are enforced]
    And [audit logs capture data access appropriately]

  # @threshold: PRD.NN.sla.uptime.target
  @quality_attribute @reliability
  Scenario: [Maintain availability during peak load]
    Given [system under peak usage conditions]
    When [high-volume requests arrive]
    Then [service remains available above @threshold: PRD.NN.sla.uptime.target uptime]
    And [degradation occurs gracefully if needed]
    And [monitoring alerts are triggered appropriately]

  # @threshold: PRD.NN.perf.api.p95_latency
  # @threshold: PRD.NN.perf.api.p99_latency
  @quality_attribute @performance @latency
  Scenario: [Response time meets user expectations]
    Given [normal system operating conditions]
    When [typical user requests are made]
    Then [response time is under @threshold: PRD.NN.perf.api.p95_latency for 95% of requests]
    And [response time is under @threshold: PRD.NN.perf.api.p99_latency for 99% of requests]
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

# =============================================================================
# 📋 COPY-PASTE READY BLOCKS (Adapt these as needed for the project)
# =============================================================================
#
# --- DOCUMENT CONTROL TABLE (copy entire block) ---
#
# ## Document Control
#
# | Item | Details |
# |------|---------|
# | **Project Name** | [Project Name] |
# | **Document Version** | 1.0.0 |
# | **Date** | YYYY-MM-DD |
# | **Document Owner** | [Team Name] |
# | **Prepared By** | [Author Name] |
# | **Status** | Draft |
# | **ADR-Ready Score** | ✅ 75% (Target: ≥90%) |
#
# --- FEATURE-LEVEL TAGS (copy and replace NN/SS with actual IDs) ---
# Format: TYPE.NN.TT.SS (DOC_NUM.ELEM_TYPE.SEQ)
#
# @brd: BRD.NN.01.SS     # Element type 01 = Functional Requirement
# @prd: PRD.NN.EE.SS     # Element type 07 = Product Feature
# @ears: EARS.NN.24.SS   # Element type 24 = EARS Statement
# Feature: [Feature Title]
#
# --- AI-AGENT FEATURE TAGS (for AI-agent primary architecture files) ---
# Format: TYPE.NN.TT.SS (DOC_NUM.ELEM_TYPE.SEQ)
#
# @brd: BRD.NN.01.SS     # Element type 01 = Functional Requirement
# @prd: PRD.NN.EE.SS     # Element type 07 = Product Feature
# @ears: EARS.NN.24.SS   # Element type 24 = EARS Statement
# @ctr: CTR-005
# Feature: [Agent Feature Title]
#   Architecture: AI-Agent Primary (AGENT-NN)
#
# --- THRESHOLD REFERENCE FORMAT ---
#
# @threshold: PRD-NN:category.subcategory.key
#
# Examples:
#   @threshold: PRD-NN:perf.api.p95_latency
#   @threshold: PRD-NN:timeout.partner.name
#   @threshold: PRD-NN:risk.high.min
#   @threshold: PRD-NN:float.utilization.critical
#
# --- ENTITY REFERENCE FORMAT ---
#
# @entity: PRD.NN.EntityName
#
# Examples:
#   @entity: PRD.NN.BusinessTransaction
#   @entity: PRD.NN.RiskEvaluationUnit
#   @entity: PRD.NN.ComplianceCase
#
# =============================================================================
# END OF TEMPLATE
# =============================================================================
