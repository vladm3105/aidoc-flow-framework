---
title: "Domain Adaptation Guide"
tags:
  - framework-guide
  - domain-customization
  - shared-architecture
custom_fields:
  document_type: guide
  priority: shared
  development_status: active
---

# Domain Adaptation Guide

**Version**: 1.0
**Last Updated**: 2025-11-05
**Purpose**: Guide for adapting the AI Dev Flow framework to specific project domains

---

## Overview

The AI Dev Flow framework is domain-agnostic and designed for reuse across any software development project. This guide provides checklists and guidance for adapting the framework templates to specific domains.

**Framework Strengths**:
- 15-layer architecture (12 documentation artifacts + 3 execution layers) from business requirements to production code
- Complete traceability through the entire development lifecycle
- AI-friendly YAML specifications for code generation
- Dual-file contracts (.md + .yaml) for human and machine consumption
- Separation of concerns: WHAT (requirements) vs HOW (specifications) vs WHO/WHEN (implementation plans)

---

## General Adaptation Process

### Step 1: Understand Your Domain
1. **Identify domain terminology**: List key concepts, entities, operations
2. **Map regulatory requirements**: Identify applicable standards (GDPR, HIPAA, SOC2, etc.)
3. **Define data classification**: Determine sensitivity levels (public, internal, confidential, restricted)
4. **List external integrations**: Third-party services, APIs, data providers

### Step 2: Replace Placeholders
1. **Copy templates** from `ai_dev_flow/` to your project's `docs/` folder
2. **Search for [PLACEHOLDERS]** - all framework placeholders use `[UPPERCASE_BRACKET]` format
3. **Replace with domain-specific values** - use your terminology consistently
4. **Update descriptions** - customize example descriptions to match your domain

### Step 3: Customize Document Structure
1. **Add domain-specific sections** as needed
2. **Remove irrelevant sections** (e.g., if not using certain patterns)
3. **Adjust complexity ratings** based on your team's expertise
4. **Tailor examples** to reflect actual use cases

### Step 4: Establish Naming Conventions
1. **Define ID prefixes**: Choose consistent prefixes (REQ-, ADR-, BDD-, etc.)
2. **Organize by domain**: Create subdirectories in `07_REQ/` (e.g., `07_REQ/auth/`, `07_REQ/billing/`)
3. **Document standards**: Update `ID_NAMING_STANDARDS.md` for your project

---

## Domain-Specific Checklists

### Financial Services (Trading, Banking, Insurance)

**Regulatory Landscape**:
- regulatory (regulatoryurities), compliance (provider-dealers), SOX (Financial reporting)
- Basel III (Banking capital), Dodd-Frank (Financial reform)
- PCI-DSS (Card payments), AML (Anti-money laundering)

**Key Terminology**:
- **Replace**: `[EXTERNAL_DATA_PROVIDER]` → Market data vendors (Bloomberg, Reuters, Alpha Vantage)
- **Replace**: `[RESOURCE_COLLECTION]` → collection, account, position
- **Replace**: `[OPERATION_EXECUTION]` → operation execution, order management
- **Replace**: `[METRICS]` → Greeks (Delta, Gamma, Theta, Vega), VaR, Sharpe ratio
- **Replace**: `[SAFETY_MECHANISM]` → Circuit breakers, position limits, risk budgets

**Data Classification**:
- Restricted: Customer PII, account numbers, transaction history
- Confidential: Trading strategies, proprietary algorithms
- Internal: Risk reports, compliance audits
- Public: Market data (if licensed for redistribution)

**Critical Requirements**:
- Real-time risk management
- Audit trail (immutable, 7-year retention)
- Pre-trade compliance checks
- Market data licensing compliance
- Disaster recovery (RTO < 4 hours, RPO < 1 hour)

**Architecture Patterns**:
- Event sourcing for audit trail
- CQRS for read-heavy analytics
- Circuit breakers for market volatility
- Multi-region deployment for disaster recovery

---

### Healthcare (EMR, Telemedicine, Medical Devices)

**Regulatory Landscape**:
- HIPAA (Privacy and security Rules)
- FDA (Medical device approval)
- HITECH (Electronic health records)
- 21 CFR Part 11 (Electronic records/signatures)

**Key Terminology**:
- **Replace**: `[ENTITY_IDENTIFIER]` → Patient ID (de-identified), MRN (Medical Record Number)
- **Replace**: `[EXTERNAL_DATA_PROVIDER]` → HL7/FHIR data sources, pharmacy databases
- **Replace**: `[RESOURCE_COLLECTION]` → Patient records, provider schedules
- **Replace**: `[OPERATION_EXECUTION]` → Prescription fulfillment, lab order processing
- **Replace**: `[METRICS]` → Clinical quality measures, patient outcomes, device telemetry

**Data Classification**:
- Restricted: PHI (Protected Health Information), ePHI (electronic PHI)
- Confidential: Provider credentials, treatment protocols
- Internal: Operational metrics, billing codes
- Public: General health education content

**Critical Requirements**:
- HIPAA compliance (encryption at rest/in transit, access controls, audit logging)
- Patient consent management
- Data de-identification for research
- Medical device integration (FDA validated interfaces)
- Disaster recovery with zero data loss (RPO = 0)

**Architecture Patterns**:
- Zero-trust security model
- Data segregation by patient
- Immutable audit logs
- Geographic data residency (state/country-specific)

---

### E-commerce (Retail, Marketplace, Subscription)

**Regulatory Landscape**:
- PCI-DSS (Card payments)
- GDPR/CCPA (Privacy)
- Consumer protection laws (FTC, state-specific)
- Accessibility standards (ADA, WCAG 2.1)

**Key Terminology**:
- **Replace**: `[ENTITY_IDENTIFIER]` → Product SKU, Order ID, Customer ID
- **Replace**: `[RESOURCE_COLLECTION]` → Shopping cart, product catalog, inventory
- **Replace**: `[OPERATION_EXECUTION]` → Order fulfillment, payment processing
- **Replace**: `[EXTERNAL_DATA_PROVIDER]` → Payment gateways (Stripe, PayPal), shipping APIs (FedEx, UPS)
- **Replace**: `[METRICS]` → Conversion rate, cart abandonment, AOV (average order value)

**Data Classification**:
- Restricted: Payment card data (PAN, CVV), customer PII
- Confidential: Pricing algorithms, supplier agreements
- Internal: Inventory levels, order volumes
- Public: Product catalogs, marketing content

**Critical Requirements**:
- PCI-DSS compliance (never store CVV, tokenize PANs)
- GDPR right to deletion
- Real-time inventory synchronization
- Fraud detection
- High availability (99.99% uptime for checkout)

**Architecture Patterns**:
- Microservices for scalability (catalog, cart, checkout, fulfillment)
- CDN for product images
- Redis for session management
- Message queues for order processing

---

### SaaS (B2B, B2C, Platform)

**Regulatory Landscape**:
- SOC2 (Service Organization Control)
- GDPR/CCPA (Privacy)
- ISO 27001 (Information security)
- Data residency requirements (region-specific)

**Key Terminology**:
- **Replace**: `[ENTITY_IDENTIFIER]` → Tenant ID, User ID, Workspace ID
- **Replace**: `[RESOURCE_COLLECTION]` → User accounts, subscriptions, workspaces
- **Replace**: `[OPERATION_EXECUTION]` → Provisioning, billing, user onboarding
- **Replace**: `[EXTERNAL_DATA_PROVIDER]` → Authentication providers (Okta, Auth0), payment processors
- **Replace**: `[METRICS]` → MRR (monthly recurring revenue), churn rate, DAU/MAU

**Data Classification**:
- Restricted: Customer data (tenant-specific), authentication credentials
- Confidential: Pricing tiers, feature flags
- Internal: Usage metrics, support tickets
- Public: Marketing materials, product documentation

**Critical Requirements**:
- Multi-tenancy with data isolation
- SOC2 compliance (access controls, encryption, monitoring)
- SLA guarantees (uptime, response time)
- Subscription billing automation
- Usage metering and quotas

**Architecture Patterns**:
- Multi-tenant database design (shared schema with tenant_id, or database-per-tenant)
- API rate limiting per tenant
- Feature flags for gradual rollouts
- Observability (per-tenant metrics)

---

### IoT (Devices, Sensors, Industrial)

**Regulatory Landscape**:
- FCC (Radio frequency), CE (European conformity)
- UL/IEC (Safety standards)
- Industry-specific (FDA for medical devices, DOT for automotive)
- GDPR/CCPA (if collecting personal data)

**Key Terminology**:
- **Replace**: `[ENTITY_IDENTIFIER]` → Device ID, Serial number, MAC address
- **Replace**: `[RESOURCE_COLLECTION]` → Device fleet, sensor network
- **Replace**: `[OPERATION_EXECUTION]` → Firmware update, command dispatch, data ingestion
- **Replace**: `[EXTERNAL_DATA_PROVIDER]` → Cloud platforms (AWS IoT, Azure IoT Hub), weather services
- **Replace**: `[METRICS]` → Telemetry (temperature, pressure, voltage), uptime, battery level

**Data Classification**:
- Restricted: Location data (if tracking individuals), biometric data
- Confidential: Device firmware, encryption keys
- Internal: Diagnostic logs, performance metrics
- Public: Product specifications, API documentation

**Critical Requirements**:
- Device authentication (mutual TLS, certificates)
- Over-the-air (OTA) firmware updates
- Command & control security
- Edge processing for low-latency
- Offline operation capability

**Architecture Patterns**:
- Edge computing (process data locally)
- Pub/Sub messaging (MQTT, CoAP)
- Digital twins (cloud representation of physical devices)
- Time-series database for telemetry

---

### Generic Software (Internal Tools, Utilities)

**Regulatory Landscape**:
- Minimal external regulations
- Company internal policies
- Industry best practices (OWASP, CWE)

**Key Terminology**:
- **Replace**: `[ENTITY_IDENTIFIER]` → Record ID, Entity reference
- **Replace**: `[RESOURCE_COLLECTION]` → Data sets, entities
- **Replace**: `[OPERATION_EXECUTION]` → Batch processing, workflow execution
- **Replace**: `[EXTERNAL_DATA_PROVIDER]` → Internal APIs, databases
- **Replace**: `[METRICS]` → Performance metrics, success rates

**Data Classification**:
- Internal: Most data (company confidential by default)
- Confidential: Employee PII, financial data
- Public: External-facing documentation

**Critical Requirements**:
- User authentication and authorization
- Audit logging for sensitive operations
- Data backup and recovery
- Reasonable performance (no strict SLAs)

**Architecture Patterns**:
- Monolith or simple microservices
- Standard CRUD operations
- Relational database (PostgreSQL, MySQL)
- Simple deployment (Docker, single server)

---

## Customization Worksheet

Use this worksheet to plan your adaptation:

### 1. Domain Identification
```
Domain Name: _______________________
Primary Use Cases:
  - ________________________________
  - ________________________________
  - ________________________________
```

### 2. Regulatory Requirements
```
Applicable Standards:
  [ ] GDPR/CCPA (Privacy)
  [ ] SOC2 (security controls)
  [ ] HIPAA (Healthcare)
  [ ] PCI-DSS (Payments)
  [ ] ISO 27001 (Inforegulatory)
  [ ] FedRAMP (Government cloud)
  [ ] Other: ____________________
```

### 3. Data Classification Scheme
```
| Classification | Definition | Examples | Retention |
|----------------|------------|----------|-----------|
| Restricted     |            |          |           |
| Confidential   |            |          |           |
| Internal       |            |          |           |
| Public         |            |          |           |
```

### 4. Key Entities
```
Primary Entities (nouns in your domain):
  1. ______________________ (e.g., User, Product, Device)
  2. ______________________
  3. ______________________

Primary Operations (verbs in your domain):
  1. ______________________ (e.g., Purchase, Register, Monitor)
  2. ______________________
  3. ______________________
```

### 5. External Integrations
```
Critical External Services:
  - Service: ______________ Purpose: ________________
  - Service: ______________ Purpose: ________________
  - Service: ______________ Purpose: ________________
```

### 6. Performance Requirements
```
SLA Targets:
  - Availability: _________% uptime
  - Latency: p95 < _________ ms
  - Throughput: __________ requests/second
  - Data Recovery: RTO = _______, RPO = _______
```

---

## Template Mapping Guide

### Requirements (REQ)
- **Financial**: Risk limits, trading rules, market data feeds
- **Healthcare**: Clinical workflows, patient consent, PHI access control
- **E-commerce**: Payment processing, inventory sync, fraud detection
- **SaaS**: Multi-tenancy, subscription billing, usage metering
- **IoT**: Device provisioning, telemetry ingestion, OTA updates
- **Generic**: CRUD operations, user management, reporting

### Architecture Decisions (ADR)
- **Financial**: Event sourcing (audit trail), circuit breakers (market volatility)
- **Healthcare**: Zero-trust security, data de-identification
- **E-commerce**: Microservices (scalability), CDN (performance)
- **SaaS**: Multi-tenant database design, API rate limiting
- **IoT**: Edge computing, pub/sub messaging
- **Generic**: Database choice, authentication method

### BDD Scenarios (BDD)
- **Financial**: "GIVEN market volatility > threshold WHEN circuit breaker triggers..."
- **Healthcare**: "GIVEN patient consent WHEN provider accesses PHI..."
- **E-commerce**: "GIVEN item in cart WHEN payment processed..."
- **SaaS**: "GIVEN tenant quota exceeded WHEN new request arrives..."
- **IoT**: "GIVEN device offline WHEN command dispatched..."
- **Generic**: "GIVEN valid credentials WHEN user logs in..."

### Implementation Plans (IMPL)
- **Financial**: Phased rollout with paper trading → live trading
- **Healthcare**: HIPAA compliance validation, PHI encryption
- **E-commerce**: PCI-DSS certification, load testing for Black Friday
- **SaaS**: Multi-tenant migration, zero-downtime deployment
- **IoT**: OTA update strategy, fleet-wide rollout
- **Generic**: Standard agile sprints, feature flags

### TASKS Execution Commands by Domain

TASKS Section 4 contains session-based execution commands. Customize for domain-specific workflows:

#### Financial Services
- **Focus**: Trading system execution, market data integration
- **Bash commands**: Database migrations for time-series data, API deployments
- **Compliance**: Include audit trail commands, regulatory checkpoint verification

#### Healthcare
- **Focus**: HIPAA compliance, PHI data handling
- **Bash commands**: Encrypted backup procedures, access logging
- **Compliance**: Include data retention commands, audit log generation

#### E-commerce
- **Focus**: Deployment and scaling, inventory management
- **Bash commands**: Blue-green deployment scripts, cache invalidation
- **Performance**: Include load testing commands, monitoring setup

#### SaaS
- **Focus**: Multi-tenant rollout, feature flags
- **Bash commands**: Tenant provisioning, configuration management
- **Scaling**: Include database sharding, service replication

---

## Common Pitfalls

### 1. Inconsistent Terminology
**Problem**: Using both domain-specific and generic terms interchangeably
**Solution**: Create a glossary and stick to it consistently across all documents

### 2. Over-Engineering for Simple Projects
**Problem**: Using all 10 layers for a simple CRUD application
**Solution**: Start with core layers (REQ, SPEC, code), add others as complexity grows

### 3. Ignoring Traceability
**Problem**: Not linking requirements → ADRs → SPEC → code
**Solution**: Use the traceability matrix, validate links with scripts

### 4. Placeholder Overload
**Problem**: Too many nested placeholders: `[COMPONENT_[SUBTYPE]]`
**Solution**: Flatten placeholders, use clear single-level naming

### 5. Skipping Domain Expertise
**Problem**: Applying framework without understanding domain requirements
**Solution**: Involve domain experts early, iterate on terminology

---

## Next Steps

1. **Review your domain**: Identify regulatory requirements, key entities, external integrations
2. **Complete the worksheet**: Document your domain-specific decisions
3. **Customize templates**: Replace placeholders with your terminology
4. **Validate traceability**: Ensure all documents link correctly
5. **Train your team**: Share the adapted framework, explain customizations
6. **Iterate**: Refine based on feedback, update templates as needed

---

## Additional Resources

- **OWASP Application security**: https://owasp.org/
- **NIST Cybersecurity Framework**: https://www.nist.gov/cyberframework
- **Regulatory Compliance Guides**:
  - GDPR: https://gdpr.eu/
  - HIPAA: https://www.hhs.gov/hipaa/
  - PCI-DSS: https://www.pcisecuritystandards.org/
  - SOC2: https://www.aicpa.org/soc-for-cybersecurity

---

**Document Control**:
- **Version**: 1.0
- **Last Updated**: 2025-11-05
- **Maintainer**: Framework Steward
- **Feedback**: Submit issues via project repository
