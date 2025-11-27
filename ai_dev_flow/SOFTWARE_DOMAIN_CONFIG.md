---
title: "Software/SaaS Domain Configuration"
tags:
  - framework-guide
  - shared-architecture
custom_fields:
  document_type: guide
  priority: shared
  development_status: active
---

# Software/SaaS Domain Configuration

**Version**: 1.0
**Purpose**: Domain configuration for software and SaaS projects
**Domain**: B2B/B2C Software Services, Multi-Tenant Applications, API Platforms
**Status**: Production
**Regulatory Scope**: SOC2, GDPR/CCPA, ISO 27001, FedRAMP (optional)

---

## Overview

Configuration for Software-as-a-Service (SaaS), Platform-as-a-Service (PaaS), and general software products with emphasis on multi-tenancy, API-first design, subscription management, and cloud-native architecture.

### Software/SaaS Scope

- **B2B SaaS**: Enterprise software, team collaboration, business tools
- **B2C SaaS**: Consumer applications, productivity tools, personal services
- **API Platforms**: API gateways, integration platforms, middleware
- **Microservices**: Distributed systems, service-oriented architecture
- **Multi-Tenant Systems**: Shared infrastructure with data isolation

---

## Placeholder Replacement Dictionary

### Core Terminology Mappings

| Placeholder | Software/SaaS Term | Context |
|-------------|-------------------|---------|
| `[RESOURCE_COLLECTION]` | **Workspace** | Container for user resources |
| `[RESOURCE_ITEM]` | **Resource** | Individual entity or object |
| `[RESOURCE_ACTION]` | **API Request** | Action performed on resources |
| `[EXTERNAL_DATA_PROVIDER]` | **Third-party Integration** | External service (Stripe, SendGrid, Auth0) |
| `[CALCULATION_ENGINE]` | **Billing Engine** | Core processing system |
| `[USER_ROLE]` | **Account Admin / Member** | User with specific permissions |
| `[TRANSACTION]` | **API Call** | System transaction |
| `[CONSTRAINT]` | **Rate Limit** | Service constraint |
| `[REGULATORY_REQUIREMENT]` | **SOC2 Control** | Compliance requirement |
| `[DATA_STORE]` | **Database / Data Lake** | Persistent storage |
| `[EVENT]` | **System Event** | State change notification |
| `[WORKFLOW]` | **User Workflow** | Business process |
| `[METRIC]` | **MRR (Monthly Recurring Revenue)** | Key performance indicator |
| `[ALERT]` | **System Alert** | Notification or alarm |
| `[REPORT]` | **Analytics Report** | Generated output |

### Extended Terminology

| Domain Concept | Software Term | Alternative Terms |
|----------------|---------------|-------------------|
| Entity Identifier | **UUID / Resource ID** | GUID, Object ID |
| Quantity | **Count / Limit** | Quota, Capacity |
| Price | **Price Point / Tier** | Subscription level, Plan |
| Timestamp | **Created At / Updated At** | Event timestamp, Modified date |
| Status | **Status** | Active, Suspended, Canceled |
| Category | **Resource Type** | Entity type, Object class |
| Organization Unit | **Tenant / Organization** | Account, Company |
| Configuration | **Settings / Preferences** | Config, Options |
| Validation | **Input Validation** | Request validation, Schema validation |
| Approval | **Admin Approval** | Authorization, Permission grant |

---

## AI Assistant Placeholder Replacement

### Automated Replacement Commands

```bash
# Core replacements for Software/SaaS
find docs/ -type f -name "*.md" -exec sed -i \
  -e 's/\[RESOURCE_COLLECTION\]/Workspace/g' \
  -e 's/\[RESOURCE_ITEM\]/Resource/g' \
  -e 's/\[RESOURCE_ACTION\]/API Request/g' \
  -e 's/\[EXTERNAL_DATA_PROVIDER\]/Third-party Integration/g' \
  -e 's/\[CALCULATION_ENGINE\]/Billing Engine/g' \
  -e 's/\[USER_ROLE\]/Account Admin/g' \
  -e 's/\[TRANSACTION\]/API Call/g' \
  -e 's/\[CONSTRAINT\]/Rate Limit/g' \
  -e 's/\[REGULATORY_REQUIREMENT\]/SOC2 Control/g' \
  -e 's/\[DATA_STORE\]/Database/g' \
  -e 's/\[EVENT\]/System Event/g' \
  -e 's/\[WORKFLOW\]/User Workflow/g' \
  -e 's/\[METRIC\]/MRR/g' \
  -e 's/\[ALERT\]/System Alert/g' \
  -e 's/\[REPORT\]/Analytics Report/g' \
  {} +

# Extended replacements
find docs/ -type f -name "*.md" -exec sed -i \
  -e 's/\[ENTITY_ID\]/UUID/g' \
  -e 's/\[QUANTITY\]/Count/g' \
  -e 's/\[PRICE\]/Price Point/g' \
  -e 's/\[TIMESTAMP\]/Created At/g' \
  -e 's/\[STATUS\]/Status/g' \
  -e 's/\[CATEGORY\]/Resource Type/g' \
  -e 's/\[ORG_UNIT\]/Tenant/g' \
  {} +
```

### YAML Specification Replacements

```bash
# Apply to YAML SPEC
find docs/SPEC/ -type f -name "*.yaml" -exec sed -i \
  -e 's/resource_collection/workspace/g' \
  -e 's/resource_item/resource/g' \
  -e 's/ResourceCollection/Workspace/g' \
  -e 's/ResourceItem/Resource/g' \
  {} +
```

---

## Regulatory Framework Mappings

### SOC2 (Service Organization Control 2)

| Control Category | Application | Requirements |
|-----------------|-------------|--------------|
| **CC6.1 Logical Access** | Authentication & Authorization | MFA, RBAC, session management |
| **CC6.6 Encryption** | Data Protection | Encryption at rest and in transit |
| **CC7.2 Monitoring** | System Monitoring | Logging, alerting, incident response |
| **CC8.1 Change Management** | Deployment Controls | CI/CD, rollback procedures |
| **A1.2 Confidentiality** | Data Isolation | Multi-tenant data segregation |

**Traceability in Documents**:
```markdown
**Regulatory Requirement**: SOC2 CC6.1 (Logical Access Controls)
**Compliance Control**: CTRL-SOC2-CC6.1-001
```

### GDPR (General Data Protection Regulation)

| Requirement | Application | Implementation |
|-------------|-------------|----------------|
| **Article 17 - Right to Erasure** | Data Deletion | User data deletion API |
| **Article 20 - Data Portability** | Data Export | Export user data in machine-readable format |
| **Article 32 - security** | Data Protection | Encryption, access controls, pseudonymization |
| **Article 33 - Breach Notification** | Incident Response | 72-hour notification procedures |

### CCPA (California Consumer Privacy Act)

| Requirement | Application | Implementation |
|-------------|-------------|----------------|
| **Right to Know** | Data Disclosure | API to retrieve collected personal information |
| **Right to Delete** | Data Deletion | Delete personal information upon request |
| **Right to Opt-Out** | Do Not Sell | Opt-out mechanism for data sales |

### ISO 27001 (Information security)

| Control | Application | Requirements |
|---------|-------------|--------------|
| **A.9 Access Control** | Identity Management | User authentication, authorization |
| **A.12 Operations security** | security Operations | Vulnerability management, malware protection |
| **A.14 System Acquisition** | regulatoryure SDLC | security requirements in development |
| **A.17 Business Continuity** | DR/BCP | Backup, disaster recovery, failover |

---

## Software/SaaS Terminology Dictionary

### Multi-Tenancy

| Term | Definition | Context |
|------|------------|---------|
| **Tenant** | Isolated customer instance | Organization, account, company |
| **Workspace** | Collaboration space within tenant | Project, team, environment |
| **Data Isolation** | Logical/physical separation | Row-level security, separate schemas |
| **Shared Infrastructure** | Multi-tenant hosting | Shared compute, storage, services |
| **Tenant Context** | Identifying scope | Tenant ID in requests, middleware |

### Subscription & Billing

| Term | Definition | Usage |
|------|------------|-------|
| **Subscription** | Ongoing service agreement | Monthly/annual billing |
| **Plan/Tier** | Service level | Free, Pro, Enterprise |
| **MRR** | Monthly Recurring Revenue | Revenue metric |
| **ARR** | Annual Recurring Revenue | Revenue metric (MRR × 12) |
| **Churn** | Customer attrition | Lost customers / total customers |
| **Usage-Based Billing** | Metered pricing | Pay per API call, storage, compute |
| **Seat-Based Licensing** | Per-user pricing | $10/user/month |

### API & Integration

| Term | Definition | Context |
|------|------------|---------|
| **REST API** | HTTP-based API | GET, POST, PUT, DELETE |
| **GraphQL** | Query language for APIs | Flexible data fetching |
| **Webhook** | Event-driven callback | HTTP POST on event |
| **API Key** | Authentication credential | Bearer token, header auth |
| **Rate Limit** | Request throttling | 1000 requests/hour |
| **API Gateway** | Entry point for APIs | Routing, auth, rate limiting |
| **SDK** | Software Development Kit | Client library (Python, JS, Go) |

### Cloud-Native Architecture

| Term | Definition | Context |
|------|------------|---------|
| **Microservice** | Independent service | Bounded context, single responsibility |
| **Serverless** | Function-as-a-Service | AWS Lambda, Google Cloud Functions |
| **Container** | Isolated runtime | Docker, Kubernetes pod |
| **Service Mesh** | Inter-service communication | Istio, Linkerd |
| **Event-Driven** | Asynchronous messaging | Pub/sub, message queues |
| **API-First** | API as primary interface | Design APIs before implementation |

### Operational Metrics

| Term | Definition | Formula/Context |
|------|------------|-----------------|
| **Uptime** | Service availability | (Total time - Downtime) / Total time |
| **SLA** | Service Level Agreement | 99.9% uptime guarantee |
| **RTO** | Recovery Time Objective | Maximum acceptable downtime |
| **RPO** | Recovery Point Objective | Maximum acceptable data loss |
| **Latency** | Request response time | P50, P95, P99 percentiles |
| **Throughput** | Requests per second | 10,000 req/s capacity |
| **Error Rate** | Failed requests | 5xx errors / total requests |

---

## Requirements Subdirectory Structure

### Software-Specific Subdirectories

```bash
mkdir -p docs/REQ/tenant/           # Multi-tenancy requirements
mkdir -p docs/REQ/tenant/isolation/ # Data isolation
mkdir -p docs/REQ/tenant/onboard/   # Tenant onboarding

mkdir -p docs/REQ/subscription/     # Subscription management
mkdir -p docs/REQ/subscription/plan/    # Plan management
mkdir -p docs/REQ/subscription/billing/ # Billing & invoicing

mkdir -p docs/REQ/billing/          # Billing engine
mkdir -p docs/REQ/billing/metered/  # Usage-based billing
mkdir -p docs/REQ/billing/invoice/  # Invoice generation

mkdir -p docs/REQ/workspace/        # Workspace features
mkdir -p docs/REQ/workspace/collab/ # Collaboration tools
mkdir -p docs/REQ/workspace/perm/   # Permissions

# Support directories
mkdir -p scripts                    # Validation and utility scripts
mkdir -p work_plans                 # Implementation plans (/save-plan output)
```

---

## Example Use Cases

### Use Case 1: B2B SaaS Project Management Platform

**Placeholder Replacements**:
```
[RESOURCE_COLLECTION] → Workspace
[RESOURCE_ITEM] → Project / Task
[RESOURCE_ACTION] → Create Project
[EXTERNAL_DATA_PROVIDER] → Slack Integration
[CALCULATION_ENGINE] → Time Tracking Engine
[USER_ROLE] → Workspace Admin / Member
[TRANSACTION] → API Call
[CONSTRAINT] → User Seat Limit
[REGULATORY_REQUIREMENT] → SOC2 CC6.1 (Access Control)
```

**Key Requirements**:
- REQ-001: Multi-tenant workspace isolation
- REQ-002: Role-based access control (Admin, Member, Guest)
- REQ-003: Real-time collaboration (WebSocket)
- REQ-004: Third-party integrations (Slack, Jira, GitHub)
- REQ-005: Usage analytics and billing

### Use Case 2: API-First CRM Platform

**Placeholder Replacements**:
```
[RESOURCE_COLLECTION] → Account
[RESOURCE_ITEM] → Contact / Lead
[RESOURCE_ACTION] → API Request
[EXTERNAL_DATA_PROVIDER] → Email Service Provider
[CALCULATION_ENGINE] → Lead Scoring Engine
[USER_ROLE] → Sales Rep / Manager
[TRANSACTION] → API Call
[CONSTRAINT] → API Rate Limit
[REGULATORY_REQUIREMENT] → GDPR Article 17 (Right to Erasure)
```

**Key Requirements**:
- REQ-010: RESTful API with OpenAPI specification
- REQ-011: Webhook support for events
- REQ-012: API rate limiting (per tenant)
- REQ-013: GDPR-compliant data export/deletion
- REQ-014: OAuth 2.0 authentication

---

## AI Assistant Application Guidance

### When to Use This Configuration

Apply SOFTWARE_DOMAIN_CONFIG.md when:
- User selects "Software/SaaS" in domain questionnaire
- User says "saas", "software", "api platform", "multi-tenant"
- Project involves subscription billing or workspace features

### Application Sequence

1. Load SOFTWARE_DOMAIN_CONFIG.md
2. Create subdirectories: tenant/, subscription/, billing/, workspace/
3. Apply placeholder replacements
4. Include SOC2/GDPR compliance references
5. Use API-first examples in templates

### Validation Checklist

- [ ] `docs/REQ/tenant/` directory exists
- [ ] `docs/REQ/subscription/` directory exists
- [ ] `docs/REQ/billing/` directory exists
- [ ] `docs/REQ/workspace/` directory exists
- [ ] Placeholder `[RESOURCE_COLLECTION]` replaced with "Workspace"
- [ ] Placeholder `[USER_ROLE]` replaced with "Account Admin"
- [ ] SOC2 controls referenced in compliance requirements
- [ ] API terminology used (REST, GraphQL, webhook)

---

## References

- [AI_ASSISTANT_RULES.md](./AI_ASSISTANT_RULES.md#rule-3-domain-configuration-application)
- [DOMAIN_SELECTION_QUESTIONNAIRE.md](./DOMAIN_SELECTION_QUESTIONNAIRE.md#2-softwaresaas)
- [FINANCIAL_DOMAIN_CONFIG.md](./FINANCIAL_DOMAIN_CONFIG.md) - Alternative domain
- [GENERIC_DOMAIN_CONFIG.md](./GENERIC_DOMAIN_CONFIG.md) - Fallback domain

---

**End of Software/SaaS Domain Configuration**
