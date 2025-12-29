# =============================================================================
# BDD-03.1: API Integration Example
# =============================================================================
# Example BDD feature file demonstrating REST API testing scenarios
# Includes Background steps, tags for filtering, and error response scenarios
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

@brd: BRD.01.01.20
@prd: PRD.01.07.10
@ears: EARS.01.24.10
@requirement: REQ-010
@adr: ADR-003
@bdd: BDD-03.1:scenarios
@section: 3.1
@parent_doc: BDD-03
@index: BDD-03.0_index.md
Feature: BDD-03.1: REST API Integration
  REST API integration ensures that external systems can reliably
  interact with the platform through well-defined endpoints.

  As an API consumer
  I want to interact with the platform via REST APIs
  So that I can integrate my systems with the platform

  Background:
    Given the API server is running
    And the database is seeded with test data
    And the API version is "v1"
    And the base URL is "https://api.example.com"
    And rate limiting is set to @threshold: PRD.035.limit.api.requests_per_minute

  # ===================
  # CRUD OPERATION SCENARIOS - CREATE
  # ===================

  @primary @functional @crud @create
  Scenario: Create a new resource via POST
    Given I am authenticated with valid API credentials
    And I have a valid request payload:
      """json
      {
        "name": "New Product",
        "description": "Product description",
        "price": 29.99,
        "category": "electronics"
      }
      """
    When I send a POST request to "/products"
    Then the response status should be 201
    And the response should include:
      | field       | type   |
      | id          | string |
      | name        | string |
      | created_at  | string |
    And the "Location" header should contain the resource URL
    And the resource should be retrievable at the returned location

  @negative @create @validation
  Scenario: Reject creation with invalid payload
    Given I am authenticated with valid API credentials
    And I have an invalid request payload:
      """json
      {
        "name": "",
        "price": -10
      }
      """
    When I send a POST request to "/products"
    Then the response status should be 400
    And the response should include validation errors:
      | field       | code             | message                    |
      | name        | FIELD_REQUIRED   | name is required           |
      | price       | INVALID_VALUE    | price must be positive     |
      | category    | FIELD_REQUIRED   | category is required       |

  # ===================
  # CRUD OPERATION SCENARIOS - READ
  # ===================

  @primary @functional @crud @read
  Scenario: Retrieve a single resource by ID
    Given I am authenticated with valid API credentials
    And a product exists with ID "prod_123"
    When I send a GET request to "/products/prod_123"
    Then the response status should be 200
    And the response should include the product details
    And the response time should be less than @threshold: PRD.035.perf.api.p95_latency

  @functional @crud @read @collection
  Scenario: Retrieve a paginated list of resources
    Given I am authenticated with valid API credentials
    And 50 products exist in the database
    When I send a GET request to "/products?page=1&limit=10"
    Then the response status should be 200
    And the response should contain 10 items
    And the response should include pagination metadata:
      | field        | value |
      | current_page | 1     |
      | per_page     | 10    |
      | total_items  | 50    |
      | total_pages  | 5     |
    And the response should include navigation links:
      | rel   | exists |
      | self  | true   |
      | first | true   |
      | last  | true   |
      | next  | true   |
      | prev  | false  |

  @functional @read @filtering
  Scenario: Filter resources by query parameters
    Given I am authenticated with valid API credentials
    And products exist in categories "electronics", "clothing", "books"
    When I send a GET request to "/products?category=electronics&min_price=10&max_price=100"
    Then the response status should be 200
    And all returned products should have category "electronics"
    And all returned products should have price between 10 and 100

  @negative @read @not_found
  Scenario: Return 404 for non-existent resource
    Given I am authenticated with valid API credentials
    When I send a GET request to "/products/nonexistent_id"
    Then the response status should be 404
    And the response should include:
      """json
      {
        "status": "error",
        "code": "RESOURCE_NOT_FOUND",
        "message": "Product not found"
      }
      """

  # ===================
  # CRUD OPERATION SCENARIOS - UPDATE
  # ===================

  @primary @functional @crud @update
  Scenario: Update a resource via PUT
    Given I am authenticated with valid API credentials
    And a product exists with ID "prod_456"
    When I send a PUT request to "/products/prod_456" with:
      """json
      {
        "name": "Updated Product Name",
        "description": "Updated description",
        "price": 39.99,
        "category": "electronics"
      }
      """
    Then the response status should be 200
    And the response should reflect the updated values
    And the "updated_at" timestamp should be current

  @functional @crud @partial_update
  Scenario: Partially update a resource via PATCH
    Given I am authenticated with valid API credentials
    And a product exists with ID "prod_789"
    When I send a PATCH request to "/products/prod_789" with:
      """json
      {
        "price": 49.99
      }
      """
    Then the response status should be 200
    And only the price should be updated
    And other fields should remain unchanged

  @negative @update @conflict
  Scenario: Handle concurrent update conflict
    Given I am authenticated with valid API credentials
    And a product exists with ID "prod_conflict"
    And another client has updated the product since my last fetch
    When I send a PUT request to "/products/prod_conflict" with outdated ETag
    Then the response status should be 409
    And the response should include conflict details
    And the response should suggest refetching the resource

  # ===================
  # CRUD OPERATION SCENARIOS - DELETE
  # ===================

  @primary @functional @crud @delete
  Scenario: Delete a resource
    Given I am authenticated with valid API credentials
    And a product exists with ID "prod_to_delete"
    When I send a DELETE request to "/products/prod_to_delete"
    Then the response status should be 204
    And subsequent GET request should return 404
    And a deletion audit log should be created

  @functional @delete @soft_delete
  Scenario: Soft delete preserves audit trail
    Given I am authenticated with admin API credentials
    And a product exists with ID "prod_soft_delete"
    When I send a DELETE request to "/products/prod_soft_delete"
    Then the response status should be 204
    And the product should be marked as deleted
    And admin can still retrieve deleted product with "?include_deleted=true"

  # ===================
  # AUTHENTICATION SCENARIOS
  # ===================

  @security @authentication
  Scenario: Reject requests without authentication
    Given I am not authenticated
    When I send a GET request to "/products"
    Then the response status should be 401
    And the response should include:
      """json
      {
        "status": "error",
        "code": "UNAUTHORIZED",
        "message": "Authentication required"
      }
      """
    And the "WWW-Authenticate" header should be present

  @security @authentication
  Scenario: Reject requests with invalid token
    Given I am authenticated with an invalid token "invalid_token_123"
    When I send a GET request to "/products"
    Then the response status should be 401
    And the response should include error code "INVALID_TOKEN"

  @security @authentication
  Scenario: Reject requests with expired token
    Given I am authenticated with an expired token
    When I send a GET request to "/products"
    Then the response status should be 401
    And the response should include error code "TOKEN_EXPIRED"
    And the response should suggest token refresh

  @security @authorization
  Scenario: Reject requests without required permissions
    Given I am authenticated as a user without admin role
    When I send a DELETE request to "/admin/products/prod_123"
    Then the response status should be 403
    And the response should include:
      """json
      {
        "status": "error",
        "code": "FORBIDDEN",
        "message": "Insufficient permissions"
      }
      """

  # ===================
  # RATE LIMITING SCENARIOS
  # ===================

  @security @rate_limiting
  Scenario: Enforce rate limiting
    Given I am authenticated with valid API credentials
    And I have made @threshold: PRD.035.limit.api.requests_per_minute requests in the current minute
    When I send another request
    Then the response status should be 429
    And the response should include:
      | header             | present |
      | X-RateLimit-Limit  | true    |
      | X-RateLimit-Reset  | true    |
      | Retry-After        | true    |

  # ===================
  # ERROR HANDLING SCENARIOS
  # ===================

  @negative @error_handling @server_error
  Scenario: Handle internal server errors gracefully
    Given the database is temporarily unavailable
    When I send a GET request to "/products"
    Then the response status should be 503
    And the response should include:
      """json
      {
        "status": "error",
        "code": "SERVICE_UNAVAILABLE",
        "message": "Service temporarily unavailable",
        "retry_after": 30
      }
      """
    And the error should be logged with request_id

  @negative @error_handling @timeout
  Scenario: Handle request timeout
    Given a request processing time exceeds @threshold: PRD.035.timeout.request.max
    When the timeout is reached
    Then the response status should be 504
    And the response should include error code "GATEWAY_TIMEOUT"
    And partial operations should be rolled back

  @negative @error_handling @invalid_json
  Scenario: Reject malformed JSON request body
    Given I am authenticated with valid API credentials
    When I send a POST request to "/products" with invalid JSON body
    Then the response status should be 400
    And the response should include error code "INVALID_JSON"
    And the error message should indicate the parse error location

  # ===================
  # VERSIONING SCENARIOS
  # ===================

  @functional @versioning
  Scenario: API version in URL path
    Given I am authenticated with valid API credentials
    When I send a GET request to "/v1/products"
    Then the response status should be 200
    And the response should use v1 format

  @functional @versioning @deprecation
  Scenario: Receive deprecation warning for old API version
    Given I am authenticated with valid API credentials
    When I send a GET request to "/v0/products"
    Then the response status should be 200
    And the response should include header "Deprecation: true"
    And the response should include header "Sunset" with date

  # ===================
  # CONTENT NEGOTIATION SCENARIOS
  # ===================

  @functional @content_type
  Scenario: Return JSON by default
    Given I am authenticated with valid API credentials
    When I send a GET request to "/products/prod_123" without Accept header
    Then the response status should be 200
    And the Content-Type should be "application/json"

  @functional @content_type
  Scenario: Return requested content type
    Given I am authenticated with valid API credentials
    And I set Accept header to "application/xml"
    When I send a GET request to "/products/prod_123"
    Then the response status should be 200
    And the Content-Type should be "application/xml"

  @negative @content_type
  Scenario: Reject unsupported content type
    Given I am authenticated with valid API credentials
    And I set Accept header to "application/unsupported"
    When I send a GET request to "/products"
    Then the response status should be 406
    And the response should list supported content types

  # ===================
  # IDEMPOTENCY SCENARIOS
  # ===================

  @functional @idempotency
  Scenario: Idempotent request handling
    Given I am authenticated with valid API credentials
    And I have an idempotency key "idem_12345"
    When I send a POST request to "/orders" with idempotency key
    And I send the same POST request again with same idempotency key
    Then both responses should be identical
    And only one order should be created

  # ===================
  # WEBHOOK SCENARIOS
  # ===================

  @integration @webhook
  Scenario: Trigger webhook on resource creation
    Given a webhook is configured for "product.created" events
    And the webhook URL is "https://client.example.com/webhooks"
    When I create a new product via POST
    Then a webhook should be sent within @threshold: PRD.035.timeout.webhook.delivery
    And the webhook payload should include:
      | field      | value             |
      | event      | product.created   |
      | timestamp  | ISO-8601 format   |
      | data       | product object    |
    And the webhook should include HMAC signature

  # ===================
  # PERFORMANCE SCENARIOS
  # ===================

  @quality_attribute @performance
  Scenario Outline: API performance under various loads
    Given I am authenticated with valid API credentials
    And system is under <load> load
    When <requests> concurrent requests are made to <endpoint>
    Then <success_rate>% of requests should succeed
    And response time p95 should be less than @threshold: PRD.035.perf.api.<tier>_latency

    Examples:
      | load   | requests | endpoint        | success_rate | tier    |
      | low    | 10       | GET /products   | 100          | p50     |
      | medium | 100      | GET /products   | 99           | p95     |
      | high   | 500      | GET /products   | 95           | p99     |

  # ===================
  # HEALTH CHECK SCENARIOS
  # ===================

  @operational @health
  Scenario: Health check endpoint returns service status
    When I send a GET request to "/health"
    Then the response status should be 200
    And the response should include:
      """json
      {
        "status": "healthy",
        "version": "1.0.0",
        "dependencies": {
          "database": "healthy",
          "cache": "healthy",
          "queue": "healthy"
        }
      }
      """

  @operational @health @degraded
  Scenario: Health check indicates degraded status
    Given the cache service is unavailable
    When I send a GET request to "/health"
    Then the response status should be 200
    And the response should include:
      """json
      {
        "status": "degraded",
        "dependencies": {
          "database": "healthy",
          "cache": "unhealthy",
          "queue": "healthy"
        }
      }
      """

# =============================================================================
# END OF BDD-03.1: REST API Integration
# =============================================================================
