# =============================================================================
# BDD-01.1: User Authentication Example
# =============================================================================
# Example BDD feature file demonstrating authentication scenarios
# Following section-based structure per BDD_SPLITTING_RULES.md
# =============================================================================

## Document Control

| Item | Details |
|------|---------|
| **Project Name** | Example E-Commerce Platform |
| **Document Version** | 1.0 |
| **Date** | 2025-12-29 |
| **Document Owner** | QA Engineering Team |
| **Prepared By** | Business Analyst |
| **Status** | Approved |
| **ADR-Ready Score** | ✅ 95% (Target: ≥90%) |

---

@brd: BRD.01.01.10
@prd: PRD.01.07.01
@ears: EARS.01.24.01
@requirement: REQ-01
@adr: ADR-01
@bdd: BDD-01.1:scenarios
@section: 1.1
@parent_doc: BDD-01
@index: BDD-01.0_index.md
Feature: BDD-01.1: User Authentication
  User authentication is a critical security feature that enables users
  to securely access their accounts while protecting against unauthorized access.

  As a registered user
  I want to authenticate using my credentials
  So that I can securely access my account and personalized content

  Background:
    Given the authentication service is operational
    And the user database is available
    And rate limiting is configured at @threshold: PRD.035.limit.auth.requests_per_minute

  # ===================
  # SUCCESS PATH SCENARIOS
  # ===================

  @primary @functional @acceptance @smoke
  Scenario: Successful login with valid credentials
    Given a registered user exists with email "user@example.com"
    And the user's account is in active status
    And the user has not exceeded login attempt limits
    When the user submits login with:
      | field    | value              |
      | email    | user@example.com   |
      | password | ValidPassword123!  |
    Then the authentication should succeed
    And a valid JWT token should be returned
    And the token should expire after @threshold: PRD.035.session.timeout.default
    And the user's last login timestamp should be updated
    And an audit log entry should be created with action "LOGIN_SUCCESS"

  @primary @functional
  Scenario: Successful login with remember me option
    Given a registered user exists with email "persistent@example.com"
    And the user's account is active
    When the user submits login with remember me enabled:
      | field       | value                  |
      | email       | persistent@example.com |
      | password    | ValidPassword123!      |
      | remember_me | true                   |
    Then the authentication should succeed
    And a persistent session token should be issued
    And the token should expire after @threshold: PRD.035.session.timeout.extended

  @primary @functional @mfa
  Scenario: Successful login with multi-factor authentication
    Given a registered user exists with MFA enabled
    And the user has a verified authenticator app configured
    When the user submits valid primary credentials
    Then the system should prompt for MFA code
    When the user provides a valid TOTP code
    Then the authentication should succeed
    And the MFA verification should be logged

  # ===================
  # ALTERNATIVE PATH SCENARIOS
  # ===================

  @alternative @functional
  Scenario: Login with email case insensitivity
    Given a registered user exists with email "User@Example.COM"
    When the user submits login with email "user@example.com"
    And the correct password
    Then the authentication should succeed
    And the canonical email should be used in the session

  @alternative @functional
  Scenario: Login after password reset
    Given a user has completed password reset
    And the new password meets complexity requirements
    When the user logs in with the new password
    Then the authentication should succeed
    And previous sessions should be invalidated

  # ===================
  # ERROR PATH SCENARIOS
  # ===================

  @negative @error_handling @security
  Scenario: Reject login with invalid password
    Given a registered user exists with email "user@example.com"
    When the user submits login with:
      | field    | value            |
      | email    | user@example.com |
      | password | WrongPassword!   |
    Then the authentication should fail with error "INVALID_CREDENTIALS"
    And the error message should not reveal whether email exists
    And the failed attempt should be recorded
    And an audit log entry should be created with action "LOGIN_FAILED"

  @negative @security @rate_limiting
  Scenario: Block login after maximum failed attempts
    Given a registered user exists with email "blocked@example.com"
    And the user has reached @threshold: PRD.035.security.max_login_attempts failed login attempts
    When the user submits another login attempt
    Then the login should be blocked
    And the error should indicate "ACCOUNT_TEMPORARILY_LOCKED"
    And the lockout duration should be @threshold: PRD.035.security.lockout_duration_minutes
    And a security alert should be triggered

  @negative @error_handling
  Scenario: Reject login for non-existent user
    Given no user exists with email "nonexistent@example.com"
    When the user submits login with:
      | field    | value                    |
      | email    | nonexistent@example.com  |
      | password | AnyPassword123!          |
    Then the authentication should fail with error "INVALID_CREDENTIALS"
    And the response time should be similar to valid user lookup
    And the error message should not reveal account existence

  @negative @security
  Scenario: Reject login for deactivated account
    Given a registered user exists with email "deactivated@example.com"
    And the user's account status is "deactivated"
    When the user submits valid credentials
    Then the authentication should fail with error "ACCOUNT_DEACTIVATED"
    And instructions for reactivation should be provided

  # ===================
  # EDGE CASE SCENARIOS
  # ===================

  @edge_case @boundary @security
  Scenario: Handle concurrent login sessions
    Given a user is already logged in from device "laptop"
    When the same user logs in from device "mobile"
    Then both sessions should remain valid
    And the user should be notified of the new login
    And the notification should include device and location info

  @edge_case @recovery
  Scenario: Handle authentication service timeout
    Given the authentication service response time exceeds @threshold: PRD.035.timeout.auth.max
    When a user attempts to login
    Then the system should return error "SERVICE_TIMEOUT"
    And a retry option should be presented
    And the incident should be logged for monitoring

  @edge_case @boundary
  Scenario: Handle special characters in password
    Given a registered user exists with a password containing special characters
    When the user submits login with password containing:
      | character_type | examples        |
      | unicode        | üöä@€£          |
      | symbols        | !@#$%^&*()_+-=  |
      | spaces         | "pass word 123" |
    Then the authentication should succeed if password matches

  # ===================
  # LOGOUT SCENARIOS
  # ===================

  @primary @functional
  Scenario: Successful logout
    Given a user is currently authenticated
    When the user initiates logout
    Then the session should be invalidated
    And the JWT token should be added to the revocation list
    And the user should be redirected to the login page
    And an audit log entry should be created with action "LOGOUT"

  @functional @security
  Scenario: Logout from all devices
    Given a user has active sessions on multiple devices
    When the user initiates "logout from all devices"
    Then all existing sessions should be invalidated
    And all refresh tokens should be revoked
    And the user should be notified on all devices

  # ===================
  # PASSWORD RESET SCENARIOS
  # ===================

  @primary @functional @password_reset
  Scenario: Initiate password reset
    Given a registered user exists with email "forgot@example.com"
    When the user requests a password reset for "forgot@example.com"
    Then a password reset email should be sent
    And the reset link should expire after @threshold: PRD.035.security.reset_token_validity_hours
    And the reset token should be single-use
    And an audit log entry should be created with action "PASSWORD_RESET_REQUESTED"

  @functional @password_reset
  Scenario: Complete password reset with valid token
    Given a valid password reset token exists for user "forgot@example.com"
    When the user submits a new password meeting complexity requirements
    Then the password should be updated
    And all existing sessions should be invalidated
    And a confirmation email should be sent
    And the reset token should be invalidated

  @negative @password_reset
  Scenario: Reject password reset with expired token
    Given a password reset token has expired
    When the user attempts to use the expired token
    Then the password reset should fail with error "TOKEN_EXPIRED"
    And the user should be directed to request a new reset

  # ===================
  # DATA-DRIVEN SCENARIOS
  # ===================

  @data_driven @validation
  Scenario Outline: Validate password complexity requirements
    Given a user is setting their password
    When the user enters password "<password>"
    Then the validation result should be "<result>"
    And the error message should be "<message>"

    Examples: Valid Passwords
      | password           | result  | message  |
      | ValidPass123!      | valid   | accepted |
      | Str0ng@P@ssw0rd    | valid   | accepted |
      | MyP@ss1234567890   | valid   | accepted |

    Examples: Invalid Passwords
      | password    | result   | message                           |
      | short1!     | invalid  | minimum 8 characters required     |
      | nouppercase | invalid  | uppercase letter required         |
      | NOLOWERCASE | invalid  | lowercase letter required         |
      | NoNumbers!  | invalid  | at least one number required      |
      | NoSpecial1  | invalid  | special character required        |

  @data_driven @performance
  Scenario Outline: Authentication response time under different loads
    Given system load is at <load_percentage> capacity
    When <concurrent_requests> simultaneous login requests are processed
    Then average response time should be less than @threshold: PRD.035.perf.auth.<percentile>_latency
    And success rate should be greater than @threshold: PRD.035.sla.success_rate.<load_level>

    Examples: Performance Benchmarks
      | load_percentage | concurrent_requests | percentile | load_level |
      | 25%             | 10                  | p50        | low        |
      | 50%             | 50                  | p95        | medium     |
      | 75%             | 100                 | p99        | high       |

  # ===================
  # QUALITY ATTRIBUTE SCENARIOS
  # ===================

  @quality_attribute @security
  Scenario: Credentials protection in transit and at rest
    Given a user submits login credentials
    When the credentials are transmitted
    Then the connection should use TLS 1.3 encryption
    And passwords should never be logged in plaintext
    And passwords should be stored using bcrypt with cost factor 12

  @quality_attribute @reliability
  Scenario: Authentication service high availability
    Given the authentication service is deployed across multiple zones
    When one availability zone becomes unavailable
    Then authentication should continue via healthy zones
    And users should not experience service interruption
    And failover should complete within @threshold: PRD.035.sla.failover_time

# =============================================================================
# END OF BDD-01.1: User Authentication
# =============================================================================
