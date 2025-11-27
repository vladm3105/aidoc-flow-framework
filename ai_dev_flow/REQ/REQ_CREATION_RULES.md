---
title: "REQ Creation Rules"
tags:
  - creation-rules
  - layer-7-artifact
  - shared-architecture
custom_fields:
  document_type: creation-rules
  artifact_type: REQ
  layer: 7
  priority: shared
  development_status: active
---

# REQ Creation Rules

**Version**: 3.0
**Date**: 2025-11-19
**Source**: Extracted from REQ-TEMPLATE.md, REQ-VALIDATION-RULES.md, README.md, and REQ-000_index.md
**Purpose**: Complete reference for creating REQ files according to doc-flow SDD framework

---

## Table of Contents

1. [File Organization and Directory Structure](#1-file-organization-and-directory-structure)
2. [Document Structure (12 Required sections)](#2-document-structure-12-required-sections)
3. [Document Control Requirements](#3-document-control-requirements)
4. [ID and Naming Standards](#4-id-and-naming-standards)
5. [Atomic Requirement Principles](#5-atomic-requirement-principles)
6. [Traceability Requirements](#6-traceability-requirements)
7. [Interface and Implementation Specifications](#7-interface-and-implementation-specifications)
8. [Acceptance Criteria Standards](#8-acceptance-criteria-standards)
9. [Quality Gates](#9-quality-gates)
10. [Business Rules and Validation](#10-business-rules-and-validation)
11. [Additional Requirements](#11-additional-requirements)

---

## 1. File Organization and Directory Structure

- **Location**: `REQ/{domain}/{subdomain}/` within project docs directory
- **Domains**: `api/` (external integrations), `risk/` (risk management), `data/` (data requirements), `ml/` (ML requirements), `auth/` (security), etc.
- **Naming**: `REQ-NNN_descriptive_slug.md` (NNN = 3-digit sequential number, lowercase snake_case slug)
- **Subdocuments**: For complex requirements: `REQ-NNN-YY_additional_detail.md` (YY = 2-digit sub-number)

---

## 2. Document Structure (12 Required sections)

Every REQ must contain these exact sections in order:

1. **Document Control** - Metadata table with 11 required fields
2. **Description** - Atomic requirement + SHALL/SHOULD/MAY language + context + scenario
3. **Functional Requirements** - Core capabilities + business rules
4. **Interface Specifications** - Protocol/ABC definitions + DTOs + REST endpoints (if applicable)
5. **Data Schemas** - JSON Schema + Pydantic models + Database schema (if applicable)
6. **Error Handling Specifications** - Exception catalog + error response schema + state machine + circuit breaker config
7. **Configuration Specifications** - YAML schema + environment variables + validation
8. **Non-Functional Requirements (NFRs)** - Performance targets (p50/p95/p99) + reliability/security/scalability/observability
9. **Implementation Guidance** - Algorithms/patterns + concurrency/async + dependency injection
10. **Acceptance Criteria** - ≥15 measurable criteria covering functional/error/quality/data/integration
11. **Verification Methods** - BDD scenarios + unit/integration/contract/performance tests
12. **Change History** - Version control table

---

## 3. Document Control Requirements (11 Mandatory Fields)

- Status, Version (semantic X.Y.Z), Date Created (ISO 8601), Last Updated
- Author, Priority (with P-level: P1/P2/P3/P4), Category (Functional/Non-Functional/etc.)
- Source Document (format: "DOC-ID section X.Y.Z"), Verification Method, Assigned Team
- SPEC-Ready Score (format: "✅ XX% (Target: ≥90%)"), IMPL-Ready Score (format: "✅ XX% (Target: ≥90%)"), Template Version (must be "3.0")

---

## 4. ID and Naming Standards

- **Filename**: `REQ-NNN_slug.md` (e.g., `REQ-003_resource_limit_enforcement.md`)
- **H1 Header**: `# REQ-NNN: [RESOURCE_INSTANCE] Title` (Template V2+) - includes resource classification tag
- **Template Version**: Must use 3.0 (current) - not legacy V1 or V2
- **Uniqueness**: Each NNN number used once (either single REQ-NNN or REQ-NNN-YY group)

---

## 5. Atomic Requirement Principles

- **Single Responsibility**: Each REQ defines exactly one requirement
- **Measurable**: Acceptance criteria provide true/false outcomes
- **Self-Contained**: Understandable without external context
- **SPEC-Ready**: Contains ALL information for automated SPEC generation (≥90% completeness)
- **Modal Language**: SHALL (absolute), SHOULD (preferred), MAY (optional)

---

## 6. Traceability Requirements (MANDATORY - Layer 7)

- **Upstream Chain**: Must reference ALL 6 artifact types: BRD, PRD, EARS, BDD, ADR, SYS
- **Cumulative Tagging**: All 6 tags required with format `@type: DOC-ID:REQ-ID`
- **Downstream Links**: SPEC, TASKS, CTR (if applicable), BDD scenarios
- **Code Paths**: Actual file paths for implementation

---

## 7. Interface and Implementation Specifications

- **Protocol/ABC**: Complete class definitions with type annotations
- **DTOs**: Data transfer objects with validation
- **REST Endpoints**: Rate limits, schemas for request/response (if applicable)
- **Error Handling**: Catalog with retry strategies, state diagrams, circuit breaker
- **Schemas**: JSON Schema + Pydantic validators + Database constraints
- **Configuration**: YAML examples + environment variables + validation
- **NFR Metrics**: Performance (p50/p95/p99), reliability, security, scalability targets

---

## 8. Acceptance Criteria Standards

- **≥15 Criteria**: Covering functional, error, edge case, quality, data, integration scenarios
- **Measurable**: Specific thresholds, pass criteria, verification methods
- **Testable**: BDD scenarios, unit/integration tests, performance benchmarks
- **Comprehensive**: Success paths, failure modes, resource limits, error recovery

---

## 9. Quality Gates (Pre-Commit Validation)

- **18 Validation Checks**: Run `./scripts/validate_req_template_v3.sh filename.md`
- **Blockers**: Missing sections, format errors, broken links, incomplete traceability
- **Warnings**: Missing resource tags, low SPEC-Ready score, incomplete upstream chain
- **SPEC-Ready Threshold**: ≥90% or reduce claimed score
- **Link Resolution**: All cross-references must resolve to existing files

---

## 10. Business Rules and Validation

- **Source Documents**: Link to specific strategy sections (BRD/PRD)
- **Original Context**: Describe why requirement exists and business justification
- **Verification Methods**: Unit/concept/integration/performance/contract tests
- **Error Recovery**: Dataclass configuration for circuit breakers and retry logic
- **Observability**: Metrics, logging, tracing, alerting requirements

---

## 11. Additional Requirements

- **Dependency Injection**: Container setup with providers for modular design
- **Database Integration**: SQLAlchemy models with constraints and migrations (if applicable)
- **Concurrent Patterns**: Async handling with semaphore and task management
- **security Requirements**: Authentication, data encryption, audit logging
- **Resource Tags**: Classify by component type (e.g., [EXTERNAL_SERVICE_GATEWAY])

---

## Quick Reference

**Pre-Commit Validation**:
```bash
# Validate single file
./scripts/validate_req_template_v3.sh filename.md

# Validate all REQ files
find docs/REQ -name "REQ-*.md" -exec ./scripts/validate_req_template_v3.sh {} \;
```

**Template Location**: [REQ-TEMPLATE.md](REQ-TEMPLATE.md)
**Validation Rules**: [REQ-VALIDATION-RULES.md](REQ-VALIDATION-RULES.md)
**Index**: [REQ-000_index.md](REQ-000_index.md)

---

**Framework Compliance**: 100% doc_flow SDD framework aligned (Layer 7 - Requirements)
**Maintained By**: System Architect, Quality Assurance Team
**Review Frequency**: Updated with template and validation rule changes

---
