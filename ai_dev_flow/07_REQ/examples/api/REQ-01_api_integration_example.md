---
title: "REQ-01: External API Integration (Example)"
tags:
  - req-example
  - layer-7-artifact
  - example-document
  - api-integration
custom_fields:
  document_type: example
  artifact_type: REQ
  layer: 7
  development_status: example
---

# REQ-01: [EXTERNAL_SERVICE] API Integration (Example)

**MVP Scope**: This example demonstrates an API client integration requirement with external service, including authentication, validation, resilience patterns, and error handling.

> **Purpose**: Show complete REQ structure for API integration with all 11 required sections following REQ-MVP-TEMPLATE.md.

---

## 1. Document Control

| Item | Details |
|------|---------|
| **Status** | Example |
| **Version** | 1.0.0 |
| **Date Created** | 2026-02-08T00:00:00 |
| **Last Updated** | 2026-02-08T00:00:00 |
| **Author** | Integration Team |
| **Priority** | High (P2) |
| **Category** | API |
| **Infrastructure Type** | None |
| **Source Document** | [SYS-01 section 3.2](../06_SYS/SYS-01_integration_layer.md#sys0132) |
| **Verification Method** | BDD + Contract Test + Integration Test |
| **Assigned Team** | Backend Team |
| **SPEC-Ready Score** | ✅ 92% (Target: ≥90%) |
| **CTR-Ready Score** | ✅ 88% (Target: ≥90%) |
| **Template Version** | 1.1 |

---

## 2. Requirement Description

### 2.1 Statement

**The system SHALL** provide an API client to integrate with external service providers, supporting authentication, request/response validation, and resilience patterns including retry with exponential backoff, circuit breaker, and caching.

### 2.2 Context

External API integration is required to:
- Connect to third-party services (payment gateways, data providers, notification services)
- Ensure reliable communication with external systems over unreliable networks
- Handle transient failures gracefully without impacting user experience
- Provide consistent interface for all external service calls
- Enable monitoring and observability of external dependencies

### 2.3 Use Case

**Primary Flow**:
1. Application initiates request to external service via API client
2. Client validates request format and parameters
3. Client adds authentication headers (API key, OAuth token, etc.)
4. Client executes HTTP request with configured timeout
5. Client validates response against expected schema
6. Client returns structured response to application
7. Client logs transaction for observability

**Error Flow**:
- When request times out, client SHALL retry with exponential backoff (max 3 attempts)
- When rate limit exceeded (HTTP 429), client SHALL wait for Retry-After header duration
- When circuit breaker is OPEN, client SHALL fail fast with CircuitBreakerOpenError
- When response validation fails, client SHALL raise ValidationError with details

---

## 3. Functional Specification

### 3.1 Core Functionality

**Required Capabilities**:
- **Request Validation**: Validate request parameters against schema before sending
- **Authentication**: Support multiple auth methods (API Key, OAuth2, Bearer Token, mTLS)
- **HTTP Operations**: Support GET, POST, PUT, DELETE, PATCH methods
- **Response Validation**: Validate response format and HTTP status codes
- **Retry Logic**: Exponential backoff with jitter for transient failures
- **Circuit Breaker**: Fail-fast pattern when external service is unhealthy
- **Response Caching**: Cache successful GET responses with TTL
- **Observability**: Structured logging with correlation IDs and metrics

### 3.2 Business Rules

**ID Format**: `REQ.01.21.SS` (Validation Rule)

| Rule ID | Condition | Action |
|---------|-----------|--------|
| REQ.01.21.01 | IF request timeout AND retry count < max_retries | THEN retry with exponential backoff |
| REQ.01.21.02 | IF HTTP 429 (rate limit) AND Retry-After header present | THEN wait for specified duration before retry |
| REQ.01.21.03 | IF failure rate > 50% in 60 seconds | THEN open circuit breaker for 30 seconds |
| REQ.01.21.04 | IF response status is 2xx AND method is GET | THEN cache response with 300s TTL |
| REQ.01.21.05 | IF circuit breaker is OPEN | THEN raise CircuitBreakerOpenError immediately |
| REQ.01.21.06 | IF response validation fails | THEN raise ValidationError with field details |

### 3.3 Input/Output Specification

**Inputs**:

| Parameter | Type | Required | Validation | Description |
|-----------|------|----------|------------|-------------|
| endpoint | string | Yes | Valid URL path format | API endpoint path (e.g., "/v1/users") |
| method | string | Yes | One of: GET, POST, PUT, DELETE, PATCH | HTTP method |
| headers | object | No | Valid HTTP headers | Additional request headers |
| body | object | No | Valid JSON (for POST/PUT/PATCH) | Request payload |
| params | object | No | Key-value pairs | Query parameters |
| use_cache | boolean | No | Default: true | Whether to use cache for GET requests |

**Outputs**:

| Field | Type | Description |
|-------|------|-------------|
| status_code | integer | HTTP response status code |
| data | object | Response body (parsed JSON) |
| headers | object | Response headers |
| cached | boolean | True if response served from cache |
| response_time_ms | integer | Round-trip response time in milliseconds |

---

## 4. Interface Definition

### 4.1 API Contract

**Python Protocol Definition**:

```python
from typing import Protocol, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

@dataclass
class APIRequest:
    """Request data structure for API client."""
    endpoint: str
    method: HTTPMethod
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, str]] = None
    use_cache: bool = True

@dataclass
class APIResponse:
    """Response data structure from API client."""
    status_code: int
    data: Dict[str, Any]
    headers: Dict[str, str]
    cached: bool = False
    response_time_ms: int = 0

class ExternalAPIClient(Protocol):
    """Protocol for external API client."""
    
    def get(self, endpoint: str, params: Optional[Dict] = None, 
            use_cache: bool = True) -> APIResponse:
        """Execute GET request with optional caching."""
        ...
    
    def post(self, endpoint: str, body: Dict[str, Any]) -> APIResponse:
        """Execute POST request with body."""
        ...
    
    def put(self, endpoint: str, body: Dict[str, Any]) -> APIResponse:
        """Execute PUT request with body."""
        ...
    
    def delete(self, endpoint: str) -> APIResponse:
        """Execute DELETE request."""
        ...
```

### 4.2 Data Schema

```python
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any

class APIRequest(BaseModel):
    """Request data structure validated by Pydantic."""
    endpoint: str = Field(..., pattern=r"^/[a-zA-Z0-9/_-]+$", 
                         description="API endpoint path")
    method: str = Field(..., pattern=r"^(GET|POST|PUT|DELETE|PATCH)$",
                       description="HTTP method")
    headers: Optional[Dict[str, str]] = Field(default=None,
                                             description="Request headers")
    body: Optional[Dict[str, Any]] = Field(default=None,
                                          description="Request body")
    params: Optional[Dict[str, str]] = Field(default=None,
                                            description="Query parameters")
    use_cache: bool = Field(default=True, 
                           description="Use cache for GET requests")

class APIResponse(BaseModel):
    """Response data structure validated by Pydantic."""
    status_code: int = Field(..., ge=100, le=599,
                            description="HTTP status code")
    data: Dict[str, Any] = Field(..., description="Response body")
    headers: Dict[str, str] = Field(..., description="Response headers")
    cached: bool = Field(default=False, 
                        description="Response served from cache")
    response_time_ms: int = Field(..., ge=0,
                                 description="Response time in ms")
```

---

## 5. Error Handling

### 5.1 Error Catalog

| Error Code | HTTP Status | Condition | User Message | System Action |
|------------|-------------|-----------|--------------|---------------|
| API_TIMEOUT | 504 | Request exceeds timeout threshold | External service timeout | Log, retry, alert if persistent |
| RATE_LIMIT_EXCEEDED | 429 | Rate limit exceeded (HTTP 429) | Rate limit exceeded, retry later | Wait for Retry-After, retry |
| CIRCUIT_BREAKER_OPEN | 503 | Circuit breaker is OPEN | Service temporarily unavailable | Fail fast, alert |
| VALIDATION_ERROR | 400 | Request/response validation failed | Invalid request format | Log, return error details |
| AUTHENTICATION_ERROR | 401 | Invalid or missing credentials | Authentication failed | Log, alert security team |
| SERVER_ERROR | 502 | External service returned 5xx | External service error | Log, retry, alert |

### 5.2 Recovery Strategy

| Error Type | Retry? | Fallback | Alert |
|------------|--------|----------|-------|
| Timeout | Yes (3x) | Return cached data (if available) | After retries exhausted |
| Rate limit | Yes (1x) | Wait for Retry-After header | After retry fails |
| Circuit breaker | No | Fail fast with error | Immediately |
| Validation error | No | Return error details | No |
| Authentication error | No | Return error | Immediately (security) |
| Server error | Yes (3x) | Return error | After retries exhausted |

---

## 6. Quality Attributes

### 6.1 Performance (REQ.01.02.01)

| Metric | Target | Measurement |
|--------|--------|-------------|
| p95 Latency | ≤ 500ms | @threshold: PRD-03.perf.api.p95_latency |
| p99 Latency | ≤ 1000ms | @threshold: PRD-03.perf.api.p99_latency |
| Throughput | 1000+ req/s | Under nominal load |
| Cache Hit Rate | ≥ 80% | For cached GET requests |

### 6.2 Security (REQ.01.02.02)

- **Authentication**: mTLS or OAuth2 for service-to-service
- **Authorization**: RBAC for endpoint access control
- **Data Protection**: No PII in logs or error messages
- **Secret Management**: API keys stored in Vault, rotated every 90 days
- **Input Validation**: Strict schema validation on all inputs

### 6.3 Reliability (REQ.01.02.03)

| Metric | Target |
|--------|--------|
| Uptime | 99.9% during business hours |
| Retry Success Rate | ≥ 95% for transient failures |
| Circuit Breaker Accuracy | < 1% false positives |
| Cache Consistency | Eventual consistency within 5s |

---

## 7. Configuration

### 7.1 Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| API_BASE_URL | string | Required | Base URL for external API |
| API_KEY | secret | Required | API authentication key |
| REQUEST_TIMEOUT_MS | integer | 5000 | Request timeout in milliseconds |
| MAX_RETRIES | integer | 3 | Maximum retry attempts |
| CIRCUIT_BREAKER_THRESHOLD | integer | 5 | Failures before opening circuit |
| CIRCUIT_BREAKER_TIMEOUT_S | integer | 30 | Circuit breaker timeout in seconds |
| CACHE_TTL_SECONDS | integer | 300 | Cache TTL for GET responses |
| RATE_LIMIT_PER_MINUTE | integer | 100 | Max requests per minute |

### 7.2 Feature Flags (if applicable)

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| ENABLE_CIRCUIT_BREAKER | boolean | true | Enable circuit breaker pattern |
| ENABLE_CACHING | boolean | true | Enable response caching |
| ENABLE_RETRY | boolean | true | Enable retry with backoff |
| DEBUG_MODE | boolean | false | Enable verbose logging |

---

## 8. Testing Requirements

### 8.1 Logical TDD (Pre-Code)

**Test Strategy Before Implementation**:

```python
# What to test (drives interface design)
def test_api_client_interface():
    """Define expected interface behavior."""
    # Given: Valid request
    request = APIRequest(endpoint="/users", method="GET")
    
    # When: Client executes request
    response = client.execute(request)
    
    # Then: Response should be valid
    assert response.status_code == 200
    assert "data" in response.data
    assert response.response_time_ms > 0

def test_retry_logic():
    """Define retry behavior for transient failures."""
    # Given: Request fails with timeout
    # When: Retry executed
    # Then: Should retry up to MAX_RETRIES times
    pass
```

### 8.2 Unit Tests

- **Request Validation**: Test valid/invalid request formats
- **Response Parsing**: Test JSON parsing and error handling
- **Retry Logic**: Test exponential backoff calculation
- **Circuit Breaker**: Test state transitions (CLOSED → OPEN → HALF_OPEN)
- **Cache Management**: Test cache hit/miss and TTL expiration

### 8.3 Integration Tests

- **External API Simulation**: Test against mock server
- **End-to-End Flow**: Test complete request-response cycle
- **Failure Scenarios**: Test timeout, rate limit, server errors
- **Circuit Breaker**: Test with simulated failures
- **Cache Behavior**: Test caching with actual Redis instance

### 8.4 BDD Scenarios

```gherkin
Feature: API Client Operations

  Scenario: Successful API call with caching
    Given a valid API request
    When the client executes the request
    Then the response should be successful
    And the response should be cached

  Scenario: Circuit breaker opens on failure
    Given the external API is failing
    When failure rate exceeds threshold
    Then the circuit breaker should open
    And subsequent requests should fail fast

  Scenario: Rate limit handling
    Given rate limit is exceeded
    When a request is made
    Then the client should wait for Retry-After duration
    And retry the request
```

---

## 9. Acceptance Criteria

### 9.1 Functional Acceptance

- [ ] API client successfully executes GET, POST, PUT, DELETE requests
- [ ] Request validation rejects invalid parameters with clear error messages
- [ ] Response validation fails gracefully for unexpected formats
- [ ] Authentication headers are correctly added to requests
- [ ] Retry logic executes up to MAX_RETRIES with exponential backoff
- [ ] Circuit breaker transitions correctly between states
- [ ] Cache serves GET responses and respects TTL
- [ ] All errors are logged with correlation IDs

### 9.2 Quality Acceptance

- [ ] p95 latency ≤ 500ms under nominal load (@threshold: PRD-03.perf.api.p95_latency)
- [ ] Retry success rate ≥ 95% for transient failures
- [ ] Circuit breaker false positive rate < 1%
- [ ] Cache hit rate ≥ 80% for repeated GET requests
- [ ] No PII leaked in logs or error messages
- [ ] 99.9% uptime during business hours

---

## 10. Traceability

### 10.1 Upstream References

**Required Tags** (Layer 7):
```markdown
@brd: BRD.01.01.03      # Platform Integration Strategy
@prd: PRD.03.01.02      # API Gateway Product Requirements
@ears: EARS.02.24.01    # External Integration Requirements
@bdd: BDD.05.13.01      # API Client Test Scenarios
@adr: ADR-05            # Circuit Breaker Pattern Decision
@sys: SYS.02.25.01      # Integration Layer Architecture
```

### 10.2 Downstream Artifacts

- **CTR-03**: API Contract for external service interface
- **SPEC-01**: Technical specification for API client implementation
- **BDD-05**: BDD test scenarios for API operations
- **TASKS-08**: Implementation tasks for API client

### 10.3 Traceability Matrix

| Upstream | Requirement ID | This REQ Section | Downstream |
|----------|----------------|------------------|------------|
| BRD.01.01.03 | External Integration | All | SPEC-01, CTR-03 |
| PRD.03.01.02 | API Management | 3, 4, 7 | SPEC-01 |
| SYS.02.25.01 | Integration Layer | 3, 4, 5, 6 | SPEC-01 |
| ADR-05 | Circuit Breaker | 3.1, 5, 6.3 | SPEC-01 |

---

## 11. Implementation Notes

### 11.1 Technical Approach

**Architecture**:
- Client library pattern with Protocol interface
- Async/await for non-blocking I/O (aiohttp)
- Redis for distributed caching
- Circuit breaker state machine with Redis backing

**Key Libraries**:
- `aiohttp`: Async HTTP client
- `pydantic`: Request/response validation
- `redis-py`: Caching backend
- `tenacity`: Retry logic with exponential backoff
- `structlog`: Structured logging

### 11.2 Code Location

```
src/
├── integrations/
│   ├── __init__.py
│   ├── external_api_client.py    # Main client implementation
│   ├── circuit_breaker.py        # Circuit breaker pattern
│   ├── cache_manager.py          # Redis caching layer
│   ├── rate_limiter.py          # Rate limiting
│   └── validators.py            # Request/response validation
└── tests/
    ├── unit/
    │   └── integrations/
    │       ├── test_external_api_client.py
    │       ├── test_circuit_breaker.py
    │       └── test_cache_manager.py
    └── integration/
        └── integrations/
            └── test_api_workflows.py
```

### 11.3 Dependencies

**Runtime Dependencies**:
- aiohttp >= 3.8.0
- pydantic >= 2.0.0
- redis >= 4.5.0
- tenacity >= 8.0.0
- structlog >= 23.0.0

**Development Dependencies**:
- pytest-asyncio >= 0.21.0
- pytest-mock >= 3.10.0
- aioresponses >= 0.7.0

---

## Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-02-08T00:00:00 | Integration Team | Initial version - Complete rewrite to REQ-MVP-TEMPLATE v1.1 structure |
