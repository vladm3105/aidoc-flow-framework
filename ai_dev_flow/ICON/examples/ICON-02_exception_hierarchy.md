# =============================================================================
# ICON-02: Exception Hierarchy Example
# =============================================================================
# Example Implementation Contract demonstrating typed exception classes
# with error codes, retry semantics, and error categorization
# =============================================================================
---
title: "ICON-02: Payment Service Exception Hierarchy"
tags:
  - implementation-contract
  - layer-11-artifact
  - shared-architecture
  - exception-hierarchy
  - example
custom_fields:
  document_type: implementation_contract
  artifact_type: ICON
  layer: 11
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  contract_type: exception
  provider_tasks: TASKS-015
  consumer_count: 4
  providers: [TASKS-015]
  consumers: [TASKS-016, TASKS-017, TASKS-018, TASKS-019]
---

# ICON-02: Payment Service Exception Hierarchy

## Document Control

| Item | Details |
|------|---------|
| **Status** | Active |
| **Version** | 1.0.0 |
| **Date Created** | 2025-12-29 |
| **Last Updated** | 2025-12-29 |
| **Author** | AI Development Team |
| **Contract Type** | Exception Hierarchy |
| **Providers** | TASKS-015 (Payment Processing Service) |
| **Consumers** | TASKS-016, TASKS-017, TASKS-018, TASKS-019 |

---

## 3. Executive Summary

This contract defines a comprehensive exception hierarchy for the payment processing service. It establishes typed exception classes with error codes, retry semantics, and categorization to enable consistent error handling across all payment-related services and provide meaningful feedback to clients.

### 3.1 Scope

**Purpose**: Enable consistent, type-safe error handling across payment processing
**Boundary**: Payment domain exceptions only; excludes infrastructure errors
**Complexity**: 3/5

---

## 1. Contract Definition

### 1.1 Contract Type

**Type**: Exception Hierarchy

**Rationale**: Payment processing requires granular error categorization for:
- Client feedback (user-actionable vs system errors)
- Retry decisions (transient vs permanent failures)
- Monitoring and alerting (severity classification)
- Audit trail (error code tracking)

### 1.2 Interface Specification

```python
"""
Payment Service Exception Hierarchy
====================================
Defines typed exceptions with error codes, retry semantics,
and categorization for the payment processing domain.

Error Code Format: PAY-{CATEGORY}-{NUMBER}
  - PAY-VAL-XXX: Validation errors (4XX client errors)
  - PAY-AUTH-XXX: Authorization errors (401/403)
  - PAY-PROC-XXX: Processing errors (5XX server errors)
  - PAY-EXT-XXX: External service errors (502/503/504)
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime


class ErrorCategory(str, Enum):
    """Error categorization for monitoring and alerting."""
    VALIDATION = "validation"      # Client input errors
    AUTHORIZATION = "authorization" # Auth/permission errors
    PROCESSING = "processing"       # Business logic errors
    EXTERNAL = "external"           # Third-party service errors
    SYSTEM = "system"               # Infrastructure errors


class RetryStrategy(str, Enum):
    """Retry semantics for exception handling."""
    NO_RETRY = "no_retry"           # Permanent failure, do not retry
    IMMEDIATE = "immediate"          # Retry immediately (transient)
    EXPONENTIAL = "exponential"      # Exponential backoff
    FIXED_DELAY = "fixed_delay"      # Fixed delay between retries


@dataclass(frozen=True)
class ErrorCode:
    """Structured error code with metadata."""
    code: str                        # e.g., "PAY-VAL-001"
    category: ErrorCategory
    http_status: int
    retry_strategy: RetryStrategy
    max_retries: int = 0
    base_delay_ms: int = 0

    def __str__(self) -> str:
        return self.code


# =============================================================================
# Error Code Registry
# =============================================================================

class PaymentErrorCodes:
    """Central registry of payment error codes."""

    # Validation Errors (PAY-VAL-XXX) - HTTP 400
    INVALID_CARD_NUMBER = ErrorCode(
        code="PAY-VAL-001",
        category=ErrorCategory.VALIDATION,
        http_status=400,
        retry_strategy=RetryStrategy.NO_RETRY
    )
    INVALID_EXPIRY_DATE = ErrorCode(
        code="PAY-VAL-002",
        category=ErrorCategory.VALIDATION,
        http_status=400,
        retry_strategy=RetryStrategy.NO_RETRY
    )
    INVALID_CVV = ErrorCode(
        code="PAY-VAL-003",
        category=ErrorCategory.VALIDATION,
        http_status=400,
        retry_strategy=RetryStrategy.NO_RETRY
    )
    INVALID_AMOUNT = ErrorCode(
        code="PAY-VAL-004",
        category=ErrorCategory.VALIDATION,
        http_status=400,
        retry_strategy=RetryStrategy.NO_RETRY
    )
    INVALID_CURRENCY = ErrorCode(
        code="PAY-VAL-005",
        category=ErrorCategory.VALIDATION,
        http_status=400,
        retry_strategy=RetryStrategy.NO_RETRY
    )
    MISSING_REQUIRED_FIELD = ErrorCode(
        code="PAY-VAL-006",
        category=ErrorCategory.VALIDATION,
        http_status=400,
        retry_strategy=RetryStrategy.NO_RETRY
    )

    # Authorization Errors (PAY-AUTH-XXX) - HTTP 401/403
    CARD_DECLINED = ErrorCode(
        code="PAY-AUTH-001",
        category=ErrorCategory.AUTHORIZATION,
        http_status=402,
        retry_strategy=RetryStrategy.NO_RETRY
    )
    INSUFFICIENT_FUNDS = ErrorCode(
        code="PAY-AUTH-002",
        category=ErrorCategory.AUTHORIZATION,
        http_status=402,
        retry_strategy=RetryStrategy.NO_RETRY
    )
    CARD_EXPIRED = ErrorCode(
        code="PAY-AUTH-003",
        category=ErrorCategory.AUTHORIZATION,
        http_status=402,
        retry_strategy=RetryStrategy.NO_RETRY
    )
    FRAUD_SUSPECTED = ErrorCode(
        code="PAY-AUTH-004",
        category=ErrorCategory.AUTHORIZATION,
        http_status=403,
        retry_strategy=RetryStrategy.NO_RETRY
    )
    MERCHANT_NOT_AUTHORIZED = ErrorCode(
        code="PAY-AUTH-005",
        category=ErrorCategory.AUTHORIZATION,
        http_status=403,
        retry_strategy=RetryStrategy.NO_RETRY
    )

    # Processing Errors (PAY-PROC-XXX) - HTTP 500/422
    DUPLICATE_TRANSACTION = ErrorCode(
        code="PAY-PROC-001",
        category=ErrorCategory.PROCESSING,
        http_status=409,
        retry_strategy=RetryStrategy.NO_RETRY
    )
    TRANSACTION_NOT_FOUND = ErrorCode(
        code="PAY-PROC-002",
        category=ErrorCategory.PROCESSING,
        http_status=404,
        retry_strategy=RetryStrategy.NO_RETRY
    )
    REFUND_EXCEEDS_ORIGINAL = ErrorCode(
        code="PAY-PROC-003",
        category=ErrorCategory.PROCESSING,
        http_status=422,
        retry_strategy=RetryStrategy.NO_RETRY
    )
    TRANSACTION_ALREADY_REFUNDED = ErrorCode(
        code="PAY-PROC-004",
        category=ErrorCategory.PROCESSING,
        http_status=409,
        retry_strategy=RetryStrategy.NO_RETRY
    )

    # External Service Errors (PAY-EXT-XXX) - HTTP 502/503/504
    GATEWAY_TIMEOUT = ErrorCode(
        code="PAY-EXT-001",
        category=ErrorCategory.EXTERNAL,
        http_status=504,
        retry_strategy=RetryStrategy.EXPONENTIAL,
        max_retries=3,
        base_delay_ms=1000
    )
    GATEWAY_UNAVAILABLE = ErrorCode(
        code="PAY-EXT-002",
        category=ErrorCategory.EXTERNAL,
        http_status=503,
        retry_strategy=RetryStrategy.EXPONENTIAL,
        max_retries=5,
        base_delay_ms=2000
    )
    GATEWAY_ERROR = ErrorCode(
        code="PAY-EXT-003",
        category=ErrorCategory.EXTERNAL,
        http_status=502,
        retry_strategy=RetryStrategy.FIXED_DELAY,
        max_retries=2,
        base_delay_ms=5000
    )
    NETWORK_ERROR = ErrorCode(
        code="PAY-EXT-004",
        category=ErrorCategory.EXTERNAL,
        http_status=503,
        retry_strategy=RetryStrategy.IMMEDIATE,
        max_retries=1
    )


# =============================================================================
# Base Exception Classes
# =============================================================================

@dataclass
class PaymentException(Exception):
    """
    Base exception for all payment-related errors.

    Attributes:
        error_code: Structured error code with metadata
        message: Human-readable error message
        details: Additional context (masked for security)
        transaction_id: Associated transaction ID if available
        timestamp: When the error occurred
        correlation_id: Request correlation ID for tracing
    """
    error_code: ErrorCode
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    transaction_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None

    def __post_init__(self):
        super().__init__(self.message)

    @property
    def is_retryable(self) -> bool:
        """Check if this error should be retried."""
        return self.error_code.retry_strategy != RetryStrategy.NO_RETRY

    @property
    def http_status(self) -> int:
        """HTTP status code for API responses."""
        return self.error_code.http_status

    @property
    def category(self) -> ErrorCategory:
        """Error category for monitoring."""
        return self.error_code.category

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for API response."""
        return {
            "error": {
                "code": str(self.error_code),
                "message": self.message,
                "category": self.category.value,
                "retryable": self.is_retryable,
                "transaction_id": self.transaction_id,
                "timestamp": self.timestamp.isoformat(),
                "correlation_id": self.correlation_id,
            }
        }


# =============================================================================
# Specialized Exception Classes
# =============================================================================

class ValidationError(PaymentException):
    """Client input validation failures."""

    def __init__(
        self,
        error_code: ErrorCode,
        field_name: str,
        invalid_value: Any = None,
        constraint: str = "",
        correlation_id: Optional[str] = None
    ):
        # Mask sensitive values
        masked_value = self._mask_sensitive(field_name, invalid_value)
        message = f"Validation failed for '{field_name}': {constraint}"

        super().__init__(
            error_code=error_code,
            message=message,
            details={"field": field_name, "value": masked_value, "constraint": constraint},
            correlation_id=correlation_id
        )
        self.field_name = field_name

    @staticmethod
    def _mask_sensitive(field_name: str, value: Any) -> str:
        """Mask sensitive field values for logging."""
        sensitive_fields = {"card_number", "cvv", "pin", "password"}
        if field_name.lower() in sensitive_fields:
            return "***MASKED***"
        if isinstance(value, str) and len(value) > 4:
            return f"{value[:2]}...{value[-2:]}"
        return str(value) if value else "null"


class AuthorizationError(PaymentException):
    """Payment authorization failures from issuer/processor."""

    def __init__(
        self,
        error_code: ErrorCode,
        decline_reason: str,
        card_last_four: Optional[str] = None,
        transaction_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        message = f"Payment authorization failed: {decline_reason}"

        super().__init__(
            error_code=error_code,
            message=message,
            details={"decline_reason": decline_reason, "card_last_four": card_last_four},
            transaction_id=transaction_id,
            correlation_id=correlation_id
        )
        self.decline_reason = decline_reason


class ProcessingError(PaymentException):
    """Business logic and processing failures."""

    def __init__(
        self,
        error_code: ErrorCode,
        reason: str,
        transaction_id: Optional[str] = None,
        original_amount: Optional[float] = None,
        requested_amount: Optional[float] = None,
        correlation_id: Optional[str] = None
    ):
        message = f"Processing error: {reason}"
        details = {"reason": reason}
        if original_amount is not None:
            details["original_amount"] = original_amount
        if requested_amount is not None:
            details["requested_amount"] = requested_amount

        super().__init__(
            error_code=error_code,
            message=message,
            details=details,
            transaction_id=transaction_id,
            correlation_id=correlation_id
        )


class ExternalServiceError(PaymentException):
    """Third-party payment gateway failures."""

    def __init__(
        self,
        error_code: ErrorCode,
        service_name: str,
        original_error: Optional[str] = None,
        response_time_ms: Optional[int] = None,
        transaction_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        message = f"External service error from {service_name}"
        if original_error:
            message += f": {original_error}"

        super().__init__(
            error_code=error_code,
            message=message,
            details={
                "service": service_name,
                "original_error": original_error,
                "response_time_ms": response_time_ms
            },
            transaction_id=transaction_id,
            correlation_id=correlation_id
        )
        self.service_name = service_name
        self.response_time_ms = response_time_ms
```

---

## 2. Provider Requirements

### 2.1 Implementation Obligations

**Provider TASKS**: TASKS-015 (Payment Processing Service)

**Requirements**:
- [ ] Implement all exception classes as defined
- [ ] Use error codes consistently across all error paths
- [ ] Include correlation_id in all exceptions
- [ ] Log exceptions with appropriate severity levels
- [ ] Never expose sensitive data in exception messages

### 2.2 Validation Criteria

**Type Checking**:
```bash
mypy --strict src/services/payment/exceptions.py
```

**Runtime Validation**:
```python
# Verify exception hierarchy
assert issubclass(ValidationError, PaymentException)
assert issubclass(AuthorizationError, PaymentException)
assert issubclass(ProcessingError, PaymentException)
assert issubclass(ExternalServiceError, PaymentException)
```

---

## 3. Consumer Requirements

### 3.1 Usage Obligations

**Consumer TASKS**: TASKS-016, TASKS-017, TASKS-018, TASKS-019

**Requirements**:
- [ ] Import exceptions from contracts module
- [ ] Catch specific exception types, not base Exception
- [ ] Check `is_retryable` before retry attempts
- [ ] Use `to_dict()` for API error responses
- [ ] Log correlation_id for distributed tracing

### 3.2 Dependency Management

**Import Pattern**:
```python
from contracts.payment.exceptions import (
    PaymentException,
    ValidationError,
    AuthorizationError,
    ProcessingError,
    ExternalServiceError,
    PaymentErrorCodes,
)

async def process_payment(request: PaymentRequest) -> PaymentResponse:
    """Process payment with proper exception handling."""
    try:
        # ... payment logic
        pass
    except ValidationError as e:
        # Client error - return 400 with details
        logger.warning(f"Validation error: {e.error_code}", extra={"correlation_id": e.correlation_id})
        return JSONResponse(status_code=e.http_status, content=e.to_dict())
    except AuthorizationError as e:
        # Authorization failure - return 402/403
        logger.info(f"Authorization declined: {e.decline_reason}", extra={"correlation_id": e.correlation_id})
        return JSONResponse(status_code=e.http_status, content=e.to_dict())
    except ExternalServiceError as e:
        if e.is_retryable:
            # Queue for retry
            await retry_queue.enqueue(request, delay_ms=e.error_code.base_delay_ms)
        logger.error(f"External service error: {e.service_name}", extra={"correlation_id": e.correlation_id})
        return JSONResponse(status_code=e.http_status, content=e.to_dict())
```

---

## 4. Change Management

### 4.1 Versioning Strategy

**Semantic Versioning**:
- **Major**: New exception classes, removed error codes
- **Minor**: New error codes, additional exception attributes
- **Patch**: Message updates, documentation fixes

### 4.2 Breaking Change Protocol

**Process**:
1. Deprecate old error codes (add `deprecated: True` flag)
2. Announce deprecation to all consumers (6-month window)
3. Add migration mapping in error code registry
4. Remove deprecated codes in next major version

### 4.3 Change History

| Version | Date | Changes | Impact |
|---------|------|---------|--------|
| 1.0.0 | 2025-12-29 | Initial exception hierarchy | N/A |

---

## 5. Testing Requirements

### 5.1 Provider Tests

**Contract Compliance**:
```python
import pytest
from contracts.payment.exceptions import (
    PaymentException,
    ValidationError,
    PaymentErrorCodes,
)

class TestExceptionHierarchy:
    """Verify exception hierarchy contract compliance."""

    def test_validation_error_structure(self):
        """ValidationError includes required fields."""
        error = ValidationError(
            error_code=PaymentErrorCodes.INVALID_CARD_NUMBER,
            field_name="card_number",
            invalid_value="1234",
            constraint="must be 16 digits",
            correlation_id="req-123"
        )

        assert error.http_status == 400
        assert error.is_retryable is False
        assert error.field_name == "card_number"
        assert "card_number" in error.message

    def test_sensitive_data_masking(self):
        """Sensitive fields are masked in error details."""
        error = ValidationError(
            error_code=PaymentErrorCodes.INVALID_CVV,
            field_name="cvv",
            invalid_value="123",
            constraint="must be 3 digits"
        )

        assert error.details["value"] == "***MASKED***"

    def test_to_dict_serialization(self):
        """Exception serializes to API response format."""
        error = ValidationError(
            error_code=PaymentErrorCodes.INVALID_AMOUNT,
            field_name="amount",
            invalid_value=-100,
            constraint="must be positive"
        )

        response = error.to_dict()
        assert "error" in response
        assert response["error"]["code"] == "PAY-VAL-004"
        assert response["error"]["retryable"] is False
```

### 5.2 Consumer Tests

**Integration Tests**:
```python
import pytest
from unittest.mock import AsyncMock
from contracts.payment.exceptions import ExternalServiceError, PaymentErrorCodes

@pytest.fixture
def retry_queue():
    """Mock retry queue for testing."""
    return AsyncMock()

async def test_retryable_error_handling(retry_queue):
    """External service errors trigger retry when retryable."""
    error = ExternalServiceError(
        error_code=PaymentErrorCodes.GATEWAY_TIMEOUT,
        service_name="stripe",
        correlation_id="req-456"
    )

    assert error.is_retryable is True
    assert error.error_code.max_retries == 3
    assert error.error_code.base_delay_ms == 1000
```

---

## 6. Documentation

### 6.1 Usage Examples

**Raising Exceptions**:
```python
# Validation error
raise ValidationError(
    error_code=PaymentErrorCodes.INVALID_CARD_NUMBER,
    field_name="card_number",
    invalid_value=card_number,
    constraint="Card number must be 16 digits",
    correlation_id=request.correlation_id
)

# External service error with retry
raise ExternalServiceError(
    error_code=PaymentErrorCodes.GATEWAY_TIMEOUT,
    service_name="stripe",
    response_time_ms=30000,
    transaction_id=txn_id,
    correlation_id=request.correlation_id
)
```

### 6.2 Common Patterns

**Error Response Middleware**:
```python
@app.exception_handler(PaymentException)
async def payment_exception_handler(request: Request, exc: PaymentException):
    """Centralized payment exception handling."""
    logger.log(
        level=logging.ERROR if exc.http_status >= 500 else logging.WARNING,
        msg=f"Payment error: {exc.error_code}",
        extra={
            "correlation_id": exc.correlation_id,
            "category": exc.category.value,
            "retryable": exc.is_retryable
        }
    )
    return JSONResponse(status_code=exc.http_status, content=exc.to_dict())
```

### 6.3 Anti-Patterns

**Avoid**:
- Catching base `Exception` instead of specific types
- Exposing raw card numbers in error messages
- Retrying non-retryable errors
- Ignoring correlation_id in error logging

---

## 7. Traceability

### 7.1 Upstream Artifacts

```markdown
@spec: SPEC-05         # Payment Processing Specification
@req: REQ.05.02.01     # Error Handling Requirements
@adr: ADR-03           # Exception Handling Architecture Decision
```

### 7.2 Provider/Consumer Tags

**This Contract**:
```markdown
@icon: ICON-02:PaymentExceptionHierarchy
```

**Provider TASKS** (TASKS-015):
```markdown
@icon: ICON-02:PaymentExceptionHierarchy
@icon-role: provider
```

**Consumer TASKS** (TASKS-016, TASKS-017, TASKS-018, TASKS-019):
```markdown
@icon: ICON-02:PaymentExceptionHierarchy
@icon-role: consumer
```

---

## 8. References

### 8.1 Internal Documentation
- [IMPLEMENTATION_CONTRACTS_GUIDE.md](../TASKS/IMPLEMENTATION_CONTRACTS_GUIDE.md)
- [TASKS-TEMPLATE.md](../TASKS/TASKS-TEMPLATE.md)
- [TRACEABILITY.md](../TRACEABILITY.md)

### 8.2 Related Contracts
- ICON-03: Order State Machine Contract
- ICON-04: Payment Data Model Contract

### 8.3 Provider TASKS
- TASKS-015: Payment Processing Service Implementation

### 8.4 Consumer TASKS
- TASKS-016: Order Service Integration
- TASKS-017: Checkout API Endpoint
- TASKS-018: Refund Processing Service
- TASKS-019: Payment Webhook Handler

---

## 9. Validation Gates

### 9.1 Pre-Activation Validation

```bash
# Verify exception hierarchy
python -c "from contracts.payment.exceptions import *; print('Import successful')"

# Type check
mypy --strict src/contracts/payment/exceptions.py

# Run contract tests
pytest tests/contracts/test_payment_exceptions.py -v
```

---

## 10. Document Metadata

**Version**: 1.0.0
**Created**: 2025-12-29
**Last Updated**: 2025-12-29
**Contract Type**: Exception Hierarchy
**Providers**: 1
**Consumers**: 4
**Complexity**: 3/5
**Token Count**: ~3500

# =============================================================================
# END OF ICON-02: Payment Service Exception Hierarchy
# =============================================================================
