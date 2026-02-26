# doc-bdd - Quick Reference

**Skill ID:** doc-bdd
**Layer:** 4 (Behavior-Driven Development)
**Purpose:** Create BDD test scenarios using Gherkin Given-When-Then format

## Quick Start

```bash
# Invoke skill
skill: "doc-bdd"

# Common requests
- "Create BDD scenarios for user authentication"
- "Generate Gherkin tests from EARS-001"
- "Write Layer 4 behavior specifications"
```

## What This Skill Does

1. Transform EARS requirements into executable test scenarios
2. Apply Given-When-Then pattern
3. Create scenario outlines with examples
4. Define background contexts for common setup
5. Generate .feature files for test frameworks

## Output Location

```text
docs/BDD/BDD-NNN_{feature_name}.feature
```

## Gherkin Syntax

```gherkin
Feature: User Authentication
  As a registered user
  I want to log in securely
  So that I can access my account

  Background:
    Given the authentication service is running

  Scenario: Successful login
    Given a user with valid credentials
    When the user submits login request
    Then the system returns a session token
    And the response time is under 500ms
```

## Upstream/Downstream

```text
BRD, PRD, EARS → BDD → ADR, SYS
```

## Quick Validation

- [ ] Feature has user story format (As a... I want... So that...)
- [ ] Scenarios follow Given-When-Then
- [ ] Background used for common setup
- [ ] Scenario Outlines for data-driven tests
- [ ] Traceability to EARS requirements

## Template Location

```text
ai_dev_flow/04_BDD/BDD-MVP-TEMPLATE.feature
```

## Related Skills

- `doc-ears` - Formal requirements (upstream)
- `doc-adr` - Architecture decisions (downstream)
- `doc-sys` - System requirements (downstream)
- `test-automation` - Execute BDD tests
