# Requirements (REQ)

Requirements (REQ) documents capture atomic, testable requirements that serve as the granular specification layer between high-level Product Requirements Documents (PRDs) and implementation. REQs transform business intentions into precise, verifiable statements that drive technical specification and testing.

## Purpose

REQs create the **formal contract** for system behavior by:
- **Atomic Decomposition**: Breaking complex business needs into single, testable requirements
- **Measurable Verification**: Defining acceptance criteria that prove requirement satisfaction
- **Implementation Guidance**: Providing design constraints and validation rules for developers
- **Quality Assurance**: Establishing baselines for testing and compliance verification
- **Traceability Bridge**: Linking business needs to architectural decisions and technical specifications

## [RESOURCE_INSTANCE - e.g., database connection, workflow instance] in Development Workflow

REQs are the **testable specification layer** that operationalizes business requirements within the complete SDD workflow:

```
BRD (Business Requirements Document): High-level business needs
        ↓
PRD (Product Requirements Document): User needs and features
        ↓
EARS (Easy Approach to Requirements Syntax): Atomic, measurable requirements using WHEN/THEN format, Requirements Expressions). All work traces back to formal technical requirements (WHEN-THE-SHALL-WITHIN format), AI generated structured requirement formatAI transforms interfaces as code specification
        ↓
BDD (Behavior-Driven Development). Business + Dev + Test AI generates acceptance scenarios
        ↓
ADR (Architecture Decisions Requirements)
        ↓
SYS (System Requirements). Technical interpretation of business requirements
        ↓
REQ (Atomic Requirements)
        ↓
SPEC (Technical Implementation)  ← )
        ↓
TASKS (Implementation Plans)
        ↓
Code (src/{module_name}/) ← AI generates Python
        ↓
Tests (tests/{suit_name}) ← AI generates test suites
        ↓
Validation ← AI runs BDD tests
        ↓
Human Review ← HUMAN reviews architecture only
        ↓
Production-Ready Code
```

## REQ Document Structure

### Header with Traceability Tags

Comprehensive links establish the requirement's context and relationships:

```markdown
@adr:[ADR-NNN](../adrs/ADR-NNN_...md#ADR-NNN)
@prd:[PRD-NNN](../../prd/PRD-NNN_...md)
@sys:[SYS-NNN](../../sys/SYS-NNN_...md)
@ears:[EARS-NNN](../../ears/EARS-NNN_...md)
@spec:[SPEC-NNN](../../specs/.../SPEC-NNN_...yaml)
@bdd:[BDD-NNN:scenarios](../../bbds/BDD-NNN.feature#scenarios)
```

### Description
Concise requirement statement using modal SHALL language:

```markdown
### Description
The system SHALL [precise, atomic requirement statement that defines one specific behavior].
```

### Acceptance Criteria
Measurable validation rules that prove requirement satisfaction:

```markdown
### Acceptance Criteria
- [Specific, quantifiable condition 1 that validates the requirement]
- [Specific, quantifiable condition 2 that validates the requirement]
- [Specific, quantifiable condition N that validates the requirement]
```

### Related ADRs
Architecture decisions that implement or impact this requirement:

```markdown
### Related ADRs
- [ADR-NNN](../adrs/ADR-NNN_...md#ADR-NNN): [Architectural approach implemented]
- [ADR-NNN](../adrs/ADR-NNN_...md#ADR-NNN): [Alternative approaches considered]
```

### Source Requirements
Links to upstream requirements this REQ implements:

```markdown
### Source Requirements
- See summary and details in [Related Requirements Document](../../path/to/document.md#section-reference)
```

### Verification
How this requirement will be tested and validated:

```markdown
### Verification
- BDD: [BDD-NNN.feature](../../bbds/BDD-NNN.feature#scenarios)
- Spec: [SPEC-NNN.yaml](../../specs/.../SPEC-NNN.yaml)
- [Additional verification methods: performance tests, security tests, etc.]
```

## File Organization Hierarchy

REQ files are organized by functional domains and subdomains:

```
reqs/
├── api/           # API Integration Requirements
│   ├── av/        # [EXTERNAL_DATA_PROVIDER - e.g., Weather API, Stock Data API] API
│   └── ib/        # [EXTERNAL_SERVICE_GATEWAY] API
├── data/          # Data Management Requirements
├── risk/          # [RESOURCE_MANAGEMENT - e.g., capacity planning, quota management] Requirements
│   ├── lim/       # [RESOURCE_INSTANCE - e.g., database connection, workflow instance] Limits
│   ├── mon/       # Risk Monitoring
│   └── hed/       # Hedging Requirements
└── perf/          # Performance Requirements
```

## File Naming Convention

```
reqs/{domain}/{subdomain}/REQ-NNN_descriptive_title.md
```

Where:
- `reqs/` is the base requirements directory
- `{domain}` is functional area (`api`, `risk`, `data`, `ui`, etc.)
- `{subdomain}` is specific sub-area (`av`, `ib`, `lim`, `mon`, etc.)
- `REQ` is the constant prefix
- `NNN` is the three-digit sequence number (001, 002, 003, etc.)
- `descriptive_title` uses snake_case describing the requirement

**Examples:**
- `reqs/api/av/REQ-001_alpha_vantage_integration.md`
- `reqs/risk/lim/REQ-003_position_limit_enforcement.md`
- `reqs/data/proc/REQ-045_real_time_data_processing.md`

## Requirement Statement Quality

### Atomic Principle (One Responsibility)
Each REQ documents exactly one requirement - never multiple behaviors.

**Good:**
```markdown
### Description
The system SHALL validate input parameters against defined schemas.
```

**Poor (violates atomic principle):**
```markdown
### Description
The system SHALL validate input parameters against defined schemas and log validation failures and return appropriate error responses.
```
<!-- Split into separate REQs -->

### Measurable Validation
Every requirement must be testable with clear true/false outcomes.

**Good Acceptance Criteria:**
```markdown
### Acceptance Criteria
- Input validation fails for values outside allowed ranges
- Validation errors include specific field names and violation reasons
- Schema validation completes within 50ms under normal load
```

**Poor Acceptance Criteria:**
```markdown
### Acceptance Criteria
- Input is validated properly
- The system works as expected
- Performance is acceptable
```

### Modal SHALL Language
Use precise modal verbs to indicate requirement strength:

- **SHALL/SHALL NOT**: Absolute requirement (must be satisfied)
- **SHOULD/SHOULD NOT**: Preferred approach (strong recommendation)
- **MAY**: Optional behavior (permitted but not required)

### Context Independence
Requirements should be understandable without external context.

**Good (self-contained):**
```markdown
### Description
The authentication service SHALL reject login attempts after three consecutive failures for the same user account within a five-minute window.
```

**Poor (context-dependent):**
```markdown
### Description
The system SHALL handle the edge case.
```

## Acceptance Criteria Patterns

### Functional Requirements
```markdown
### Acceptance Criteria
- [Functionality] succeeds when [valid inputs] are provided
- [Functionality] fails gracefully when [invalid inputs] are provided
- [Output format] matches [specified schema] exactly
- [Error conditions] result in [specific response codes and messages]
```

### Performance Requirements
```markdown
### Acceptance Criteria
- [Operation] completes within [X milliseconds] for 95th percentile
- [Resource usage] does not exceed [Y units] under peak load
- [Throughput] maintains [Z operations/second] during stress testing
```

### Security Requirements
```markdown
### Acceptance Criteria
- [Authentication] requires valid [credential type] for access
- [Data] is encrypted using [algorithm] during [transmission/storage]
- [Access control] enforces [role-based permissions] correctly
```

### Integration Requirements
```markdown
### Acceptance Criteria
- [System interface] accepts and processes [expected message format]
- [Data synchronization] completes within [time window] with [accuracy level]
- [Error scenarios] trigger appropriate [compensation actions]
```

## Requirement Refinement Process

### From PRD to REQ
1. **Analyze PRD**: Break down functional requirements into atomic behaviors
2. **Identify Actors**: Determine system components and user roles
3. **Define Interfaces**: Specify inputs, outputs, and interaction points
4. **Set Constraints**: Include performance, security, and operational limits
5. **Create Testable Criteria**: Write acceptance criteria that prove satisfaction

### REQ Evolution
```markdown
Initial Draft → Acceptance Criteria Added → ADR Reference Added → Verification Linked → Production Ready

Basic Description → Acceptance Criteria → Constraints & Boundaries → Error Handling → Performance Targets
```

## Cross-Reference Linking

### Upstream Traceability
Requirements must link to their source business logic:

```markdown
### Source Requirements
- PRD: [PRD-NNN](../../prd/PRD-NNN_...md): [Section reference]
- SRS: [SYS-NNN](../../sys/SYS-NNN_...md): [Section reference]
- Business Rules: [Document](../../path/document.md#section)
```

### Downstream Dependencies
Track implementation artifacts that realize the requirement:

```markdown
### Verification
- ADR: [ADR-NNN](../adrs/ADR-NNN_...md#ADR-NNN) - [Implementation approach]
- BDD: [BDD-NNN.feature](../../bbds/BDD-NNN.feature#scenario-1)
- Spec: [SPEC-NNN.yaml](../../specs/.../SPEC-NNN.yaml)
- Code Module: `component.module.function()`
```

## Quality Gates

**Every REQ must:**
- Reference upstream PRD or SRS as source requirement
- Express exactly one atomic requirement using SHALL language
- Include measurable acceptance criteria with specific validation conditions
- Link to relevant ADR(s) that address the requirement
- Define verification methods (BDD scenarios, specifications, tests)
- Maintain traceability to downstream implementation artifacts

**REQ validation checklist:**
- ✅ Description uses precise SHALL/SHOULD/MAY language
- ✅ Acceptance criteria are quantitative and testable
- ✅ No compound requirements (single responsibility principle)
- ✅ Cross-reference links are functional and point to valid artifacts
- ✅ No implementation details (focus on what, not how)
- ✅ Requirement is independently verifiable

## REQ Writing Guidelines

### 1. Be Concrete and Specific
Avoid abstract or vague language that allows multiple interpretations:

**Good:**
```markdown
The API SHALL return HTTP 401 status code for requests lacking valid authentication credentials.
```

**Poor:**
```markdown
The API SHALL handle authentication properly.
```

### 2. Include Error and Edge Cases
Requirements should explicitly address failure modes:

**Good:**
```markdown
The validation service SHALL reject malformed JSON input with a descriptive error message and HTTP 400 status code.
```

### 3. Use Consistent Terminology
Establish domain-specific terms and use them consistently across related REQs.

### 4. Include Performance Characteristics
Where performance matters, specify quantitative requirements:

```markdown
### Acceptance Criteria
- Response time is less than 200ms for 95th percentile of requests
- Concurrent requests are handled without resource exhaustion up to 1000 RPS
```

### 5. Enable Independent Testing
Write acceptance criteria that can be tested without human interpretation:

```markdown
### Acceptance Criteria
- Purple button background is RGB(128, 0, 128) with 100% opacity
- NOT: Purple button looks correct  (subjective interpretation)
```

## Common REQ Patterns

### Data Validation Requirements
```markdown
## REQ-NNN: Input Data Validation

### Description
The [component] SHALL validate all input data against the defined schema and reject invalid requests with appropriate error responses.

### Acceptance Criteria
- Schema validation occurs before any business logic processing
- Invalid inputs result in HTTP 400 responses with detailed error messages
- Required fields missing trigger FIELD_REQUIRED error codes
- Type mismatches produce TYPE_MISMATCH error codes
- Schema validation completes within 100ms
```

### Authentication Requirements
```markdown
## REQ-NNN: User Authentication

### Description
The system SHALL authenticate users using [method] before granting access to protected resources.

### Acceptance Criteria
- Valid credentials result in successful authentication and session creation
- Invalid credentials fail with UNAUTHORIZED response
- Account lockout occurs after 5 consecutive failures within 15 minutes
- Sessions expire after 30 minutes of inactivity
```

### Error Handling Requirements
```markdown
## REQ-NNN: Error Response Standardization

### Description
The API SHALL return consistent error responses following the defined error schema for all failure conditions.

### Acceptance Criteria
- All errors include error.code, error.message, and error.timestamp fields
- Error codes are unique identifiers from the predefined list
- Correlation IDs are included when provided in the original request
- Error responses maintain HTTP status code conventions
```

## REQ Lifecycle Management

### Draft Status
Initial creation with basic description while design is evolving.

### Accepted Status
Stable requirement approved for implementation.

### Superseded Status
Requirement replaced by new REQ-NNN (with reference link).

### Retired Status
No longer relevant, archived for historical reference.

### Implementation Tracking
- Track REQ status through development phases
- Update verification links as BDD scenarios and specs are created
- Mark completed when all acceptance criteria are satisfied
- Maintain audit trail of changes and rationales

## Integration with Development Workflow

### During Definition
- Use REQs to drive BDD scenario creation
- Reference REQs in ADR evaluations as requirements satisfied
- Link REQs to specification development

### During Implementation
- Verify each code change contributes to at least one REQ acceptance criterion
- Use REQ acceptance criteria to validate unit test completeness
- Reference REQs in code comments and documentation

### During Testing
- Map test cases directly to REQ acceptance criteria
- Test REQs independently and in combination
- Verify all REQs have corresponding executable tests

### During Review
- Ensure PR descriptions reference satisfied REQs
- Validate that changes don't violate existing REQ contracts
- Confirm new functionality includes corresponding new REQs

## Benefits of Atomic Requirements

1. **Clarity**: Single focus eliminates requirement interpretation disputes
2. **Testability**: Clear criteria enable precise verification planning
3. **Traceability**: Easy to track from requirement through implementation and testing
4. **Modularity**: Changes to one REQ minimally impact others
5. **Progress Tracking**: Binary completion status for each requirement

## Avoiding Common Pitfalls

1. **Compound Requirements**: "System SHALL handle authentication AND authorization AND logging"
   - Solution: Split into separate REQs with individual acceptance criteria

2. **Implementation Details**: "System SHALL use PostgreSQL database with connection pooling"
   - Solution: Use "SHALL persist data durably with ACID properties" (implementation agnostic)

3. **Vague Acceptance**: "System SHALL perform well under load"
   - Solution: "System SHALL maintain 95th percentile response time under 200ms with 1000 concurrent users"

4. **Untestable Requirements**: "System SHALL be user-friendly"
   - Solution: "System SHALL provide accessible form labels for all input fields"

5. **Missing Error Cases**: Defining success paths without failure handling
   - Solution: Include explicit error conditions and expected behaviors

## Tools and Automation

### REQ Validation Scripts
```bash
# Validate REQ format and links
python validate_reqs.py --directory reqs/

# Check acceptance criteria completeness
python check_req_quality.py --req-file reqs/api/av/REQ-001_*.md

# Generate traceability matrices
python generate_req_matrix.py --domain api --format html
```

### Test Mapping Tools
```python
def test_req_coverage():
    """Ensure all REQs have corresponding tests"""
    reqs = load_all_reqs()
    tests = load_all_tests()
    for req in reqs:
        assert req.id in tests.coverage_map, f"Missing test for {req.id}"
```

## Example REQ Template

See `reqs/api/av/REQ-001_alpha_vantage_integration.md` for a complete example of a well-structured requirement document that follows these conventions and includes proper traceability and acceptance criteria.
