# Behavior-Driven Development (BDD) Features

Behavior-Driven Development (BDD) feature files capture executable specifications written in natural language, enabling collaboration between business stakeholders, developers, and testers. BDD files transform requirements into concrete, verifiable scenarios that drive automated testing and development validation.

## Purpose

BDD files serve as the **living specification** that:
- **Clarify Requirements**: Convert abstract requirements into specific, testable behaviors
- **Bridge Communication Gaps**: Provide common language for technical and business teams
- **Enable Automation**: Create executable tests directly from specification scenarios
- **Ensure Verification**: Validate that implementations meet behavioral expectations
- **Maintain Traceability**: Link behavior specifications to upstream requirements and downstream code

## Position in Development Workflow

**⚠️ See [../index.md](../index.md#traceability-flow) for the authoritative workflow visualization.**

BDD is in the **Testing Layer** within the complete SDD workflow:

**Business Layer** (BRD → PRD → EARS) → **Testing Layer** (BDD) ← **YOU ARE HERE** → **Architecture Layer** (ADR → SYS) → **Requirements Layer** (REQ) → **Project Management Layer** (IMPL) → **Interface Layer** (CTR - optional) → **Implementation Layer** (SPEC) → **Code Generation Layer** (TASKS) → **Execution Layer** (Code → Tests) → **Validation Layer** (Validation → Review → Production)

**Key Points**:
- **Upstream**: EARS (Easy Approach to Requirements Syntax)
- **Downstream**: ADR (Architecture Decision Records)
- **Decision Point**: After IMPL, CTR is created if the requirement specifies an interface; otherwise, proceed directly to SPEC

For the complete workflow diagram with all relationships and styling, see [index.md](../index.md#traceability-flow).

## BDD File Creation Order: Prerequisites and Sequence

BDD files should be created **after** business requirements are defined but **before** technical implementation begins. This ensures behavioral specifications are built on solid requirements foundations.

### When to Create BDD Files

BDD files should be created **immediately after** initial requirements are gathered but **before** any code implementation begins:

```
Business Requirements (PRD) → BDD Scenarios ← Technical Design → Implementation
                                              ↓
                                      Acceptance Tests
```

#### Development Workflow Timing
1. **Before BDD**: Business analysts, product managers, and stakeholders collaborate on understanding user needs
2. **Create BDD**: Product owners and business analysts write BDD scenarios describing desired behavior
3. **Validate BDD**: Development and testing teams review BDD scenarios for technical feasibility and testability
4. **After BDD**: Technical teams use BDD scenarios to guide implementation planning and automated test creation

### Prerequisites for BDD Creation

#### ✅ **Must Exist Before BDD Creation**
- **Business Requirements Documents (PRDs)**: High-level business needs and user stories
- **Domain Understanding**: Clear grasp of business rules, processes, and terminology
- **Stakeholder Agreement**: Consensus among business stakeholders on what the system should do
- **Acceptance Criteria**: Measurable success criteria defined for each business requirement

#### ✅ **Should Exist Before BDD Creation**
- **Atomic Requirements (EARS/SYS)**: Atomic, testable requirements using conditional WHEN/THEN format
- **Architecture Decision Records (ADRs)**: High-level technical architecture decisions
- **System Boundaries**: Defined scope and interfaces for the system
- **Success Metrics**: Quantifiable measures of system success

#### ❌ **Should NOT Be Started Before BDD**
- **Detailed Technical Design**: BDD focuses on what the system should do, not how it will be implemented
- **Code Implementation**: BDD defines requirements that code must fulfill, not the implementation approach
- **Unit Test Creation**: BDD creates acceptance tests, not granular implementation tests
- **Database Schemas**: BDD specifies behavior, not data storage structures

### File Dependencies and Sequence

```
1. PRD-NNN.md (Business Requirements)     ← Foundation documents
2. EARS-NNN.md (Atomic Requirements)      ← Prerequisite - provides WHEN/THEN statements
3. ADR-NNN.md (Architecture Decisions)    ← Optional but helpful context
4. BDD-NNN.feature (BDD Scenarios)        ← Created from steps 1-3
5. SPEC-NNN.yaml (Technical Specs)        ← Can start in parallel with BDD
6. TASKS-NNN.md (Implementation Plans)    ← Uses BDD scenarios for validation
7. Code Implementation                    ← Validates against BDD scenarios
8. Automated Tests                        ← Generated from BDD scenarios
```

### Critical Success Factors

#### Business Readiness
- **Domain Experts Available**: Subject matter experts must be involved in BDD scenario creation
- **Requirements Stability**: Core business requirements should be relatively stable before investing in detailed BDD scenarios
- **Stakeholder Buy-in**: All key stakeholders must agree on the defined behavior scenarios

#### Technical Readiness
- **Automation Framework**: Test automation capability should be established or planned
- **Integration Planning**: Understanding of how BDD scenarios will integrate with CI/CD pipelines
- **Performance Considerations**: BDD scenarios should be designed for efficient automated execution

#### Process Readiness
- **Three-Amigos Collaboration**: Business, development, and testing teams should be prepared for collaborative scenario definition
- **Review Processes**: BDD scenarios should be reviewed for clarity, completeness, and testability
- **Maintenance Planning**: Strategy for evolving BDD scenarios as requirements change should be established

## BDD Feature Structure

### Header with Traceability Tags

Feature files include mandatory traceability linking:

```gherkin
# REQUIREMENTS VERIFIED:
#   - REQ-NNN: [Brief description]
# TRACEABILITY:
#   Upstream: [REQ-NNN](../reqs/.../REQ-NNN_...md#REQ-NNN), [ADR-NNN](../../../adrs/ADR-NNN_...md#ADR-NNN)
#   Downstream: Spec(../specs/.../SPEC-NNN_...yaml), Code(`component.module`)

@requirement:[REQ-NNN](../reqs/.../REQ-NNN_...md#REQ-NNN)
@adr:[ADR-NNN](../adrs/ADR-NNN_...md#ADR-NNN)
@bdd:[BDD-NNN:scenarios](feature_name.feature#scenarios)
Feature: Feature Title
```

### Feature Statement
Describes the system capability being validated:

```gherkin
Feature: [Clear, concise feature description]
  [Additional context about business value]
  As a [user/stakeholder role]
  I want [specific capability]
  So that [business benefit achieved]
```

### Background Context
Shared setup that applies to all scenarios:

```gherkin
Background:
    Given [initial context that applies to all scenarios]
    And [additional context setup]
    And [more context as needed]
```

### Scenarios
Executable specifications with clear behavioral steps:

```gherkin
@scenario_tag
Scenario: [Descriptive scenario name]
    Given [initial state or context]
    When [specific action performed]
    Then [expected outcome result]
    And [additional outcome verification]
```

## Scenario Types

### Success Path Scenarios
Validate expected behavior under normal conditions:

```gherkin
Scenario: Process valid data successfully
    Given valid input data is provided
    When the service processes the request
    Then the expected result is returned
    And no errors are reported
```

### Alternative Path Scenarios
Validate behavior under different but valid conditions:

```gherkin
Scenario: Handle optional parameters correctly
    Given optional parameters are present
    When the service processes the request
    Then optional parameters are included in processing
    And standard behavior still occurs
```

### Error Path Scenarios
Validate proper error handling and boundary conditions:

```gherkin
Scenario: Reject invalid input gracefully
    Given invalid input data is provided
    When the service attempts to process the request
    Then an appropriate error response is returned
    And error details are logged
```

### Edge Case Scenarios
Validate limits and boundary conditions:

```gherkin
Scenario: Handle maximum input size
    Given input data at the maximum allowed size
    When the service processes the request
    Then processing completes successfully
    And performance meets requirements
```

## Gherkin Keywords

### Given - Setup Context
Establishes the initial state before action:

```gherkin
Given the user is authenticated
Given the account has sufficient balance
Given the market is open for trading
```

### When - Action Performed
Describes the action being tested:

```gherkin
When the user submits an order
When the system processes market data
When the calculation service receives parameters
```

### Then - Outcomes Verified
Specifies expected results and validations:

```gherkin
Then the order is successfully placed
Then the response includes expected data
Then no errors are returned
```

### And/But - Additional Conditions
Add multiple Given/When/Then conditions:

```gherkin
When the user requests data
And caching is enabled
Then data is returned immediately
And cache hit metrics are incremented
```

## File Naming Convention

```
BDD-NNN_descriptive_requirements.feature
```

Where:
- `BDD` is the constant prefix
- `NNN` is the three-digit sequence number (001, 002, 003, etc.)
- `descriptive_requirements` uses snake_case focusing on what requirements are being validated
- `.feature` is the mandatory Gherkin file extension

**Examples:**
- `BDD-001_alpha_vantage_integration_requirements.feature`
- `BDD-003_risk_limits_requirements.feature`
- `BDD-042_ml_model_serving_requirements.feature`

## Tagging Standards

Tags establish traceability and enable selective execution:

### Requirement Tags - Mandatory
```gherkin
@requirement:[REQ-NNN](../reqs/.../REQ-NNN_...md#REQ-NNN)
@requirement:[REQ-NNN](../reqs/.../REQ-NNN_...md#REQ-NNN):L23
```

### Architecture Tags
```gherkin
@adr:[ADR-NNN](../adrs/ADR-NNN_...md#ADR-NNN)
```

### Custom Tags
```gherkin
@rate_limit @performance @error_handling
@integration @security @acceptance
```

## Writing Guidelines

### 1. Business Language
- **Write in business terms**: Use language stakeholders understand
- **Avoid technical jargon**: Prefer "user account" over "database record"
- **Focus on behavior**: Describe what should happen, not how

### 2. One Behavioral Concept Per Scenario
- **Single behavior**: Each scenario tests one specific behavior
- **Clear intent**: Scenario name should describe the behavior being validated
- **Independent execution**: Scenarios should run independently

### 3. Declarative, Not Imperative
- **Bad**: "Click the submit button"
- **Good**: "When the user submits the form"
- **Focus**: What the user wants, not how they achieve it

### 4. Data-Driven Scenarios
- **Avoid hardcoded values**: Use parameters and examples tables
- **Example tables**: For multiple test cases with same behavior

```gherkin
Scenario Outline: Validate input ranges
    Given input parameter is <value>
    When validation occurs
    Then result is <expected_result>

    Examples:
      | value | expected_result |
      | 5     | valid          |
      | -1    | invalid        |
      | 100   | valid          |
```

### 5. Positive and Negative Testing
- **Success paths**: Validate expected behavior
- **Alternative paths**: Different valid approaches
- **Error paths**: Invalid inputs, failure conditions
- **Edge cases**: Boundary conditions and limits

## BDD Execution and Automation

### Test Automation
BDD scenarios are executable in multiple frameworks:

**Python with Behave:**
```python
@given('the account balance is ${amount}')
def step_account_balance(context, amount):
    context.account.balance = float(amount)

@when('the withdrawal of ${withdrawal_amount} is requested')
def step_withdrawal_requested(context, withdrawal_amount):
    context.result = context.account.withdraw(float(withdrawal_amount))

@then('the withdrawal should be successful')
def step_withdrawal_successful(context):
    assert context.result.success
```

### Scenario Status
Track execution results:

```gherkin
# PASS - All steps executed successfully
# FAIL - One or more steps failed
# PENDING - Steps not yet implemented
# SKIPPED - Conditions not met for execution
```

### Test Environment Tags
Control execution environments:

```gherkin
@staging @production
Feature: Production validations

@development @testing
Feature: Development build validations

@smoke_test
Feature: Quick regression checks
```

## BDD Quality Gates

**Every BDD scenario must:**
- Use proper Gherkin syntax (Given/When/Then)
- Be independently executable
- Include relevant traceability tags
- Validate specific behavioral requirements
- Be written in clear, business-readable language

**Every BDD feature must:**
- Focus on one primary requirement set
- Include both positive and negative scenarios
- Provide sufficient background context
- Maintain stable, descriptive scenario names
- Link to upstream and downstream artifacts

## Scenario Coverage Guidelines

### Functional Coverage
Ensure scenarios cover all requirement aspects:

- **Input Validation**: Valid, invalid, edge case inputs
- **Business Rules**: All defined decision paths
- **Error Handling**: Expected failure modes and responses
- **Performance**: Load and timing requirements where specified

### End-to-End Coverage
Map scenarios to complete business journeys:

```gherkin
Feature: Order to fulfillment
  Scenario: Complete order lifecycle
    Given a customer places an order
    When payment is processed
    And inventory is confirmed
    Then order status shows "processing"
    And fulfillment email is sent
```

### Integration Coverage
Validate component interactions:

```gherkin
Feature: Data synchronization
  Scenario: Sync external feed
    Given external system updates are available
    When sync process executes
    Then local data matches external source
    And sync status is logged
```

## BDD Integration with Development

### Red-Green-Refactor with BDD
1. **Red**: Write failing BDD scenario first
2. **Green**: Implement code to make scenario pass
3. **Refactor**: Improve code while maintaining all scenarios

### Three Amigos Collaboration
- **Business**: Defines what should happen (acceptance criteria)
- **Development**: Implements how it happens (code)
- **Testing**: Verifies that it works (BDD scenarios)

### Continuous Integration
- Execute BDD scenarios on every commit
- Fail builds when scenarios don't pass
- Include BDD results in build reports
- Alert on new failing or pending scenarios

## Common BDD Patterns

### Authentication Scenarios
```gherkin
Feature: User authentication

Background:
    Given I am on the login page

Scenario: Successful login
    When I enter valid credentials
    Then I should be logged in
    And redirected to the dashboard

Scenario: Failed login attempts
    When I enter invalid credentials 3 times
    Then my account should be locked
    And I should see security warning
```

### Data Processing Scenarios
```gherkin
Feature: Data import validation

Background:
    Given the import system is active

Scenario: Valid data import
    Given valid CSV data file is uploaded
    When import processing completes
    Then all records are successfully imported
    And validation report is generated

Scenario: Handle duplicate data
    Given file contains duplicate records
    When import processing runs
    Then duplicates are identified
    And merge resolution is prompted
```

### Error Handling Scenarios
```gherkin
Feature: Service resilience

Background:
    Given the service is running

Scenario: Graceful external service degradation
    Given external dependency becomes unavailable
    When requests requiring that dependency arrive
    Then graceful fallback behavior occurs
    And users see appropriate messaging
    And incidents are logged for monitoring
```

## BDD Maintenance

### Scenario Updates
- Review scenarios when requirements change
- Update Givens/Whens/Thens to match new behavior
- Maintain backward compatibility where possible
- Add scenarios for new requirements

### Test Data Management
- Use realistic data in scenarios
- Maintain test data independence
- Update data when production data shapes change
- Include edge cases and boundary values

### Performance Scenarios
```gherkin
Scenario: Response within time limits
    Given system load is within normal parameters
    When request is made under peak conditions
    Then response time is less than 200ms
    And all service level agreements are met
```

## Benefits of Quality BDD

1. **Shared Understanding**: Creates common language across teams
2. **Living Documentation**: Scenarios that evolve with the system
3. **Early Feedback**: Catch issues before implementation completes
4. **Regression Protection**: Automated checks prevent unintended changes
5. **Requirements Validation**: Ensures business needs are correctly implemented

## Avoiding Common BDD Pitfalls

1. **UI Details**: Focus on business behavior, not interface implementation
2. **Implementation Coupling**: Don't write "technical tutorials" disguised as scenarios
3. **Vague Assertions**: Include specific, measurable outcomes
4. **Over-Complication**: Keep scenarios simple and focused
5. **Missing Contexts**: Always provide adequate background setup

## Example BDD Template

See `BDD-001_alpha_vantage_integration_requirements.feature` for a complete example of a well-structured BDD feature file that follows these conventions.
