---
title: "TASKS-TEMPLATE: task-breakdown-document"
tags:
  - tasks-template
  - layer-11-artifact
  - shared-architecture
  - document-template
custom_fields:
  document_type: template
  artifact_type: TASKS
  layer: 11
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  template_for: task-breakdown-document
---

# TASKS-NNN: [Descriptive Component/Feature Name]

**⚠️ CRITICAL**: Always reference [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) as the single source of truth for workflow steps, artifact definitions, and quality gates.

**[RESOURCE_INSTANCE - e.g., database connection, workflow instance]**: TASKS is in Layer 11 (Code Generation Layer) - creates detailed implementation plans from SPEC files.

## Document Control

| Item | Details |
|------|---------|
| **Status** | Draft/Planned/In Progress/Completed/Blocked/On Hold |
| **Version** | [Semantic version, e.g., 1.0.0] |
| **Date Created** | YYYY-MM-DD |
| **Last Updated** | YYYY-MM-DD |
| **Author** | [Developer/AI Assistant/Team Name] |
| **Assigned To** | [Primary developer or team responsible] |
| **Priority** | Critical/High/Medium/Low |
| **Estimated Effort** | [Story Points or Person-Hours] |
| **Actual Effort** | [Actual hours spent - update upon completion] |
| **Due Date** | YYYY-MM-DD |
| **Completion Date** | YYYY-MM-DD (when completed) |
| **Dependencies** | [List of TASKS-IDs that must be completed first] |
| **Blockers** | [Current blockers preventing progress] |

## Executive Summary

[2-3 sentence overview of what this implementation task accomplishes, which component/feature it builds, and its role in the larger system architecture]

### Implementation Context

[Brief context explaining:
- Which system component or feature this task implements
- How it fits into the overall architecture
- What upstream requirements drive this task
- What downstream artifacts will result from this task]

### Business Value

[Clear statement of business value delivered by completing this implementation:
- Specific business capability enabled
- User benefit or operational improvement
- Risk reduction or compliance satisfaction
- Performance or reliability enhancement]

## [RESOURCE_INSTANCE - e.g., database connection, workflow instance] in Development Workflow

**TASKS (Code Generation Plans)** ← YOU ARE HERE

For the complete traceability workflow with visual diagram, see: [index.md - Traceability Flow](../index.md#traceability-flow)

**Quick Reference**:
```
... → SPEC → **TASKS** → Code → Tests → Validation → ...
                 ↑
         Code Generation Layer
         (AI-structured implementation steps)
```

**TASKS Purpose**: AI-assisted implementation guidance translating formal specifications into production code
- **Input**: SPEC (technical blueprint), CTR (interface contracts), REQ (requirements)
- **Output**: Step-by-step implementation plan with acceptance criteria
- **Consumer**: AI agents and developers use TASKS to generate code

---

## Scope

### Implementation Goal

[Single-sentence statement of what will be delivered upon task completion]

**Detailed Description**:
[Comprehensive description of what will be implemented including:
- Core functionality to be delivered
- Interface points and contracts to be fulfilled
- Quality standards and performance targets to be met
- Success criteria for completion verification]

### Boundaries & Included Features

**Included in This Task**:
- [Specific functionality #1 with clear definition]
- [Specific functionality #2 with clear definition]
- [Specific feature #3 with clear definition]
- [Integration point #4 with contract reference]
- [Quality attribute #5 with measurable target]

### Exclusions & Out of Scope

**Explicitly NOT Included**:
- [Out of scope item #1 - to be addressed in future task]
- [Out of scope item #2 - handled by different component]
- [Nice-to-have item #3 - deferred to future enhancement]
- [Adjacent functionality #4 - separate responsibility]

### Assumptions & Prerequisites

**Environmental Assumptions**:
- [Required infrastructure is available and configured]
- [Dependent services are operational and accessible]
- [Development environment meets minimum requirements]
- [Access credentials and permissions are granted]

**Technical Prerequisites**:
- [Required libraries and frameworks are installed]
- [Database schemas are created and migrated]
- [External APIs are accessible and authenticated]
- [Configuration files are present and validated]

---

## Implementation Plan

### Overview

[High-level approach to implementation with key phases and milestones]

### Phase 1: Preparation & Setup

#### 1.1 Review Prerequisites
- **Action**: Analyze upstream specifications and requirements
- **Artifacts to Review**:
  - [REQ-NNN](../REQ/.../REQ-NNN.md) - Atomic requirements
  - [SPEC-NNN](../SPEC/.../SPEC-NNN.yaml) - Technical specification
  - [ADR-NNN](../ADR/ADR-NNN.md) - Architecture decisions
- **Success Criteria**: All requirements understood, ambiguities resolved
- **Estimated Duration**: [X hours]

#### 1.2 Environment Setup
- **Action**: Prepare development environment and tooling
- **Tasks**:
  - Clone repository and checkout feature branch
  - Install dependencies from requirements.txt/package.json
  - Configure local environment variables and secrets
  - Verify database connections and external service access
  - Set up IDE/editor with linting and formatting tools
- **Success Criteria**: Development environment passes verification script
- **Estimated Duration**: [X hours]

#### 1.3 Specification Deep Dive
- **Action**: Detailed analysis of technical specifications
- **Focus Areas**:
  - Interface definitions and data contracts
  - Business logic and algorithm specifications
  - Error handling and edge case requirements
  - Performance and scalability expectations
  - Security and compliance requirements
- **Deliverable**: Implementation notes document with clarifications
- **Estimated Duration**: [X hours]

### Phase 2: Implementation

#### 2.1 Component Foundation
- **Action**: Create base structures, interfaces, and skeletons
- **Deliverables**:
  - Class/module structure matching specification
  - Interface definitions and type annotations
  - Configuration schema and validation
  - Logging and metrics infrastructure
- **Success Criteria**: Foundation code passes static analysis and type checking
- **Estimated Duration**: [X hours]

#### 2.2 Core Business Logic
- **Action**: Implement primary functionality and algorithms
- **Focus**:
  - Business rule implementation per specifications
  - Algorithm implementation with documented complexity
  - State management and data transformation logic
  - Validation rules and business constraints
- **Success Criteria**: Core logic passes unit tests with 85%+ coverage
- **Estimated Duration**: [X hours]

#### 2.3 Integration Points
- **Action**: Implement external interfaces and communication protocols
- **Deliverables**:
  - API client implementations with retry logic
  - Database access layer with connection pooling
  - Message queue producers/consumers
  - Event emitters and listeners
- **Success Criteria**: Integration tests validate all external interactions
- **Estimated Duration**: [X hours]

#### 2.4 Error Handling & Resilience
- **Action**: Add comprehensive error handling and edge cases
- **Implementation**:
  - Input validation with detailed error messages
  - Exception handling with graceful degradation
  - Circuit breakers for external dependencies
  - Retry logic with exponential backoff
  - Dead letter queue handling for unprocessable messages
- **Success Criteria**: All error scenarios have defined behavior and tests
- **Estimated Duration**: [X hours]

#### 2.5 Observability & Monitoring
- **Action**: Implement logging, metrics, and tracing
- **Deliverables**:
  - Structured logging with correlation IDs
  - Prometheus metrics for key operations
  - Distributed tracing instrumentation
  - Health check endpoints
  - Performance profiling hooks
- **Success Criteria**: All critical operations emit observable signals
- **Estimated Duration**: [X hours]

### Phase 3: Testing & Validation

#### 3.1 Unit Testing
- **Action**: Develop comprehensive unit tests
- **Coverage Requirements**:
  - ≥85% line coverage for all functional code
  - ≥90% branch coverage for critical paths
  - All public methods have positive and negative tests
  - All error conditions have dedicated test cases
- **Success Criteria**: All unit tests pass with required coverage
- **Estimated Duration**: [X hours]

#### 3.2 Integration Testing
- **Action**: Validate component interactions and contracts
- **Test Scenarios**:
  - End-to-end workflow validation
  - Cross-component data flow verification
  - External service integration validation
  - Database transaction integrity tests
- **Success Criteria**: All integration tests pass; contracts validated
- **Estimated Duration**: [X hours]

#### 3.3 BDD Scenario Execution
- **Action**: Execute automated behavior-driven tests
- **Scenarios to Validate**:
  - [BDD-NNN.feature](../BDD/BDD-NNN.feature) - [Scenario description]
  - [BDD-MMM.feature](../BDD/BDD-MMM.feature) - [Scenario description]
- **Success Criteria**: All BDD scenarios pass with expected outcomes
- **Estimated Duration**: [X hours]

#### 3.4 Performance Testing
- **Action**: Verify non-functional requirements under load
- **Test Types**:
  - Latency testing (p50, p95, p99 percentiles)
  - Throughput testing (requests per second capacity)
  - Load testing (sustained load handling)
  - Stress testing (failure point identification)
  - Resource utilization profiling
- **Success Criteria**: All performance targets met per NFRs
- **Estimated Duration**: [X hours]

#### 3.5 Security Testing
- **Action**: Validate security controls and data protection
- **Validation**:
  - Authentication and authorization checks
  - Input sanitization and SQL injection prevention
  - XSS and CSRF protection validation
  - Secret management and encryption verification
  - Dependency vulnerability scanning
- **Success Criteria**: Security scan passes with no high/critical issues
- **Estimated Duration**: [X hours]

### Phase 4: Completion & Deployment Readiness

#### 4.1 Documentation
- **Action**: Update all documentation artifacts
- **Deliverables**:
  - Inline code documentation (docstrings/JSDoc)
  - API documentation (OpenAPI/Swagger updates)
  - README updates with usage examples
  - Operational runbooks for deployment/troubleshooting
  - Architecture diagrams if needed
- **Success Criteria**: Documentation review approved
- **Estimated Duration**: [X hours]

#### 4.2 Code Review & Verification
- **Action**: Conduct thorough code review
- **Review Checklist**:
  - Code follows style guide and naming conventions
  - All acceptance criteria are met and verified
  - Test coverage meets minimum thresholds
  - No security vulnerabilities or code smells
  - Performance characteristics are acceptable
  - Error handling is comprehensive
- **Success Criteria**: Code review approved by senior developer/architect
- **Estimated Duration**: [X hours]

#### 4.3 Deployment Readiness
- **Action**: Ensure production deployment capability
- **Validation**:
  - CI/CD pipeline passes all checks
  - Deployment scripts tested in staging
  - Configuration management validated
  - Rollback procedures documented and tested
  - Monitoring alerts configured
  - On-call runbooks updated
- **Success Criteria**: Deployment checklist 100% complete
- **Estimated Duration**: [X hours]

---

## Constraints

### Technical Constraints

#### Architecture Constraints
- **Pattern**: [Must use hexagonal/clean architecture pattern]
- **Language**: [Python 3.11+ with type hints required]
- **Framework**: [FastAPI/Flask/Django for API services]
- **Database**: [PostgreSQL for transactional data, Redis for caching]
- **Message Queue**: [Google Cloud Pub/Sub for async messaging]

#### Platform & Infrastructure
- **Cloud Provider**: [Google Cloud Platform (GCP) required]
- **Compute**: [Cloud Run for containerized services]
- **Storage**: [Cloud Storage for object storage]
- **Networking**: [VPC and private service connect for security]
- **CI/CD**: [Cloud Build with GitHub Actions integration]

#### Dependencies & Versions
- **Approved Libraries**: [List of pre-approved dependencies]
- **Version Constraints**: [Specific version requirements or ranges]
- **License Compliance**: [MIT/Apache 2.0 licenses only]
- **Security Requirements**: [No known CVEs in dependencies]

### Functional Constraints

#### Data Formats & Validation
- **Input Validation**: [JSON Schema validation required for all inputs]
- **Output Formatting**: [Consistent response envelope structure]
- **Error Responses**: [RFC 7807 Problem Details format]
- **Data Types**: [Strict type enforcement with Pydantic/marshmallow]

#### Business Rules
- **Domain Logic**: [Must implement business rules from REQ-NNN exactly]
- **State Transitions**: [Finite state machine per SYS-NNN specification]
- **Calculations**: [Precise algorithms from option_strategy/ documentation]
- **Thresholds**: [Risk parameters from ADR-008 centralized configuration]

### Quality Constraints

#### Performance Requirements
- **Response Time**: [p95 latency < XXXms for API requests]
- **Throughput**: [Minimum XXX requests/second sustained]
- **Concurrency**: [Handle XXX concurrent connections]
- **Resource Utilization**: [CPU < 70% under normal load, Memory < YYY MB]

#### Reliability Requirements
- **Availability**: [99.9% uptime during market hours]
- **Error Rate**: [< 0.1% error rate for all operations]
- **Recovery Time**: [Automatic recovery within 5 minutes]
- **Data Durability**: [Zero data loss for committed transactions]

#### Security Requirements
- **Authentication**: [OAuth 2.0/JWT token validation required]
- **Authorization**: [RBAC with least privilege principle]
- **Encryption**: [TLS 1.3 for transit, AES-256 for rest]
- **Audit Logging**: [All privileged operations logged to WORM storage]

#### Observability Requirements
- **Logging**: [Structured JSON logs with correlation IDs]
- **Metrics**: [Prometheus metrics at /metrics endpoint]
- **Tracing**: [OpenTelemetry with 1% sampling rate]
- **Alerts**: [SLO-based alerting for error rate and latency]

### Operational Constraints

#### Deployment Constraints
- **Pipeline**: [Must pass CI/CD checks: linting, tests, security scans]
- **Rollout Strategy**: [Blue-green or canary deployment only]
- **Environment Parity**: [Staging must mirror production configuration]
- **Approval Gates**: [Manual approval required for production deploys]

#### Maintenance Constraints
- **Code Style**: [Black formatter, Flake8 linter, mypy type checking]
- **Test Coverage**: [Minimum 85% coverage, no decrease from baseline]
- **Documentation**: [All public APIs documented, no missing docstrings]
- **Dependency Updates**: [Automated dependency updates with Dependabot]

#### Monitoring Constraints
- **Health Checks**: [Liveness and readiness probes required]
- **Metrics Collection**: [Prometheus scraping every 15 seconds]
- **Log Retention**: [30 days in Cloud Logging, 1 year in BigQuery]
- **Alert Response**: [P1 alerts require < 15 minute response time]

---

## Acceptance Criteria

### Functional Acceptance

#### Core Functionality
- [ ] Component implements all requirements from REQ-NNN specifications
- [ ] Business logic correctly implements rules from SYS-NNN
- [ ] State transitions follow finite state machine from specifications
- [ ] Data transformations produce correct outputs for all test cases

#### Integration Acceptance
- [ ] Successfully integrates with all specified external systems
- [ ] API contract tests pass for all integration points
- [ ] Message queue interactions validated (publish/consume)
- [ ] Database transactions maintain ACID properties
- [ ] External service failures handled gracefully with fallbacks

#### Error Handling Acceptance
- [ ] All input validation errors return detailed, actionable messages
- [ ] All exception types have explicit handling with logging
- [ ] Circuit breakers activate correctly under failure conditions
- [ ] Retry logic implements exponential backoff with jitter
- [ ] Dead letter queues capture unprocessable messages

#### Data Validation Acceptance
- [ ] Input data validates against JSON schemas
- [ ] Output data conforms to specified response formats
- [ ] Data consistency maintained across all operations
- [ ] Schema migrations tested and reversible

### Non-Functional Acceptance

#### Performance Acceptance
- [ ] p95 latency < XXXms for all API operations
- [ ] p99 latency < YYYms for critical path operations
- [ ] Throughput ≥ XXX requests/second under sustained load
- [ ] Resource utilization within specified limits (CPU/Memory)
- [ ] Database query performance < 100ms for p95

#### Scalability Acceptance
- [ ] Horizontal scaling tested (add instances, verify load distribution)
- [ ] Handles 2x baseline load without performance degradation
- [ ] Auto-scaling triggers work correctly based on metrics
- [ ] Resource limits defined and enforced

#### Reliability Acceptance
- [ ] Maintains availability during single instance failure
- [ ] Recovers automatically from transient failures within 5 minutes
- [ ] Data durability guaranteed (no data loss on commit)
- [ ] Graceful degradation when non-critical services unavailable
- [ ] Health checks correctly reflect service status

#### Security Acceptance
- [ ] Authentication validates all requests with proper token checks
- [ ] Authorization enforces RBAC policies correctly
- [ ] Sensitive data encrypted at rest (AES-256)
- [ ] All communications use TLS 1.3
- [ ] Security scanning passes with no high/critical vulnerabilities
- [ ] Secrets stored in Secret Manager, not in code/config

### Operational Acceptance

#### Deployment Acceptance
- [ ] CI/CD pipeline passes all stages (lint, test, security scan, build)
- [ ] Deployment scripts tested in staging environment
- [ ] Blue-green/canary deployment verified in pre-production
- [ ] Rollback procedure tested and documented
- [ ] Configuration management validated across environments

#### Monitoring Acceptance
- [ ] Health check endpoints respond correctly (liveness/readiness)
- [ ] Prometheus metrics exposed at /metrics with required labels
- [ ] Distributed tracing propagates correlation IDs correctly
- [ ] Alerts trigger at appropriate thresholds and route to correct teams
- [ ] Dashboards display key operational metrics

#### Documentation Acceptance
- [ ] All public APIs documented with usage examples
- [ ] Inline code documentation (docstrings) complete and accurate
- [ ] Operational runbooks updated with deployment/troubleshooting
- [ ] Architecture diagrams reflect current implementation
- [ ] README.md updated with setup instructions and examples

#### Testing Acceptance
- [ ] Unit test coverage ≥ 85% with no decrease from baseline
- [ ] Integration tests validate all external dependencies
- [ ] BDD scenarios from upstream requirements all pass
- [ ] Performance tests validate NFRs under realistic load
- [ ] Security tests pass vulnerability scans

### Validation Methods

| Acceptance Criterion | Validation Method | Evidence Location | Target |
|---------------------|-------------------|-------------------|--------|
| Functional correctness | BDD scenario execution | tests/acceptance/ | 100% pass |
| API contract compliance | Contract testing | tests/contract/ | 100% pass |
| Performance targets | Load testing | tests/performance/ | All NFRs met |
| Security compliance | Vulnerability scanning | Security reports | 0 high/critical |
| Code coverage | Unit testing | Coverage reports | ≥85% |
| Integration correctness | Integration testing | tests/integration/ | 100% pass |

---

## Risk Assessment

### Implementation Risks

#### Technical Risks

**Risk 1: External API Dependency Failure**
- **Description**: Third-party API ([EXTERNAL_DATA_PROVIDER - e.g., Weather API, Stock Data API]/[EXTERNAL_SERVICE_GATEWAY]) becomes unavailable or returns errors
- **Likelihood**: Medium
- **Impact**: High (blocks core functionality)
- **Mitigation**:
  - Implement [SAFETY_MECHANISM - e.g., rate limiter, error threshold] with fallback to cached data
  - Add retry logic with exponential backoff
  - Design graceful degradation with reduced functionality
  - Monitor API health proactively with alerts
- **Contingency**: Use secondary data source if available

**Risk 2: Performance Requirements Not Achievable**
- **Description**: Component cannot meet p95 latency targets under load
- **Likelihood**: Low
- **Impact**: High (violates NFRs)
- **Mitigation**:
  - Profile code early to identify bottlenecks
  - Implement caching strategy for frequently accessed data
  - Optimize database queries with proper indexing
  - Consider async processing for non-critical operations
- **Contingency**: Revise NFRs with stakeholder approval

**Risk 3: Complex Business Logic Implementation**
- **Description**: Algorithm from specifications is ambiguous or difficult to implement correctly
- **Likelihood**: Medium
- **Impact**: Medium (requires clarification, delays)
- **Mitigation**:
  - Clarify requirements with product owner early
  - Implement comprehensive unit tests for edge cases
  - Use property-based testing for algorithm validation
  - Get early code review from domain expert
- **Contingency**: Prototype algorithm separately before integration

**Risk 4: Security Vulnerability in Dependencies**
- **Description**: Third-party library has known CVE
- **Likelihood**: Low
- **Impact**: High (security breach risk)
- **Mitigation**:
  - Use Dependabot for automated dependency updates
  - Run Snyk/OWASP security scans in CI/CD
  - Maintain approved dependencies list
  - Have alternative libraries vetted as fallbacks
- **Contingency**: Replace vulnerable dependency with secure alternative

#### Integration Risks

**Risk 5: Breaking Changes in External APIs**
- **Description**: Upstream service introduces breaking API changes
- **Likelihood**: Low
- **Impact**: High (service outage)
- **Mitigation**:
  - Monitor API provider changelogs and deprecation notices
  - Implement API versioning in client code
  - Add integration tests that detect contract violations
  - Maintain backward compatibility layer
- **Contingency**: Pin to stable API version until migration complete

**Risk 6: Database Schema Migration Failure**
- **Description**: Schema migration causes data corruption or service downtime
- **Likelihood**: Low
- **Impact**: Critical (data loss)
- **Mitigation**:
  - Test migrations in staging with production data snapshots
  - Implement reversible migrations with rollback scripts
  - Backup database before migration
  - Use blue-green deployment to minimize downtime
- **Contingency**: Roll back migration and restore from backup

### Dependencies & Prerequisites

#### Required Before Implementation

**Infrastructure Dependencies**:
- [ ] GCP project provisioned with required APIs enabled
- [ ] Cloud Run service configured with appropriate resource limits
- [ ] Database instance created with connection pooling
- [ ] Secret Manager populated with credentials and API keys
- [ ] VPC and firewall rules configured for service communication

**Service Dependencies**:
- [ ] [Service A] operational and accessible (status: available/pending)
- [ ] [Service B] API credentials obtained (status: available/pending)
- [ ] [Database] schemas migrated and validated (status: available/pending)
- [ ] [Message Queue] topics created and permissions granted (status: available/pending)

**Access & Permissions**:
- [ ] Development environment access granted to team members
- [ ] GCP service account created with least privilege IAM roles
- [ ] Repository write access for feature branch creation
- [ ] Staging environment deployment permissions configured

#### Critical Path Dependencies

**Blocking Tasks** (must complete before this task can start):
- [TASKS-NNN]: [Description of blocking task], Status: [in progress/completed]
- [TASKS-YY]: [Description of blocking task], Status: [in progress/completed]

**Dependent Tasks** (blocked by this task):
- [TASKS-AAA]: [Description of dependent task], Will unblock when: [condition]
- [TASKS-BBB]: [Description of dependent task], Will unblock when: [condition]

**Parallel Tasks** (can execute concurrently):
- [TASKS-PPP]: [Description of parallel task], Coordination needed for: [integration points]
- [TASKS-QQQ]: [Description of parallel task], Coordination needed for: [shared resources]

### Contingency Plans

**Contingency 1: External API Unavailable**
- **Trigger**: API returns 503/504 errors for > 5 minutes
- **Action**: Activate [SAFETY_MECHANISM - e.g., rate limiter, error threshold], serve cached data with freshness warnings
- **Communication**: Notify product owner and customers of degraded functionality
- **Recovery**: Resume normal operations when API health check passes

**Contingency 2: Performance Targets Missed**
- **Trigger**: Load tests show p95 latency > target
- **Action**: Conduct performance profiling, identify top 3 bottlenecks
- **Optimization**: Implement caching, async processing, or algorithm optimization
- **Escalation**: If unresolvable, request NFR revision from stakeholders

**Contingency 3: Scope Creep Detected**
- **Trigger**: Requested features not in SPEC/REQ documents
- **Action**: Document as future enhancement, create new TASKS document
- **Communication**: Confirm scope with product owner, update backlog
- **Protection**: Ensure current task delivers approved specifications only

**Contingency 4: Critical Bug in Production**
- **Trigger**: P1 incident caused by newly deployed code
- **Action**: Execute rollback procedure immediately
- **Investigation**: Root cause analysis within 24 hours
- **Resolution**: Fix, test, and redeploy with additional validation

---

## Success Metrics

### Technical Metrics

#### Code Quality Metrics
- **Static Analysis**: Flake8 score < 10 issues, mypy 100% type coverage
- **Complexity**: Cyclomatic complexity < 10 for all functions
- **Duplication**: Code duplication < 5% (measured by SonarQube)
- **Test Coverage**: Line coverage ≥ 85%, branch coverage ≥ 80%

#### Performance Metrics
- **API Latency**: p50 < XXXms, p95 < YYYms, p99 < ZZZms
- **Throughput**: ≥ XXX requests/second sustained
- **Resource Utilization**: CPU < 70% normal, < 90% peak; Memory < YYY MB
- **Database Performance**: Query p95 < 100ms, connection pool < 80% capacity

#### Reliability Metrics
- **Error Rate**: < 0.1% for all operations over 24-hour period
- **Uptime**: 99.9% availability during operational hours
- **MTTR**: Mean time to recovery < 5 minutes for transient failures
- **Data Integrity**: Zero data loss events, 100% transaction consistency

#### Security Metrics
- **Vulnerability Scan**: Zero high/critical vulnerabilities
- **Dependency Health**: Zero known CVEs in production dependencies
- **Secret Management**: 100% secrets in Secret Manager (0 in code/config)
- **Compliance**: 100% audit log coverage for privileged operations

### Business Metrics

#### Functionality Metrics
- **Feature Completeness**: 100% of REQ specifications implemented
- **Contract Compliance**: 100% API contract tests passing
- **BDD Coverage**: 100% BDD scenarios from upstream SPEC passing
- **Integration Success**: 100% of integration points functional

#### User Experience Metrics (if user-facing)
- **Error Messages**: Clear, actionable guidance for 100% of error conditions
- **Response Times**: User-perceivable operations < 200ms p95
- **Success Rate**: > 99% successful operation completion rate
- **Documentation**: API documentation completeness score ≥ 90%

#### Maintainability Metrics
- **Documentation Coverage**: 100% of public APIs documented
- **Code Comments**: > 20% comment-to-code ratio for complex logic
- **Test Maintainability**: Average test execution time < 30 seconds
- **Technical Debt**: SonarQube maintainability rating A or B

### Process Metrics

#### Planning Accuracy
- **Estimate Accuracy**: Actual effort within 20% of estimate
- **Scope Stability**: Zero unapproved scope changes during implementation
- **Dependency Management**: 100% of dependencies identified upfront
- **Risk Prediction**: Mitigation plans in place for all identified risks

#### Quality Efficiency
- **Defect Rate**: < 5 defects per 1000 lines of code
- **Rework Percentage**: < 10% of effort spent on rework/bug fixes
- **Code Review Efficiency**: First-pass approval rate > 80%
- **Test Effectiveness**: > 95% of bugs caught before production

#### Delivery Speed
- **Cycle Time**: Time from task start to production deployment
- **Lead Time**: Time from task creation to production deployment
- **Deployment Frequency**: Ability to deploy to production daily
- **Change Failure Rate**: < 15% of deployments cause incidents

#### Team Effectiveness
- **Collaboration**: Zero blocked time waiting for dependency resolution
- **Knowledge Sharing**: Implementation notes reviewed by 2+ team members
- **Skill Development**: New techniques/patterns documented for team learning
- **Morale**: Task completed within estimated timeline without overtime

---

## Traceability

### Upstream Sources

Document the business strategy, product requirements, system specifications, and atomic requirements that drive this implementation task.

| Source Type | Document ID | Document Title | Relevant Sections | Relationship |
|-------------|-------------|----------------|-------------------|--------------|
| BRD | [BRD-NNN](../BRD/BRD-NNN_...md) | [Business requirements title] | Sections X.Y | Business objectives this task supports |
| PRD | [PRD-NNN](../PRD/PRD-NNN_...md) | [Product requirements title] | Features A, B, C | Product features this task implements |
| EARS | [EARS-NNN](../EARS/EARS-NNN_...md) | [Engineering requirements] | Event-001, State-002 | Formal requirements this task satisfies |
| ADR | [ADR-NNN](../ADR/ADR-NNN_...md#ADR-NNN) | [Architecture decision title] | Decision, Consequences | Architectural approach this task follows |
| SYS | [SYS-NNN](../SYS/SYS-NNN_...md) | [System requirements title] | Sections 3.1, 4.2 | System specification this task implements |
| REQ | [REQ-NNN](../REQ/.../REQ-NNN_...md#REQ-NNN) | [Atomic requirement title] | All acceptance criteria | Detailed requirements this task fulfills |

**Business Context**:
- Business Objective: [Specific goal from BRD] → Enabled by completing this task
- Product Feature: [User-facing capability from PRD] → Delivered by this implementation
- Strategic Value: [Business value proposition] → Realized through this component

**Engineering Context**:
- EARS Requirements: [Event-driven/state-driven requirements] → Implemented in this task
- System Capabilities: [System-level functionality] → Delivered by this component
- Quality Attributes: [Performance, security, reliability NFRs] → Achieved through implementation

**Architecture Context**:
- Architecture Decision: [ADR title and key decision] → Applied in this implementation
- Technology Selection: [Chosen technologies and frameworks] → Used in this task
- Integration Pattern: [How this fits into overall architecture] → Implemented here

### Downstream Artifacts

Document the technical specifications, contracts, and tests that guide and validate this implementation.

#### Technical Specifications

| SPEC ID | Specification Title | Task Implementation Scope | Relationship |
|---------|-------------------|-------------------------|--------------|
| [SPEC-NNN](../SPEC/.../SPEC-NNN.yaml) | [Technical spec title] | This task implements sections X, Y, Z | Implementation blueprint |
| [SPEC-MMM](../SPEC/.../SPEC-MMM.yaml) | [Interface spec] | This task implements API contracts | Interface implementation |

**Specification Coverage**:
- All SPEC sections mapped to implementation plan steps
- All interface definitions implemented and validated
- All NFRs from specifications met and verified

|  |  | Task Contract Implementation | Relationship |
|-------------|---------------|----------------------------|--------------|

**Contract Compliance**:
- All API endpoints match OpenAPI specification exactly
- All request/response schemas validated
- All error responses follow RFC 7807 format
- All message formats match schema definitions

#### Behavior-Driven Development

| BDD ID | BDD Feature/Scenario | Task BDD Coverage | Test Status | Relationship |
|--------|---------------------|------------------|-------------|--------------|
| [BDD-NNN](../BDD/BDD-NNN.feature) | Feature: [Feature name] | Scenarios 1-5 validated by this task | Pending/Pass/Fail | Acceptance test |
| [BDD-NNN](../BDD/BDD-NNN.feature#scenario-1) | Scenario: [Specific scenario] | Specific acceptance criterion validated | Pending/Pass/Fail | Functional validation |
| [BDD-MMM](../BDD/BDD-MMM.feature) | Feature: [Error handling] | Error scenarios validated | Pending/Pass/Fail | Negative testing |

**BDD Coverage Summary**:
- Total BDD scenarios: [count]
- Scenarios covered by this task: [count]
- Scenarios passing: [count]
- Scenarios pending: [count]
- Scenarios failing: [count requiring remediation]

### BDD Mapping

**Detailed Scenario-to-Implementation Mapping**:

| BDD Scenario | Implementation Step | Code Location | Test File | Status |
|--------------|-------------------|---------------|-----------|--------|
| [BDD-NNN#scenario-1](../BDD/BDD-NNN.feature#scenario-1) | Phase 2.2: Core Logic | src/module/component.py:function_name() | tests/acceptance/test_scenario_1.py | ✅ Pass |
| [BDD-NNN#scenario-2](../BDD/BDD-NNN.feature#scenario-2) | Phase 2.3: Integration | src/module/api_client.py:call_external() | tests/acceptance/test_scenario_2.py | 🔄 Pending |
| [BDD-MMM#error-1](../BDD/BDD-MMM.feature#error-1) | Phase 2.4: Error Handling | src/module/error_handler.py:handle_error() | tests/acceptance/test_errors.py | ✅ Pass |

**Acceptance Criteria Validation**:

| Acceptance Criterion (from REQ-NNN) | BDD Validation | Implementation Evidence | Status |
|------------------------------------|----------------|------------------------|--------|
| Primary Functional Criteria #1 | [BDD-NNN.feature](../BDD/BDD-NNN.feature) Lines 20-45 | src/module/component.py:120-145 | ✅ Validated |
| Error and Edge Case #1 | [BDD-MMM.feature](../BDD/BDD-MMM.feature) Lines 100-120 | src/module/error_handler.py:50-75 | ✅ Validated |
| Quality and Constraint #1 | Performance test results | tests/performance/load_test.py | 🔄 Pending |

### Code Implementation Paths

**Primary Implementation Locations**:
- `src/[module_name]/[component_name].py`: Core implementation (Lines XXX-YY)
- `src/[module_name]/interfaces/[interface_name].py`: External API interfaces
- `src/[module_name]/services/[service_name].py`: Business logic and service layer
- `src/[module_name]/repositories/[repo_name].py`: Data access layer
- `src/[module_name]/models/[model_name].py`: Domain models and data structures
- `src/[module_name]/utils/[util_name].py`: Helper utilities and shared functions

**Configuration Paths**:
- `config/[module_name].yaml`: Component configuration
- `config/environments/[env]/[module_name].yaml`: Environment-specific configuration
- `config/environments/[env]/.env`: Environment variables (not in version control)

**Test Paths**:
- `tests/unit/[module_name]/test_[component].py`: Unit tests for this component
- `tests/integration/[module_name]/test_[integration].py`: Integration tests
- `tests/acceptance/[module_name]/test_[scenario].py`: BDD scenario tests
- `tests/performance/[module_name]/test_[load].py`: Load and performance tests
- `tests/contract/[module_name]/test_[contract].py`: Contract validation tests
- `tests/security/[module_name]/test_[security].py`: Security validation tests

**Supporting Components**:
- `src/[module_name]/validators/[validator].py`: Input and output validation
- `src/[module_name]/transformers/[transformer].py`: Data transformation logic
- `src/[module_name]/handlers/[handler].py`: Event and error handlers
- `src/[module_name]/middleware/[middleware].py`: Request/response middleware

**Infrastructure**:
- `.github/workflows/[workflow].yml`: CI/CD pipeline configuration
- `docker/Dockerfile.[component]`: Container image definition
- `terraform/[component]/`: Infrastructure as Code
- `k8s/[component]/`: Kubernetes manifests (if applicable)

### Validation Evidence

Document evidence that this task has been implemented correctly and meets all acceptance criteria.

| Validation Type | Validation Method | Evidence Location | Result | Date Validated |
|----------------|-------------------|-------------------|--------|----------------|
| Unit Testing | Automated unit tests | tests/unit/test_[component].py | PASS (85% coverage) | YYYY-MM-DD |
| Integration Testing | Automated integration tests | tests/integration/test_[workflow].py | PASS | YYYY-MM-DD |
| BDD Scenarios | Automated acceptance tests | tests/acceptance/test_scenarios.py | PASS (10/10 scenarios) | YYYY-MM-DD |
| Performance Testing | Load testing | tests/performance/load_test_results.html | PASS (all NFRs met) | YYYY-MM-DD |
| Security Testing | Vulnerability scan | security_reports/scan_YYYY-MM-DD.pdf | PASS (0 high/critical) | YYYY-MM-DD |
| Contract Testing | API contract validation | tests/contract/contract_test_results.json | PASS | YYYY-MM-DD |
| Code Review | Manual peer review | GitHub PR #XXXX reviews | APPROVED | YYYY-MM-DD |
| Documentation Review | Manual review | Docs reviewed by [reviewer] | APPROVED | YYYY-MM-DD |

**Test Coverage Summary**:
- Unit test coverage: [XX]% (target: ≥85%)
- Integration test coverage: [YY]% (target: ≥75%)
- BDD scenario coverage: [ZZ]% acceptance criteria (target: 100%)
- Contract test coverage: [WW]% integration points (target: 100%)

**Quality Gate Results**:
- ✅ All unit tests passing (XXX tests, 0 failures)
- ✅ All integration tests passing (YYY tests, 0 failures)
- ✅ All BDD scenarios passing (ZZZ scenarios, 0 failures)
- ✅ Code coverage meets threshold (≥85%)
- ✅ Static analysis passes (0 high-severity issues)
- ✅ Security scan passes (0 high/critical vulnerabilities)
- ✅ Performance tests meet NFRs
- ✅ Code review approved

### Cross-Reference Validation

**Validation Checklist**:
- ✅ All BRD references resolve to valid business documents
- ✅ All PRD references resolve to valid product requirements
- ✅ All EARS references resolve to valid engineering requirements
- ✅ All ADR references resolve to valid architecture decisions
- ✅ All SYS references resolve to valid system specifications
- ✅ All REQ references resolve to valid atomic requirements
- ✅ All SPEC references resolve to valid technical specifications
- ✅ All BDD references resolve to valid test scenarios
- ✅ All code paths exist in implementation
- ✅ All test paths exist in test suites
- ✅ All configuration files exist and are valid

**Reference Integrity**:
- Last validated: [YYYY-MM-DD]
- Validation tool: [scripts/validate_traceability.py]
- Broken references: [0] (target: 0)
- Stale references: [0] references to deprecated documents (target: 0)

**Traceability Metrics**:
- Upstream traceability: 100% (all requirements traced to source)
- Downstream traceability: 100% (all artifacts traced to implementation)
- Bidirectional traceability: 100% (complete trace chains)
- Orphaned artifacts: 0 (all artifacts have source requirements)

**Document Metadata**:
- Document format: Markdown (.md)
- Schema version: 1.0 (TASKS-TEMPLATE v1.0)
- Line count: [Auto-generated on save]
- Last modified: [Auto-generated on save]
- Git hash: [Commit SHA when checked in]
- Template compliance: ✅ Validated

### Traceability Tags

**Required Tags** (Cumulative Tagging Hierarchy - Layer 11):
```markdown
@brd: BRD-NNN:REQUIREMENT-ID
@prd: PRD-NNN:REQUIREMENT-ID
@ears: EARS-NNN:STATEMENT-ID
@bdd: BDD-NNN:SCENARIO-ID
@adr: ADR-NNN
@sys: SYS-NNN:SECTION-ID
@req: REQ-NNN:REQUIREMENT-ID
@impl: IMPL-NNN:PHASE-ID
@ctr: CTR-NNN
@spec: SPEC-NNN
```

**Format**: `@artifact-type: DOCUMENT-ID:REQUIREMENT-ID`

**Layer 11 Requirements**: TASKS must reference ALL upstream artifacts:
- `@brd`: Business Requirements Document(s)
- `@prd`: Product Requirements Document(s)
- `@ears`: EARS Requirements
- `@bdd`: BDD Scenarios
- `@adr`: Architecture Decision Records
- `@sys`: System Requirements
- `@req`: Atomic Requirements
- `@impl`: Implementation Plans (optional - include if exists in chain)
- `@ctr`: API Contracts (optional - include if exists in chain)
- `@spec`: Technical Specifications

**Tag Placement**: Include tags in this section or at the top of the document (after Document Control).

**Example**:
```markdown
@brd: BRD-001:FR-030
@prd: PRD-003:FEATURE-002
@ears: EARS-001:EVENT-003
@bdd: BDD-003:scenario-realtime-quote
@adr: ADR-033
@sys: SYS-008:PERF-001
@req: REQ-003:interface-spec
@impl: IMPL-001:phase1
@ctr: CTR-001
@spec: SPEC-003
```

**Validation**: Tags must reference existing documents and requirement IDs. Complete chain validation ensures all upstream artifacts (BRD through SPEC) are properly linked.

**Purpose**: Cumulative tagging enables complete traceability chains from business requirements through code generation plans. See [TRACEABILITY.md](../TRACEABILITY.md#cumulative-tagging-hierarchy) for complete hierarchy documentation.

---

## Implementation Notes

### Design Considerations

#### Architectural Patterns

**Pattern Selection**:
- **Hexagonal Architecture**: Isolate business logic from infrastructure concerns
  - Core domain in `src/[module]/domain/`
  - Ports (interfaces) in `src/[module]/ports/`
  - Adapters (implementations) in `src/[module]/adapters/`
- **Repository Pattern**: Abstract data access behind interfaces
  - Define repository interfaces in domain layer
  - Implement concrete repositories for database, cache, external APIs
- **Service Layer**: Orchestrate business workflows
  - Services coordinate multiple repositories and domain objects
  - Keep services thin, business logic in domain models

**Integration Approaches**:
- **API Client Pattern**: Encapsulate external API calls
  - Retry logic with exponential backoff
  - [SAFETY_MECHANISM - e.g., rate limiter, error threshold] for fault tolerance
  - Request/response logging with correlation IDs
- **Event-Driven Communication**: Use pub/sub for async operations
  - Publisher publishes domain events to topics
  - Subscribers process events independently
  - Dead letter queue for failed message processing

**Scalability Patterns**:
- **Stateless Services**: No local state, all state in database/cache
- **Horizontal Scaling**: Add instances to handle increased load
- **Caching Strategy**: Redis for frequently accessed data
  - Cache-aside pattern with TTL
  - Cache invalidation on write operations
  - Fallback to database on cache miss

#### Technology Choices

**Language & Framework**:
- **Python 3.11+**: Modern Python with type hints
- **FastAPI**: High-performance async web framework
- **Pydantic**: Data validation and settings management
- **SQLAlchemy**: ORM for database access
- **Alembic**: Database migrations

**Data Storage**:
- **PostgreSQL**: Primary transactional database
  - Connection pooling with pg_bouncer
  - Read replicas for read-heavy operations
- **Redis**: Caching and session storage
  - Redis Cluster for high availability
  - TTL-based eviction policy

**Communication**:
- **Google Cloud Pub/Sub**: Async messaging
  - Topic-per-domain pattern
  - Message deduplication with idempotency keys
- **gRPC**: Inter-service synchronous communication
  - Protobuf for schema definition
  - HTTP/2 multiplexing for efficiency

**Observability**:
- **Google Cloud Logging**: Centralized logging
  - Structured JSON logs
  - Correlation ID propagation
- **Cloud Monitoring**: Metrics and alerts
  - Prometheus-compatible metrics
  - SLO-based alerting
- **Cloud Trace**: Distributed tracing
  - OpenTelemetry instrumentation
  - 1% sampling rate

#### Algorithm Approaches

**Core Algorithm Implementation**:
- [Description of key algorithm from specifications]
- Time complexity: O(n log n) for [operation]
- Space complexity: O(n) for [data structure]
- Edge cases handled: [list specific edge cases]

**Optimization Techniques**:
- Memoization for expensive calculations
- Batch processing for multiple items
- Lazy evaluation for deferred computation
- Index-based lookups for O(1) access

### Testing Strategy

#### Unit Testing Approach

**Test Framework**: pytest with pytest-cov for coverage

**Test Organization**:
- One test file per implementation file
- Test class per implementation class
- Test method per public method
- Fixtures for common test data

**Test Coverage Goals**:
- ≥85% line coverage
- ≥90% branch coverage for critical paths
- 100% coverage for error handling code
- Property-based tests for algorithms (hypothesis library)

**Mocking Strategy**:
- Mock external dependencies (APIs, databases, message queues)
- Use dependency injection for easy mocking
- Verify mock interactions (method calls, arguments)
- Use real implementations for internal dependencies

#### Integration Testing Approach

**Test Scope**:
- End-to-end workflow validation
- Database transaction integrity
- External service integration
- Message queue publish/consume

**Test Environment**:
- Docker Compose for local test environment
- Test database with isolated schema
- Mock external services with WireMock
- Local Pub/Sub emulator for messaging

**Data Management**:
- Test fixtures for consistent test data
- Database reset between test runs
- Idempotent tests (repeatable)
- Cleanup test data after execution

#### Performance Testing Approach

**Load Testing**:
- Tool: Locust or k6 for load generation
- Scenarios: Realistic user workflows
- Ramp-up: Gradual increase from 0 to peak load
- Duration: Sustained load for 30+ minutes
- Metrics: Latency percentiles, throughput, error rate

**Stress Testing**:
- Push system beyond normal capacity
- Identify breaking point and failure modes
- Verify graceful degradation
- Test recovery after stress removal

**Profiling**:
- CPU profiling with cProfile
- Memory profiling with memory_profiler
- Identify performance bottlenecks
- Optimize hot paths

### Deployment Strategy

#### CI/CD Pipeline

**Build Stage**:
1. Lint code (Flake8, Black, mypy)
2. Run unit tests with coverage
3. Security scan dependencies (Snyk, OWASP)
4. Build container image
5. Push image to Artifact Registry

**Test Stage**:
1. Deploy to test environment
2. Run integration tests
3. Run acceptance tests (BDD scenarios)
4. Run performance tests
5. Run security tests (DAST, penetration testing)

**Deploy Stage**:
1. Deploy to staging (automatic)
2. Run smoke tests
3. Manual approval for production
4. Deploy to production (blue-green/canary)
5. Monitor health checks and alerts

#### Deployment Approach

**Blue-Green Deployment**:
- Maintain two identical production environments (blue/green)
- Deploy new version to inactive environment
- Run smoke tests on inactive environment
- Switch traffic to new version with load balancer
- Keep old version running for quick rollback

**Canary Deployment**:
- Deploy new version to small subset of instances (5-10%)
- Monitor metrics (error rate, latency) for 15-30 minutes
- Gradually increase traffic to new version (25%, 50%, 75%, 100%)
- Rollback if metrics degrade
- Full rollout if metrics remain healthy

**Rollback Procedure**:
1. Detect deployment issue (monitoring alerts, manual observation)
2. Execute rollback command (`gcloud run services update-traffic --to-revisions=previous=100`)
3. Verify old version is serving traffic
4. Investigate root cause
5. Fix issue and redeploy

#### Configuration Management

**Environment Variables**:
- Loaded from `.env` files (local) or Secret Manager (cloud)
- Separate configuration per environment (dev/staging/prod)
- Never commit secrets to version control
- Use Pydantic Settings for type-safe configuration

**Feature Flags**:
- LaunchDarkly or similar feature flag service
- Toggle features without code deployment
- Percentage-based rollouts
- User/organization-targeted flags
- Kill switch for problematic features

**Secrets Management**:
- Google Secret Manager for all secrets
- Secrets mounted as environment variables or files
- Automatic rotation for credentials
- Audit logging for secret access

---

## Change History

| Date | Version | Change | Author | Approved By |
|------|---------|--------|--------|-------------|
| YYYY-MM-DD | 1.0 | Initial task document created | [Author Name] | [Approver Name] |
| YYYY-MM-DD | 1.1 | Updated acceptance criteria based on code review feedback | [Author Name] | [Approver Name] |
| YYYY-MM-DD | 1.2 | Added performance optimization notes after load testing | [Author Name] | [Approver Name] |
| YYYY-MM-DD | 2.0 | Major revision to align with new SPEC-NNN specification | [Author Name] | [Approver Name] |

**Template Version**: 1.0
**Template Compliance**: ✅ Validated against REQ/SYS/EARS/PRD templates
**Next Review**: YYYY-MM-DD (recommended: upon task completion or every 30 days for long-running tasks)
**Technical Contact**: [Name/Email for technical questions]
**Product Owner**: [Name/Email for requirements clarification]

---

## References

### Internal Documentation

- [TASKS Guidelines](README.md) - Best practices for writing implementation tasks
- [REQ Template](../REQ/REQ-TEMPLATE.md) - Atomic requirements format
- [SPEC Template](../SPEC/SPEC-TEMPLATE.yaml) - Technical specification format
- [BDD Template](../BDD/BDD-TEMPLATE.feature) - Behavior-driven development scenarios
- [ADR Template](../ADR/ADR-TEMPLATE.md) - Architecture decision records

### Development Resources

- [Python Style Guide](https://peps.python.org/pep-0008/) - PEP 8 coding standards
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Web framework reference
- [pytest Documentation](https://docs.pytest.org/) - Testing framework reference
- [Google Cloud Python SDK](https://cloud.google.com/python/docs/reference) - GCP client libraries

### Architecture & Patterns

- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/) - Ports and Adapters pattern
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html) - Data access abstraction
- [[SAFETY_MECHANISM - e.g., rate limiter, error threshold] Pattern](https://martinfowler.com/bliki/CircuitBreaker.html) - Fault tolerance pattern
- [Event-Driven Architecture](https://martinfowler.com/articles/201701-event-driven.html) - Async communication

### Testing Resources

- [Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html) - Testing strategy
- [Contract Testing](https://pactflow.io/blog/what-is-contract-testing/) - API contract validation
- [Property-Based Testing](https://hypothesis.readthedocs.io/) - Hypothesis library for Python
- [BDD Best Practices](https://cucumber.io/docs/bdd/) - Behavior-driven development guide

### Domain References

- [[DOMAIN_ACTIVITY - e.g., payment processing, content moderation] Concepts](https://www.theocc.com/Company-Information/What-We-Do) - Options Clearing Corporation
- [[RESOURCE_MANAGEMENT - e.g., capacity planning, quota management]](https://www.cmegroup.com/education/risk-management.html) - CME Group resources
- [[EXTERNAL_DATA - e.g., customer data, sensor readings] Protocols](https://www.fixtrading.org/standards/) - FIX Protocol standards

### Technology Standards

- [OpenAPI Specification](https://swagger.io/specification/) - API contract format
- [JSON Schema](https://json-schema.org/) - Data validation schema
- [RFC 7807](https://datatracker.ietf.org/doc/html/rfc7807) - Problem Details for HTTP APIs
- [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339) - Date and time format

### Observability & Monitoring

- [Prometheus Best Practices](https://prometheus.io/docs/practices/) - Metrics collection
- [OpenTelemetry](https://opentelemetry.io/docs/) - Distributed tracing standard
- [Google Cloud Monitoring](https://cloud.google.com/monitoring/docs) - GCP monitoring guide
- [SLO/SLI Best Practices](https://cloud.google.com/blog/products/devops-sre/sre-fundamentals-sli-vs-slo-vs-sla) - Service level objectives

---

**End of TASKS Template**

**Usage Instructions**:
1. Copy this template to create new TASKS documents
2. Replace all placeholders (NNN, [descriptions], YYYY-MM-DD) with actual values
3. Remove sections that are not applicable (mark as "N/A" instead of deleting)
4. Ensure all traceability links resolve to valid documents
5. Update Document Control table as task progresses
6. Validate template compliance using `python scripts/validate_traceability.py`
7. Update Change History upon each significant modification
8. Review and update TASKS-000_index.md when creating new tasks
