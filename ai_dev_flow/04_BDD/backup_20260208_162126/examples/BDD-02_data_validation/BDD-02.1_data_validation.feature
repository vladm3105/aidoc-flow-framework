# =============================================================================
# BDD-02.1: Data Validation Example
# =============================================================================
# Example BDD feature file demonstrating input validation scenarios
# Demonstrates Scenario Outline with Examples tables and negative test cases
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

@brd: BRD.01.01.15
@prd: PRD.01.07.05
@ears: EARS.01.24.05
@requirement: REQ-05
@adr: ADR-02
@bdd: BDD-02.1:scenarios
@section: 2.1
@parent_doc: BDD-02
@index: BDD-02.0_index.md
Feature: BDD-02.1: Data Validation
  Data validation ensures that all user inputs are properly validated
  before processing to maintain data integrity and prevent security vulnerabilities.

  As a system
  I want to validate all incoming data
  So that only valid, safe data enters the system

  Background:
    Given the validation service is operational
    And validation rules are loaded from configuration
    And the request rate is within @threshold: PRD.035.limit.api.requests_per_second

  # ===================
  # STRING VALIDATION SCENARIOS
  # ===================

  @primary @functional @validation
  Scenario: Validate required string fields
    Given a form submission endpoint
    When the user submits a form with:
      | field      | value                 |
      | first_name | John                  |
      | last_name  | Doe                   |
      | email      | john.doe@example.com  |
    Then the validation should pass
    And all fields should be trimmed of whitespace
    And the data should be accepted for processing

  @negative @validation @required_fields
  Scenario: Reject submission with missing required fields
    Given a form submission endpoint
    When the user submits a form with:
      | field      | value |
      | first_name | John  |
      | last_name  |       |
      | email      |       |
    Then the validation should fail
    And the error response should include:
      | field     | error_code          | message                        |
      | last_name | FIELD_REQUIRED      | Last name is required          |
      | email     | FIELD_REQUIRED      | Email is required              |
    And HTTP status code should be 400

  @data_driven @validation @string_length
  Scenario Outline: Validate string length constraints
    Given a field "<field_name>" with length constraints
    When the user submits value of length <length>
    Then the validation result should be "<result>"
    And the error should be "<error_message>"

    Examples: Valid Length Inputs
      | field_name | length | result | error_message |
      | username   | 3      | valid  | none          |
      | username   | 20     | valid  | none          |
      | bio        | 1      | valid  | none          |
      | bio        | 500    | valid  | none          |

    Examples: Invalid Length Inputs
      | field_name | length | result  | error_message                      |
      | username   | 2      | invalid | minimum 3 characters required      |
      | username   | 51     | invalid | maximum 50 characters exceeded     |
      | bio        | 0      | invalid | bio cannot be empty if provided    |
      | bio        | 1001   | invalid | maximum 1000 characters exceeded   |

  # ===================
  # EMAIL VALIDATION SCENARIOS
  # ===================

  @data_driven @validation @email
  Scenario Outline: Validate email format
    Given an email validation rule
    When the user submits email "<email>"
    Then the validation result should be "<result>"
    And the error should be "<error_message>"

    Examples: Valid Email Formats
      | email                      | result | error_message |
      | user@example.com           | valid  | none          |
      | user.name@example.com      | valid  | none          |
      | user+tag@example.com       | valid  | none          |
      | user@subdomain.example.com | valid  | none          |
      | USER@EXAMPLE.COM           | valid  | none          |

    Examples: Invalid Email Formats
      | email              | result  | error_message                |
      | userexample.com    | invalid | email must contain @         |
      | user@              | invalid | domain is required           |
      | @example.com       | invalid | local part is required       |
      | user@.com          | invalid | invalid domain format        |
      | user@example       | invalid | top-level domain required    |
      | user@@example.com  | invalid | invalid email format         |
      | user name@test.com | invalid | spaces not allowed in email  |

  # ===================
  # NUMERIC VALIDATION SCENARIOS
  # ===================

  @data_driven @validation @numeric
  Scenario Outline: Validate numeric field constraints
    Given a numeric field "<field_name>" with range [<min>, <max>]
    When the user submits value <value>
    Then the validation result should be "<result>"
    And the error should be "<error_message>"

    Examples: Valid Numeric Inputs
      | field_name | min  | max    | value  | result | error_message |
      | quantity   | 1    | 1000   | 1      | valid  | none          |
      | quantity   | 1    | 1000   | 500    | valid  | none          |
      | quantity   | 1    | 1000   | 1000   | valid  | none          |
      | price      | 0.01 | 999999 | 99.99  | valid  | none          |
      | age        | 0    | 150    | 25     | valid  | none          |

    Examples: Invalid Numeric Inputs
      | field_name | min  | max    | value   | result  | error_message                  |
      | quantity   | 1    | 1000   | 0       | invalid | must be at least 1             |
      | quantity   | 1    | 1000   | 1001    | invalid | must not exceed 1000           |
      | quantity   | 1    | 1000   | -5      | invalid | negative values not allowed    |
      | price      | 0.01 | 999999 | 0       | invalid | must be at least 0.01          |
      | age        | 0    | 150    | -1      | invalid | age cannot be negative         |

  @negative @validation @type_coercion
  Scenario: Reject non-numeric values for numeric fields
    Given a form with numeric field "quantity"
    When the user submits:
      | field    | value |
      | quantity | abc   |
    Then the validation should fail
    And the error should indicate "quantity must be a number"
    And HTTP status code should be 400

  # ===================
  # DATE VALIDATION SCENARIOS
  # ===================

  @data_driven @validation @date
  Scenario Outline: Validate date format and range
    Given a date field with format "YYYY-MM-DD"
    When the user submits date "<date>"
    Then the validation result should be "<result>"
    And the error should be "<error_message>"

    Examples: Valid Date Inputs
      | date       | result | error_message |
      | 2024-01-15 | valid  | none          |
      | 2024-12-31 | valid  | none          |
      | 2024-02-29 | valid  | none          |

    Examples: Invalid Date Inputs
      | date       | result  | error_message                |
      | 2024/01/15 | invalid | invalid date format          |
      | 01-15-2024 | invalid | invalid date format          |
      | 2024-13-01 | invalid | month must be 1-12           |
      | 2024-02-30 | invalid | invalid day for month        |
      | 2023-02-29 | invalid | 2023 is not a leap year      |
      | not-a-date | invalid | invalid date format          |

  @functional @validation @date_range
  Scenario: Validate date range constraints
    Given a booking form with start_date and end_date fields
    When the user submits:
      | field      | value      |
      | start_date | 2024-03-15 |
      | end_date   | 2024-03-10 |
    Then the validation should fail
    And the error should indicate "end_date must be after start_date"

  # ===================
  # COLLECTION VALIDATION SCENARIOS
  # ===================

  @functional @validation @arrays
  Scenario: Validate array size constraints
    Given an API endpoint accepting a list of items
    And the maximum items allowed is @threshold: PRD.035.limit.batch.max_items
    When the user submits a list with 101 items
    Then the validation should fail
    And the error should indicate "maximum 100 items allowed"

  @functional @validation @arrays
  Scenario: Validate unique items in array
    Given an API endpoint requiring unique tag values
    When the user submits:
      | tags                    |
      | ["red", "blue", "red"]  |
    Then the validation should fail
    And the error should indicate "duplicate tag values not allowed"

  # ===================
  # NESTED OBJECT VALIDATION SCENARIOS
  # ===================

  @functional @validation @nested
  Scenario: Validate nested object structure
    Given an API endpoint accepting address information
    When the user submits:
      """json
      {
        "shipping_address": {
          "street": "123 Main St",
          "city": "",
          "state": "CA",
          "postal_code": "invalid"
        }
      }
      """
    Then the validation should fail
    And the errors should include:
      | path                          | error_code     | message                     |
      | shipping_address.city         | FIELD_REQUIRED | city is required            |
      | shipping_address.postal_code  | INVALID_FORMAT | invalid postal code format  |

  # ===================
  # SECURITY VALIDATION SCENARIOS
  # ===================

  @negative @security @xss_prevention
  Scenario: Sanitize potential XSS in string inputs
    Given a comment submission endpoint
    When the user submits:
      | field   | value                                  |
      | comment | <script>alert('xss')</script>          |
    Then the script tags should be sanitized
    And the stored value should be safe for display
    And a security event should be logged

  @negative @security @sql_injection
  Scenario: Prevent SQL injection in inputs
    Given a search endpoint
    When the user submits:
      | field | value                      |
      | query | '; DROP TABLE users; --    |
    Then the input should be properly escaped
    And no SQL commands should execute
    And the search should proceed safely

  @negative @security @path_traversal
  Scenario: Prevent path traversal in file references
    Given a file download endpoint
    When the user requests file "../../../etc/passwd"
    Then the request should be rejected
    And the error should indicate "invalid file path"
    And a security alert should be triggered

  # ===================
  # BOUNDARY VALUE SCENARIOS
  # ===================

  @edge_case @boundary
  Scenario Outline: Test boundary values for numeric fields
    Given a quantity field accepting 1-1000
    When the user submits quantity <value>
    Then the validation result should be "<result>"

    Examples: Boundary Values
      | value | result  |
      | 0     | invalid |
      | 1     | valid   |
      | 2     | valid   |
      | 999   | valid   |
      | 1000  | valid   |
      | 1001  | invalid |

  # ===================
  # CONDITIONAL VALIDATION SCENARIOS
  # ===================

  @functional @validation @conditional
  Scenario: Apply conditional validation rules
    Given a payment form with payment_type field
    When the user selects payment_type "credit_card"
    Then the following fields become required:
      | field           |
      | card_number     |
      | expiry_date     |
      | cvv             |
    And bank_account_number should not be required

  @functional @validation @conditional
  Scenario: Validate based on country-specific rules
    Given a shipping address form
    When the user selects country "US"
    Then postal_code should match pattern "^\d{5}(-\d{4})?$"
    When the user selects country "UK"
    Then postal_code should match pattern "^[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}$"

  # ===================
  # ERROR RESPONSE FORMAT SCENARIOS
  # ===================

  @functional @error_handling
  Scenario: Return structured validation errors
    Given a form with multiple validation failures
    When validation is performed
    Then the error response should follow structure:
      """json
      {
        "status": "error",
        "code": "VALIDATION_FAILED",
        "errors": [
          {
            "field": "string",
            "code": "string",
            "message": "string"
          }
        ],
        "timestamp": "ISO-8601",
        "request_id": "string"
      }
      """
    And all validation errors should be returned in single response

  # ===================
  # QUALITY ATTRIBUTE SCENARIOS
  # ===================

  @quality_attribute @performance
  Scenario: Validation performance under load
    Given validation rules are cached
    When 1000 requests are validated per second
    Then validation should complete within @threshold: PRD.035.perf.validation.max_latency
    And no requests should timeout

  @quality_attribute @reliability
  Scenario: Handle validation rule configuration errors gracefully
    Given a malformed validation rule in configuration
    When the validation service starts
    Then the malformed rule should be logged as error
    And default strict validation should be applied
    And the service should remain operational

# =============================================================================
# END OF BDD-02.1: Data Validation
# =============================================================================
