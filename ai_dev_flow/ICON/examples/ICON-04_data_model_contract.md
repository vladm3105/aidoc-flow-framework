# =============================================================================
# ICON-04: Data Model Contract Example
# =============================================================================
# Example Implementation Contract demonstrating Pydantic/TypedDict schemas
# with validation rules, serialization, and data transfer objects
# =============================================================================
---
title: "ICON-04: Customer Data Model Contract"
tags:
  - implementation-contract
  - layer-11-artifact
  - shared-architecture
  - data-model
  - example
custom_fields:
  document_type: implementation_contract
  artifact_type: ICON
  layer: 11
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  contract_type: data-model
  provider_tasks: TASKS-030
  consumer_count: 6
  providers: [TASKS-030]
  consumers: [TASKS-031, TASKS-032, TASKS-033, TASKS-034, TASKS-035, TASKS-036]
---

# ICON-04: Customer Data Model Contract

## Document Control

| Item | Details |
|------|---------|
| **Status** | Active |
| **Version** | 1.0.0 |
| **Date Created** | 2025-12-29 |
| **Last Updated** | 2025-12-29 |
| **Author** | AI Development Team |
| **Contract Type** | Data Model |
| **Providers** | TASKS-030 (Customer Service) |
| **Consumers** | TASKS-031-036 |

---

## 3. Executive Summary

This contract defines the customer data model schema using Pydantic for the e-commerce platform. It establishes validated data structures, serialization formats, and data transfer objects for consistent customer data handling across all services.

### 3.1 Scope

**Purpose**: Type-safe customer data models with validation
**Boundary**: Customer entity and related DTOs only
**Complexity**: 3/5

---

## 1. Contract Definition

### 1.1 Contract Type

**Type**: Data Model

**Rationale**: Customer data requires:
- Strict validation at system boundaries
- Consistent serialization across services
- Privacy compliance (PII handling)
- Versioned schema evolution

### 1.2 Interface Specification

```python
"""
Customer Data Model Contract
============================
Pydantic-based data models for customer entities with validation,
serialization, and privacy-compliant PII handling.
"""

from datetime import datetime, date
from typing import Optional, List, Annotated, Any
from enum import Enum
from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    field_validator,
    model_validator,
    ConfigDict,
    SecretStr,
)
import re


# =============================================================================
# Enumerations
# =============================================================================

class CustomerStatus(str, Enum):
    """Customer account status."""
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


class CustomerTier(str, Enum):
    """Customer loyalty tier."""
    STANDARD = "standard"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class AddressType(str, Enum):
    """Address classification."""
    BILLING = "billing"
    SHIPPING = "shipping"
    BOTH = "both"


class CommunicationPreference(str, Enum):
    """Preferred communication channel."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    NONE = "none"


# =============================================================================
# Value Objects
# =============================================================================

class PhoneNumber(BaseModel):
    """
    Validated phone number value object.

    Attributes:
        country_code: ISO country calling code (e.g., "1" for US)
        number: Phone number without country code
        is_verified: Whether number has been verified via OTP
    """
    model_config = ConfigDict(frozen=True)

    country_code: Annotated[str, Field(pattern=r"^\d{1,4}$")]
    number: Annotated[str, Field(min_length=6, max_length=15)]
    is_verified: bool = False

    @field_validator("number")
    @classmethod
    def validate_phone_format(cls, v: str) -> str:
        """Remove non-digit characters and validate."""
        cleaned = re.sub(r"\D", "", v)
        if len(cleaned) < 6:
            raise ValueError("Phone number must have at least 6 digits")
        return cleaned

    @property
    def formatted(self) -> str:
        """E.164 formatted phone number."""
        return f"+{self.country_code}{self.number}"

    @property
    def masked(self) -> str:
        """Masked phone for display (last 4 digits visible)."""
        return f"+{self.country_code}****{self.number[-4:]}"


class Address(BaseModel):
    """
    Validated postal address.

    Attributes:
        type: Address type (billing/shipping/both)
        line1: Street address line 1
        line2: Optional street address line 2
        city: City name
        state: State/province/region
        postal_code: ZIP/postal code
        country: ISO 3166-1 alpha-2 country code
        is_default: Whether this is the default address for its type
    """
    model_config = ConfigDict(frozen=True)

    type: AddressType
    line1: Annotated[str, Field(min_length=1, max_length=100)]
    line2: Optional[Annotated[str, Field(max_length=100)]] = None
    city: Annotated[str, Field(min_length=1, max_length=50)]
    state: Annotated[str, Field(min_length=1, max_length=50)]
    postal_code: Annotated[str, Field(min_length=3, max_length=20)]
    country: Annotated[str, Field(pattern=r"^[A-Z]{2}$")]
    is_default: bool = False

    @field_validator("postal_code")
    @classmethod
    def validate_postal_code(cls, v: str, info) -> str:
        """Validate postal code format based on country."""
        # Country-specific validation would go here
        return v.strip().upper()

    @property
    def one_line(self) -> str:
        """Single-line address representation."""
        parts = [self.line1]
        if self.line2:
            parts.append(self.line2)
        parts.extend([self.city, self.state, self.postal_code, self.country])
        return ", ".join(parts)


class PaymentMethod(BaseModel):
    """
    Tokenized payment method reference.

    Note: Actual card data stored in PCI-compliant vault.
    This model only contains non-sensitive tokens and metadata.
    """
    model_config = ConfigDict(frozen=True)

    id: str
    type: str  # "card", "bank_account", "paypal"
    token: str  # Vault token, not actual card number
    last_four: Annotated[str, Field(pattern=r"^\d{4}$")]
    brand: Optional[str] = None  # "visa", "mastercard", etc.
    expiry_month: Optional[Annotated[int, Field(ge=1, le=12)]] = None
    expiry_year: Optional[Annotated[int, Field(ge=2024, le=2050)]] = None
    is_default: bool = False

    @property
    def is_expired(self) -> bool:
        """Check if payment method is expired."""
        if self.expiry_month is None or self.expiry_year is None:
            return False
        today = date.today()
        return (
            self.expiry_year < today.year or
            (self.expiry_year == today.year and self.expiry_month < today.month)
        )

    @property
    def display_name(self) -> str:
        """Human-readable display name."""
        if self.brand:
            return f"{self.brand.title()} ****{self.last_four}"
        return f"****{self.last_four}"


# =============================================================================
# Customer Entity Model
# =============================================================================

class CustomerBase(BaseModel):
    """
    Base customer model with common fields.
    Used as parent for create/update DTOs.
    """
    first_name: Annotated[str, Field(min_length=1, max_length=50)]
    last_name: Annotated[str, Field(min_length=1, max_length=50)]
    email: EmailStr
    phone: Optional[PhoneNumber] = None
    date_of_birth: Optional[date] = None
    communication_preference: CommunicationPreference = CommunicationPreference.EMAIL
    marketing_opt_in: bool = False

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and normalize name."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Name cannot be empty")
        return cleaned.title()

    @field_validator("date_of_birth")
    @classmethod
    def validate_age(cls, v: Optional[date]) -> Optional[date]:
        """Validate customer is at least 13 years old."""
        if v is None:
            return None
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 13:
            raise ValueError("Customer must be at least 13 years old")
        if age > 120:
            raise ValueError("Invalid date of birth")
        return v

    @property
    def full_name(self) -> str:
        """Full name concatenation."""
        return f"{self.first_name} {self.last_name}"


class Customer(CustomerBase):
    """
    Complete customer entity model.

    Attributes:
        id: Unique customer identifier
        status: Account status
        tier: Loyalty program tier
        addresses: List of customer addresses
        payment_methods: List of tokenized payment methods
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        last_login_at: Last successful login
        email_verified_at: Email verification timestamp
        metadata: Extensible metadata dictionary
    """
    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode
        json_schema_extra={
            "example": {
                "id": "cust_abc123",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "status": "active",
                "tier": "gold",
            }
        }
    )

    id: str
    status: CustomerStatus = CustomerStatus.PENDING_VERIFICATION
    tier: CustomerTier = CustomerTier.STANDARD
    addresses: List[Address] = Field(default_factory=list)
    payment_methods: List[PaymentMethod] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_default_addresses(self) -> "Customer":
        """Ensure at most one default per address type."""
        for addr_type in AddressType:
            defaults = [a for a in self.addresses if a.is_default and a.type == addr_type]
            if len(defaults) > 1:
                raise ValueError(f"Multiple default {addr_type.value} addresses")
        return self

    @property
    def is_active(self) -> bool:
        """Check if customer account is active."""
        return self.status == CustomerStatus.ACTIVE

    @property
    def default_shipping_address(self) -> Optional[Address]:
        """Get default shipping address."""
        return next(
            (a for a in self.addresses
             if a.is_default and a.type in (AddressType.SHIPPING, AddressType.BOTH)),
            None
        )

    @property
    def default_payment_method(self) -> Optional[PaymentMethod]:
        """Get default payment method."""
        return next((p for p in self.payment_methods if p.is_default), None)


# =============================================================================
# Data Transfer Objects (DTOs)
# =============================================================================

class CustomerCreate(CustomerBase):
    """
    DTO for customer creation requests.

    Excludes system-managed fields like id, status, timestamps.
    Password is handled separately via auth service.
    """
    password: SecretStr = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: SecretStr) -> SecretStr:
        """Validate password meets complexity requirements."""
        password = v.get_secret_value()
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain lowercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError("Password must contain special character")
        return v


class CustomerUpdate(BaseModel):
    """
    DTO for partial customer updates.

    All fields optional for PATCH semantics.
    """
    first_name: Optional[Annotated[str, Field(min_length=1, max_length=50)]] = None
    last_name: Optional[Annotated[str, Field(min_length=1, max_length=50)]] = None
    phone: Optional[PhoneNumber] = None
    date_of_birth: Optional[date] = None
    communication_preference: Optional[CommunicationPreference] = None
    marketing_opt_in: Optional[bool] = None

    def apply_to(self, customer: Customer) -> dict[str, Any]:
        """
        Get dictionary of fields to update.

        Returns only non-None values for partial update.
        """
        return {k: v for k, v in self.model_dump().items() if v is not None}


class CustomerResponse(BaseModel):
    """
    DTO for API responses.

    Excludes sensitive fields like password hash.
    Includes computed fields for client convenience.
    """
    model_config = ConfigDict(from_attributes=True)

    id: str
    first_name: str
    last_name: str
    full_name: str
    email: EmailStr
    phone: Optional[str] = None  # Masked format
    status: CustomerStatus
    tier: CustomerTier
    addresses: List[Address]
    has_payment_method: bool
    is_email_verified: bool
    communication_preference: CommunicationPreference
    created_at: datetime

    @classmethod
    def from_customer(cls, customer: Customer) -> "CustomerResponse":
        """Create response DTO from customer entity."""
        return cls(
            id=customer.id,
            first_name=customer.first_name,
            last_name=customer.last_name,
            full_name=customer.full_name,
            email=customer.email,
            phone=customer.phone.masked if customer.phone else None,
            status=customer.status,
            tier=customer.tier,
            addresses=customer.addresses,
            has_payment_method=len(customer.payment_methods) > 0,
            is_email_verified=customer.email_verified_at is not None,
            communication_preference=customer.communication_preference,
            created_at=customer.created_at,
        )


class CustomerSummary(BaseModel):
    """
    Minimal customer summary for list views and references.
    """
    id: str
    full_name: str
    email: EmailStr
    status: CustomerStatus
    tier: CustomerTier


# =============================================================================
# Event Models
# =============================================================================

class CustomerEvent(BaseModel):
    """Base model for customer domain events."""
    event_type: str
    customer_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None


class CustomerCreatedEvent(CustomerEvent):
    """Event emitted when customer is created."""
    event_type: str = "customer.created"
    email: EmailStr
    tier: CustomerTier


class CustomerUpdatedEvent(CustomerEvent):
    """Event emitted when customer is updated."""
    event_type: str = "customer.updated"
    changed_fields: List[str]


class CustomerStatusChangedEvent(CustomerEvent):
    """Event emitted when customer status changes."""
    event_type: str = "customer.status_changed"
    old_status: CustomerStatus
    new_status: CustomerStatus
    reason: Optional[str] = None
```

---

## 2. Provider Requirements

### 2.1 Implementation Obligations

**Provider TASKS**: TASKS-030 (Customer Service)

**Requirements**:
- [ ] Implement all models as defined
- [ ] Use Pydantic validation at service boundaries
- [ ] Emit domain events on entity changes
- [ ] Never expose internal entities in API responses

### 2.2 Validation Criteria

```bash
# Type check
mypy --strict src/contracts/customer/models.py

# Schema validation
python -c "from contracts.customer.models import Customer; print(Customer.model_json_schema())"
```

---

## 3. Consumer Requirements

### 3.1 Usage Obligations

**Consumer TASKS**: TASKS-031 through TASKS-036

**Requirements**:
- [ ] Use DTOs for API input/output
- [ ] Handle validation errors from Pydantic
- [ ] Use `CustomerResponse.from_customer()` for API responses
- [ ] Never serialize full `Customer` entity to API

### 3.2 Dependency Management

```python
from contracts.customer.models import (
    Customer,
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerStatus,
    CustomerTier,
)

async def create_customer(data: CustomerCreate) -> CustomerResponse:
    """Create customer with validated input."""
    # Pydantic validates CustomerCreate automatically
    customer = Customer(
        id=generate_id(),
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone=data.phone,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    await repository.save(customer)
    return CustomerResponse.from_customer(customer)
```

---

## 5. Testing Requirements

### 5.1 Provider Tests

```python
import pytest
from pydantic import ValidationError
from contracts.customer.models import CustomerCreate, PhoneNumber

class TestCustomerCreate:
    """Validate CustomerCreate DTO."""

    def test_valid_customer(self):
        """Valid data passes validation."""
        data = CustomerCreate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            password="SecurePass123!"
        )
        assert data.full_name == "John Doe"

    def test_password_complexity(self):
        """Weak passwords are rejected."""
        with pytest.raises(ValidationError) as exc:
            CustomerCreate(
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                password="weak"
            )
        assert "Password must contain" in str(exc.value)

    def test_email_validation(self):
        """Invalid emails are rejected."""
        with pytest.raises(ValidationError):
            CustomerCreate(
                first_name="John",
                last_name="Doe",
                email="not-an-email",
                password="SecurePass123!"
            )


class TestPhoneNumber:
    """Validate PhoneNumber value object."""

    def test_phone_masking(self):
        """Phone numbers are properly masked."""
        phone = PhoneNumber(country_code="1", number="5551234567")
        assert phone.masked == "+1****4567"
```

---

## 7. Traceability

### 7.1 Upstream Artifacts

```markdown
@spec: SPEC-07         # Customer Management Specification
@req: REQ.07.01.01     # Customer Data Requirements
@adr: ADR-05           # Data Model Architecture Decision
```

### 7.2 Provider/Consumer Tags

```markdown
@icon: ICON-04:CustomerDataModel
```

---

## 10. Document Metadata

**Version**: 1.0.0
**Created**: 2025-12-29
**Last Updated**: 2025-12-29
**Contract Type**: Data Model
**Providers**: 1
**Consumers**: 6
**Complexity**: 3/5
**Token Count**: ~4500

# =============================================================================
# END OF ICON-04: Customer Data Model Contract
# =============================================================================
