---
title: "SPEC Creation Rules"
tags:
  - creation-rules
  - layer-10-artifact
  - shared-architecture
custom_fields:
  document_type: creation-rules
  artifact_type: SPEC
  layer: 10
  priority: shared
  development_status: active
---

> **📋 Document Role**: This is a **CREATION HELPER** for SPEC-TEMPLATE.md/.yaml.
> - **Authority**: `SPEC-TEMPLATE.yaml` is the primary source of truth for SPEC structure
> - **Validation**: Use `SPEC_VALIDATION_RULES.md` after SPEC creation/changes

# SPEC Creation Rules

**Version**: 1.0
**Date**: 2025-11-19
**Last Updated**: 2025-11-19
**Source**: Derived from SPEC-TEMPLATE.yaml and technical specification patterns
**Purpose**: Complete reference for creating SPEC YAML files according to doc_flow SDD framework
**Changes**: Added TASKS-ready scoring system for SPEC documents

---

## Table of Contents

1. [File Organization and Directory Structure](#1-file-organization-and-directory-structure)
2. [Document Structure (YAML Specification)](#2-document-structure-yaml-specification)
3. [Document Control and Metadata](#3-document-control-and-metadata)
4. [ID and Naming Standards](#4-id-and-naming-standards)
5. [Technical Specification Categories](#5-technical-specification-categories)
6. [TASKS Relationship Guidelines](#6-tasks-relationship-guidelines)
7. [TASKS-Ready Scoring System](#7-tasks-ready-scoring-system)
8. [Traceability Requirements](#8-traceability-requirements)
9. [Quality Attributes](#9-quality-attributes)
10. [Quality Gates](#10-quality-gates)
11. [Additional Requirements](#11-additional-requirements)

---

## 1. File Organization and Directory Structure

- **Location**: `docs/SPEC/` within project docs directory
- **Naming**: `SPEC-NNN_descriptive_component_name.yaml` (NNN = 3-digit sequential)
- **Structure**: One primary SPEC file per architectural component

---

## 2. Document Structure (YAML Specification)

**Complete YAML structure with 7 major sections:**

```yaml
# Header section with required metadata
id: component_name
summary: Single-sentence description

# Metadata with TASKS-ready scoring
metadata:
  version: "1.0.0"
  status: "draft"
  task_ready_score: ✅ 95% (Target: ≥90%)  # Added for quality gates

# Complete traceability chain
traceability:
  upstream_sources: [...]
  downstream_artifacts: [...]
  cumulative_tags: [...]

# Architecture definition
architecture: [...]

# Interface definitions (CTR references)
interfaces: [...]

# Behavioral specifications
behavior: [...]

# Quality attributes (caching, rate limiting, circuit breaker)
# Performance specifications
performance: [...]

# security specifications
security: [...]

# Observability specifications
observability: [...]

# Verification and validation
verification: [...]

# Implementation specifics
implementation: [...]

# Operational runbook
operations: [...]
```

---

## 3. Document Control and Metadata

**Required Metadata Fields**:
- version, status, created_date, authors, reviewers
- TASKS-ready score (⭐ NEW) format: `✅ NN% (Target: ≥90%)`

**Authors and Reviewers**:
- authors: Technical implementers
- reviewers: Architecture leads, senior engineers

---

## 4. ID and Naming Standards

- **Filename**: `SPEC-NNN_descriptive_component_name.yaml`
- **id field**: `component_name` (snake_case, unique)
- **Versioning**: Semantic versioning (1.0.0)

---

## 5. Technical Specification Categories

**Component Types**:
- **API Services**: REST, GraphQL interfaces
- **Data Processors**: ETL, stream processing
- **Integration Adapters**: Third-party service connectors
- **Supporting Services**: Caching, messaging, configuration

**Specification Categories**:
- **Functional Specs**: Request/response workflows
- **Performance Specs**: Latency, throughput targets
- **security Specs**: Authentication, authorization
- **Operational Specs**: Monitoring, deployment, scaling

---

## 6. TASKS Relationship Guidelines

**SPEC → TASKS Workflow**:
- SPECs define technical HOW (implementation blueprints)
- TASKS provide AI-assisted coding instructions using SPEC definitions
- Code generation tools consume SPEC YAML directly

**TASKS Implementation Requirements**:
- All SPEC sections must be translatable to TASKS tasks
- Interface definitions must enable API contract generation
- Behavior sections must enable method implementation planning

---

## 7. TASKS-Ready Scoring System ⭐ NEW

### Overview
TASKS-ready scoring measures SPEC maturity and readiness for progression to TASKS implementation planning.

**Format**: `✅ NN% (Target: ≥90%)`
**Location**: metadata.task_ready_score field
**Validation**: Enforced before TASKS creation

### Scoring Criteria

**YAML Completeness (25%)**:
- All required metadata fields present: 10%
- Complete traceability chain defined: 10%
- All specification sections populated: 5%

**Interface Definitions (25%)**:
- External APIs fully specified with contracts: 15%
- Internal interfaces documented: 5%
- Data schemas and types defined: 5%

**Implementation Specifications (25%)**:
- Behavior sections enable code generation: 15%
- Performance/security targets quantifiable: 5%
- Dependencies and configuration specified: 5%

**Code Generation Readiness (25%)**:
- All fields machine-readable and parseable: 15%
- TASKS-ready tags and metadata included: 5%
- Validation schemas complete: 5%

### Quality Gate Enforcement
- Score <90% prevents TASKS artifact creation
- Format validation requires ✅ emoji and percentage
- YAML syntax must be valid for TASKS parsing

---

## 8. Traceability Requirements (MANDATORY - Layer 10)

**Complete Upstream Tag Chain**:
```yaml
cumulative_tags:
  brd: "BRD-NNN:REQUIREMENT-ID"
  prd: "PRD-NNN:REQUIREMENT-ID"
  ears: "EARS-NNN:STATEMENT-ID"
  bdd: "BDD-NNN:SCENARIO-ID"
  adr: "ADR-NNN"
  sys: "SYS-NNN:regulatoryTION-ID"
  req: "REQ-NNN:REQUIREMENT-ID"
```

**Layer 10 Requirements**: SPEC must reference ALL previous artifacts

---

## 9. Quality Attributes

**Machine-Readable**: All specifications parseable by code generation tools

**Implementation-Complete**: Sufficient detail for autonomous development

**Interface-First**: API contracts separated but referenced

**Test-Driving**: Specifications enable comprehensive testing strategies

---

## 10. Quality Gates (Pre-Commit Validation)

- YAML syntax validation
- TASKS-ready score verification ≥90%
- Traceability completeness
- Interface contract references validation

---

## 11. Additional Requirements

- Contract separation: CTR files for interface specifications
- Implementation-path metadata for code generation
- Configuration schemas for deployment automation
- Performance benchmarks for operational monitoring

---

**Framework Compliance**: 100% doc_flow SDD framework (Layer 10)
**Integration**: Enforces SPEC → TASKS progression quality gates


## 12. Upstream Artifact Verification Process

### Before Creating This Document

**Step 1: Inventory Existing Upstream Artifacts**

```bash
# List existing upstream artifacts for this layer
ls -la docs/BRD/    # Layer 1
ls -la docs/PRD/    # Layer 2
ls -la docs/EARS/   # Layer 3
ls -la docs/BDD/    # Layer 4
ls -la docs/ADR/    # Layer 5
ls -la docs/SYS/    # Layer 6
ls -la docs/REQ/    # Layer 7
# ... continue for applicable layers
```

**Step 2: Map Existing Documents to Traceability Tags**

| Tag | Required for This Layer | Existing Document | Action |
|-----|------------------------|-------------------|--------|
| @brd | Yes/No | BRD-001 or null | Reference/Create/Skip |
| @prd | Yes/No | PRD-001 or null | Reference/Create/Skip |
| ... | ... | ... | ... |

**Step 3: Decision Rules**

| Situation | Action |
|-----------|--------|
| Upstream exists | Reference with exact document ID |
| Upstream required but missing | Skip that functionality - do NOT implement |
| Upstream optional and missing | Use `null` in traceability tag |
| Upstream not applicable | Omit tag entirely |

### Traceability Tag Rules

- **NEVER** use placeholder IDs like `BRD-XXX` or `TBD`
- **NEVER** reference documents that don't exist
- **ALWAYS** verify document exists before adding reference
- **USE** `null` only when artifact type is genuinely not applicable
