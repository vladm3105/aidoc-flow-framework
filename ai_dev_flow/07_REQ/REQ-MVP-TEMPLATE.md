---
title: "REQ-MVP-TEMPLATE: Requirements Document (MVP)"
tags:
  - req-template
  - mvp-template
  - layer-7-artifact
  - document-template
  - shared-architecture
custom_fields:
  document_type: template
  artifact_type: REQ
  layer: 7
  template_variant: mvp
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  schema_version: "1.1"
  complexity: 1 # 1-5 scale
---

<!--
AI_CONTEXT_START
Role: AI Requirements Engineer
Objective: Create a streamlined MVP Atomic Requirement.
Constraints:
- Define exactly ONE atomic requirement per document.
- 12 sections required (aligned with MVP requirements template).
- All 6 upstream traceability tags required (@brd, @prd, @ears, @bdd, @adr, @sys).
- Use @threshold tags for all quantitative values.
- SPEC-Ready thresholds: ≥70% for MVP profile.
- Ensure SPEC-ready clarity (Inputs, Processing, Outputs).
- Use distinct P1/P2/P3 priorities.
- Do not create external references to non-existent files.
- Maintain single-file structure (no document splitting in MVP).
AI_CONTEXT_END
-->

**MVP Template** — Single-file, streamlined REQ for rapid MVP development.
 Use this template for MVP atomic requirements (10-20 core requirements).

**Validation Note**: MVP templates are intentionally streamlined and will show validation errors when run against full template validators (e.g., `validate_req_template.sh`). This is expected behavior. See `scripts/README.md` → "MVP Template Validation" for guidance.

  References: Schema `REQ_MVP_SCHEMA.yaml` | Rules `REQ_MVP_CREATION_RULES.md`, `REQ_MVP_VALIDATION_RULES.md` | Matrix `REQ-00_TRACEABILITY_MATRIX-TEMPLATE.md`


# REQ-NN: [RESOURCE_TYPE] [Requirement Title]

**MVP Scope**: This requirement document focuses on essential, SPEC-ready requirements for MVP delivery.

> **Resource Tags**: Replace `[RESOURCE_TYPE]` with project-specific resource classification (e.g., `[EXTERNAL_SERVICE_GATEWAY]`, `[HEALTH_CHECK_SERVICE]`, `[DATA_VALIDATION]`). See project ADR for resource taxonomy.

## 1. Document Control

| Item | Details |
|------|---------|
| **Status** | Draft / Review / Approved / Implemented |
| **Version** | 0.1.0 |
| **Date Created** | YYYY-MM-DD |
| **Last Updated** | YYYY-MM-DD |
| **Author** | [Author name] |
| **Priority** | P1 (Critical) / P2 (High) / P3 (Medium) |
| **Category** | Functional / Security / Performance |
| **Source Document** | [SYS-NN section X.Y.Z] |
| **Verification Method** | BDD / Unit Test / Integration Test |
| **Assigned Team** | [Team name] |
| **SPEC-Ready Score** | ✅ [XX]% (Target: ≥70%) |
| **CTR-Ready Score** | ✅ [XX]% (Target: ≥70%) |
| **Template Version** | 1.0 |
| **Deployment Complexity** | simple / standard / enterprise (see Section 9.5 Guidance) |

---

## 2. Requirement Description

### 2.1 Statement

**The system SHALL** [precise, atomic requirement statement that defines exactly one specific behavior].

### 2.2 Context

[1-2 paragraphs: Why this requirement exists and what problem it solves]

### 2.3 Use Case

**Primary Flow**:
1. [Actor] initiates [action/trigger]
2. System validates [precondition]
3. System executes [core behavior]
4. System returns [outcome]

**Error Flow**:
- When [error condition], system SHALL [error behavior]

---

## 3. Functional Specification

### 3.1 Core Functionality

**Required Capabilities**:
- [Capability 1]: [Specific behavior with measurable outcome]
- [Capability 2]: [Specific behavior with measurable outcome]

### 3.2 Business Rules

**ID Format**: `REQ.NN.21.SS` (Validation Rule)

| Rule ID | Condition | Action |
|---------|-----------|--------|
| REQ.NN.21.01 | IF [condition] | THEN [action/outcome] |
| REQ.NN.21.02 | IF [condition] | THEN [action/outcome] |

### 3.3 Input/Output Specification

**Inputs**:

| Parameter | Type | Required | Validation | Description |
|-----------|------|----------|------------|-------------|
| [param1] | [string/int/etc] | Yes/No | [rules] | [what it is] |
| [param2] | [string/int/etc] | Yes/No | [rules] | [what it is] |

**Outputs**:

| Field | Type | Description |
|-------|------|-------------|
| [field1] | [string/int/etc] | [what it contains] |
| [field2] | [string/int/etc] | [what it contains] |

---

## 4. Interface Definition

### 4.1 API Contract (if applicable)

> **Note**: This section provides JSON wire format examples. If using Section 4.2 Pydantic schemas with `.model_json_schema()`, this section is optional and may be omitted to avoid redundancy with Section 3.3 Input/Output.

**Endpoint**: `[METHOD] /api/v1/[resource]`

**Request**:
```json
{
  "field1": "value",
  "field2": 123
}
```

**Response (Success)**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "result": "value"
  }
}
```

**Response (Error)**:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Description"
  }
}
```

### 4.2 Data Schema

```python
from pydantic import BaseModel, Field
from datetime import datetime

class RequestModel(BaseModel):
    """Request data structure."""
    field1: str = Field(..., min_length=1, max_length=100)
    field2: int = Field(..., ge=0)

class ResponseModel(BaseModel):
    """Response data structure."""
    id: str
    result: str
    timestamp: datetime
```

---

## 5. Error Handling

### 5.1 Error Catalog

| Error Code | HTTP Status | Condition | User Message | System Action |
|------------|-------------|-----------|--------------|---------------|
| [ERR_001] | 400 | Invalid input | [Message] | Log, return error |
| [ERR_002] | 404 | Resource not found | [Message] | Log, return error |
| [ERR_003] | 500 | Processing failed | [Message] | Log, alert, retry |

### 5.2 Recovery Strategy

| Error Type | Retry? | Fallback | Alert |
|------------|--------|----------|-------|
| Validation error | No | Return error | No |
| Transient failure | Yes (3x) | Queue/Cache | After retries |
| Permanent failure | No | Graceful error | Yes |

---

## 6. Quality Attributes

**ID Format**: `REQ.NN.02.SS` (Quality Attribute)

### 6.1 Performance (REQ.NN.02.01)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Response time (p95) | < @threshold: PRD.NN.perf.api.p95_latency | APM traces |
| Throughput | @threshold: PRD.NN.perf.api.throughput | Load test |

> **Note**: Use `@threshold` tags for all quantitative values. Reference centralized threshold registry in PRD.

### 6.2 Security (REQ.NN.02.02)

- [ ] Input validation: All inputs validated
- [ ] Authentication: [Required/Optional]
- [ ] Authorization: [Role-based check]
- [ ] Data protection: [PII handling]

### 6.3 Reliability (REQ.NN.02.03)

- Error rate: < @threshold: PRD.NN.reliability.error_rate
- Idempotency: [Required for POST/PUT operations]

---

## 7. Configuration

### 7.1 Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| [CONFIG_1] | [type] | [default] | [what it controls] |
| [CONFIG_2] | [type] | [default] | [what it controls] |

### 7.2 Feature Flags (if applicable)

| Flag | Default | Description |
|------|---------|-------------|
| [FLAG_NAME] | false | [When to enable] |

---

## 8. Testing Requirements

### 8.1 Unit Tests

| Test Case | Input | Expected Output | Coverage |
|-----------|-------|-----------------|----------|
| [Happy path] | [valid input] | [expected result] | Core logic |
| [Edge case] | [boundary input] | [expected behavior] | Boundary |
| [Error case] | [invalid input] | [error response] | Error handling |

### 8.2 Integration Tests

- [ ] API endpoint responds correctly
- [ ] Database operations work
- [ ] External service integration works

### 8.3 BDD Scenarios

**Feature**: [Feature name]
**File**: `04_BDD/BDD-NN_{suite}/BDD-NN.SS_{slug}.feature`

| Scenario | Priority | Status |
|----------|----------|--------|
| [Scenario 1] | P1 | [Pending/Passed] |
| [Scenario 2] | P1 | [Pending/Passed] |

---

## 9. Acceptance Criteria

**ID Format**: `REQ.NN.06.SS` (Acceptance Criteria)

### 9.1 Functional Acceptance

> **Note**: Each criterion should trace to one or more BDD scenarios in Section 8.3. Use `@bdd` tags for traceability.

| Criteria ID | Criterion | Measurable Outcome | Status |
|-------------|-----------|-------------------|--------|
| REQ.NN.06.01 | [Criterion 1] | [Measurable outcome] | [ ] |
| REQ.NN.06.02 | [Criterion 2] | [Measurable outcome] | [ ] |
| REQ.NN.06.03 | [Criterion 3] | [Measurable outcome] | [ ] |

### 9.2 Quality Acceptance

> **Note**: Reference Section 6 Quality Attributes for target values. Use `@threshold` tags to avoid duplication.

| Criteria ID | Criterion | Target | Status |
|-------------|-----------|--------|--------|
| REQ.NN.06.04 | Performance target | @threshold: REQ.NN.02.01 | [ ] |
| REQ.NN.06.05 | Security | No critical vulnerabilities | [ ] |
| REQ.NN.06.06 | Test coverage | ≥ @threshold: PRD.NN.quality.coverage | [ ] |

---

## 9.5 Deployment Requirements

> **Note**: Deployment scope and cloud provider are defined in upstream BRD, PRD, and ADR documents. This section captures specific infrastructure and deployment artifact requirements for automated generation.

> **Quick Start** (For Simple Deployments): Complete only these subsections based on `Deployment Complexity`:
> - **Simple (PaaS)**: 9.5.1, 9.5.2, 9.5.3 (skip 9.5.1, 9.5.4, 9.5.6, 9.5.7, 9.5.8)
> - **Standard/Enterprise**: All 8 subsections (9.5.1 through 9.5.8)
> See examples in `examples/deployment/` for complete patterns

### 9.5.0 Deployment Tier Selection

> **Tier Selection**: Choose one tier based on deployment complexity. This determines which subsections are required in Section 9.5.

**Decision Tree**:

```
Does your deployment require infrastructure provisioning?
├── No → Tier 1: Simple PaaS (Cloud Run, Lambda, App Engine)
│   ├── Subsection 9.5.1: ❌ Skip (Optional)
│   ├── Subsection 9.5.2: ✅ Required
│   ├── Subsection 9.5.3: ✅ Required (Simple: deploy.sh + health-check.sh)
│   └── Subsections 9.5.4-9.5.8: ❌ Optional
│
├── Yes → Is deployment multi-region/multi-cloud?
│   ├── Yes → Tier 3: Enterprise (Multi-Cloud)
│   │   ├── Subsection 9.5.1: ✅ Required
│   │   ├── Subsection 9.5.2: ✅ Required
│   │   ├── Subsection 9.5.3: ✅ Required
│   │   ├── Subsection 9.5.4: ✅ Required
│   │   ├── Subsection 9.5.5: ✅ Required
│   │   ├── Subsection 9.5.6: ✅ Required
│   │   ├── Subsection 9.5.7: ✅ Required
│   │   └── Subsection 9.5.8: ✅ Required
│   │
│   └── No → Tier 2: Standard (Containerized VM/ECS)
│       ├── Subsection 9.5.1: ✅ Required
│       ├── Subsection 9.5.2: ✅ Required
│       ├── Subsection 9.5.3: ✅ Required
│       ├── Subsection 9.5.4: ⚠️ Optional (Infrastructure already provisioned)
│       ├── Subsection 9.5.5: ✅ Required
│       ├── Subsection 9.5.6: ✅ Required
│       ├── Subsection 9.5.7: ✅ Required
│       └── Subsection 9.5.8: ✅ Required
```

**Tier Definitions**:
- **Tier 1: Simple PaaS** - Platform-as-a-Service (Cloud Run, Lambda, App Engine, App Engine, Cloud Functions)
- **Tier 2: Standard** - Containerized VMs on ECS/GKE/Cloud Run with provisioned infrastructure
- **Tier 3: Enterprise** - Multi-region, multi-cloud deployments with full observability, cost management

### 9.5.1 Infrastructure Requirements

| Resource Type | Provider | Configuration | Requirements |
|---------------|----------|--------------|--------------|
| Compute | [From @adr: ADR-NN] | [Type: EC2/ECS/Cloud Run/GKE] | [CPU, Memory, Scaling: min/max] |
| Database | [From @adr: ADR-NN] | [Type: RDS/Cloud SQL/Postgres] | [Version, Storage: GB, HA: yes/no] |
| Storage | [From @adr: ADR-NN] | [Type: S3/Cloud Storage/EBS] | [Bucket type, Retention: days] |
| Network | [From @adr: ADR-NN] | [VPC, Subnets, Load Balancer] | [CIDR, AZs, Security Groups] |
| Cache | [Optional] | [Type: Redis/Memcached/ElastiCache] | [Memory: GB, TTL: seconds] |
| Message Queue | [Optional] | [Type: SQS/PubSub/Kafka] | [Queue type, Retention: days] |

> **Reference**: Cloud provider decisions in `@brd: BRD.NN.TT.SS`, `@prd: PRD.NN.TT.SS`, `@adr: ADR-NN`

> **Complexity Indicator**: ⚠️ [Standard+] - Required for Standard/Enterprise deployments, Optional for Simple (PaaS) deployments

### 9.5.2 Environment Configuration

| Environment | Deployment Strategy | Rollback Time | Replicas | Regions |
|-------------|---------------------|---------------|-----------|---------|
| Development | [Manual/CI] | N/A | [1] | [Region] |
| Staging | [Blue-Green/Canary/Rolling] | [X minutes] | [N] | [Region] |
| Production | [Blue-Green/Canary/Rolling] | [X minutes] | [N] | [Regions for HA] |

**Health Endpoints**:
- Liveness: `/health/live` - Container health check
- Readiness: `/health/ready` - Service availability check
- Startup: `/health/startup` - Initialization complete check

### 9.5.3 Deployment Scripts Requirements

> **Note**: All scripts generated automatically by Autopilot from this section.

| Script Name | Purpose | Automation Level | Required for Environments |
|-------------|---------|------------------|-------------------------|
| `setup.sh` | Initial environment setup (dependencies, tools, paths) | Fully automated | All |
| `install.sh` | Application installation/configuration (packages, config files) | Fully automated | All |
| `deploy.sh` | Main deployment orchestration (build, push, deploy) | Fully automated | Staging, Production |
| `rollback.sh` | Rollback to previous version | Fully automated | Staging, Production |
| `health-check.sh` | Health verification post-deployment | Fully automated | All |
| `cleanup.sh` | Cleanup old versions, temporary files | Fully automated | All |

**Script Standards**:
- Shell: Bash 4.0+ compatible
- Logging: All scripts log to `logs/deployment_YYYYMMDD_HHMMSS.log`
- Exit codes: 0 (success), 1 (error), 2 (warning)
- Error handling: `set -euo pipefail` for all scripts
- Idempotency: All scripts safe to run multiple times

### 9.5.4 Ansible Playbook Requirements

> **Note**: All playbooks generated automatically by Autopilot from this section.

| Playbook Name | Purpose | Target | Variables | Tags |
|---------------|---------|--------|------------|------|
| `provision_infra.yml` | Provision infrastructure (VPC, EC2, RDS, etc.) | Cloud provider API | Cloud resources config | `infra, provision` |
| `configure_instances.yml` | Configure instances (OS settings, packages, users) | Instance hosts | Instance config, packages | `config, instances` |
| `deploy_app.yml` | Deploy application (copy code, restart service) | Application hosts | App version, config | `deploy, app` |
| `configure_monitoring.yml` | Setup monitoring/alerting (Prometheus, Grafana) | Monitoring hosts | Monitoring config, alerts | `monitoring, observability` |
| `configure_security.yml` | Setup security (firewall, IAM, TLS) | All hosts | Security rules, certificates | `security, hardening` |
| `backup_restore.yml` | Backup/restore procedures (database, config) | Backup hosts | Backup schedule, retention | `backup, recovery` |

**Playbook Standards**:
- Ansible version: 2.9+
- Inventory: Dynamic inventory from cloud provider
- Roles: Modular role-based structure
- Idempotency: All playbooks idempotent
- Handlers: Service restart handlers for configuration changes
- Check mode: Support `--check` for dry-run

### 9.5.5 Observability Requirements

| Type | Tool | Metrics/Logs | Retention | Alerts |
|------|------|--------------|-----------|--------|
| Logging | [Cloud Logging/ELK] | [Format: JSON] | [X days] | [Error threshold, rate thresholds] |
| Metrics | [Prometheus/Datadog] | [p50/p95/p99 latency, throughput, errors] | [X days] | [SLA breaches, degradation] |
| Tracing | [Jaeger/Cloud Trace/OpenTelemetry] | [Sample rate: %] | [X days] | [Slow requests, errors] |
| Dashboards | [Grafana/Datadog] | [Business metrics, health metrics] | N/A | N/A |

### 9.5.6 Security Requirements

| Security Aspect | Requirement | Tool/Service | Verification |
|-----------------|-------------|---------------|---------------|
| Secrets Management | [Vault/AWS Secrets Manager/GCP Secret Manager] | [Service name, path] | [Secrets rotated every X days] |
| TLS/SSL | [Certificate manager/Let's Encrypt] | [Domain, certificate type] | [TLS 1.3+, valid certificate] |
| IAM | [Roles/Policies] | [Permissions: read/write/admin] | [Least privilege enforced] |
| Network Security | [VPC, Security Groups, NACLs] | [Allowed IPs, ports] | [Firewall rules audited] |
| Container Security | [Image scanning] | [Vulnerability thresholds] | [No critical vulnerabilities] |

### 9.5.7 Cost Constraints

| Resource | Budget | Alerts | Optimization |
|----------|--------|--------|--------------|
| Compute | [Monthly: $X] | [Threshold: 80%] | [Savings plans, spot instances] |
| Storage | [Monthly: $X] | [Threshold: 80%] | [Lifecycle policies, compression] |
| Network | [Monthly: $X] | [Threshold: 80%] | [CDN, compression] |
| Total | [Monthly: $X] | [Threshold: 80%] | [Resource rightsizing] |

### 9.5.8 Deployment Automation Requirements

**Automation Level**: Fully automated (no manual steps)

**Deployment Workflow**:
1. Autopilot generates deployment artifacts (scripts, playbooks)
2. CI/CD pipeline triggers on merge to main
3. Scripts run setup → install → deploy → health-check
4. If health-check fails: auto-rollback
5. Success: update load balancer, monitoring dashboards

**Validation Requirements**:
- Pre-deployment: All tests pass, no security vulnerabilities
- Post-deployment: Health checks pass, performance within SLA
- Monitoring: All metrics collected, dashboards updated
- Rollback: Ready within X minutes

> **Downstream Artifacts**: See Section 10.2 for generated scripts and playbooks

---

## 10. Traceability

### 10.1 Upstream References

| Source Type | Document ID | Element Reference | Relationship |
|-------------|-------------|-------------------|--------------|
| BRD | BRD-NN | BRD.NN.TT.SS | Primary business need |
| PRD | PRD-NN | PRD.NN.TT.SS | Product requirement |
| EARS | EARS-NN | EARS.NN.TT.SS | Formal requirement |
| BDD | BDD-NN | BDD.NN.TT.SS | Acceptance test |
| ADR | ADR-NN | — | Architecture decision |
| SYS | SYS-NN | SYS.NN.TT.SS | System requirement |

> **Complete Upstream Chain**: Layer 7 (REQ) requires references to all 6 upstream artifact types.

### 10.2 Downstream Artifacts

| Artifact | Status | Relationship |
|----------|--------|--------------|
| CTR-NN | TBD | API contract (if external interface) |
| SPEC-NN | TBD | Technical specification |
| TASKS-NN | TBD | Implementation tasks |

#### Deployment Artifacts (Generated by Autopilot)

| Artifact Type | Artifact | Status | Generation Source |
|--------------|----------|--------|-------------------|
| Shell Scripts | `scripts/setup.sh` | TBD | Section 9.5.3 |
| Shell Scripts | `scripts/install.sh` | TBD | Section 9.5.3 |
| Shell Scripts | `scripts/deploy.sh` | TBD | Section 9.5.3 |
| Shell Scripts | `scripts/rollback.sh` | TBD | Section 9.5.3 |
| Shell Scripts | `scripts/health-check.sh` | TBD | Section 9.5.3 |
| Shell Scripts | `scripts/cleanup.sh` | TBD | Section 9.5.3 |
| Ansible Playbooks | `ansible/provision_infra.yml` | TBD | Section 9.5.4 |
| Ansible Playbooks | `ansible/configure_instances.yml` | TBD | Section 9.5.4 |
| Ansible Playbooks | `ansible/deploy_app.yml` | TBD | Section 9.5.4 |
| Ansible Playbooks | `ansible/configure_monitoring.yml` | TBD | Section 9.5.4 |
| Ansible Playbooks | `ansible/configure_security.yml` | TBD | Section 9.5.4 |
| Ansible Playbooks | `ansible/backup_restore.yml` | TBD | Section 9.5.4 |
| IaC Templates | `terraform/` or `cloudformation/` | TBD | Section 9.5.1 + devops-flow |
| Docker Config | `Dockerfile`, `docker-compose.yml` | TBD | Section 9.5.1 |
| CI/CD Pipeline | `.github/workflows/deploy.yml` | TBD | Section 9.5.8 |

> **Note**: All deployment artifacts are generated automatically by Autopilot from REQ Section 9.5 and SPEC deployment section.

### 10.3 Traceability Tags

```markdown
@brd: BRD.NN.TT.SS
@prd: PRD.NN.TT.SS
@ears: EARS.NN.TT.SS
@bdd: BDD.NN.TT.SS
@adr: ADR-NN
@sys: SYS.NN.TT.SS
```

> **Note**: Document references use dash notation (`ADR-NN`). Element references within documents use 4-segment dot notation (`BRD.NN.TT.SS`). Layer 7 (REQ) requires ALL 6 upstream tags.

**Downstream Traceability Tags** (for generated artifacts):

```markdown
@ctr: CTR-NN          # If API contract exists
@spec: SPEC-NN         # Technical specification
@tasks: TASKS-NN       # Implementation tasks
@deployment: scripts/   # Deployment scripts directory
@ansible: ansible/      # Ansible playbooks directory
@iac: terraform/       # IaC templates directory
```

> **Note**: Downstream tags reference generated artifacts (scripts, playbooks, IaC) for bidirectional traceability.

---

## 11. Implementation Notes

### 11.1 Technical Approach

[Brief description of recommended implementation approach]

### 11.2 Code Location

- **Primary**: `src/[module]/[component].py`
- **Tests**: `tests/[module]/test_[component].py`

### 11.3 Dependencies

| Package/Service | Version | Purpose |
|-----------------|---------|---------|
| [dependency1] | [version] | [why needed] |
| [dependency2] | [version] | [why needed] |

---

## 12. Change History

| Date | Version | Change | Author |
|------|---------|--------|--------|
| YYYY-MM-DD | 0.1.0 | Initial draft | [Author] |

---

## 13. Migration to Full REQ Template

### 13.1 When to Migrate

- [ ] Requirement complexity requires 12-section format
- [ ] Need comprehensive interface protocols (Python)
- [ ] Full error catalog with state machines required
- [ ] SPEC generation requires maximum detail
- [ ] Compliance requires comprehensive test coverage

### 13.2 Migration Steps

2. **Transfer core content**: Map MVP sections to full template
3. **Expand detailed sections**:
   - Full interface protocols (Python classes)
   - Complete data schemas (JSON, Pydantic, SQLAlchemy)
   - Comprehensive error catalogs with circuit breakers
   - Detailed configuration specifications
4. **Add missing sections**: EARS statements, verification matrix
5. **Update traceability**: Ensure SPEC documents reference new REQ
6. **Archive MVP version**: Move to archive with "superseded" note
7. **Run validation**: Execute `./07_REQ/scripts/validate_req_template.sh` on new document

### 13.3 Section Mapping (MVP → Full)

| MVP Section | Full Template Section | Migration Notes |
|-------------|----------------------|-----------------|
| 1. Document Control | 1. Document Control | Add all 12 required fields |
| 2. Requirement Description | 1. Description | Expand EARS statements |
| 3. Functional Specification | 2. Functional Requirements | Add business rules |
| 4. Interface Definition | 3. Interface Specifications | Full Protocol/ABC classes |
| 5. Error Handling | 5. Error Handling Specifications | Full catalog + state machine |
| 6. Quality Attributes | 7. Quality Attributes | Add p50/p99 metrics |
| 7. Configuration | 6. Configuration Specifications | Full YAML schema |
| 8. Testing Requirements | 10. Verification Methods | Full test matrix |
| 9. Acceptance Criteria | 9. Acceptance Criteria | Expand to ≥15 criteria |
| 10. Traceability | 11. Traceability | Add matrix if complex |
| 11. Implementation Notes | 8. Implementation Guidance | Add patterns/DI |
| 12. Change History | 12. Change History | — |

---

**Document Version**: 0.1.0
**Template Version**: 1.0 (MVP)
**Last Updated**: 2026-01-13

---

> **MVP Template Notes**:
> - 12 sections aligned with full REQ template structure
> - Single file - no document splitting required
> - Focus on SPEC-ready, atomic requirements
> - All 6 upstream traceability tags required (Layer 7)
> - SPEC-Ready/CTR-Ready thresholds: ≥70% (vs ≥90% for full template)
> - Uses `@threshold` tags for quantitative values
