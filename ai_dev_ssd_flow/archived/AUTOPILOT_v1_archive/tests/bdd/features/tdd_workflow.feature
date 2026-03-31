@bdd @tdd-workflow
Feature: TDD Workflow Automation
  As a developer using the AI Dev Flow framework
  I want automated TDD workflow support
  So that I can follow test-driven development practices efficiently

  Background:
    Given a project with SDD directory structure
    And unit tests exist in the tests/unit directory

  @smoke @analyze
  Scenario: Analyze test requirements from unit tests
    Given unit test files with traceability tags
    When I run the test requirement analyzer
    Then a JSON file with test requirements is generated
    And the JSON contains test file information
    And the JSON contains traceability tags
    And the JSON contains test method signatures

  @smoke @spec-gen
  Scenario: Generate test-aware SPEC from test requirements
    Given a test requirements JSON file exists
    When I run the SPEC generator with TDD mode
    Then SPEC YAML files are generated
    And each SPEC contains traceability to source tests
    And each SPEC contains method signatures from tests

  @validation @red-state
  Scenario: Validate Red state before implementation
    Given unit tests exist but no implementation code
    When I validate the Red TDD state
    Then the validation passes
    And the result indicates tests are expected to fail

  @validation @green-state
  Scenario: Validate Green state after implementation
    Given unit tests exist with implementation code
    And all tests pass
    When I validate the Green TDD state
    Then the validation passes
    And coverage meets the threshold

  @traceability
  Scenario: Update PENDING traceability tags
    Given test files have PENDING traceability tags
    And corresponding SPEC and code files exist
    When I run the traceability updater
    Then PENDING tags are replaced with actual file paths
    And no PENDING tags remain in test files

  @integration-gen
  Scenario: Generate integration tests from SPEC
    Given SPEC files exist with interface definitions
    When I run the integration test generator
    Then integration test files are generated
    And tests have proper pytest markers
    And tests reference source SPEC files

  @smoke-gen
  Scenario: Generate smoke tests from BDD
    Given BDD feature files exist with scenarios
    When I run the smoke test generator
    Then smoke test files are generated
    And critical scenarios are prioritized
    And tests have timeout configuration

  @e2e @slow
  Scenario: Complete TDD workflow end-to-end
    Given a fresh project directory
    When I run the E2E validation with simple scenario
    Then all workflow stages complete
    And a validation report is generated
    And the report shows overall status

  @error-handling
  Scenario: Handle missing test directory gracefully
    Given a non-existent test directory path
    When I run the test requirement analyzer
    Then an appropriate error message is displayed
    And the script exits with non-zero code

  @error-handling
  Scenario: Handle empty test directory
    Given an empty test directory
    When I run the test requirement analyzer
    Then the script completes successfully
    And the output shows zero test files
