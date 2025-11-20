# REQ Implementation Patterns & Best Practices

**Companion Document**: REQ_STRUCTURE_COMPREHENSIVE_ANALYSIS.md

This document provides practical templates and patterns for implementing REQs following the V2 SPEC-Ready standard.

---

## PATTERN 1: External API Integration (REQ-001)

### Use Case
Integrating third-party APIs with resilience patterns (retry, circuit breaker, rate limiting, caching).

### File Structure
```
REQ/api/av/REQ-001_alpha_vantage_integration.md
REQ/api/ib/REQ-002_ib_gateway_integration.md
```

### Key Sections Filled In

**Section 3 - Interface Specifications**:
```python
class MarketDataAPIClient(Protocol):
    async def connect(
        self,
        credentials: APICredentials,
        timeout: float = 5.0
    ) -> ConnectionResult:
        """Establish connection with full error specification."""
        ...

    async def get_quote(
        self,
        symbol: str,
        retry_config: RetryConfig | None = None
    ) -> QuoteResponse:
        """Fetch real-time quote with resilience."""
        ...
```

**Section 5 - Error Handling**:
```markdown
| Exception | HTTP Code | Error Code | Retry? | Recovery |
|-----------|-----------|------------|--------|----------|
| ConnectionError | 503 | CONN_001 | Yes | Exponential backoff (1s, 2s, 4s, 8s, 16s) |
| RateLimitExceeded | 429 | RATE_001 | Yes | Queue request, wait for reset |
| AuthenticationError | 401 | AUTH_001 | No | Refresh credentials, alert admin |
| ValidationError | 400 | VALID_001 | No | Log error, return details |
```

**Section 6 - Configuration**:
```yaml
api_client:
  connection:
    base_url: "https://api.example.com/v1"
    timeout_seconds: 30.0
    max_connections: 100
  rate_limits:
    tier: "premium"
    requests_per_minute: 75
    burst_allowance: 10
  retry:
    max_attempts: 5
    backoff_multiplier: 2.0
    retryable_status_codes: [429, 500, 502, 503, 504]
```

**Section 8 - Implementation Guidance**:
```python
async def fetch_with_resilience(
    client: MarketDataAPIClient,
    request: DataRequest,
    config: RetryConfig
) -> DataResponse:
    """Fetch with retry + circuit breaker.
    
    Algorithm:
    1. Check circuit breaker state
    2. If open, fail fast
    3. Attempt request
    4. On retryable error, apply exponential backoff
    5. Update circuit breaker state
    """
```

### Acceptance Criteria Pattern
```markdown
## 9. Acceptance Criteria

- ✅ **AC-001**: Connection established within 5 seconds
  - **Verification**: Integration test
  - **Pass**: 100% of attempts succeed in <5s

- ✅ **AC-002**: Rate limiting enforced at 75 req/min (premium tier)
  - **Verification**: Chaos test (send 100 req in 1 min)
  - **Pass**: 76th request returns 429

- ✅ **AC-003**: Circuit breaker opens after 5 consecutive failures
  - **Verification**: Inject 5 failures
  - **Pass**: 6th request fails fast with CircuitOpenError

- ✅ **AC-004**: Exponential backoff retries on transient failures
  - **Verification**: Network failure simulation
  - **Pass**: Retries at 1s, 2s, 4s, 8s, 16s intervals

- ✅ **AC-005**: Response latency <500ms at p95 under normal load
  - **Verification**: Load test with APM
  - **Pass**: p95 <500ms, p99 <1000ms across 10k requests
```

---

## PATTERN 2: Data Validation (REQ-002)

### Use Case
Multi-layer validation pipeline: schema validation → business rules → database constraints.

### File Structure
```
REQ/data/REQ-002_data_validation_example.md
```

### Key Sections Filled In

**Section 1 - Description**:
```markdown
The system SHALL validate all incoming data through a three-layer pipeline: 
schema validation, business rule enforcement, and database constraint checking, 
rejecting invalid data with specific error codes and validation details.
```

**Section 2 - Business Rules**:
```markdown
### Business Rules

1. **Bid-Ask Spread Rule**: bid ≤ price ≤ ask (when all present)
   - Condition: Quote has bid, price, ask values
   - Action: Reject if spread violates ordering

2. **Symbol Format Rule**: 1-5 uppercase letters only
   - Condition: Symbol field present
   - Action: Reject if not matching ^[A-Z]{1,5}$

3. **Price Precision Rule**: Max 2 decimal places
   - Condition: Price field present
   - Action: Reject if more than 2 decimals
```

**Section 3 - Interface**:
```python
class DataValidator(Protocol):
    def validate_schema(self, data: dict) -> ValidationResult:
        """Validate against JSON Schema."""
        ...
    
    def validate_business_rules(
        self,
        data: dict,
        rules: BusinessRuleSet
    ) -> ValidationResult:
        """Validate against business rules."""
        ...
    
    def validate_database_constraints(
        self,
        model: BaseModel,
        session: Session
    ) -> ValidationResult:
        """Validate against database constraints."""
        ...
```

**Section 4 - Schemas**:
```python
class QuoteResponse(BaseModel):
    """Quote with cross-field validation."""
    
    symbol: str = Field(
        ...,
        pattern=r"^[A-Z]{1,5}$",
        min_length=1,
        max_length=5
    )
    price: float = Field(..., gt=0, decimal_places=2)
    bid: float | None = Field(None, ge=0)
    ask: float | None = Field(None, ge=0)
    
    @field_validator('price', 'bid', 'ask')
    @classmethod
    def validate_precision(cls, v: float) -> float:
        if v is not None and round(v, 2) != v:
            raise ValueError(f"Max 2 decimals, got {v}")
        return v
    
    @model_validator(mode='after')
    def validate_spread(self) -> 'QuoteResponse':
        if self.bid and self.ask and self.price:
            if not (self.bid <= self.price <= self.ask):
                raise ValueError("Bid must be <= Price <= Ask")
        return self
```

**Section 5 - Error Handling**:
```markdown
### Error Types

| Exception | Code | Retry | Recovery |
|---|---|---|---|
| SchemaValidationError | VALID_001 | No | Return field-level errors |
| BusinessRuleViolation | VALID_002 | No | Log rule violated, suggest fix |
| DatabaseConstraintError | VALID_003 | No | Check constraint name, return details |
| CrossFieldValidationError | VALID_004 | No | Indicate which fields conflict |
```

**Section 9 - Acceptance Criteria**:
```markdown
- ✅ **AC-001**: Schema validation rejects invalid types
  - **Pass**: All type violations caught

- ✅ **AC-002**: Business rule violations include rule name and violation reason
  - **Pass**: Error message specifies which rule and why

- ✅ **AC-003**: Validation completes within 100ms
  - **Pass**: p95 latency <100ms for 1000 validations

- ✅ **AC-004**: Field-level errors returned with field names and violation details
  - **Pass**: JSON response includes field names + violation reasons

- ✅ **AC-005**: Bid-Ask spread validation enforces bid ≤ price ≤ ask
  - **Pass**: Violation test cases all rejected with correct error code
```

---

## PATTERN 3: Authentication & Authorization (REQ-003)

### Use Case
Role-based access control (RBAC) with JWT tokens and permission inheritance.

### File Structure
```
REQ/auth/REQ-003_access_control_example.md
```

### Key Sections Filled In

**Section 1 - Description**:
```markdown
The system SHALL implement role-based access control (RBAC) with JWT token authentication, 
role hierarchy with permission inheritance, fine-grained permission checking, and audit logging 
of all authorization decisions.
```

**Section 3 - Interface**:
```python
class AuthorizationService(Protocol):
    """RBAC authorization interface."""
    
    def authenticate(
        self,
        username: str,
        password: str
    ) -> JWTToken:
        """Authenticate user, return JWT token."""
        ...
    
    def authorize(
        self,
        token: JWTToken,
        required_permission: str
    ) -> bool:
        """Check if token grants required permission."""
        ...
    
    def get_user_permissions(
        self,
        user_id: str
    ) -> Set[str]:
        """Get all permissions (including inherited from roles)."""
        ...
```

**Section 5 - Error Handling**:
```markdown
| Exception | Code | Retry | Recovery |
|---|---|---|---|
| InvalidCredentials | AUTH_001 | No | Reject login, log attempt |
| TokenExpired | AUTH_002 | Yes* | Prompt for re-authentication |
| InsufficientPermission | AUTH_003 | No | Return 403, log access denial |
| InvalidToken | AUTH_004 | No | Reject, require re-login |

*: Automatic retry with refresh token if available
```

**Section 6 - Configuration**:
```yaml
authentication:
  jwt:
    algorithm: "HS256"
    secret_key: "${JWT_SECRET}"
    expiration_seconds: 3600
    refresh_token_expiration_seconds: 86400
  
  password_policy:
    min_length: 12
    require_uppercase: true
    require_numbers: true
    require_special_chars: true
  
  session:
    max_concurrent: 3
    inactivity_timeout_minutes: 30
    lock_after_failed_attempts: 5
```

**Section 8 - Implementation Guidance**:
```markdown
### Role Hierarchy Algorithm

Algorithm: Resolve Permissions with Inheritance

```
Input: user_id, required_permission
Output: boolean (allowed/denied)

1. Load user object
2. Get user's direct roles
3. For each role:
   a. Get role's direct permissions
   b. Get role's parent roles (recursively)
   c. Accumulate all permissions
4. Check if required_permission in accumulated permissions
5. Log authorization decision (audit)
6. Return result
```

### JWT Token Structure

Header:
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

Payload:
```json
{
  "sub": "user_123",
  "iat": 1516239022,
  "exp": 1516242622,
  "roles": ["admin", "trader"],
  "permissions": ["trade.create", "trade.cancel", "report.read"]
}
```
```

**Section 9 - Acceptance Criteria**:
```markdown
- ✅ **AC-001**: Invalid credentials rejected with 401 Unauthorized
  - **Pass**: Wrong password returns 401, no token issued

- ✅ **AC-002**: Token expires after 1 hour
  - **Pass**: Token created at T, fails at T+3601 seconds

- ✅ **AC-003**: Refresh token rotates on each use
  - **Pass**: Old refresh token can't be reused after new token generated

- ✅ **AC-004**: Role hierarchy permits permission inheritance
  - **Pass**: Child role inherits parent role permissions

- ✅ **AC-005**: Fine-grained permissions enforced
  - **Pass**: User with "trade.read" blocked from "trade.delete"

- ✅ **AC-006**: All authorization decisions logged with timestamp
  - **Pass**: Audit logs contain all allow/deny decisions with user/permission/outcome
```

---

## PATTERN 4: Risk Management (REQ-003)

### Use Case
Position limit enforcement with real-time monitoring and breach notifications.

### File Structure
```
REQ/risk/lim/REQ-003_position_limit_enforcement.md
```

### Key Sections Filled In

**Section 1 - Description**:
```markdown
The system SHALL enforce position limits at multiple levels (per-user, per-strategy, 
per-product) with real-time monitoring, automatic breach notifications, and position 
scaling actions when limits are approached.
```

**Section 2 - Business Rules**:
```markdown
### Business Rules

1. **Position Limit Enforcement**: No positions exceeding configured limits
   - Condition: Trade execution received
   - Action: Check position against limit, reject if exceeded

2. **Soft Limit Warning**: Notify when position reaches 80% of limit
   - Condition: Position >= 80% of limit
   - Action: Send alert email, log warning

3. **Hard Limit Block**: Prevent trades that would exceed limit
   - Condition: Proposed trade would exceed limit
   - Action: Reject trade with error, log attempt

4. **Intraday Reset**: Limits reset at end of trading day
   - Condition: End of day (4:00 PM ET)
   - Action: Reset all positions to zero, archive history
```

**Section 3 - Interface**:
```python
class RiskManager(Protocol):
    """Position limit enforcement interface."""
    
    def check_position_limit(
        self,
        user_id: str,
        symbol: str,
        proposed_quantity: int
    ) -> LimitCheckResult:
        """Check if proposed position violates limits."""
        ...
    
    def get_position(
        self,
        user_id: str,
        symbol: str
    ) -> Position:
        """Get current position for symbol."""
        ...
    
    def get_position_utilization(
        self,
        user_id: str
    ) -> PositionUtilization:
        """Get % of limit used across all symbols."""
        ...
```

**Section 4 - Schemas**:
```python
@dataclass
class PositionLimit:
    user_id: str
    symbol: str
    max_quantity: int  # Maximum allowed position
    warning_threshold: float = 0.8  # Warn at 80%
    
    @property
    def warning_quantity(self) -> int:
        return int(self.max_quantity * self.warning_threshold)

@dataclass
class Position:
    user_id: str
    symbol: str
    current_quantity: int
    average_price: float
    market_value: float
    created_at: datetime
    updated_at: datetime
    
    def get_utilization_percent(self, limit: PositionLimit) -> float:
        return (self.current_quantity / limit.max_quantity) * 100
```

**Section 5 - Error Handling**:
```markdown
| Exception | Code | Retry | Recovery |
|---|---|---|---|
| PositionLimitExceeded | RISK_001 | No | Reject trade, suggest max quantity |
| PositionLimitWarning | RISK_002 | No | Allow trade, send notification |
| InsufficientMarginAvailable | RISK_003 | No | Reject trade, suggest position reduction |
| RiskEngineUnavailable | RISK_004 | Yes | Queue trade for later verification |

### State Machine

Current State: Position Monitoring

States:
- UNDER_LIMIT: Position < 80% of limit (normal operation)
- APPROACHING_LIMIT: Position 80-99% (warning issued)
- AT_LIMIT: Position = 100% (no new trades allowed)
- OVER_LIMIT: Position > 100% (error state, needs manual resolution)
```

**Section 9 - Acceptance Criteria**:
```markdown
- ✅ **AC-001**: Positions cannot exceed configured limit
  - **Pass**: All trades exceeding limit rejected

- ✅ **AC-002**: Soft limit warning triggered at 80% utilization
  - **Pass**: Position at 81% generates alert email

- ✅ **AC-003**: Hard limit blocks new positions
  - **Pass**: Trade that would exceed limit rejected with RISK_001

- ✅ **AC-004**: Positions reset at end of trading day (4:00 PM ET)
  - **Pass**: At 4:00 PM UTC-4, positions zeroed, history archived

- ✅ **AC-005**: Position utilization queryable in <100ms
  - **Pass**: get_position_utilization() returns in <100ms

- ✅ **AC-006**: All limit violations logged with trader name, symbol, quantity, time
  - **Pass**: Audit log contains complete violation context
```

---

## PRACTICAL CHECKLIST: Creating a New REQ

### Pre-Writing
- [ ] Identify upstream requirement (PRD section, EARS statement, SYS requirement)
- [ ] Check REQ-000_index.md for next available NNN number
- [ ] Choose appropriate domain/subdomain folder
- [ ] Decide if atomic (REQ-NNN) or multi-doc (REQ-NNN-YY)

### Writing Phase

**Section 1 - Description**:
- [ ] Start with "The system SHALL..." (use SHALL/SHOULD/MAY)
- [ ] Single, atomic behavior (no "and", no compound requirements)
- [ ] Include context explaining why this requirement exists
- [ ] Include use case scenario with primary and alternative flows
- [ ] Avoid implementation details (focus on WHAT, not HOW)

**Section 2 - Document Control**:
- [ ] Set Status to "Draft"
- [ ] Set Version to "1.0.0"
- [ ] Fill in all metadata fields (author, priority, category, etc.)
- [ ] Set SPEC-Ready Score (initially <90%, improve as you fill sections)

**Section 3 - Interface Specifications**:
- [ ] Define Protocol or ABC class (use typing.Protocol)
- [ ] Include all method signatures with type annotations
- [ ] Write docstrings with Args/Returns/Raises
- [ ] Include example DTOs or REST endpoints if applicable
- [ ] Make all types explicit (no `Any` unless justified)

**Section 4 - Data Schemas**:
- [ ] Write JSON Schema with all constraints
- [ ] Create Pydantic models with validators
- [ ] Include database schema (SQLAlchemy) if persistence needed
- [ ] Add concrete examples (no [PLACEHOLDER] text)
- [ ] Validate manually that examples pass schemas

**Section 5 - Error Handling**:
- [ ] Create exception catalog with error codes
- [ ] Specify which errors are retryable vs. terminal
- [ ] Include state machine diagram for complex flows
- [ ] Define circuit breaker thresholds if applicable
- [ ] Map error codes to HTTP status codes

**Section 6 - Configuration**:
- [ ] Write YAML configuration with realistic values
- [ ] List all environment variables
- [ ] Create Pydantic validator for config
- [ ] Include validation rules (ranges, patterns)
- [ ] Add comments explaining each setting

**Section 7 - Non-Functional Requirements**:
- [ ] Specify performance targets (p50/p95/p99)
- [ ] Include reliability SLOs (uptime %, error rate)
- [ ] Document security requirements (crypto, auth)
- [ ] Define scalability targets (concurrent users, throughput)
- [ ] Make all metrics quantifiable (not "fast" or "reliable")

**Section 8 - Implementation Guidance**:
- [ ] Include algorithm pseudocode for complex logic
- [ ] Describe design patterns (retry, circuit breaker, etc.)
- [ ] Show concurrency strategies if applicable
- [ ] Suggest dependency injection container setup
- [ ] Provide working code examples

**Section 9 - Acceptance Criteria**:
- [ ] Write 8-12 criteria numbered AC-001 through AC-NNN
- [ ] Include functional criteria (happy path)
- [ ] Include error/edge case criteria
- [ ] Include performance criteria (latency, throughput)
- [ ] Include security/quality criteria
- [ ] For each, specify verification method and pass criteria

**Section 10 - Verification Methods**:
- [ ] Link BDD scenarios in `BDD/` folder
- [ ] Specify unit test file paths
- [ ] Specify integration test file paths
- [ ] Specify contract test file paths
- [ ] Include performance test file paths
- [ ] Link SPEC document (if exists)

**Section 11 - Traceability**:
- [ ] Document upstream sources (BRD, PRD, EARS, SYS, ADR)
- [ ] List downstream artifacts (SPEC, BDD, CTR, Code)
- [ ] Add cumulative tags (@brd, @prd, @ears, @bdd, @adr, @sys)
- [ ] Include code implementation paths
- [ ] Create markdown links with relative paths

**Section 12 - Change History**:
- [ ] Record initial creation
- [ ] Add current date and version
- [ ] Update SPEC-Ready Score
- [ ] Mark as complete

### Post-Writing
- [ ] Run `validate_requirement_ids.py` to check format
- [ ] Run `validate_req_spec_readiness.py` to score completeness
- [ ] Run `validate_traceability_matrix.py` to check links
- [ ] Run `validate_tags_against_docs.py` to verify cumulative tags
- [ ] Update REQ-000_index.md with new REQ entry
- [ ] Peer review for quality gates compliance
- [ ] Update SPEC-Ready Score based on validation results
- [ ] Change Status to "Review" when ready for approval

---

## QUALITY METRICS

### SPEC-Ready Score Calculation

```
Score = (Sections Completed / 12) * 100

Scoring:
- Section present and filled: 100%
- Section skeleton only: 50%
- Section missing: 0%

Target: ≥90% (11+ sections completed)

Example:
- 11 sections complete = 11/12 = 91.7% (ACCEPTABLE)
- 10 sections complete = 10/12 = 83.3% (NEEDS WORK)
- 12 sections complete = 12/12 = 100% (EXCELLENT)
```

### Validation Results Summary

```
Valid REQ should produce:
✅ validate_requirement_ids.py: All checks pass
✅ validate_req_spec_readiness.py: Score ≥90%
✅ validate_traceability_matrix.py: 100% upstream coverage
✅ validate_tags_against_docs.py: All tags valid
✅ validate_documentation_paths.py: All links valid
```

---

## COMMON MISTAKES & HOW TO AVOID THEM

### Mistake 1: Compound Requirements
**Wrong**: "The system SHALL authenticate users AND authorize access AND log actions"
**Right**: Split into three separate REQs
- REQ-NNN: User authentication
- REQ-NNN+1: Access authorization
- REQ-NNN+2: Action logging

### Mistake 2: Implementation Details
**Wrong**: "The system SHALL use PostgreSQL connection pool with 20 max connections"
**Right**: "The system SHALL persist data durably with ACID properties and support 1000 concurrent requests"
(Implementation chosen later)

### Mistake 3: Vague Acceptance Criteria
**Wrong**: "System SHALL perform well under load"
**Right**: "System SHALL maintain p95 latency <500ms with 1000 concurrent users"

### Mistake 4: Untestable Requirements
**Wrong**: "The API SHALL be user-friendly"
**Right**: "The API response schema SHALL comply with JSON Schema specification and include descriptive error messages"

### Mistake 5: Missing Error Cases
**Wrong**: Only describe the happy path
**Right**: Include error flows, timeout scenarios, boundary conditions, invalid inputs

### Mistake 6: Placeholder Examples
**Wrong**: Use `[EXAMPLE_API_URL]`, `[NNN_VALUE]`
**Right**: Use actual, concrete values: `https://api.example.com/v1`, `75` (for rate limit)

### Mistake 7: No Traceability
**Wrong**: REQ stands alone with no upstream/downstream links
**Right**: Every REQ references BRD/SYS upstream, SPEC/BDD downstream

### Mistake 8: Incomplete Sections
**Wrong**: Interface spec is just text description, no code
**Right**: Include Protocol/ABC class with type annotations and docstrings

---

## TOOLS & AUTOMATION

### Running Validation Suite

```bash
cd ai_dev_flow/

# Check all REQ ID format and structure
python scripts/validate_requirement_ids.py --directory REQ/

# Score SPEC-readiness
python scripts/validate_req_spec_readiness.py --req-file REQ/api/REQ-001.md

# Check traceability matrix
python scripts/validate_traceability_matrix.py --directory REQ/

# Validate cumulative tags
python scripts/validate_tags_against_docs.py --directory REQ/

# Check all markdown links
python scripts/validate_documentation_paths.py --directory REQ/
```

### Generating Traceability Matrix

```bash
python scripts/generate_traceability_matrix.py \
    --directory REQ/ \
    --output REQ/REQ-000_TRACEABILITY_MATRIX.md \
    --format markdown
```

---

## RESOURCES

- **REQ/README.md**: Complete reference guide
- **REQ/REQ-TEMPLATE.md**: V2 template with all 12 sections
- **REQ/examples/**: Real-world examples (API, data validation, auth, risk)
- **ai_dev_flow/TRACEABILITY.md**: 16-layer workflow documentation
- **ai_dev_flow/ID_NAMING_STANDARDS.md**: Naming conventions and patterns
- **ai_dev_flow/scripts/**: Automated validation tools
