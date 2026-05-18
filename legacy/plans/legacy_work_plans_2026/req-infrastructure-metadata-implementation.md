# Implementation Plan: Add Infrastructure Metadata to REQ Layer

**Date**: 2026-01-19
**Status**: Complete
**Priority**: High
**Architectural Impact**: Supports SYS → SPEC → Code/Config/IaC generation workflow

---

## Context and Background

### Architectural Principle
Deployment infrastructure belongs at **system level (SYS - Layer 6)**, not at atomic requirement level (REQ - Layer 7).

### Completed Work
✅ SYS layer updated with deployment infrastructure sections:
   - SYS-MVP-TEMPLATE.md - Section 9.1 (8 subsections) with Applicability template
   - SYS-MVP-TEMPLATE.md - Section 9.2 (3 subsections) with Applicability template
   - SYS_MVP_VALIDATION_RULES.md - CHECK 10 (Section 9.1) and CHECK 11 (Section 9.2)
   - SYS_MVP_CREATION_RULES.md - Guidance for 9.1 and 9.2
   - SYS-DEPLOYMENT_EXAMPLE.md - Full infrastructure example
   - SYS-LOGIC-ONLY_EXAMPLE.md - Pure logic example (no infrastructure)

### Current Gap
REQ layer needs to support infrastructure-related requirements that:
1. Derive from SYS Section 9.1/9.2 infrastructure/operational requirements
2. Provide metadata for SPEC generation
3. Enable Autopilot to create deployment artifacts (scripts, playbooks, IaC templates)
4. Maintain traceability from REQ → SYS → SPEC → Generated Artifacts

---

## Files to Modify

### 1. REQ-MVP-TEMPLATE.md
**Purpose**: Add metadata fields and infrastructure guidance to support REQ → SPEC → Code/Config/IaC generation

**Changes**:

#### Change 1.1: Add infrastructure_type to Document Control
- **Location**: After Document Control table (after line ~50)
- **Add**:
  ```markdown
  | **Infrastructure Type** | Compute | Database | Storage | Network | Cache | Messaging | Deployment_Automation | Observability | Security | Cost | None |
  ```
- **Purpose**: Tag infrastructure-related REQs for SPEC generation

#### Change 1.2: Update Section 10.3 Traceability Tags
- **Location**: Update existing traceability tags section
- **Add**: Infrastructure-specific traceability patterns:
  - `@sys: SYS.NN.09.01.X` - Reference specific SYS infrastructure subsection
  - `@iac: terraform/` / `@ansible: ansible/` - IaC tool tags
  - `@deployment: scripts/` - Deployment artifact tags
  - `@config_file_type: shell` - Configuration file type tag
  - `@source_code: https://github.com/org/repo` - Generated code repository

> **Note**: We will NOT add static "Category Definition" or "Infrastructure Guidance" sections to the Template itself to maintain the "Atomic Requirement" focus. This guidance belongs in `REQ_MVP_CREATION_RULES.md`.

---

### 2. REQ_MVP_SCHEMA.yaml
**Purpose**: Validate metadata fields and traceability tags for infrastructure-related REQs

**Changes**:

#### Change 2.1: Add infrastructure_type to optional_custom_fields
- **Location**: Under `optional_custom_fields` (after line ~82)
- **Add**:
  ```yaml
    infrastructure_type:
      type: string
      allowed_values: ["Compute", "Database", "Storage", "Network", "Cache", "Messaging", "Deployment_Automation", "Observability", "Security", "Cost", "None"]
      description: "Type of infrastructure requirement (from SYS 9.1.x)"
  ```

#### Change 2.2: Add category to optional_custom_fields
- **Location**: Under `optional_custom_fields`
- **Add**:
  ```yaml
    category:
      type: string
      allowed_values: ["Functional", "Logic", "API", "UI", "UX", "Database", "Config", "Infra", "FinOps", "Security", "Performance", "Reliability", "Scalability", "Compliance", "None"]
      description: "Functional category of this requirement"
  ```

#### Change 2.3: Add iac_provider to optional_custom_fields
- **Location**: Under `optional_custom_fields`
- **Add**:
  ```yaml
    iac_provider:
      type: string
      allowed_values: ["terraform", "cloudformation", "ansible", "pulumi", "kubernetes", "helm", "None"]
      description: "IaC provider used for deployment"
  ```

#### Change 2.4: Add config_file_type to optional_custom_fields
- **Location**: Under `optional_custom_fields`
- **Add**:
  ```yaml
    config_file_type:
      type: string
      allowed_values: ["shell", "yaml", "json", "toml", "ini", "None"]
      description: "Configuration file format type for config generation"
  ```

#### Change 2.5: Add shell_scripts_dir to optional_custom_fields
- **Location**: Under `optional_custom_fields`
- **Add**:
  ```yaml
    shell_scripts_dir:
      type: string
      allowed_values: ["scripts/"]
      description: "Directory path for generated shell scripts"
  ```

#### Change 2.6: Add source_code_url to optional_custom_fields
- **Location**: Under `optional_custom_fields`
- **Add**:
  ```yaml
    source_code_url:
      type: string
      format: "url"
      description: "URL to generated source code repository"
  ```

#### Change 2.7: Update required_sections validation
- **Location**: Under `required_sections`
- **Purpose**: Ensure NO new static sections are required (keep strict 12-section structure)
- **Remove**: Ensure checks do not expect Sections 11/12 to contain specific new titles.

#### Change 2.9: Add content validation rules
- **Location**: Under `validation_rules > content`
- **Add**:
  ```yaml
    content:
      - rule: "When infrastructure_type is set, iac_provider must be set or 'None'"
        severity: warning
      - rule: "When infrastructure_type is 'deployment_automation', iac_provider must include 'ansible' or 'terraform'"
        severity: warning
      - rule: "source_code_url must be valid URL format when set"
        severity: error
      - rule: "shell_scripts_dir must be 'scripts/' when deployment artifacts are generated"
        severity: warning
  ```

---

### 3. REQ_MVP_CREATION_RULES.md
**Purpose**: Document how to create infrastructure-related REQs

**Changes**:

#### Change 3.1: Update Section 2: Document Structure
- **Location**: After existing Section 2, before Section 3
- **Add**: Update section list to include Sections 11 and 12

#### Change 3.2: Add Section 7: Document Control Requirements
- **Location**: After Section 6 (Quality Attributes), before Section 7 (Configuration Specifications)
- **Add**: Update section to include category field in Document Control table

#### Change 3.3: Add Section 11: Document Control Categories
- **Location**: After Section 10 (Traceability), before Section 11 (Implementation Notes)
- **Add**: Complete section with:
  - Category definitions (20 categories)
  - Category usage guidelines
  - Category selection examples
  - Relationship to infrastructure_type

#### Change 3.4: Add Section 12: Infrastructure-Related Requirements
- **Location**: After Section 11 (Implementation Notes), before Section 12 (Change History)
- **Add**: Complete section with:
  - Architectural flow: SYS → REQ → SPEC → Code/Config/IaC
  - When to use infrastructure_type metadata
  - Traceability patterns for infrastructure REQs
  - Examples for all 10 infrastructure types
  - REQ creation workflow

---

### 4. REQ_MVP_VALIDATION_RULES.md
**Purpose**: Add validation rules for infrastructure metadata and new sections

**Changes**:

#### Change 4.1: Add CHECK 13: Document Control Category Validation
- **Location**: After CHECK 12, before Error Fix Guide
- **Add**:
  ```markdown
  ### CHECK 13: Document Control Category Validation ⭐ NEW

  **Purpose**: Verify category field in Document Control is set and valid.

  **Validation Rules**:

  1. **Category Present**: Document Control table must include "Category" field

  2. **Valid Category Value**: Category must be one of allowed values

  3. **Category Alignment**: Category value should align with requirement description and scope

  **Type**: Warning

  **Error Messages**:
  - Missing: `⚠️ WARNING: Document Control missing 'Category' field`
  - Invalid: `❌ ERROR: Category '${category}' is not valid. Use one of: compute, storage, network, database, api, security, ui, logic, config, deployment, observability, monitoring, logging, testing, messaging, cache, performance, reliability, scalability, compliance, None`
  ```

#### Change 4.2: Add CHECK 14: Infrastructure Metadata Validation ⭐ NEW
- **Location**: After CHECK 13, before Error Fix Guide
- **Add**:
  ```markdown
  ### CHECK 14: Infrastructure Metadata Validation ⭐ NEW

  **Purpose**: Verify infrastructure-related REQs have proper metadata and traceability tags.

  **Validation Rules**:

  1. **infrastructure_type Set**: If REQ relates to SYS infrastructure requirements, infrastructure_type must be set

  2. **Valid infrastructure_type Value**: Must be one of allowed values (compute, database, storage, network, cache, messaging, deployment_automation, observability, security, cost)

  3. **@sys Tag Format**: Must reference specific SYS subsection: `@sys: SYS.NN.09.01.X` (X = 1-8 for 9.1.x, X = 1-3 for 9.2.x)

  4. **@iac Tag Consistency**: When infrastructure_type requires IaC artifacts:
     - infrastructure_type = compute/database/storage/network/cache/messaging → Must include `@iac: @terraform` or `@iac: @ansible`
     - infrastructure_type = deployment_automation → Must include `@iac: @ansible`
     - infrastructure_type = observability → May include `@iac: @ansible` if scripts generated

  5. **@deployment Tag**: Required when infrastructure_type = deployment_automation or observability → `@deployment: scripts/`

  6. **@config_file_type**: Required when config files generated → `@config_file_type: shell`/`yaml`/`json`/`toml`/`ini`

  7. **@source_code_url**: Optional when code generation required

  8. **category Field**: Must be set for infrastructure-related REQs

  **Type**: Warning

  **Error Messages**:
  - Missing infrastructure_type: `⚠️ WARNING: Infrastructure-related REQ missing infrastructure_type metadata`
  - Invalid infrastructure_type: `❌ ERROR: infrastructure_type '${type}' is not valid`
  - Invalid @sys format: `⚠️ WARNING: @sys tag format invalid. Use: @sys: SYS.NN.09.01.X where X matches SYS subsection number`
  - Missing @iac: `⚠️ WARNING: infrastructure_type '${type}' requires @iac tag (@iac: @terraform or @iac: @ansible)`
  - Extra @iac: `⚠️ WARNING: infrastructure_type 'None' should not include @iac tags`
  - Missing @deployment: `⚠️ WARNING: infrastructure_type 'deployment_automation' or 'observability' missing @deployment: scripts/ tag`
  - Missing @config_file_type: `⚠️ WARNING: Config generation REQ missing @config_file_type tag`
  - Missing category: `⚠️ WARNING: Infrastructure-related REQ missing category metadata`
  ```

#### Change 4.3: Update Quick Fix Matrix
- **Location**: Under Quick Fix Matrix section
- **Add**:
  ```markdown
  | **CHECK 13** | Add valid Category field to Document Control table |
  | **CHECK 14** | Ensure infrastructure metadata (Type) and traceability tags (@sys, @iac) are complete |
  ```

### 5. Custom Validation Script: `validate_requirement_ids.py`
**Purpose**: Implement the actual logic for Checks 13 and 14.

**Changes**:
#### Change 5.1: Update `_validate_document_control`
- Parse `Infrastructure Type` (optional) and `Category` (mandatory) fields.
- Validate values against allowed lists in Schema.

#### Change 5.2: Add `_validate_infrastructure_metadata`
- Check consistency rules (e.g. `If infra_type=compute THEN iac_provider=terraform`).
- Validate `@sys` traceability to infrastructure sections.

---

## Implementation Phases

### Phase 1: Core Template Updates
1. ✅ Update REQ-MVP-TEMPLATE.md - Add Document Control category field
2. ✅ Update REQ-MVP-TEMPLATE.md - Moved Category Categories to Creation Rules (avoid bloat)
3. ✅ Update REQ-MVP-TEMPLATE.md - Update Section 10.3 with infrastructure traceability patterns
4. ✅ Update REQ-MVP-TEMPLATE.md - Moved Infrastructure Requirements guidance to Creation Rules (avoid bloat)

### Phase 2: Schema Validation
5. ✅ Update REQ_MVP_SCHEMA.yaml - Add 6 custom fields
6. ✅ Update REQ_MVP_SCHEMA.yaml - Add content validation rules
7. ✅ Update REQ_MVP_SCHEMA.yaml - Add Sections 11 and 12 to required_sections

### Phase 3: Creation Rules
8. ✅ Update REQ_MVP_CREATION_RULES.md - Update Section 2 structure
9. ✅ Update REQ_MVP_CREATION_RULES.md - Update Section 7 with category guidance
10. ✅ Update REQ_MVP_CREATION_RULES.md - Add Section 11 guidance
11. ✅ Update REQ_MVP_CREATION_RULES.md - Add Section 12 guidance

### Phase 4: Validation Rules
12. ✅ Update REQ_MVP_VALIDATION_RULES.md - Add CHECK 13
13. ✅ Update REQ_MVP_VALIDATION_RULES.md - Add CHECK 14
14. ✅ Update REQ_MVP_VALIDATION_RULES.md - Update Quick Fix Matrix

### Phase 5: Script Implementation
15. ✅ Update `validate_requirement_ids.py` - Implement `_validate_document_control` updates
16. ✅ Update `validate_requirement_ids.py` - Implement `_validate_infrastructure_metadata`

### Phase 6: Migration
17. ✅ Create `migrate_req_v1_to_v2.py` - Script to add default metadata (`Category: Functional`, `Infra: None`) to existing files.
18. ✅ Run migration on `docs/07_REQ/` to prevent regression.

---

## Files Modified Summary

| File | Changes | Purpose |
|------|---------|---------|
| REQ-MVP-TEMPLATE.md | 2 major changes | Metadata fields, traceability tags |
| REQ_MVP_SCHEMA.yaml | 7 custom fields + validation | Schema validation |
| REQ_MVP_CREATION_RULES.md | 5 sections updated | Creation guidance |
| REQ_MVP_VALIDATION_RULES.md | 2 new checks + matrix update | Validation rules |
| validate_requirement_ids.py | Python script logic | Enforce validation |
| migrate_req_v1_to_v2.py | New Script | Migration support |

---

## Validation Strategy

After implementation, REQ validation will support:

| Validation | Check | Result |
|-----------|-------|--------|
| Category field | CHECK 13 | Must be valid category |
| Infrastructure metadata | CHECK 14 | All tags complete and correct |
| Traceability | Section 10.3 | Proper @sys/@iac/@deployment tags |

---

## Workflow Support

**REQ → SPEC → Code/Config/IaC Generation**:

```mermaid
graph LR
  SYS[SYS Layer 6<br/>9.1 Infrastructure<br/>9.2 Operational] -->|Extract Requirements|
  REQ[REQ Layer 7<br/>Atomic Requirements] -->|Add Metadata<br/>@sys Tags<br/>@iac Tags|
  SPEC[SPEC Layer 10<br/>Technical Specs] -->|Generate Artifacts<br/>Based on Metadata|
  Code[Generated Source Code<br/>Python/Config] -->|Deploy|
  IaC[Generated IaC<br/>Terraform/Ansible] -->|Deploy|
  Config[Generated Config<br/>YAML/JSON/TOML] -->|Deploy|
  Scripts[Generated Scripts<br/>Shell/Bash] -->|Deploy|
```

**Traceability**:
- `@sys: SYS.NN.09.01.X` → References specific SYS infrastructure subsection
- `@iac: terraform/` / `@ansible: ansible/` → Specifies IaC provider
- `@deployment: scripts/` → Indicates shell script generation
- `@config_file_type: shell` → Indicates config file format
- `@spec: SPEC-NN` → Technical specification
- `@tasks: TASKS-NN` → Implementation tasks

---

## Examples to Add

### Example 1: Compute Infrastructure REQ
```markdown
## 12. Infrastructure-Related Requirements

### Example: Compute Infrastructure REQ

**Document Control**:
| **Infrastructure Type** | compute |
| **Category** | compute |

**Description**
The order processing service SHALL be deployed with 2 vCPU and 2GB memory per instance to handle peak order volume during business hours.

**Acceptance Criteria**
- Instance CPU utilization ≤ 70% under peak load
- Instance memory utilization ≤ 80% under peak load
- Scalability configured for 2-10 instances

**Source Requirements**
@sys: SYS.01.09.01.1 # Infrastructure Requirements - Compute
@iac: terraform/
@spec: SPEC-01
@tasks: TASKS-01
```

### Example 2: Deployment Automation REQ
```markdown
## 12. Infrastructure-Related Requirements

### Example: Deployment Automation REQ

**Document Control**:
| **Infrastructure Type** | deployment_automation |
| **Category** | deployment |

**Description**
The order processing service SHALL support blue-green deployment with automated rollback capability within 10 minutes.

**Acceptance Criteria**
- Blue-green deployment pipeline configured
- Health endpoints operational: /health/live, /health/ready, /health/startup
- Rollback completes within 10 minutes on failure

**Source Requirements**
@sys: SYS.01.09.01.8 # Deployment Automation Requirements
@iac: ansible/
@deployment: scripts/
@spec: SPEC-01
@tasks: TASKS-01
```

### Example 3: Pure Logic REQ (No Infrastructure)
```markdown
## 12. Infrastructure-Related Requirements

### Example: Pure Logic REQ

**Document Control**:
| **Infrastructure Type** | None |
| **Category** | logic |

**Description**
The order processing service SHALL validate order amounts against customer purchase history limits.

**Acceptance Criteria**
- Validation logic executes in < 50ms per order
- Validation failures logged with customer ID and reason
- Limits configurable via feature flags

**Source Requirements**
@sys: SYS.01 # General SYS document
@spec: SPEC-01
@tasks: TASKS-01
```

> **Note**: The above examples demonstrate *content* but should rely on `REQ_MVP_CREATION_RULES.md` for the full context, not static template sections.

---

## Change History

| Date | Version | Change | Author |
|------|---------|--------|---------|
| 2026-01-19 | 1.0.0 | Initial implementation plan for infrastructure metadata in REQ layer | System Architect |

---

## Related Files

- `06_SYS/SYS-MVP-TEMPLATE.md` - SYS template with deployment sections
- `06_SYS/SYS_MVP_VALIDATION_RULES.md` - SYS validation with CHECK 10/11
- `06_SYS/SYS_MVP_CREATION_RULES.md` - SYS creation rules with 9.1/9.2 guidance
- `06_SYS/examples/SYS-DEPLOYMENT_EXAMPLE.md` - Full infrastructure example
- `06_SYS/examples/SYS-LOGIC-ONLY_EXAMPLE.md` - Pure logic example

---

## Next Steps

1. ✅ Review and approve implementation plan
2. ✅ Execute phases 1-6
3. ✅ Validate changes with existing REQ examples
4. ✅ Test validation rules on new metadata fields
5. ✅ Migration complete for 85 files in REQ-11_domain_core
