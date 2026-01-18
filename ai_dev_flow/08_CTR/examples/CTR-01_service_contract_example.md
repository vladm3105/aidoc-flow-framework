---
title: "CTR-01: Service Contract Example"
tags:
  - ctr-example
  - layer-9-artifact
  - example-document
custom_fields:
  document_type: example
  artifact_type: CTR
  layer: 9
  development_status: example
---

# CTR-01: [SERVICE_NAME] API Contract

**Contract ID**: CTR-01
**Service**: [SERVICE_NAME - e.g., User Service, Payment Gateway, Notification Service]
**Type**: [TYPE - e.g., REST API, GraphQL, gRPC, WebSocket]
**Version**: 1.0.0
**Status**: Example

**Owner Team**: [TEAM_NAME]
**Consumers**: [CONSUMER_LIST - e.g., Frontend App, Mobile App, Partner Integrations]

**Created**: [YYYY-MM-DD]
**Updated**: [YYYY-MM-DD]

---

## Purpose

This contract defines the interface between [PROVIDER_SERVICE] and [CONSUMER_SERVICES]. It establishes:
- API endpoints and operations
- Request/response formats
- Authentication and authorization requirements
- Error handling conventions
- Performance guarantees (SLA)

**Contract Guarantees**:
- **Backward Compatibility**: Changes must not break existing consumers
- **Versioning**: API version in URL path (`/v1/`, `/v2/`)
- **Deprecation Policy**: 6-month notice before removing endpoints

---

## Traceability

### Requirements Coverage
| Requirement | Description | Priority |
|-------------|-------------|----------|
| REQ-XXX | [REQUIREMENT - e.g., User authentication] | High |
| REQ-YYY | [REQUIREMENT - e.g., Data validation] | High |
| REQ-ZZZ | [REQUIREMENT - e.g., Rate limiting] | Medium |

### Architecture Decisions
| ADR | Decision | Impact |
|-----|----------|--------|
| ADR-XXX | [DECISION - e.g., REST over GraphQL] | Simpler client implementation |
| ADR-YYY | [DECISION - e.g., JWT authentication] | Stateless authentication |

### Related Specifications
| Component | Specification | Relationship |
|-----------|---------------|--------------|
| [COMPONENT] | SPEC-XXX | Implements this contract |
| [COMPONENT] | SPEC-YYY | Consumes this contract |

---

## API Overview

### Base Configuration
```
Base URL: [URL - e.g., https://api.example.com]
API Prefix: /api/v1
Content-Type: application/json
Authentication: Bearer Token (JWT)
```

### Supported Operations
| Operation | Endpoint | Method | Description |
|-----------|----------|--------|-------------|
| [OPERATION_1] | [PATH - e.g., /users] | POST | [DESC - e.g., Create new user] |
| [OPERATION_2] | [PATH - e.g., /users/{id}] | GET | [DESC - e.g., Retrieve user by ID] |
| [OPERATION_3] | [PATH - e.g., /users/{id}] | PUT | [DESC - e.g., Update user] |
| [OPERATION_4] | [PATH - e.g., /users/{id}] | DELETE | [DESC - e.g., Delete user] |
| [OPERATION_5] | [PATH - e.g., /users/search] | POST | [DESC - e.g., Search users] |

---

## Authentication

### Authentication Flow
1. Client obtains JWT token from `/auth/login`
2. Client includes token in `Authorization: Bearer {token}` header
3. Server validates token signature and expiration
4. Server extracts user identity and permissions

### Token Format
```json
{
  "sub": "[USER_ID]",
  "name": "[USER_NAME]",
  "email": "[USER_EMAIL]",
  "roles": ["[ROLE_1]", "[ROLE_2]"],
  "permissions": ["[PERMISSION_1]", "[PERMISSION_2]"],
  "iat": 1234567890,
  "exp": 1234571490
}
```

### Error Responses
- **401 Unauthorized**: Token missing, invalid, or expired
- **403 Forbidden**: Valid token but insufficient permissions

---

## Endpoints

### 1. Create [RESOURCE]

**Endpoint**: `POST /api/v1/[RESOURCE]`

**Description**: Creates a new [RESOURCE] with the provided data.

**Request**:
```json
{
  "[FIELD_1]": "[TYPE - e.g., string]",  // [DESCRIPTION]
  "[FIELD_2]": "[TYPE - e.g., integer]", // [DESCRIPTION]
  "[FIELD_3]": {                          // [NESTED_OBJECT]
    "[SUB_FIELD_1]": "[TYPE]",
    "[SUB_FIELD_2]": "[TYPE]"
  },
  "[FIELD_4]": ["[ARRAY_TYPE]"]          // [ARRAY_DESCRIPTION]
}
```

**Request Example**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30,
  "address": {
    "street": "123 Main St",
    "city": "Anytown",
    "country": "US"
  },
  "tags": ["customer", "premium"]
}
```

**Validation Rules**:
- `[FIELD_1]`: Required, [CONSTRAINTS - e.g., 1-255 characters, alphanumeric only]
- `[FIELD_2]`: Optional, [CONSTRAINTS - e.g., range 18-120]
- `[FIELD_3]`: Required if [CONDITION]
- `[FIELD_4]`: Max [COUNT] elements

**Success Response** (201 Created):
```json
{
  "id": "[UUID]",
  "[FIELD_1]": "[VALUE]",
  "[FIELD_2]": "[VALUE]",
  "created_at": "[ISO8601_TIMESTAMP]",
  "updated_at": "[ISO8601_TIMESTAMP]",
  "created_by": "[USER_ID]"
}
```

**Error Responses**:
```json
// 400 Bad Request - Validation Error
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "[FIELD_PATH]",
        "error": "[ERROR_MESSAGE]",
        "expected": "[EXPECTED_FORMAT]"
      }
    ]
  },
  "request_id": "[CORRELATION_ID]",
  "timestamp": "[ISO8601]"
}

// 409 Conflict - Resource Already Exists
{
  "error": {
    "code": "RESOURCE_EXISTS",
    "message": "[RESOURCE] with email 'john@example.com' already exists",
    "existing_resource_id": "[UUID]"
  }
}
```

**Rate Limiting**: 100 requests/minute per user

---

### 2. Retrieve [RESOURCE] by ID

**Endpoint**: `GET /api/v1/[RESOURCE]/{id}`

**Description**: Retrieves a single [RESOURCE] by its unique identifier.

**Path Parameters**:
- `id` (string, UUID): Unique identifier of the [RESOURCE]

**Success Response** (200 OK):
```json
{
  "id": "[UUID]",
  "[FIELD_1]": "[VALUE]",
  "[FIELD_2]": "[VALUE]",
  "[FIELD_3]": { ... },
  "created_at": "[ISO8601]",
  "updated_at": "[ISO8601]",
  "created_by": "[USER_ID]",
  "updated_by": "[USER_ID]"
}
```

**Error Responses**:
```json
// 404 Not Found
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "[RESOURCE] with ID '{id}' not found"
  }
}
```

**Caching**:
- `Cache-Control: private, max-age=300` (5 minutes)
- `ETag` header for conditional requests

---

### 3. Update [RESOURCE]

**Endpoint**: `PUT /api/v1/[RESOURCE]/{id}`

**Description**: Updates an existing [RESOURCE]. Partial updates supported (PATCH semantics).

**Request** (same as Create, but all fields optional):
```json
{
  "[FIELD_1]": "[NEW_VALUE]",  // Only include fields to update
  "[FIELD_2]": "[NEW_VALUE]"
}
```

**Success Response** (200 OK):
```json
{
  "id": "[UUID]",
  // ... updated fields ...
  "updated_at": "[ISO8601]",
  "updated_by": "[USER_ID]",
  "version": 2  // Optimistic locking version
}
```

**Error Responses**:
```json
// 409 Conflict - Optimistic Lock Failure
{
  "error": {
    "code": "CONCURRENT_MODIFICATION",
    "message": "[RESOURCE] was modified by another user",
    "current_version": 3,
    "your_version": 2
  }
}
```

---

### 4. Delete [RESOURCE]

**Endpoint**: `DELETE /api/v1/[RESOURCE]/{id}`

**Description**: Soft-deletes a [RESOURCE] (marks as deleted, does not physically remove).

**Success Response** (204 No Content):
- Empty response body

**Error Responses**:
```json
// 404 Not Found
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "[RESOURCE] with ID '{id}' not found or already deleted"
  }
}
```

---

### 5. Search [RESOURCE]

**Endpoint**: `POST /api/v1/[RESOURCE]/search`

**Description**: Searches for [RESOURCE] matching criteria. Uses POST to support complex queries.

**Request**:
```json
{
  "filters": {
    "[FIELD_1]": {
      "operator": "[OPERATOR - e.g., eq, ne, gt, lt, in, like]",
      "value": "[VALUE]"
    },
    "[FIELD_2]": {
      "operator": "in",
      "value": ["[VALUE_1]", "[VALUE_2]"]
    }
  },
  "sort": [
    { "field": "[FIELD]", "order": "asc|desc" }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20  // Max 100
  }
}
```

**Success Response** (200 OK):
```json
{
  "results": [
    { /* [RESOURCE] object */ },
    { /* [RESOURCE] object */ }
  ],
  "pagination": {
    "total_count": 150,
    "page": 1,
    "page_size": 20,
    "total_pages": 8
  },
  "links": {
    "self": "/api/v1/[RESOURCE]/search?page=1",
    "next": "/api/v1/[RESOURCE]/search?page=2",
    "prev": null,
    "first": "/api/v1/[RESOURCE]/search?page=1",
    "last": "/api/v1/[RESOURCE]/search?page=8"
  }
}
```

---

## Data Models

### [RESOURCE] Model
```typescript
interface [RESOURCE_TYPE] {
  id: string;                    // UUID v4
  [FIELD_1]: string;             // [DESCRIPTION, CONSTRAINTS]
  [FIELD_2]: number;             // [DESCRIPTION, CONSTRAINTS]
  [FIELD_3]: [NESTED_TYPE];     // [DESCRIPTION]
  [FIELD_4]: [TYPE][];          // [DESCRIPTION]
  created_at: string;            // ISO8601 timestamp
  updated_at: string;            // ISO8601 timestamp
  created_by: string;            // User ID
  updated_by: string;            // User ID
  version: number;               // Optimistic locking
  deleted_at?: string;           // Soft delete timestamp (optional)
}
```

### Error Response Model
```typescript
interface ErrorResponse {
  error: {
    code: string;                // Machine-readable error code
    message: string;             // Human-readable message
    details?: Array<{            // Optional validation details
      field: string;
      error: string;
      expected?: string;
    }>;
  };
  request_id: string;            // Correlation ID for tracing
  timestamp: string;             // ISO8601
}
```

---

## Error Handling

### HTTP Status Codes
| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT |
| 201 | Created | Successful POST (resource created) |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation error, malformed JSON |
| 401 | Unauthorized | Authentication required or failed |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource already exists, version conflict |
| 422 | Unprocessable Entity | Business rule violation |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |
| 503 | Service Unavailable | Temporary unavailability |

### Error Codes
| Code | HTTP Status | Description |
|------|-------------|-------------|
| VALIDATION_ERROR | 400 | Request validation failed |
| AUTHENTICATION_FAILED | 401 | Invalid credentials |
| TOKEN_EXPIRED | 401 | JWT token expired |
| INSUFFICIENT_PERMISSIONS | 403 | User lacks required permissions |
| RESOURCE_NOT_FOUND | 404 | Requested resource doesn't exist |
| RESOURCE_EXISTS | 409 | Duplicate resource |
| CONCURRENT_MODIFICATION | 409 | Optimistic lock failure |
| BUSINESS_RULE_VIOLATION | 422 | Operation violates business rules |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Unexpected server error |

---

## Performance SLA

### Response Time Targets
| Operation | p50 | p95 | p99 |
|-----------|-----|-----|-----|
| GET by ID | < 50ms | < 100ms | < 200ms |
| POST (Create) | < 100ms | < 300ms | < 500ms |
| PUT (Update) | < 100ms | < 300ms | < 500ms |
| DELETE | < 50ms | < 100ms | < 200ms |
| POST (Search) | < 200ms | < 500ms | < 1s |

### Availability
- **Target**: 99.9% uptime (excluding planned maintenance)
- **Maintenance Window**: Sundays 2-4 AM [TIMEZONE]

### Rate Limits
| Consumer Type | Requests/Minute | Burst Allowance |
|---------------|-----------------|-----------------|
| Authenticated User | 100 | 20 |
| Service Account | 1000 | 100 |
| Anonymous | 10 | 5 |

**Rate Limit Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 75
X-RateLimit-Reset: 1234567890 (Unix timestamp)
```

---

## Versioning & Deprecation

### Versioning Strategy
- **URL Path Versioning**: `/api/v1/`, `/api/v2/`
- **Major Version**: Breaking changes (incompatible)
- **Minor Version**: Backward-compatible additions (no URL change)

### Deprecation Process
1. **Announcement** (T-6 months): Deprecation notice in docs, headers
2. **Warning Period** (T-3 months): Warning header on deprecated endpoints
3. **Sunset** (T-0): Endpoint returns 410 Gone

**Deprecation Headers**:
```
Deprecation: true
Sunset: Sat, 31 Dec 2024 23:59:59 GMT
Link: </api/v2/users>; rel="successor-version"
```

---

## security

### Authentication
- **Required**: All endpoints except `/health`, `/metrics`
- **Type**: Bearer Token (JWT)
- **Token Lifetime**: 15 minutes (access), 7 days (refresh)

### Authorization
- **Model**: Role-Based Access Control (RBAC)
- **Enforcement**: Every endpoint checks permissions
- **Principle**: Least privilege

### Data Protection
- **In Transit**: TLS 1.3+
- **At Rest**: AES-256 encryption
- **PII Fields**: Logged only in encrypted form

### Audit Logging
- **Events**: All mutations (POST, PUT, DELETE)
- **Data**: User ID, timestamp, operation, before/after state
- **Retention**: 7 years

---

## Testing

### Contract Testing
**Tool**: [TOOL - e.g., Pact, Spring Cloud Contract]

**Provider Verification**:
- Provider must pass all consumer contract tests
- Automated in CI/CD pipeline

**Consumer Verification**:
- Consumers must verify against OpenAPI spec
- Breaking changes detected automatically

### Integration Testing
- **Environment**: Staging environment with test data
- **Approach**: Automated test suite covering all endpoints
- **Frequency**: On every deployment

---

## Monitoring & Observability

### Metrics
- `http_requests_total` (counter by endpoint, method, status)
- `http_request_duration_seconds` (histogram)
- `http_active_requests` (gauge)
- `http_errors_total` (counter by error_code)

### Logging
- **Format**: Structured JSON
- **Fields**: request_id, user_id, endpoint, method, status, latency_ms, error
- **Sampling**: 100% for errors, 10% for success

### Tracing
- **Standard**: OpenTelemetry
- **Propagation**: `traceparent` header (W3C Trace Context)
- **Sampling**: 10% of requests

---

## Migration Guide

### From v0 (Legacy) to v1 (This Contract)
| Legacy Endpoint | New Endpoint | Changes |
|-----------------|--------------|---------|
| `/old/path` | `/api/v1/new/path` | Field renamed: `old_field` → `[FIELD_1]` |

**Compatibility Period**: 6 months parallel support

---

## OpenAPI Specification

**Full OpenAPI 3.0 specification**: See companion file `CTR-01_service_contract_example.yaml`

---

## Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | [YYYY-MM-DD] | Initial release | [AUTHOR] |

---

## Contact

**Team**: [TEAM_NAME]
**Slack Channel**: [CHANNEL]
**Email**: [TEAM_EMAIL]
**On-Call**: [ONCALL_SCHEDULE]

---

**Example Usage**: This is a template contract. Replace all [PLACEHOLDERS] with your service-specific values. Generate the companion OpenAPI YAML using the provided template.
