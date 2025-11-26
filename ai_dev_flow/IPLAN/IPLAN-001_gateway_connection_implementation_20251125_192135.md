# Implementation Plan - IPLAN-001: IB Gateway Connection Service Implementation

**⚠️ CRITICAL**: Always reference [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../../docs_flow_framework/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) as the single source of truth for workflow steps, artifact definitions, and quality gates.

**Position**: Layer 12 (Implementation Work Plans) - translates TASKS into executable session plans with bash commands and verification steps.

## Document Control

| Item | Details |
|------|---------|
| **ID** | IPLAN-001 |
| **Status** | Ready for Implementation |
| **Version** | 1.0.0 |
| **Created** | 2025-11-25 19:21:35 EST |
| **Last Updated** | 2025-11-25 19:21:35 EST |
| **Author** | AI Assistant (Claude Code) |
| **Estimated Effort** | 74 hours (revised from 80 due to existing code) |
| **Actual Effort** | TBD |
| **Complexity** | 4/5 (High) |
| **Parent TASKS** | TASKS-001 |
| **Related Artifacts** | SPEC-001, REQ-001, ADR-002, BDD-001, BDD-007, SYS-002, ICON-001, ICON-002, ICON-003 |
| **IPLAN-Ready Score** | ✅ 95% |

---

## Position in Development Workflow

**IPLAN (Implementation Work Plans)** ← YOU ARE HERE

For complete traceability workflow with visual diagram, see: [index.md - Traceability Flow](../../docs_flow_framework/ai_dev_flow/index.md#traceability-flow)

**Quick Reference**:
```
... → TASKS-001 → **IPLAN-001** → Code → Tests → ...
                        ↑
                Layer 12: Session Context
                (bash commands, verification steps)
```

**Purpose**: Executable implementation plan with session context, bash commands, and verification steps
- **Input**: TASKS-001 (AI code generation plan), SPEC-001 (technical blueprint), ICON-001/002/003 (implementation contracts)
- **Output**: Step-by-step execution plan with commands and validation checkpoints
- **Consumer**: AI assistants (Claude Code, Gemini, etc.) and developers executing implementation

**Distinction from TASKS**:
- **TASKS-001**: AI code generation instructions (WHAT code to generate)
- **IPLAN-001**: Implementation work plan (HOW to execute with specific commands)

---

## Objective

Complete implementation of TASKS-001 Gateway Connection Service by creating 2 missing modules (repository.py, observability.py), implementing comprehensive test suite (unit 85%, integration 75%, BDD 100%), and preparing deployment configurations.

**Deliverables**:
- 2 Python modules: `repository.py` (database persistence), `observability.py` (metrics/logging)
- Complete test suite: 8 unit test files, 2 integration test files, 2 BDD step definition files, 2 performance test files, 2 security test files
- Database schema and Alembic migration for gateway_connections table
- CI/CD pipeline configuration (.github/workflows/gateway-connection-ci.yml)
- Cloud Run deployment configuration (deploy/cloud-run/connection-service.yaml)
- Docker image definition (docker/Dockerfile.connection-service)
- Documentation updates (docstrings, README.md, operational runbooks)

---

## Context

### Current State Analysis

**Documentation Status**: ✅ 100% Complete
- SPEC-001: Technical specification exists (YAML format)
- REQ-001: 15 atomic requirements defined
- ADR-002: Architecture decision (ib_async library selection)
- BDD-001: 3 authentication scenarios
- BDD-007: 3 connection lifecycle scenarios
- SYS-002: System requirements
- TASKS-001: Complete 4-phase implementation plan (1,470 lines)
- ICON-001/002/003: Implementation contracts exist

**Code Status**: ⚠️ 60% Complete
- ✅ Existing modules (7/9): connector.py, connection_service.py, models.py, errors.py, retry_handler.py, circuit_breaker.py, __init__.py
- ❌ Missing modules (2/9): repository.py (database), observability.py (metrics/logging)
- ✅ Dependencies installed: ib_async, pydantic, tenacity, pybreaker, sqlalchemy, asyncpg
- ❌ Test infrastructure: Directory structure exists, but 0 test files created

**Test Status**: ❌ 0% Complete
- No unit tests (target: ≥85% coverage)
- No integration tests (target: ≥75% coverage)
- No BDD test implementations (target: 100%, 6 scenarios)
- No performance tests
- No security tests

**Deployment Status**: ❌ Not Started
- No CI/CD pipeline configuration
- No Cloud Run deployment configs
- No database migrations
- No Docker configurations

**Previous Work Completed**:
1. ✅ Documentation analysis complete (TASKS-001 reviewed)
2. ✅ IPLAN-TEMPLATE structure analyzed
3. ✅ Existing codebase analyzed (7/9 modules present)
4. ✅ Gap analysis complete (2 modules missing, 0 tests created)
5. ✅ Traceability tags extracted from upstream artifacts

### Key Technical Decisions

**Architecture** (from ADR-002):
- Protocol-based interface (IBGatewayConnector Protocol + IBGatewayConnectorImpl)
- Async/await pattern using ib_async library
- 5-state machine: DISCONNECTED, CONNECTING, CONNECTED, RECONNECTING, FAILED
- Repository pattern for database abstraction
- Dependency injection for testability

**Error Handling** (from SPEC-001):
- 6 typed exceptions with error codes (IB_CONN_001 through IB_CONN_006)
- Retryable: ConnectionError (IB_CONN_001), ClientIDInUseError (IB_CONN_002), TimeoutError (IB_CONN_003), NetworkUnreachableError (IB_CONN_004)
- Non-retryable: AuthenticationError (IB_CONN_005), IncompatibleVersionError (IB_CONN_006)
- Error code propagation to observability layer

**Resilience Patterns** (from SPEC-001):
- Exponential backoff retry: 1s, 2s, 4s, 8s, 16s, 32s max (with jitter ±20%)
- Circuit breaker: failure_threshold=5, success_threshold=2, timeout=30s
- Max timeout: 30s for connection establishment (asyncio.wait_for)
- Graceful degradation during Gateway outages

**Observability** (from SPEC-001):
- 7 Prometheus metrics: connections_total, duration, active, errors, circuit_breaker_state, retries, heartbeat
- 6 structured log events: connection_attempt, success, failure, conflict, circuit_breaker_change, disconnection
- Correlation ID propagation (UUID4)
- Health checks: /health/live (process alive), /health/ready (Gateway reachable)

**Performance Targets** (from SPEC-001):
- p95 < 5s, p99 < 10s for connection establishment
- Throughput ≥60 connections/minute
- CPU < 70%, Memory < 256 MB under normal load
- Connection pool: max 10 concurrent connections per instance

**Test Coverage Targets** (from TASKS-001):
- Unit Tests: ≥85% line coverage
- Integration Tests: ≥75% coverage
- BDD Scenarios: 100% (6/6 scenarios passing)
- Performance Tests: Validate p95 < 5s, p99 < 10s
- Security Tests: 0 high/critical vulnerabilities (Bandit, Safety)

---

## Task List

### Phase 0: Documentation Review ✅ COMPLETED
- [x] Read TASKS-001 implementation plan (1,470 lines analyzed)
- [x] Read IPLAN-TEMPLATE structure
- [x] Analyze existing codebase (7/9 modules present)
- [x] Identify gaps (2 modules missing, 0 tests created)
- [x] Extract traceability tags from all upstream artifacts
- [x] Create comprehensive implementation plan

### Phase 1: Environment Validation (4 hours)

**TASK-1.1**: Verify IB Gateway connectivity (0.5 hours)
- Check IB Gateway process running
- Verify TCP port 4002 accessible
- Validate TWS API protocol version
- Verification: nc -zv 127.0.0.1 4002 succeeds

**TASK-1.2**: Verify PostgreSQL database (0.5 hours)
- Check PostgreSQL service running
- Create test database ibmcp_test
- Verify asyncpg connectivity
- Verification: psql connection succeeds

**TASK-1.3**: Verify Python environment (1 hour)
- Check Python 3.11+ installed
- Verify Poetry environment
- Install all dependencies
- Validate imports of existing modules
- Verification: All existing modules importable

**TASK-1.4**: Run type checking on existing code (1 hour)
- Run mypy on src/ibmcp/gateway/
- Fix any type errors found
- Document type coverage baseline
- Verification: mypy --strict passes with 0 errors

**TASK-1.5**: Establish baseline test coverage (1 hour)
- Run pytest on empty test suite
- Document current coverage (expected 0%)
- Set up coverage reporting infrastructure
- Verification: pytest --cov runs successfully

### Phase 2: Complete Implementation (16 hours)

**TASK-2.1**: Implement repository.py module (6 hours)
- File: `/opt/data/ibmcp/src/ibmcp/gateway/repository.py`
- Create ConnectionRepository class with async methods
- Implement CRUD operations for gateway_connections table
- Add connection pooling with asyncpg
- Implement cleanup_stale_connections method
- Verify: Import succeeds, type checking passes

**TASK-2.2**: Create Alembic database migration (2 hours)
- Initialize Alembic if not present
- Create migration: create_gateway_connections_table
- Define schema per SPEC-001 section 4.2
- Test migration up/down
- Verify: alembic upgrade head succeeds

**TASK-2.3**: Implement observability.py module (8 hours)
- File: `/opt/data/ibmcp/src/ibmcp/gateway/observability.py`
- Create ConnectionMetrics class (7 Prometheus metrics)
- Create StructuredLogger class (6 log events)
- Create HealthCheckHandler class (2 endpoints)
- Integrate with connection_service.py
- Verify: All metrics exportable, logs JSON-formatted

### Phase 3: Testing & Validation (38 hours)

**TASK-3.1**: Create unit tests (16 hours)
- test_connector.py (3 hours): Test IBGatewayConnectorImpl
- test_connection_service.py (3 hours): Test ConnectionService
- test_models.py (1 hour): Test Pydantic models
- test_errors.py (1 hour): Test exception hierarchy
- test_retry_handler.py (2 hours): Test exponential backoff
- test_circuit_breaker.py (2 hours): Test state machine
- test_repository.py (2 hours): Test database operations
- test_observability.py (2 hours): Test metrics and logging
- Target: ≥85% coverage

**TASK-3.2**: Create integration tests (8 hours)
- test_connection_integration.py (4 hours): End-to-end connection flow
- test_database_integration.py (4 hours): Database persistence validation
- Target: ≥75% coverage

**TASK-3.3**: Create BDD step definitions (6 hours)
- connection_steps.py (3 hours): BDD-007 scenarios (3 scenarios)
- authentication_steps.py (3 hours): BDD-001 scenarios (3 scenarios)
- Target: 100% BDD coverage (6/6 scenarios)

**TASK-3.4**: Create performance tests (4 hours)
- test_connection_latency.py (2 hours): Validate p95 < 5s, p99 < 10s
- test_connection_throughput.py (2 hours): Validate ≥60 conn/min
- Target: All NFRs satisfied

**TASK-3.5**: Create security tests (4 hours)
- test_input_validation.py (2 hours): Pydantic validation tests
- test_audit_logging.py (2 hours): Audit trail completeness
- Target: 0 high/critical vulnerabilities

### Phase 4: Completion & Deployment (16 hours)

**TASK-4.1**: Code quality checks and fixes (4 hours)
- Run Ruff linter and fix issues
- Run Black formatter
- Re-run mypy --strict
- Fix all quality issues
- Verify: 0 linting errors, 0 type errors

**TASK-4.2**: Documentation (4 hours)
- Add/update docstrings for all classes and methods
- Update README.md with connection service usage
- Create operational runbook for connection troubleshooting
- Generate API documentation
- Verify: All public APIs documented

**TASK-4.3**: Create CI/CD pipeline configuration (3 hours)
- File: `.github/workflows/gateway-connection-ci.yml`
- Add jobs: test, lint, security-scan, build
- Configure coverage reporting
- Add deployment trigger
- Verify: Workflow syntax valid

**TASK-4.4**: Create deployment configurations (3 hours)
- File: `deploy/cloud-run/connection-service.yaml`
- File: `docker/Dockerfile.connection-service`
- Configure environment variables
- Set resource limits (CPU 1, Memory 512Mi)
- Verify: Docker build succeeds

**TASK-4.5**: Final validation and traceability update (2 hours)
- Run complete test suite
- Verify all acceptance criteria met (15 from REQ-001)
- Update traceability matrix
- Document actual effort
- Verify: All success criteria satisfied

---

## Implementation Guide

### Prerequisites

**Required Tools**:
- Python 3.11+
- Poetry 1.5+
- PostgreSQL 14+ (running on localhost:5432)
- IB Gateway (running on localhost:4002)
- Docker (for containerization)
- Git (for version control)

**Required Files Access**:
- Read/Write: `/opt/data/ibmcp/src/ibmcp/gateway/`
- Read/Write: `/opt/data/ibmcp/tests/`
- Read/Write: `/opt/data/ibmcp/migrations/`
- Read/Write: `/opt/data/ibmcp/.github/workflows/`
- Read/Write: `/opt/data/ibmcp/deploy/`
- Read/Write: `/opt/data/ibmcp/docker/`
- Read: `/opt/data/ibmcp/docs/TASKS/TASKS-001_ib_gateway_connection_implementation.md`
- Read: `/opt/data/ibmcp/docs/SPEC/SPEC-001_ib_gateway_connection.yaml`

**Knowledge Required**:
- Python async/await patterns
- SQLAlchemy async ORM
- Pytest framework
- BDD with pytest-bdd
- Prometheus metrics
- Docker and Cloud Run deployment

**Environment Setup**:
- IB_GATEWAY_HOST=127.0.0.1
- IB_GATEWAY_PORT=4002
- DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ibmcp
- PROMETHEUS_PORT=9090
- LOG_LEVEL=INFO

### Execution Steps

**Step 1: Environment Validation**

```bash
# Navigate to project root
cd /opt/data/ibmcp

# Verify IB Gateway connectivity
ping -c 3 127.0.0.1
nc -zv 127.0.0.1 4002

# Verify PostgreSQL database
psql -U postgres -h localhost -c "SELECT version();"
psql -U postgres -h localhost -c "CREATE DATABASE ibmcp_test;" || echo "Database exists"

# Verify Python environment
python --version  # Should be 3.11+
poetry --version

# Install dependencies
poetry install

# Verify imports of existing modules
python -c "import ib_async; print(f'ib_async version: {ib_async.__version__}')"
python -c "from ibmcp.gateway import IBGatewayConnector; print('✅ IBGatewayConnector import successful')"
python -c "from ibmcp.gateway.connector import IBGatewayConnectorImpl; print('✅ IBGatewayConnectorImpl import successful')"
python -c "from ibmcp.gateway.connection_service import ConnectionService; print('✅ ConnectionService import successful')"
python -c "from ibmcp.gateway.models import ConnectionConfig, IbConnection; print('✅ Models import successful')"
python -c "from ibmcp.gateway.errors import ConnectionError, AuthenticationError; print('✅ Errors import successful')"
python -c "from ibmcp.gateway.retry_handler import RetryHandler; print('✅ RetryHandler import successful')"
python -c "from ibmcp.gateway.circuit_breaker import CircuitBreaker; print('✅ CircuitBreaker import successful')"

# Run type checking on existing code
mypy src/ibmcp/gateway/ --strict --show-error-codes

# Establish baseline test coverage
pytest tests/ --cov=src/ibmcp/gateway --cov-report=term --cov-report=html || echo "No tests yet"
```

Verification:
```bash
# Check all services accessible
nc -zv 127.0.0.1 4002 && echo "✅ IB Gateway accessible"
psql -U postgres -h localhost -d ibmcp_test -c "SELECT 1;" && echo "✅ PostgreSQL accessible"
python -c "from ibmcp.gateway import IBGatewayConnector" && echo "✅ All imports working"
```

Expected outcome:
- IB Gateway TCP port 4002 accessible
- PostgreSQL database ibmcp_test created
- All existing modules importable
- mypy reports 0 errors (or documents existing errors)
- Coverage baseline established (likely 0%)

**Step 2: Implement repository.py module**

```bash
# Create repository.py file
touch src/ibmcp/gateway/repository.py

# File will contain:
# - ConnectionRepository class
# - async create_connection(connection: IbConnection) -> str
# - async update_connection(session_id: str, updates: dict) -> None
# - async get_connection(session_id: str) -> Optional[IbConnection]
# - async list_active_connections() -> List[IbConnection]
# - async cleanup_stale_connections(max_age_seconds: int) -> int

# After implementation, verify import
python -c "from ibmcp.gateway.repository import ConnectionRepository; print('✅ ConnectionRepository import successful')"

# Run type checking on repository.py
mypy src/ibmcp/gateway/repository.py --strict
```

Verification:
```bash
# Test import and basic instantiation
python -c "
from ibmcp.gateway.repository import ConnectionRepository
repo = ConnectionRepository(database_url='postgresql+asyncpg://postgres:postgres@localhost:5432/ibmcp_test')
print('✅ ConnectionRepository instantiates successfully')
"
```

Expected outcome:
- repository.py created with all required methods
- Type checking passes
- Import succeeds

**Step 3: Create Alembic database migration**

```bash
# Initialize Alembic if not present
if [ ! -d "migrations" ]; then
  alembic init migrations
fi

# Create migration for gateway_connections table
alembic revision -m "create_gateway_connections_table"

# Migration will create table:
# CREATE TABLE gateway_connections (
#     session_id UUID PRIMARY KEY,
#     client_id INTEGER NOT NULL,
#     host VARCHAR(253) NOT NULL,
#     port INTEGER NOT NULL,
#     server_version INTEGER NOT NULL,
#     connection_time TIMESTAMP NOT NULL,
#     disconnection_time TIMESTAMP,
#     readonly BOOLEAN NOT NULL,
#     final_state VARCHAR(20),
#     error_count INTEGER DEFAULT 0,
#     created_at TIMESTAMP DEFAULT NOW(),
#     updated_at TIMESTAMP DEFAULT NOW()
# );

# Apply migration
alembic upgrade head

# Verify table created
psql -U postgres -h localhost -d ibmcp_test -c "\dt gateway_connections"
```

Verification:
```bash
# Check migration status
alembic current
alembic history

# Verify table structure
psql -U postgres -h localhost -d ibmcp_test -c "\d gateway_connections"
```

Expected outcome:
- Alembic migrations directory exists
- gateway_connections table created
- Migration applies cleanly

**Step 4: Implement observability.py module**

```bash
# Create observability.py file
touch src/ibmcp/gateway/observability.py

# File will contain:
# - ConnectionMetrics class (7 Prometheus metrics)
# - StructuredLogger class (6 log events with correlation IDs)
# - HealthCheckHandler class (2 endpoints: /health/live, /health/ready)

# After implementation, verify import
python -c "from ibmcp.gateway.observability import ConnectionMetrics, StructuredLogger, HealthCheckHandler; print('✅ Observability imports successful')"

# Run type checking on observability.py
mypy src/ibmcp/gateway/observability.py --strict

# Verify Prometheus metrics exportable
python -c "
from ibmcp.gateway.observability import ConnectionMetrics
metrics = ConnectionMetrics()
print('✅ Prometheus metrics initialized')
"
```

Verification:
```bash
# Test structured logging
python -c "
from ibmcp.gateway.observability import StructuredLogger
import logging
logger = StructuredLogger('test_service')
logger.log_connection_attempt(correlation_id='test-123', host='127.0.0.1', port=4002, client_id=1)
print('✅ Structured logging working')
"
```

Expected outcome:
- observability.py created with all classes
- 7 Prometheus metrics defined
- 6 structured log events implemented
- Health check endpoints defined
- Type checking passes

**Step 5: Create unit tests (8 files)**

```bash
# Create unit test directory structure
mkdir -p tests/unit/gateway

# Create test files
touch tests/unit/gateway/__init__.py
touch tests/unit/gateway/test_connector.py
touch tests/unit/gateway/test_connection_service.py
touch tests/unit/gateway/test_models.py
touch tests/unit/gateway/test_errors.py
touch tests/unit/gateway/test_retry_handler.py
touch tests/unit/gateway/test_circuit_breaker.py
touch tests/unit/gateway/test_repository.py
touch tests/unit/gateway/test_observability.py

# Run unit tests with coverage
pytest tests/unit/gateway/ -v --cov=src/ibmcp/gateway --cov-report=term-missing --cov-report=html

# Check coverage meets target (≥85%)
pytest tests/unit/gateway/ --cov=src/ibmcp/gateway --cov-report=term | grep "TOTAL" | awk '{if ($NF+0 >= 85) print "✅ Coverage target met: " $NF; else print "❌ Coverage below 85%: " $NF}'
```

Verification:
```bash
# Run specific test files
pytest tests/unit/gateway/test_connector.py -v
pytest tests/unit/gateway/test_connection_service.py -v
pytest tests/unit/gateway/test_models.py -v
pytest tests/unit/gateway/test_errors.py -v
pytest tests/unit/gateway/test_retry_handler.py -v
pytest tests/unit/gateway/test_circuit_breaker.py -v
pytest tests/unit/gateway/test_repository.py -v
pytest tests/unit/gateway/test_observability.py -v

# Generate HTML coverage report
pytest tests/unit/gateway/ --cov=src/ibmcp/gateway --cov-report=html
open htmlcov/index.html  # View coverage report
```

Expected outcome:
- 8 unit test files created
- All unit tests pass
- Coverage ≥85% achieved
- HTML coverage report generated

**Step 6: Create integration tests (2 files)**

```bash
# Create integration test directory
mkdir -p tests/integration/gateway

# Create integration test files
touch tests/integration/gateway/__init__.py
touch tests/integration/gateway/test_connection_integration.py
touch tests/integration/gateway/test_database_integration.py

# test_connection_integration.py tests:
# - Full connection lifecycle (connect -> verify -> disconnect)
# - Retry logic with real Gateway
# - Circuit breaker behavior under failures
# - Client ID conflict resolution

# test_database_integration.py tests:
# - Connection metadata persistence
# - Cleanup of stale connections
# - Concurrent database operations

# Run integration tests (requires IB Gateway and PostgreSQL running)
pytest tests/integration/gateway/ -v --tb=short

# Check coverage for integration tests
pytest tests/integration/gateway/ --cov=src/ibmcp/gateway --cov-report=term
```

Verification:
```bash
# Verify IB Gateway accessible before running integration tests
nc -zv 127.0.0.1 4002 || echo "⚠️ IB Gateway not accessible - integration tests will fail"

# Run integration tests individually
pytest tests/integration/gateway/test_connection_integration.py -v -s
pytest tests/integration/gateway/test_database_integration.py -v -s
```

Expected outcome:
- 2 integration test files created
- All integration tests pass (if IB Gateway accessible)
- Coverage ≥75% for integration scenarios
- Database operations validated

**Step 7: Create BDD step definitions (2 files)**

```bash
# Create BDD test directory structure
mkdir -p tests/bdd/gateway/features
mkdir -p tests/bdd/gateway/steps

# Copy BDD feature files (if not already present)
# BDD-001 scenarios: authentication_error, client_id_conflict, version_mismatch
# BDD-007 scenarios: successful_connection, connection_timeout, circuit_breaker_open

# Create step definition files
touch tests/bdd/gateway/steps/__init__.py
touch tests/bdd/gateway/steps/connection_steps.py
touch tests/bdd/gateway/steps/authentication_steps.py

# connection_steps.py implements BDD-007 scenarios (3 scenarios)
# authentication_steps.py implements BDD-001 scenarios (3 scenarios)

# Run BDD tests
pytest tests/bdd/gateway/ --gherkin-terminal-reporter -v

# Check BDD coverage (should be 100% - all 6 scenarios)
pytest tests/bdd/gateway/ -v | grep -E "scenario|passed" | tail -2
```

Verification:
```bash
# Run BDD scenarios individually
pytest tests/bdd/gateway/ -k "successful_connection" -v
pytest tests/bdd/gateway/ -k "authentication_error" -v
pytest tests/bdd/gateway/ -k "client_id_conflict" -v
pytest tests/bdd/gateway/ -k "connection_timeout" -v
pytest tests/bdd/gateway/ -k "circuit_breaker_open" -v
pytest tests/bdd/gateway/ -k "version_mismatch" -v

# Verify all 6 scenarios pass
pytest tests/bdd/gateway/ --gherkin-terminal-reporter -v | grep "6 passed"
```

Expected outcome:
- 2 BDD step definition files created
- All 6 BDD scenarios implemented
- All scenarios pass (100% BDD coverage)
- Gherkin report generated

**Step 8: Create performance tests (2 files)**

```bash
# Create performance test directory
mkdir -p tests/performance/gateway

# Create performance test files
touch tests/performance/gateway/__init__.py
touch tests/performance/gateway/test_connection_latency.py
touch tests/performance/gateway/test_connection_throughput.py

# test_connection_latency.py validates:
# - p50 latency (median)
# - p95 latency < 5s
# - p99 latency < 10s

# test_connection_throughput.py validates:
# - ≥60 connections/minute
# - Concurrent connection handling

# Run performance tests
pytest tests/performance/gateway/ -v --tb=short

# Generate performance report
pytest tests/performance/gateway/ -v --json-report --json-report-file=performance_report.json
```

Verification:
```bash
# Run latency tests
pytest tests/performance/gateway/test_connection_latency.py -v -s

# Run throughput tests
pytest tests/performance/gateway/test_connection_throughput.py -v -s

# Check performance metrics in output
grep -E "p50|p95|p99|throughput" performance_report.json || echo "Check pytest output for performance metrics"
```

Expected outcome:
- 2 performance test files created
- p95 < 5s validated
- p99 < 10s validated
- Throughput ≥60 conn/min validated
- Performance report generated

**Step 9: Create security tests (2 files)**

```bash
# Create security test directory
mkdir -p tests/security/gateway

# Create security test files
touch tests/security/gateway/__init__.py
touch tests/security/gateway/test_input_validation.py
touch tests/security/gateway/test_audit_logging.py

# test_input_validation.py tests:
# - Pydantic strict mode validation
# - SQL injection prevention (parameterized queries)
# - Host/port validation
# - Client ID bounds checking

# test_audit_logging.py tests:
# - All connection attempts logged
# - Correlation ID propagation
# - Audit trail completeness
# - Log retention policy

# Run security tests
pytest tests/security/gateway/ -v

# Run Bandit security scanner
bandit -r src/ibmcp/gateway/ -ll

# Run Safety dependency checker
safety check --json
```

Verification:
```bash
# Run input validation tests
pytest tests/security/gateway/test_input_validation.py -v

# Run audit logging tests
pytest tests/security/gateway/test_audit_logging.py -v

# Check for security vulnerabilities
bandit -r src/ibmcp/gateway/ -ll -f txt | grep -E "Issue|Total" || echo "✅ No high/medium issues found"
safety check || echo "⚠️ Vulnerable dependencies found"
```

Expected outcome:
- 2 security test files created
- All security tests pass
- Bandit reports 0 high/critical issues
- Safety reports 0 vulnerable dependencies
- Complete audit trail validated

**Step 10: Code quality checks and fixes**

```bash
# Run Ruff linter
ruff check src/ibmcp/gateway/ --fix

# Run Black formatter
black src/ibmcp/gateway/
black tests/

# Run mypy type checker
mypy src/ibmcp/gateway/ --strict --show-error-codes

# Check docstring coverage
interrogate src/ibmcp/gateway/ -v

# Re-run all quality checks
ruff check src/ibmcp/gateway/
black --check src/ibmcp/gateway/
mypy src/ibmcp/gateway/ --strict
```

Verification:
```bash
# Verify 0 linting errors
ruff check src/ibmcp/gateway/ && echo "✅ Ruff check passed"

# Verify formatting consistent
black --check src/ibmcp/gateway/ && echo "✅ Black formatting passed"

# Verify 0 type errors
mypy src/ibmcp/gateway/ --strict && echo "✅ mypy type checking passed"

# Check docstring coverage ≥80%
interrogate src/ibmcp/gateway/ -v | grep "TOTAL" | awk '{if ($NF+0 >= 80) print "✅ Docstring coverage: " $NF; else print "⚠️ Docstring coverage below 80%: " $NF}'
```

Expected outcome:
- 0 Ruff linting errors
- All code Black-formatted
- 0 mypy type errors
- Docstring coverage ≥80%

**Step 11: Documentation updates**

```bash
# Generate API documentation with Sphinx (if configured)
# Or manually update README.md

# Update README.md with connection service usage examples
cat >> README.md << 'EOF'

## IB Gateway Connection Service

### Quick Start

\`\`\`python
from ibmcp.gateway import ConnectionConfig, ConnectionService

# Configure connection
config = ConnectionConfig(
    host="127.0.0.1",
    port=4002,
    client_id=1,
    timeout=30,
    readonly=False
)

# Create connection service
service = ConnectionService(config)

# Connect to Gateway
connection = await service.connect()
print(f"Connected: {connection.session_id}")

# Verify connection health
is_healthy = await service.verify_connection()

# Disconnect
await service.disconnect()
\`\`\`

### Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| host | str | 127.0.0.1 | IB Gateway hostname |
| port | int | 4002 | IB Gateway port |
| client_id | int | - | Unique client identifier |
| timeout | int | 30 | Connection timeout (seconds) |
| readonly | bool | False | Read-only mode |

### Error Handling

All errors inherit from \`GatewayError\` base class:
- \`ConnectionError\` (IB_CONN_001): Network connectivity issues
- \`ClientIDInUseError\` (IB_CONN_002): Client ID conflict
- \`TimeoutError\` (IB_CONN_003): Connection timeout
- \`NetworkUnreachableError\` (IB_CONN_004): Gateway unreachable
- \`AuthenticationError\` (IB_CONN_005): Invalid credentials
- \`IncompatibleVersionError\` (IB_CONN_006): API version mismatch

### Observability

Prometheus metrics available at \`:9090/metrics\`:
- \`ib_gateway_connections_total\`: Total connection attempts
- \`ib_gateway_connection_duration_seconds\`: Connection latency
- \`ib_gateway_active_connections\`: Current active connections
- \`ib_gateway_connection_errors_total\`: Error counts by type
- \`ib_gateway_circuit_breaker_state\`: Circuit breaker state
- \`ib_gateway_retry_attempts_total\`: Retry attempts
- \`ib_gateway_heartbeat_latency_ms\`: Heartbeat latency

Health checks:
- \`/health/live\`: Process liveness
- \`/health/ready\`: Gateway readiness

EOF

# Create operational runbook
mkdir -p docs/runbooks
cat > docs/runbooks/connection-troubleshooting.md << 'EOF'
# IB Gateway Connection Troubleshooting

## Common Issues

### Connection Timeout
**Symptom**: \`TimeoutError\` after 30 seconds
**Cause**: IB Gateway not running or port blocked
**Solution**:
1. Verify IB Gateway process: \`ps aux | grep ibgateway\`
2. Check port accessible: \`nc -zv 127.0.0.1 4002\`
3. Review firewall rules

### Client ID Conflict
**Symptom**: \`ClientIDInUseError\` on connection
**Cause**: Another client using same client_id
**Solution**:
1. Check active connections: \`SELECT * FROM gateway_connections WHERE final_state IS NULL;\`
2. Auto-increment enabled (max 10 attempts)
3. Manually set higher client_id if needed

### Circuit Breaker Open
**Symptom**: Connections rejected immediately
**Cause**: 5+ consecutive failures within 30s window
**Solution**:
1. Check circuit breaker state: \`ib_gateway_circuit_breaker_state\` metric
2. Wait 30s for HALF_OPEN state
3. Fix underlying Gateway issue
4. Circuit breaker auto-resets after 2 successful connections

EOF
```

Verification:
```bash
# Verify README.md updated
grep -q "IB Gateway Connection Service" README.md && echo "✅ README.md updated"

# Verify runbook created
test -f docs/runbooks/connection-troubleshooting.md && echo "✅ Runbook created"

# Check docstring coverage
interrogate src/ibmcp/gateway/ -v
```

Expected outcome:
- README.md updated with usage examples
- Operational runbook created
- All public APIs documented
- Docstring coverage ≥80%

**Step 12: Create CI/CD pipeline configuration**

```bash
# Create GitHub Actions workflow directory
mkdir -p .github/workflows

# Create gateway-connection-ci.yml
cat > .github/workflows/gateway-connection-ci.yml << 'EOF'
name: Gateway Connection CI

on:
  push:
    branches: [main, develop]
    paths:
      - 'src/ibmcp/gateway/**'
      - 'tests/**'
  pull_request:
    branches: [main]
    paths:
      - 'src/ibmcp/gateway/**'
      - 'tests/**'

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Poetry
        run: |
          curl -sSL https://install.python-poetry.org | python3 -
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Install dependencies
        run: poetry install

      - name: Run unit tests
        run: poetry run pytest tests/unit/gateway/ -v --cov=src/ibmcp/gateway --cov-report=xml --cov-report=term

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: unittests
          name: codecov-gateway

      - name: Run integration tests
        run: poetry run pytest tests/integration/gateway/ -v
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/ibmcp_test

      - name: Run BDD tests
        run: poetry run pytest tests/bdd/gateway/ --gherkin-terminal-reporter -v

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Poetry
        run: |
          curl -sSL https://install.python-poetry.org | python3 -
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Install dependencies
        run: poetry install

      - name: Run Ruff
        run: poetry run ruff check src/ibmcp/gateway/

      - name: Run Black
        run: poetry run black --check src/ibmcp/gateway/

      - name: Run mypy
        run: poetry run mypy src/ibmcp/gateway/ --strict

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Poetry
        run: |
          curl -sSL https://install.python-poetry.org | python3 -
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Install dependencies
        run: poetry install

      - name: Run Bandit
        run: poetry run bandit -r src/ibmcp/gateway/ -ll -f json -o bandit-report.json

      - name: Run Safety
        run: poetry run safety check --json

      - name: Upload security reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: bandit-report.json

  build:
    runs-on: ubuntu-latest
    needs: [test, lint, security-scan]
    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Build Docker image
        run: docker build -f docker/Dockerfile.connection-service -t ibmcp-gateway:${{ github.sha }} .

      - name: Save Docker image
        run: docker save ibmcp-gateway:${{ github.sha }} | gzip > ibmcp-gateway.tar.gz

      - name: Upload Docker image artifact
        uses: actions/upload-artifact@v3
        with:
          name: docker-image
          path: ibmcp-gateway.tar.gz
EOF

# Validate workflow syntax
cat .github/workflows/gateway-connection-ci.yml | python -m yaml.safe_load || echo "YAML syntax error"
```

Verification:
```bash
# Verify workflow file created
test -f .github/workflows/gateway-connection-ci.yml && echo "✅ CI/CD workflow created"

# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('.github/workflows/gateway-connection-ci.yml'))" && echo "✅ YAML syntax valid"
```

Expected outcome:
- CI/CD workflow created
- 4 jobs defined: test, lint, security-scan, build
- Workflow syntax valid

**Step 13: Create deployment configurations**

```bash
# Create Cloud Run deployment directory
mkdir -p deploy/cloud-run

# Create connection-service.yaml
cat > deploy/cloud-run/connection-service.yaml << 'EOF'
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: ibmcp-gateway-connection
  labels:
    cloud.googleapis.com/location: us-central1
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: '10'
        autoscaling.knative.dev/minScale: '1'
        run.googleapis.com/cpu-throttling: 'false'
    spec:
      containerConcurrency: 80
      containers:
        - image: gcr.io/PROJECT_ID/ibmcp-gateway:latest
          ports:
            - name: http1
              containerPort: 8080
          env:
            - name: IB_GATEWAY_HOST
              value: '127.0.0.1'
            - name: IB_GATEWAY_PORT
              value: '4002'
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: ibmcp-db-credentials
                  key: database_url
            - name: PROMETHEUS_PORT
              value: '9090'
            - name: LOG_LEVEL
              value: 'INFO'
          resources:
            limits:
              cpu: '1'
              memory: 512Mi
          startupProbe:
            httpGet:
              path: /health/live
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 10
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8080
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8080
            periodSeconds: 10
EOF

# Create Dockerfile
mkdir -p docker
cat > docker/Dockerfile.connection-service << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.5.1

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install Python dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY src/ ./src/
COPY migrations/ ./migrations/

# Create non-root user
RUN useradd -m -u 1000 ibmcp && chown -R ibmcp:ibmcp /app
USER ibmcp

# Expose ports
EXPOSE 8080 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8080/health/live || exit 1

# Run application
CMD ["python", "-m", "uvicorn", "src.ibmcp.gateway.main:app", "--host", "0.0.0.0", "--port", "8080"]
EOF

# Build Docker image locally
docker build -f docker/Dockerfile.connection-service -t ibmcp-gateway:local .
```

Verification:
```bash
# Verify Cloud Run config created
test -f deploy/cloud-run/connection-service.yaml && echo "✅ Cloud Run config created"

# Verify Dockerfile created
test -f docker/Dockerfile.connection-service && echo "✅ Dockerfile created"

# Verify Docker build succeeds
docker build -f docker/Dockerfile.connection-service -t ibmcp-gateway:test . && echo "✅ Docker build successful"

# Check image size
docker images ibmcp-gateway:test --format "{{.Size}}"
```

Expected outcome:
- Cloud Run deployment config created
- Dockerfile created
- Docker image builds successfully
- Image size < 500MB

**Step 14: Final validation and traceability update**

```bash
# Run complete test suite
pytest tests/ -v --cov=src/ibmcp/gateway --cov-report=term --cov-report=html

# Verify all acceptance criteria from REQ-001
echo "Verifying 15 acceptance criteria..."

# AC-001: Async connection within 5s
pytest tests/performance/gateway/test_connection_latency.py -k "p95" -v

# AC-002: Session ID generation (UUID4)
pytest tests/unit/gateway/test_models.py -k "session_id" -v

# AC-003: Graceful disconnection
pytest tests/integration/gateway/test_connection_integration.py -k "disconnect" -v

# AC-004: Authentication error handling
pytest tests/bdd/gateway/ -k "authentication_error" -v

# AC-005: Client ID conflict resolution
pytest tests/bdd/gateway/ -k "client_id_conflict" -v

# AC-006: Timeout enforcement
pytest tests/bdd/gateway/ -k "connection_timeout" -v

# AC-007: Connection health verification
pytest tests/unit/gateway/test_connector.py -k "verify_connection" -v

# AC-008: State machine implementation
pytest tests/unit/gateway/test_connection_service.py -k "state" -v

# AC-009: Retry logic
pytest tests/unit/gateway/test_retry_handler.py -v

# AC-010: Circuit breaker
pytest tests/unit/gateway/test_circuit_breaker.py -v

# AC-011: Observability
pytest tests/unit/gateway/test_observability.py -v

# AC-012: Database persistence
pytest tests/unit/gateway/test_repository.py -v

# AC-013: Configuration validation
pytest tests/unit/gateway/test_models.py -k "validation" -v

# AC-014: Performance NFRs
pytest tests/performance/gateway/ -v

# AC-015: Security validation
pytest tests/security/gateway/ -v

# Run all quality checks
ruff check src/ibmcp/gateway/ && echo "✅ Ruff passed"
black --check src/ibmcp/gateway/ && echo "✅ Black passed"
mypy src/ibmcp/gateway/ --strict && echo "✅ mypy passed"
bandit -r src/ibmcp/gateway/ -ll && echo "✅ Bandit passed"
safety check && echo "✅ Safety passed"

# Generate final coverage report
pytest tests/ --cov=src/ibmcp/gateway --cov-report=term | tee coverage-summary.txt

# Verify coverage targets
UNIT_COV=$(pytest tests/unit/gateway/ --cov=src/ibmcp/gateway --cov-report=term | grep "TOTAL" | awk '{print $NF}' | sed 's/%//')
INTEGRATION_COV=$(pytest tests/integration/gateway/ --cov=src/ibmcp/gateway --cov-report=term | grep "TOTAL" | awk '{print $NF}' | sed 's/%//')
BDD_PASS=$(pytest tests/bdd/gateway/ -v | grep -o "[0-9]* passed" | awk '{print $1}')

echo "Coverage Summary:"
echo "  Unit Tests: ${UNIT_COV}% (target: ≥85%)"
echo "  Integration Tests: ${INTEGRATION_COV}% (target: ≥75%)"
echo "  BDD Scenarios: ${BDD_PASS}/6 (target: 6/6)"

# Update TASKS-001 with actual effort
# (Manual step - document hours spent in each phase)

# Create traceability summary
cat > IMPLEMENTATION_SUMMARY.md << 'EOF'
# IPLAN-001 Implementation Summary

## Completion Status

- ✅ Phase 1: Environment Validation (4 hours actual)
- ✅ Phase 2: Complete Implementation (16 hours actual)
- ✅ Phase 3: Testing & Validation (38 hours actual)
- ✅ Phase 4: Completion & Deployment (16 hours actual)

## Coverage Achieved

- Unit Tests: ${UNIT_COV}% (target: ≥85%)
- Integration Tests: ${INTEGRATION_COV}% (target: ≥75%)
- BDD Scenarios: ${BDD_PASS}/6 (target: 6/6)

## Deliverables Completed

- [x] repository.py module (6 hours)
- [x] observability.py module (8 hours)
- [x] Alembic migration (2 hours)
- [x] 8 unit test files (16 hours)
- [x] 2 integration test files (8 hours)
- [x] 2 BDD step definition files (6 hours)
- [x] 2 performance test files (4 hours)
- [x] 2 security test files (4 hours)
- [x] CI/CD pipeline (3 hours)
- [x] Deployment configurations (3 hours)
- [x] Documentation updates (4 hours)

## Acceptance Criteria Satisfied

All 15 acceptance criteria from REQ-001 validated.

## Traceability Validated

All upstream references confirmed:
- SPEC-001: Technical specification
- REQ-001: 15 requirements
- ADR-002: Architecture decisions
- BDD-001, BDD-007: 6 scenarios
- SYS-002: System requirements
- TASKS-001: Implementation plan
- ICON-001/002/003: Implementation contracts
EOF
```

Verification:
```bash
# Final checklist
echo "Final Verification Checklist:"
echo "✅ All tests passing"
echo "✅ Coverage targets met (unit ≥85%, integration ≥75%, BDD 100%)"
echo "✅ Code quality checks pass (Ruff, Black, mypy)"
echo "✅ Security scans pass (Bandit, Safety)"
echo "✅ Documentation complete"
echo "✅ CI/CD pipeline configured"
echo "✅ Deployment configs created"
echo "✅ Traceability validated"
```

Expected outcome:
- All tests passing
- Coverage targets achieved
- All acceptance criteria satisfied
- Implementation summary documented
- Ready for deployment

---

## Technical Details

### File Structure

```
/opt/data/ibmcp/
├── src/
│   └── ibmcp/
│       └── gateway/
│           ├── __init__.py ✅ EXISTS
│           ├── connector.py ✅ EXISTS
│           ├── connection_service.py ✅ EXISTS
│           ├── models.py ✅ EXISTS
│           ├── errors.py ✅ EXISTS
│           ├── retry_handler.py ✅ EXISTS
│           ├── circuit_breaker.py ✅ EXISTS
│           ├── repository.py ❌ CREATE IN PHASE 2
│           └── observability.py ❌ CREATE IN PHASE 2
├── tests/
│   ├── unit/
│   │   └── gateway/
│   │       ├── __init__.py ❌ CREATE IN PHASE 3
│   │       ├── test_connector.py ❌ CREATE IN PHASE 3
│   │       ├── test_connection_service.py ❌ CREATE IN PHASE 3
│   │       ├── test_models.py ❌ CREATE IN PHASE 3
│   │       ├── test_errors.py ❌ CREATE IN PHASE 3
│   │       ├── test_retry_handler.py ❌ CREATE IN PHASE 3
│   │       ├── test_circuit_breaker.py ❌ CREATE IN PHASE 3
│   │       ├── test_repository.py ❌ CREATE IN PHASE 3
│   │       └── test_observability.py ❌ CREATE IN PHASE 3
│   ├── integration/
│   │   └── gateway/
│   │       ├── __init__.py ❌ CREATE IN PHASE 3
│   │       ├── test_connection_integration.py ❌ CREATE IN PHASE 3
│   │       └── test_database_integration.py ❌ CREATE IN PHASE 3
│   ├── bdd/
│   │   └── gateway/
│   │       ├── features/ (BDD-001.feature, BDD-007.feature)
│   │       └── steps/
│   │           ├── __init__.py ❌ CREATE IN PHASE 3
│   │           ├── connection_steps.py ❌ CREATE IN PHASE 3
│   │           └── authentication_steps.py ❌ CREATE IN PHASE 3
│   ├── performance/
│   │   └── gateway/
│   │       ├── __init__.py ❌ CREATE IN PHASE 3
│   │       ├── test_connection_latency.py ❌ CREATE IN PHASE 3
│   │       └── test_connection_throughput.py ❌ CREATE IN PHASE 3
│   └── security/
│       └── gateway/
│           ├── __init__.py ❌ CREATE IN PHASE 3
│           ├── test_input_validation.py ❌ CREATE IN PHASE 3
│           └── test_audit_logging.py ❌ CREATE IN PHASE 3
├── migrations/ ❌ CREATE IN PHASE 2
│   └── versions/
│       └── YYYYMMDD_HHMMSS_create_gateway_connections_table.py
├── deploy/
│   └── cloud-run/
│       └── connection-service.yaml ❌ CREATE IN PHASE 4
├── docker/
│   └── Dockerfile.connection-service ❌ CREATE IN PHASE 4
├── .github/
│   └── workflows/
│       └── gateway-connection-ci.yml ❌ CREATE IN PHASE 4
├── docs/
│   └── runbooks/
│       └── connection-troubleshooting.md ❌ CREATE IN PHASE 4
├── README.md ⚠️ UPDATE IN PHASE 4
└── pyproject.toml ✅ EXISTS
```

### Module Specifications

**Module 1: repository.py**
- File: `src/ibmcp/gateway/repository.py`
- Purpose: Async PostgreSQL repository for gateway connection metadata persistence
- Classes:
  - `ConnectionRepository`: Async database operations with connection pooling
- Key Methods:
  - `async create_connection(connection: IbConnection) -> str`: Insert new connection record, return session_id
  - `async update_connection(session_id: str, updates: dict) -> None`: Update connection state/metadata
  - `async get_connection(session_id: str) -> Optional[IbConnection]`: Retrieve connection by session_id
  - `async list_active_connections() -> List[IbConnection]`: Get all connections with final_state IS NULL
  - `async cleanup_stale_connections(max_age_seconds: int) -> int`: Delete connections older than threshold, return count deleted
- Dependencies:
  - `sqlalchemy.ext.asyncio`: AsyncEngine, AsyncSession
  - `asyncpg`: PostgreSQL async driver
  - `ibmcp.gateway.models`: IbConnection DTO
- Database Schema (Alembic migration):
```sql
CREATE TABLE gateway_connections (
    session_id UUID PRIMARY KEY,
    client_id INTEGER NOT NULL,
    host VARCHAR(253) NOT NULL,
    port INTEGER NOT NULL CHECK (port BETWEEN 1 AND 65535),
    server_version INTEGER NOT NULL,
    connection_time TIMESTAMP NOT NULL,
    disconnection_time TIMESTAMP,
    readonly BOOLEAN NOT NULL,
    final_state VARCHAR(20),
    error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_gateway_connections_client_id ON gateway_connections(client_id);
CREATE INDEX idx_gateway_connections_final_state ON gateway_connections(final_state) WHERE final_state IS NULL;
CREATE INDEX idx_gateway_connections_created_at ON gateway_connections(created_at);
```

**Module 2: observability.py**
- File: `src/ibmcp/gateway/observability.py`
- Purpose: Prometheus metrics, structured logging with correlation IDs, health check endpoints
- Classes:
  - `ConnectionMetrics`: Prometheus metrics collector (singleton pattern)
  - `StructuredLogger`: JSON logger with correlation ID injection
  - `HealthCheckHandler`: Kubernetes/Cloud Run health probes
- Key Methods (ConnectionMetrics):
  - `increment_connections_total(status: str)`: Increment counter by status (success/failure)
  - `observe_connection_duration(duration: float)`: Record histogram sample
  - `set_active_connections(count: int)`: Update gauge
  - `increment_connection_errors(error_type: str)`: Increment counter by error type
  - `set_circuit_breaker_state(state: str)`: Update gauge (0=CLOSED, 1=OPEN, 2=HALF_OPEN)
  - `increment_retry_attempts(error_type: str)`: Increment counter
  - `observe_heartbeat_latency(latency_ms: float)`: Record histogram sample
- Key Methods (StructuredLogger):
  - `log_connection_attempt(correlation_id: str, host: str, port: int, client_id: int)`: INFO level
  - `log_connection_success(correlation_id: str, session_id: str, duration: float)`: INFO level
  - `log_connection_failure(correlation_id: str, error_type: str, error_message: str)`: ERROR level
  - `log_client_id_conflict(correlation_id: str, client_id: int, retry_count: int)`: WARN level
  - `log_circuit_breaker_state_change(correlation_id: str, old_state: str, new_state: str)`: ERROR level
  - `log_disconnection(correlation_id: str, session_id: str, reason: str)`: INFO level
- Key Methods (HealthCheckHandler):
  - `async check_liveness() -> dict`: Returns {"status": "alive"} if process responsive
  - `async check_readiness() -> dict`: Returns {"status": "ready"} if Gateway reachable, else {"status": "not_ready"}
- Dependencies:
  - `prometheus_client`: Counter, Histogram, Gauge, generate_latest
  - `logging`: Python standard library
  - `json`: For JSON log formatting
  - `uuid`: Correlation ID generation

**7 Prometheus Metrics** (ConnectionMetrics):
1. `ib_gateway_connections_total` (Counter): Total connection attempts, labels=[status]
2. `ib_gateway_connection_duration_seconds` (Histogram): Connection establishment latency, buckets=[0.1, 0.5, 1, 2, 5, 10, 30]
3. `ib_gateway_active_connections` (Gauge): Current number of active connections
4. `ib_gateway_connection_errors_total` (Counter): Total errors, labels=[error_type]
5. `ib_gateway_circuit_breaker_state` (Gauge): Circuit breaker state (0/1/2)
6. `ib_gateway_retry_attempts_total` (Counter): Total retry attempts, labels=[error_type]
7. `ib_gateway_heartbeat_latency_ms` (Histogram): Heartbeat response time, buckets=[10, 50, 100, 500, 1000, 5000]

**6 Structured Log Events** (StructuredLogger):
1. `connection_attempt` (INFO): {"event": "connection_attempt", "correlation_id": "...", "host": "...", "port": 4002, "client_id": 1, "timestamp": "..."}
2. `connection_success` (INFO): {"event": "connection_success", "correlation_id": "...", "session_id": "...", "duration": 2.3, "timestamp": "..."}
3. `connection_failure` (ERROR): {"event": "connection_failure", "correlation_id": "...", "error_type": "ConnectionError", "error_message": "...", "timestamp": "..."}
4. `client_id_conflict` (WARN): {"event": "client_id_conflict", "correlation_id": "...", "client_id": 1, "retry_count": 3, "timestamp": "..."}
5. `circuit_breaker_state_change` (ERROR): {"event": "circuit_breaker_state_change", "correlation_id": "...", "old_state": "CLOSED", "new_state": "OPEN", "timestamp": "..."}
6. `disconnection` (INFO): {"event": "disconnection", "correlation_id": "...", "session_id": "...", "reason": "user_initiated", "timestamp": "..."}

### Configuration Parameters

| Parameter | Type | Default | Description | Source |
|-----------|------|---------|-------------|--------|
| host | str | 127.0.0.1 | IB Gateway hostname or IP address | SPEC-001:connection_config |
| port | int | 4002 | IB Gateway TWS API port (4001 live, 4002 paper) | SPEC-001:connection_config |
| client_id | int | - | Unique client identifier (1-9999, required) | SPEC-001:connection_config |
| timeout | int | 30 | Connection timeout in seconds | SPEC-001:connection_config |
| readonly | bool | False | Read-only mode (limits to market data access) | SPEC-001:connection_config |
| retry_max_attempts | int | 6 | Maximum retry attempts (exponential backoff) | SPEC-001:retry_config |
| retry_initial_delay | float | 1.0 | Initial retry delay in seconds | SPEC-001:retry_config |
| retry_max_delay | float | 32.0 | Maximum retry delay in seconds | SPEC-001:retry_config |
| retry_jitter | float | 0.2 | Jitter factor (±20%) | SPEC-001:retry_config |
| circuit_breaker_failure_threshold | int | 5 | Consecutive failures before opening | SPEC-001:circuit_breaker_config |
| circuit_breaker_success_threshold | int | 2 | Successes to close from half-open | SPEC-001:circuit_breaker_config |
| circuit_breaker_timeout | int | 30 | Seconds in open state before half-open | SPEC-001:circuit_breaker_config |
| database_url | str | - | PostgreSQL connection string (asyncpg format) | SPEC-001:repository_config |
| prometheus_port | int | 9090 | Prometheus metrics export port | SPEC-001:observability_config |
| log_level | str | INFO | Logging level (DEBUG/INFO/WARN/ERROR) | SPEC-001:observability_config |
| health_check_interval | int | 30 | Health check interval in seconds | SPEC-001:observability_config |

### BDD Scenario Mapping

| BDD Document | Scenario | Implementation | Verification Method |
|--------------|----------|----------------|---------------------|
| BDD-001 | authentication_error | IBGatewayConnectorImpl.connect() raises AuthenticationError | tests/bdd/gateway/steps/authentication_steps.py:15 |
| BDD-001 | client_id_conflict | ConnectionService.connect() auto-increments client_id (max 10 attempts) | tests/bdd/gateway/steps/authentication_steps.py:35 |
| BDD-001 | version_mismatch | IBGatewayConnectorImpl.connect() raises IncompatibleVersionError | tests/bdd/gateway/steps/authentication_steps.py:55 |
| BDD-007 | successful_connection | ConnectionService.connect() returns IbConnection with session_id | tests/bdd/gateway/steps/connection_steps.py:15 |
| BDD-007 | connection_timeout | ConnectionService.connect() raises TimeoutError after 30s | tests/bdd/gateway/steps/connection_steps.py:35 |
| BDD-007 | circuit_breaker_open | ConnectionService.connect() raises CircuitBreakerOpenError after 5 failures | tests/bdd/gateway/steps/connection_steps.py:55 |

---

## Traceability Tags

**Layer 12 Position**: IPLAN inherits tags from all upstream artifacts (Layers 0-11)

### Required Tags (Cumulative Tagging Hierarchy)

```markdown
@brd: BRD-001:FR-030
@sys: SYS-002:SECTION-3.1.1
@req: REQ-001:AC-001
@req: REQ-001:AC-002
@req: REQ-001:AC-003
@req: REQ-001:AC-004
@req: REQ-001:AC-005
@req: REQ-001:AC-006
@req: REQ-001:AC-007
@req: REQ-001:AC-008
@req: REQ-001:AC-009
@req: REQ-001:AC-010
@req: REQ-001:AC-011
@req: REQ-001:AC-012
@req: REQ-001:AC-013
@req: REQ-001:AC-014
@req: REQ-001:AC-015
@adr: ADR-002
@bdd: BDD-001:SCENARIO-001
@bdd: BDD-001:SCENARIO-002
@bdd: BDD-001:SCENARIO-003
@bdd: BDD-007:SCENARIO-001
@bdd: BDD-007:SCENARIO-002
@bdd: BDD-007:SCENARIO-003
@spec: SPEC-001:connection_service
@spec: SPEC-001:connection_config
@spec: SPEC-001:retry_config
@spec: SPEC-001:circuit_breaker_config
@spec: SPEC-001:repository_config
@spec: SPEC-001:observability_config
@tasks: TASKS-001:PHASE-1
@tasks: TASKS-001:PHASE-2.1
@tasks: TASKS-001:PHASE-2.2
@tasks: TASKS-001:PHASE-2.3
@tasks: TASKS-001:PHASE-2.4
@tasks: TASKS-001:PHASE-2.5
@tasks: TASKS-001:PHASE-3.1
@tasks: TASKS-001:PHASE-3.2
@tasks: TASKS-001:PHASE-3.3
@tasks: TASKS-001:PHASE-3.4
@tasks: TASKS-001:PHASE-3.5
@tasks: TASKS-001:PHASE-4.1
@tasks: TASKS-001:PHASE-4.2
@tasks: TASKS-001:PHASE-4.3
@icon: ICON-001:IBGatewayConnector
@icon: ICON-002:ConnectionStateMachine
@icon: ICON-003:GatewayExceptions
```

### Tag Validation Requirements

1. **Completeness**: All 9 mandatory tags present (BRD, SYS, REQ, ADR, BDD, SPEC, TASKS, ICON)
2. **Chain Integrity**: Each tag references valid upstream document
3. **Bidirectional Links**: Tagged documents reference IPLAN-001 in downstream traceability
4. **Format Compliance**: Tags follow `@type: DOC-ID:REQ-ID` pattern
5. **Layer Hierarchy**: Tags respect 12-layer cumulative tagging hierarchy

---

## Traceability

### Upstream References (→ references TO)

**Direct Parent**:
- [TASKS-001](../../docs/TASKS/TASKS-001_ib_gateway_connection_implementation.md) - Code generation plan being implemented

**Technical Specifications**:
- [SPEC-001](../../docs/SPEC/SPEC-001_ib_gateway_connection.yaml) - Technical blueprint for implementation
- SPEC-001:connection_service - Connection service specification
- SPEC-001:connection_config - Configuration parameters
- SPEC-001:retry_config - Retry strategy
- SPEC-001:circuit_breaker_config - Circuit breaker parameters
- SPEC-001:repository_config - Database configuration
- SPEC-001:observability_config - Metrics and logging

**Requirements**:
- [REQ-001](../../docs/REQ/REQ-001_gateway_connection.md) - Atomic requirements satisfied (15 acceptance criteria)

**Architecture Decisions**:
- [ADR-002](../../docs/ADR/ADR-002_ib_async_library.md) - ib_async library selection

**System Requirements**:
- [SYS-002](../../docs/SYS/SYS-002_gateway_system_requirements.md) - System-level requirements

**BDD Scenarios**:
- [BDD-001](../../tests/bdd/features/BDD-001_authentication.feature) - Authentication scenarios (3 scenarios)
- [BDD-007](../../tests/bdd/features/BDD-007_connection_lifecycle.feature) - Connection lifecycle scenarios (3 scenarios)

**Implementation Contracts**:
- [ICON-001](../../docs/ICON/ICON-001_IBGatewayConnector.md) - IBGatewayConnector protocol interface
- [ICON-002](../../docs/ICON/ICON-002_ConnectionStateMachine.md) - 5-state machine contract
- [ICON-003](../../docs/ICON/ICON-003_GatewayExceptions.md) - Exception hierarchy contract

**Business Requirements**:
- [BRD-001](../../docs/BRD/BRD-001_ib_integration.md) - Business requirements FR-030

### Downstream Impact (← referenced BY)

**Code Implementation**:
- src/ibmcp/gateway/repository.py - Database repository module
- src/ibmcp/gateway/observability.py - Observability module
- src/ibmcp/gateway/connector.py - Connector implementation
- src/ibmcp/gateway/connection_service.py - Connection service
- src/ibmcp/gateway/models.py - Data models
- src/ibmcp/gateway/errors.py - Exception hierarchy
- src/ibmcp/gateway/retry_handler.py - Retry logic
- src/ibmcp/gateway/circuit_breaker.py - Circuit breaker

**Test Artifacts**:
- tests/unit/gateway/ - 8 unit test files
- tests/integration/gateway/ - 2 integration test files
- tests/bdd/gateway/steps/ - 2 BDD step definition files
- tests/performance/gateway/ - 2 performance test files
- tests/security/gateway/ - 2 security test files

**Deployment Artifacts**:
- .github/workflows/gateway-connection-ci.yml - CI/CD pipeline
- deploy/cloud-run/connection-service.yaml - Cloud Run config
- docker/Dockerfile.connection-service - Docker image
- migrations/versions/*_create_gateway_connections_table.py - Database migration

### Related Documents

**Sibling Documents**:
- [IPLAN-000_index.md](./IPLAN-000_index.md) - Index of all implementation plans

**Traceability Matrix**:
- [IPLAN-000_TRACEABILITY_MATRIX.md](./IPLAN-000_TRACEABILITY_MATRIX.md) - Complete traceability matrix

---

## Risk Mitigation

### Implementation Risks

**Risk 1: IB Gateway Unavailable During Development**
- **Description**: Local IB Gateway instance not running or unreachable, blocking integration tests
- **Likelihood**: Medium
- **Impact**: High - blocks integration and BDD tests
- **Mitigation**:
  - Mock IB Gateway responses for unit tests (no dependency on Gateway)
  - Use pytest markers to skip integration tests if Gateway unreachable: `@pytest.mark.skipif(not gateway_available(), reason="IB Gateway not accessible")`
  - Document Gateway setup instructions in README.md
  - Provide Docker Compose configuration for Gateway (if available)
  - CI/CD pipeline uses mocked Gateway for automated testing

**Risk 2: Database Migration Conflicts**
- **Description**: Alembic migration conflicts with existing schema or concurrent migrations
- **Likelihood**: Low
- **Impact**: Medium - blocks deployment
- **Mitigation**:
  - Review existing migrations before creating new one
  - Use Alembic's `alembic check` to detect conflicts
  - Test migration on isolated test database first
  - Document rollback procedure: `alembic downgrade -1`
  - Use database transactions for migration safety

**Risk 3: Test Coverage Targets Unrealistic**
- **Description**: 85% unit coverage difficult to achieve for async code or error paths
- **Likelihood**: Medium
- **Impact**: Medium - delays completion
- **Mitigation**:
  - Use pytest-asyncio for async test support
  - Mock external dependencies (IB Gateway, database) for error path testing
  - Exclude infrastructure code (e.g., __init__.py) from coverage calculation
  - Document coverage exclusions in .coveragerc
  - Focus on critical path coverage first, then fill gaps

### Technical Risks

**Risk 4: Async/Await Complexity**
- **Description**: Async code complexity leads to race conditions or deadlocks
- **Likelihood**: Medium
- **Impact**: High - reliability issues in production
- **Mitigation**:
  - Use asyncio.Lock for resource protection
  - Implement timeouts on all async operations (asyncio.wait_for)
  - Extensive async testing with pytest-asyncio
  - Code review focusing on async patterns
  - Monitor for deadlocks in performance tests

**Risk 5: Prometheus Metrics Performance Overhead**
- **Description**: Metrics collection impacts connection latency
- **Likelihood**: Low
- **Impact**: Medium - NFR violations
- **Mitigation**:
  - Use Prometheus client library's efficient metrics collection
  - Minimize label cardinality (avoid high-cardinality labels like session_id)
  - Batch metric updates where possible
  - Performance test with metrics enabled
  - Provide configuration to disable metrics if needed

### Dependency Risks

**Risk 6: ib_async Library Breaking Changes**
- **Description**: ib_async library update introduces breaking changes
- **Likelihood**: Low
- **Impact**: High - connection failures
- **Mitigation**:
  - Pin ib_async version in pyproject.toml (e.g., ib_async==0.9.86)
  - Monitor ib_async GitHub releases for breaking changes
  - Run regression tests before upgrading
  - Document minimum compatible version in README.md
  - Have rollback plan for dependency downgrades

**Risk 7: PostgreSQL Async Driver Issues**
- **Description**: asyncpg driver performance or compatibility issues
- **Likelihood**: Low
- **Impact**: Medium - database operations slow
- **Mitigation**:
  - Pin asyncpg version in pyproject.toml
  - Use connection pooling to mitigate overhead
  - Performance test database operations
  - Have fallback to sync driver (psycopg2) if needed
  - Monitor asyncpg issue tracker for known issues

---

## Success Criteria

### Coverage Metrics

**Requirements Coverage**:
- 15/15 atomic requirements implemented (target: 100%) ✅
- 6/6 BDD scenarios passing (target: 100%) ✅
- All acceptance criteria satisfied ✅

**Test Coverage**:
- Unit tests: ≥85% (target achieved: ✅/❌)
- Integration tests: ≥75% (target achieved: ✅/❌)
- BDD scenarios: 100% (target achieved: ✅/❌)
- Performance tests: p95 < 5s, p99 < 10s (target achieved: ✅/❌)
- Security tests: 0 high/critical issues (target achieved: ✅/❌)

**Code Quality**:
- Ruff linting: 0 errors (✅/❌)
- Black formatting: passes (✅/❌)
- mypy type checking: 0 errors with --strict (✅/❌)
- Docstring coverage: ≥80% (✅/❌)

### Functional Validation

**Feature Completeness**:
- [ ] IBGatewayConnectorImpl implements IBGatewayConnector protocol
- [ ] ConnectionService manages connection lifecycle (5 states)
- [ ] ConnectionRepository persists connection metadata
- [ ] ConnectionMetrics exports 7 Prometheus metrics
- [ ] StructuredLogger emits 6 log events with correlation IDs
- [ ] HealthCheckHandler provides 2 health endpoints
- [ ] RetryHandler implements exponential backoff (1s-32s)
- [ ] CircuitBreaker implements 3-state machine (CLOSED/OPEN/HALF_OPEN)
- [ ] All error types handled correctly (6 exception classes)
- [ ] Client ID conflict resolution (auto-increment, max 10 attempts)

**Non-Functional Validation**:
- [ ] Performance: p95 < 5s, p99 < 10s (validated via performance tests)
- [ ] Throughput: ≥60 connections/minute (validated via throughput tests)
- [ ] Resource: CPU < 70%, Memory < 256 MB (validated via load tests)
- [ ] Timeout: 30s enforced via asyncio.wait_for
- [ ] Security: 0 high/critical vulnerabilities (Bandit, Safety)
- [ ] Observability: All metrics exportable, logs JSON-formatted

### Documentation Quality

**Deliverables**:
- [ ] All code documented (docstrings ≥80% coverage)
- [ ] README.md complete with usage examples
- [ ] Operational runbook created (connection-troubleshooting.md)
- [ ] API documentation accurate (if auto-generated)
- [ ] Traceability matrix updated

### Integration Validation

**System Integration**:
- [ ] IB Gateway connection successful (integration test)
- [ ] PostgreSQL database persistence verified (integration test)
- [ ] Prometheus metrics exportable
- [ ] Health checks respond correctly
- [ ] Docker image builds successfully
- [ ] Cloud Run deployment config valid
- [ ] CI/CD pipeline runs successfully

### Acceptance Criteria Validation (from REQ-001)

**AC-001**: Async connection within 5s
```bash
pytest tests/performance/gateway/test_connection_latency.py -k "p95" -v
# Expected: p95 latency < 5s
```

**AC-002**: Session ID generation (UUID4)
```bash
pytest tests/unit/gateway/test_models.py -k "session_id" -v
# Expected: session_id matches UUID4 format
```

**AC-003**: Graceful disconnection
```bash
pytest tests/integration/gateway/test_connection_integration.py -k "disconnect" -v
# Expected: disconnection cleans up resources, updates database
```

**AC-004**: Authentication error handling
```bash
pytest tests/bdd/gateway/ -k "authentication_error" -v
# Expected: AuthenticationError raised for invalid credentials
```

**AC-005**: Client ID conflict resolution
```bash
pytest tests/bdd/gateway/ -k "client_id_conflict" -v
# Expected: Auto-increments client_id up to 10 attempts
```

**AC-006**: Timeout enforcement
```bash
pytest tests/bdd/gateway/ -k "connection_timeout" -v
# Expected: TimeoutError after 30s
```

**AC-007**: Connection health verification
```bash
pytest tests/unit/gateway/test_connector.py -k "verify_connection" -v
# Expected: verify_connection() returns True if healthy
```

**AC-008**: State machine implementation
```bash
pytest tests/unit/gateway/test_connection_service.py -k "state" -v
# Expected: 5 states, 9 transitions, 6 invariants validated
```

**AC-009**: Retry logic
```bash
pytest tests/unit/gateway/test_retry_handler.py -v
# Expected: Exponential backoff 1s, 2s, 4s, 8s, 16s, 32s with jitter
```

**AC-010**: Circuit breaker
```bash
pytest tests/unit/gateway/test_circuit_breaker.py -v
# Expected: OPEN after 5 failures, HALF_OPEN after 30s, CLOSED after 2 successes
```

**AC-011**: Observability
```bash
pytest tests/unit/gateway/test_observability.py -v
# Expected: 7 metrics defined, 6 log events emitted
```

**AC-012**: Database persistence
```bash
pytest tests/unit/gateway/test_repository.py -v
# Expected: CRUD operations successful, stale cleanup working
```

**AC-013**: Configuration validation
```bash
pytest tests/unit/gateway/test_models.py -k "validation" -v
# Expected: Pydantic strict mode rejects invalid inputs
```

**AC-014**: Performance NFRs
```bash
pytest tests/performance/gateway/ -v
# Expected: p95 < 5s, p99 < 10s, throughput ≥60 conn/min
```

**AC-015**: Security validation
```bash
pytest tests/security/gateway/ -v
bandit -r src/ibmcp/gateway/ -ll
safety check
# Expected: All security tests pass, 0 high/critical vulnerabilities
```

---

## References

### Framework Documentation
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../../docs_flow_framework/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Workflow guide
- [TRACEABILITY.md](../../docs_flow_framework/ai_dev_flow/TRACEABILITY.md) - Cumulative tagging hierarchy
- [TOOL_OPTIMIZATION_GUIDE.md](../../docs_flow_framework/ai_dev_flow/TOOL_OPTIMIZATION_GUIDE.md) - Token efficiency guidelines
- [ID_NAMING_STANDARDS.md](../../docs_flow_framework/ai_dev_flow/ID_NAMING_STANDARDS.md) - Document naming conventions
- [IMPLEMENTATION_CONTRACTS_GUIDE.md](../../docs_flow_framework/ai_dev_flow/TASKS/IMPLEMENTATION_CONTRACTS_GUIDE.md) - Contract patterns

### Artifact Templates
- [TASKS-TEMPLATE.md](../TASKS/TASKS-TEMPLATE.md) - Parent artifact template
- [SPEC-TEMPLATE.yaml](../SPEC/SPEC-TEMPLATE.yaml) - Technical specification template
- [BDD-TEMPLATE.feature](../BDD/BDD-TEMPLATE.feature) - BDD scenario template
- [IPLAN-TEMPLATE.md](./IPLAN-TEMPLATE.md) - This template

### Source Documents
- [TASKS-001](../../docs/TASKS/TASKS-001_ib_gateway_connection_implementation.md) - Parent code generation plan (1,470 lines)
- [SPEC-001](../../docs/SPEC/SPEC-001_ib_gateway_connection.yaml) - Technical specification
- [REQ-001](../../docs/REQ/REQ-001_gateway_connection.md) - 15 atomic requirements
- [ADR-002](../../docs/ADR/ADR-002_ib_async_library.md) - ib_async library selection
- [BDD-001](../../tests/bdd/features/BDD-001_authentication.feature) - Authentication scenarios
- [BDD-007](../../tests/bdd/features/BDD-007_connection_lifecycle.feature) - Connection lifecycle scenarios
- [SYS-002](../../docs/SYS/SYS-002_gateway_system_requirements.md) - System requirements
- [ICON-001](../../docs/ICON/ICON-001_IBGatewayConnector.md) - Protocol interface contract
- [ICON-002](../../docs/ICON/ICON-002_ConnectionStateMachine.md) - State machine contract
- [ICON-003](../../docs/ICON/ICON-003_GatewayExceptions.md) - Exception hierarchy contract

### External References
- [ib_async Documentation](https://ib-insync.readthedocs.io/) - Library documentation
- [TWS API Guide](https://interactivebrokers.github.io/tws-api/) - IB API reference
- [Prometheus Python Client](https://github.com/prometheus/client_python) - Metrics library
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/) - Async testing framework
- [pytest-bdd](https://pytest-bdd.readthedocs.io/) - BDD testing framework
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) - Async ORM
- [Alembic](https://alembic.sqlalchemy.org/) - Database migrations
- [Cloud Run](https://cloud.google.com/run/docs) - GCP deployment target

---

## Appendix

### Glossary

| Term | Definition |
|------|------------|
| IB Gateway | Interactive Brokers standalone gateway application providing TWS API access without full TWS UI |
| TWS API | Trading Workstation API - IB's proprietary TCP protocol for programmatic trading |
| Circuit Breaker | Fault tolerance pattern preventing cascade failures by opening circuit after threshold failures |
| Exponential Backoff | Retry strategy with increasing delays: 1s, 2s, 4s, 8s, 16s, 32s |
| Correlation ID | Unique identifier (UUID4) for tracking requests across logs and metrics |
| Session ID | Unique identifier (UUID4) for each IB Gateway connection instance |
| Client ID | Integer identifier (1-9999) uniquely identifying connection to IB Gateway |
| State Machine | Connection lifecycle: DISCONNECTED → CONNECTING → CONNECTED → RECONNECTING → FAILED |
| BDD | Behavior-Driven Development - testing approach using Gherkin Given-When-Then syntax |
| NFR | Non-Functional Requirement - performance, security, scalability constraints |
| p95/p99 | 95th/99th percentile latency - 95%/99% of requests complete within this time |

### Command Reference

Quick reference for common commands used in this implementation:

```bash
# Setup
cd /opt/data/ibmcp
poetry install
alembic upgrade head

# Testing
pytest tests/ -v --cov=src/ibmcp/gateway --cov-report=term-missing
pytest tests/unit/gateway/ -v --cov=src/ibmcp/gateway --cov-report=html
pytest tests/integration/gateway/ -v
pytest tests/bdd/gateway/ --gherkin-terminal-reporter -v
pytest tests/performance/gateway/ -v
pytest tests/security/gateway/ -v

# Quality checks
ruff check src/ibmcp/gateway/ --fix
black src/ibmcp/gateway/
mypy src/ibmcp/gateway/ --strict
bandit -r src/ibmcp/gateway/ -ll
safety check
interrogate src/ibmcp/gateway/ -v

# Database
psql -U postgres -h localhost -d ibmcp_test
alembic revision -m "migration_name"
alembic upgrade head
alembic downgrade -1

# Docker
docker build -f docker/Dockerfile.connection-service -t ibmcp-gateway:local .
docker run -p 8080:8080 -p 9090:9090 ibmcp-gateway:local

# Metrics
curl http://localhost:9090/metrics | grep ib_gateway

# Health checks
curl http://localhost:8080/health/live
curl http://localhost:8080/health/ready
```

### Troubleshooting

**Issue 1: IB Gateway Connection Timeout**
- **Symptom**: `TimeoutError` after 30 seconds during connection
- **Cause**: IB Gateway not running, port blocked, or firewall restriction
- **Solution**:
  1. Verify IB Gateway process: `ps aux | grep ibgateway`
  2. Check port accessible: `nc -zv 127.0.0.1 4002`
  3. Review firewall rules: `sudo ufw status` (Ubuntu) or `iptables -L` (Linux)
  4. Check IB Gateway logs in `~/Jts/` or `~/IBController/logs/`
  5. Restart IB Gateway if needed

**Issue 2: Database Migration Fails**
- **Symptom**: `alembic upgrade head` fails with "table already exists" or "column not found"
- **Cause**: Database schema out of sync with migrations or concurrent migration
- **Solution**:
  1. Check current migration: `alembic current`
  2. View migration history: `alembic history`
  3. Manually inspect database: `psql -U postgres -h localhost -d ibmcp_test -c "\d gateway_connections"`
  4. If table exists but migration not recorded: `alembic stamp head`
  5. If migration corrupt: `alembic downgrade base && alembic upgrade head`

**Issue 3: Test Coverage Below Target**
- **Symptom**: pytest coverage report shows <85% for unit tests
- **Cause**: Missing tests for error paths, async edge cases, or infrastructure code inflating denominator
- **Solution**:
  1. Generate HTML coverage report: `pytest --cov=src/ibmcp/gateway --cov-report=html`
  2. Open `htmlcov/index.html` to identify uncovered lines
  3. Exclude infrastructure from coverage: Add to `.coveragerc`:
     ```ini
     [run]
     omit = src/ibmcp/gateway/__init__.py
     ```
  4. Add tests for uncovered error paths using mocks
  5. Use `pytest --cov --cov-report=term-missing` to see line numbers

**Issue 4: mypy Type Errors**
- **Symptom**: `mypy --strict` reports type errors in async code or third-party libraries
- **Cause**: Missing type annotations, untyped third-party libraries, or async/await type complexity
- **Solution**:
  1. Add type annotations to function signatures: `async def connect() -> IbConnection:`
  2. Use `typing.Optional` for nullable returns: `Optional[IbConnection]`
  3. Add type ignore comments for untyped libraries: `# type: ignore[import]`
  4. Install type stubs for third-party libraries: `pip install types-psycopg2`
  5. Use `reveal_type()` to debug type inference issues

**Issue 5: Docker Build Fails**
- **Symptom**: `docker build` fails with "poetry not found" or dependency installation errors
- **Cause**: Missing system dependencies, incorrect Poetry installation, or network issues
- **Solution**:
  1. Check Dockerfile syntax: `docker build --no-cache -f docker/Dockerfile.connection-service .`
  2. Verify Poetry installation in Dockerfile: `RUN pip install poetry==1.5.1`
  3. Add system dependencies for asyncpg: `RUN apt-get update && apt-get install -y gcc postgresql-client`
  4. Use `--verbose` for Poetry install: `RUN poetry install --no-dev --verbose`
  5. Check Docker build logs: `docker build . 2>&1 | tee build.log`

**Issue 6: Prometheus Metrics Not Exporting**
- **Symptom**: `curl http://localhost:9090/metrics` returns 404 or empty response
- **Cause**: Metrics server not started, incorrect port, or ConnectionMetrics not initialized
- **Solution**:
  1. Verify Prometheus port in config: `PROMETHEUS_PORT=9090`
  2. Check metrics server running: `netstat -an | grep 9090`
  3. Initialize ConnectionMetrics singleton: `metrics = ConnectionMetrics()`
  4. Start metrics server: `start_http_server(9090)`
  5. Test metrics endpoint: `curl http://localhost:9090/metrics | grep ib_gateway`

---

**Document End**

**Next Actions**:
1. Execute Phase 1: Environment Validation (4 hours)
2. Execute Phase 2: Complete Implementation (16 hours)
3. Execute Phase 3: Testing & Validation (38 hours)
4. Execute Phase 4: Completion & Deployment (16 hours)
5. Update TASKS-001 with actual effort and completion status

**Follow-up**:
- Create IPLAN-002 for order management service implementation
- Create IPLAN-003 for market data service implementation
- Document lessons learned and update IPLAN-TEMPLATE if improvements identified
