---
doc_id: BDD-01
artifact_id: BDD-01
artifact_type: BDD
layer: 4
deliverable_type: code
---
# BDD-01

## Document Control

Owner, status, and revision history for this BDD document.

## Feature Definition

The feature under test maps to the upstream EARS login response requirement.

- @brd: BRD.01.07.aaaa
- @prd: PRD.01.09.aaaa
- @ears: EARS.01.03.aaaa

Feature: Authentication acceptance scenarios for the MVP catalog.

### BDD.01.04.aaaa Authenticated session feature

The catalog must authenticate registered buyers and return a session token on success.

## Scenario Structure

Executable Gherkin scenarios covering success, error, and recovery paths.

### BDD.01.04.bbbb Scenario: Valid credentials yield a session token

Given a registered buyer with email "<buyer@example.com>"
When the buyer submits valid credentials
Then the authentication service returns a session token
And the response time is at or below the documented threshold

- @brd: BRD.01.07.aaaa
- @prd: PRD.01.09.aaaa
- @ears: EARS.01.03.aaaa

### BDD.01.04.cccc Scenario: Invalid credentials produce an error response

Given a registered buyer with email "<buyer@example.com>"
When the buyer submits an incorrect password
Then the authentication service rejects the request
And the response carries error code "AUTH_INVALID"

- @brd: BRD.01.07.aaaa
- @prd: PRD.01.09.aaaa
- @ears: EARS.01.03.aaaa

### BDD.01.04.dddd Scenario: Catalog search returns ranked results

Given the catalog service is available
When a buyer submits a product query
Then the catalog service returns ranked results
And the response time is at or below the documented threshold

- @brd: BRD.01.07.aaaa
- @prd: PRD.01.09.aaaa
- @ears: EARS.01.03.bbbb

## Traceability

Upstream BRD, PRD, and EARS references for this BDD document.

- @brd: BRD.01.07.aaaa
- @prd: PRD.01.09.aaaa
- @ears: EARS.01.03.aaaa

## Glossary

Project-specific terms used across the BDD scenarios above.
