# How to Create Product Requirements Documents (PRD)

**Document**: Unified Context Creation (UCC) Phase for PRD  
**Layer**: 2 (Product Requirements)  
**Version**: 1.0.0  
**Last Updated**: 2026-03-19  
**Status**: Active (v1.20.0)

---

## Table of Contents

1. [Overview](#overview)
2. [The Creation Workflow](#the-creation-workflow)
3. [Understanding the 7 Personas](#understanding-the-7-personas)
4. [The 21-Section Structure](#the-21-section-structure)
5. [Element ID System](#element-id-system)
6. [Critical Sections: Deep Dive](#critical-sections-deep-dive)
7. [Dual Readiness Scoring](#dual-readiness-scoring)
8. [CLI Commands](#cli-commands)
9. [Python API Usage](#python-api-usage)
10. [Common Mistakes & Fixes](#common-mistakes--fixes)
11. [Validation & Post-Creation](#validation--post-creation)

---

## Overview

### What is PRD Creation?

PRD (Product Requirements Document) creation is the **UCC (Unified Context Creation)** phase where multiple expert personas analyze an upstream BRD (Business Requirements Document) and produce a complete, structured PRD. The PRD bridges business requirements to product features and acceptance criteria.

**The Workflow:**
```
BRD (Layer 1)
    ↓
UCC_PROMPT_PRD.md + 7 Personas + Persona Skills
    ↓
    [Single AI Call]
    ↓
PRD (Layer 2) with 21 sections + Element IDs + Dual Scores
    ↓
Tier 1 Validation (auto-checking)
    ↓
Ready for EARS (Layer 3)
```

### Why This Approach?

Traditional single-author PRDs often suffer from:
- **Vague features** → Developers interpret differently → implementation delays
- **Missing acceptance criteria** → QA can't validate → bugs in production
- **No customer messaging** → UX inconsistencies → poor user experience
- **Layer violations** → BDD patterns in PRD → downstream confusion

**Unified Context approach fixes this** by having 7 specialized personas review the BRD simultaneously and contribute their expertise to a single, coherent document.

---

## The Creation Workflow

### Three-Input Model

PRD creation combines three inputs:

| Input | Purpose | Example |
|-------|---------|---------|
| **UCC Prompt** | Instructions to AI on PRD structure, rules, quality gates | `/opt/data/docs_flow_framework/UCX/creation/UCC_PROMPT_PRD.md` (~450 lines) |
| **Persona Skills** | Domain expertise per persona (architect skills, QA skills, etc.) | 7 files in `/opt/data/docs_flow_framework/UCX/skills/personas/` |
| **Upstream BRD** | Source document with business requirements to transform | `docs/01_BRD/BRD-01.md` (your input) |

All three feed into **one AI call** that produces the complete PRD.

### Creation Command

```bash
# Basic PRD creation
ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01

# With post-creation validation and scoring (v1.20.0+)
ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01 --validate

# With strict validation (warnings treated as errors)
ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01 --validate --strict
```

### Execution Details

1. **AI reads**:
   - UCC_PROMPT_PRD.md (structural rules, quality gates)
   - All 7 persona skill files (domain knowledge)
   - The upstream BRD document

2. **AI generates** the complete PRD following:
   - 21-section structure (mandatory)
   - Element ID format (PRD.NN.TT.SS)
   - Section 10 blocking requirement
   - Section 8 layer separation rule
   - Dual readiness scoring

3. **Post-creation** (if `--validate` flag used):
   - Tier 1 validation runs (checks structure, format, blocking issues)
   - Readiness scores computed
   - Scores injected into Document Control
   - Report generated

---

## Understanding the 7 Personas

During PRD creation, **seven specialized personas** collaborate. Each brings domain expertise and reviews different sections.

### Persona Breakdown

#### 1. **PRODUCT_OWNER**
- **Role**: Defines features, prioritizes scope, owns MVP decisions
- **Primary Sections**: 1-7 (definition), 14-17 (implementation)
- **Key Responsibilities**:
  - Feature scope and prioritization (Section 7)
  - MVP boundaries (Section 16)
  - Business value and ROI (Section 17)
- **Quality Focus**: Is every feature justified by business need?

#### 2. **UX_STRATEGIST**
- **Role**: Ensures user experience clarity, accessibility, usability
- **Primary Sections**: 4, 8, 9 (user-centric content)
- **Key Responsibilities**:
  - User personas and journeys (Section 4)
  - User story clarity and completeness (Section 8)
  - Feature usability and accessibility (Section 9)
- **Quality Focus**: Will users understand and use this?

#### 3. **CONTENT_STRATEGIST** ⭐ **NEW in v1.20.0**
- **Role**: Designs customer-facing messaging, help text, error messages
- **Primary Section**: **10** (Customer-Facing Content - BLOCKING)
- **Key Responsibilities**:
  - Product positioning statement
  - Key messaging themes
  - Help text templates
  - Error message patterns (with recovery actions)
  - Release notes structure
- **Quality Focus**: Does customer-facing language match brand voice?
- **Minimum Requirements**:
  - Positioning: ≥50 characters
  - Messaging themes: ≥3 themes
  - Error patterns: ≥3 patterns

#### 4. **TECH_LEAD**
- **Role**: Assesses technical feasibility, identifies constraints
- **Primary Sections**: 9, 12, 16, 18, 21 (technical aspects)
- **Key Responsibilities**:
  - Technical implementation feasibility (Section 9)
  - Technical constraints and dependencies (Section 12)
  - Testing strategy (Section 16, 21)
  - Traceability to technical decisions (Section 18)
- **Quality Focus**: Can we build this with our capabilities?

#### 5. **QA_LEAD**
- **Role**: Ensures testability, defines acceptance criteria quality
- **Primary Sections**: 11, 20, 21 (quality assurance)
- **Key Responsibilities**:
  - Acceptance criteria clarity and testability (Section 11)
  - EARS boundary values and thresholds (Section 20)
  - QA standards and test strategy (Section 21)
- **Quality Focus**: Can we test this completely?

#### 6. **ARCHITECT**
- **Role**: Designs system-level structure, integration patterns
- **Primary Sections**: 9, 18, 20 (architecture aspects)
- **Key Responsibilities**:
  - System architecture implications (Section 9)
  - Diagram requirements (C4-L2, DFD-L1, Sequence)
  - Architecture decision topics for ADR (Section 18)
  - State machines and timing profiles (Section 20)
- **Quality Focus**: Does this architecture support the features?

#### 7. **REQUIREMENTS_SPECIALIST** ⭐ **ENHANCED in v1.20.0**
- **Role**: Ensures formal requirement quality, layer separation
- **Primary Section**: **8** (User Stories - Layer Separation)
- **Key Responsibilities**:
  - User story scope (PRD-level only, not EARS/BDD)
  - Layer separation note enforcement
  - Requirement atomicity and clarity
  - Anti-pattern detection (no Given-When-Then, no WHEN-THE-SHALL)
- **Quality Focus**: Are stories at the right layer for PRD?
- **Action**: Flags any downstream-layer syntax detected

---

## The 21-Section Structure

Every PRD has exactly **21 numbered sections** in this order. This structure is **mandatory** and enforced by validators.

### Complete Section Reference

| § | Section Name | Purpose | Key Content | Element Codes | Blocking? |
|---|--------------|---------|-------------|---------------|-----------|
| 1 | Document Control | Metadata, version, dual scores | Frontmatter, version, scores | — | No |
| 2 | Executive Summary | Business context | 2-3 sentence overview, value prop | — | No |
| 3 | Problem Statement | Current state pain | Existing pain, business impact | — | No |
| 4 | Target Audience & Personas | User identification | Primary/secondary personas, roles | 24 | No |
| 5 | Success Metrics (KPIs) | Measurement criteria | Primary/secondary KPIs, thresholds | 08 | No |
| 6 | Goals & Objectives | Strategic direction | Business goals, objectives | 23 | No |
| 7 | Scope & Requirements | Boundaries | In-scope, out-of-scope, dependencies | 05, 22 | No |
| 8 | User Stories | PRD-level stories | Stories with layer separation note | 09 | No |
| 9 | Functional Requirements | Core capabilities | Features, use cases, journeys | 01, 11, 22 | No |
| 10 | **Customer-Facing Content** | **BLOCKING** - User messaging | Positioning, help text, errors | — | **YES** |
| 11 | Acceptance Criteria | Definition of done | Business/technical acceptance | 06 | No |
| 12 | Constraints & Assumptions | Limits & premises | Technical/business constraints | 03, 04 | No |
| 13 | Risk Assessment | High-risk items | Risk identification, mitigation | 07 | No |
| 14 | Success Definition | Launch criteria | Go-live criteria, validation gates | — | No |
| 15 | Stakeholders & Communication | Decision makers | RACI matrix, communication plan | 24 | No |
| 16 | Implementation Approach | Execution plan | MVP phases, rollout strategy | — | No |
| 17 | Budget & Resources | Financial | Development cost, ROI hypothesis | — | No |
| 18 | Traceability | Upstream/downstream | BRD references, ADR topics table | — | No |
| 19 | References | Documentation | Links to related documents | — | No |
| 20 | EARS Enhancement Appendix | Formal requirement prep | Timing profiles, boundary values | — | No |
| 21 | Quality Assurance | Testing approach | QA standards, testing strategy | 02 | No |

### Critical Notes

**Section 10 is BLOCKING**: If Section 10 is missing, has placeholders, or lacks substantive content, the PRD **fails validation**. This ensures customer-facing messaging is defined early in the product lifecycle.

**Section 8 requires layer separation note**: Must include explicit note distinguishing PRD (Layer 2) user stories from EARS (Layer 3) formal requirements and BDD (Layer 4) test scenarios.

---

## Element ID System

### Format: PRD.NN.TT.SS

All PRD elements use a unified 4-segment identifier:

```
PRD.{DOC#}.{TYPE}.{SEQ}
```

**Example**: `PRD.01.09.03` = PRD document 01, Type 09 (User Story), sequence 03

### Valid Element Types (13 codes)

| Code | Type | Primary Section | Example |
|------|------|-----------------|---------|
| 01 | Functional Requirement | 9 | "Users can reset password" |
| 02 | Quality Attribute / NFR | 21 | "System must support 10K concurrent users" |
| 03 | Constraint | 12 | "Must comply with PCI-DSS" |
| 04 | Assumption | 12 | "Users have internet connectivity" |
| 05 | Dependency | 7 | "Requires Stripe API integration" |
| 06 | Acceptance Criteria | 11 | "Reset link expires after 24 hours" |
| 07 | Risk | 13 | "Third-party API outage" |
| 08 | Metric / KPI | 5 | "98% uptime SLA" |
| 09 | User Story | 8 | "As a user, I want to reset password..." |
| 11 | Use Case | 9 | "Password Reset Use Case" |
| 22 | Feature Item | 7, 9 | "User Authentication Module" |
| 23 | Goal | 6 | "Enable self-service account recovery" |
| 24 | Stakeholder Need | 4, 15 | "Support department needs audit logs" |

### FORBIDDEN Patterns (Legacy - Do NOT Use)

- ❌ `FR-XXX`, `NFR-XXX` (old format)
- ❌ `US-XXX`, `US-01-001` (old user story format)
- ❌ `AC-XXX`, `RISK-XXX`, `METRIC-XXX` (old format)
- ❌ `Feature-NNN-NNN`, `Story-NNN` (non-standard)

### Example Element in PRD

```markdown
#### PRD.01.09.02: User Can Reset Forgotten Password

**As a** registered user,  
**I want** to reset my password if I forget it,  
**So that** I can regain access to my account.

**Summary**: Users request a password reset via email. They receive a 
time-limited link (24 hours). Clicking the link opens a secure form to 
set a new password. Old password is invalidated immediately.

**Product-Level Acceptance**:
- User can request reset via login page link
- Reset email arrives within 5 minutes
- Reset link expires after 24 hours
- Invalid attempts locked after 3 tries
- UI confirms successful password change

**EARS Reference**: To be detailed in EARS-NN (Layer 3)
**BDD Reference**: To be specified in BDD-NN (Layer 4)
```

---

## Critical Sections: Deep Dive

### Section 10: Customer-Facing Content (BLOCKING)

**This section is CRITICAL.** It ensures product messaging is defined early.

#### Required Subsections and Minimums

| Subsection | Minimum Content | Purpose |
|------------|-----------------|---------|
| **10.1 Product Positioning** | ≥50 characters | Unique value proposition |
| **10.2 Messaging Themes** | ≥3 themes | Target audience messaging |
| **10.3 Content Samples** | ≥2 samples | Welcome, onboarding text |
| **10.4 Help Text Templates** | ≥2 templates | Feature-level guidance |
| **10.5 Error Patterns** | ≥3 patterns | User-friendly error messages |
| **10.6 Release Notes Template** | Structure defined | Release communication format |

#### Example: Section 10.1 Product Positioning

**GOOD** (concrete, specific):
```
BeeLocal enables seamless cross-border remittance through mobile-first 
payment corridors that reduce transfer costs by 60% and settlement times 
to under 2 minutes, making international money transfer accessible to 
unbanked populations in developing markets.
```

**BAD** (vague, placeholder):
```
BeeLocal is a fintech platform for money transfer. It will be fast and 
secure. [TBD: Add more positioning details]
```

#### Example: Section 10.2 Messaging Themes

| Theme | Target Audience | Message |
|-------|-----------------|---------|
| Speed | Urgent senders | Send money home in 2 minutes, not 2 days |
| Cost | Price-conscious users | Save up to 60% on transfer fees |
| Trust | First-time users | Bank-grade security and 1M+ users trust us |

#### Example: Section 10.5 Error Message Patterns

**Pattern Template:**
```
What happened: [Clear, non-technical description]
Why it happened: [Context if helpful]
What to do: [Specific recovery action]
Help link: [Support resource]
```

**Example - Insufficient Balance:**
```
What happened: Your wallet balance is too low for this transfer.
Why it happened: Your account has $45.00, but this transfer needs $50.00.
What to do: Add funds via Settings → Payment Methods, or reduce transfer amount.
Help link: Learn how to add funds
```

**Example - Network Error:**
```
What happened: We couldn't reach the payment network right now.
Why it happened: Your internet connection may be weak or our service is experiencing issues.
What to do: Check your connection and try again, or come back in a few minutes.
Help link: Troubleshooting connection issues
```

### Section 8: User Stories with Layer Separation Note

**This section must clarify layer boundaries** to prevent downstream confusion.

#### Required Opening Note

Every Section 8 **MUST begin with this note**:

```markdown
## Section 8: User Stories & User Roles

**Layer Separation Note**: This section contains PRD-level user stories 
with role definitions, story titles, 2-3 sentence summaries, and 
product-level acceptance criteria. 

Detailed WHEN-THE-SHALL formal requirements belong in EARS (Layer 3). 
Executable Given-When-Then test scenarios belong in BDD (Layer 4).
```

#### Correct PRD User Story Format

```markdown
#### PRD.01.09.01: User Can Login with Email

**As a** new user,  
**I want** to create an account and login,  
**So that** I can access my personal wallet.

**Summary**: Users should be able to sign up with email and password on 
the login page. The system validates email format, stores password securely, 
and allows login within 60 seconds.

**Product-Level Acceptance**:
- User can enter email and password on signup form
- Email validation prevents invalid formats
- Password is stored securely (hashed)
- Login succeeds with correct credentials
- Account creation triggers welcome email

**EARS Reference**: To be detailed in EARS-NN (Layer 3)
**BDD Reference**: To be specified in BDD-NN (Layer 4)
```

#### FORBIDDEN Patterns in Section 8

**❌ WRONG - BDD Syntax (belongs in Layer 4):**
```markdown
#### Scenario: User Login
Given the user is on the login page
When they enter their email and password
Then they see their dashboard
```

**❌ WRONG - EARS Syntax (belongs in Layer 3):**
```markdown
WHEN a user submits login credentials
THE system SHALL validate the email format
AND SHALL authenticate against stored credentials
```

**❌ WRONG - Technical Details (belongs in Layer 9 SPEC):**
```markdown
The login endpoint uses bcrypt with salt rounds of 12. 
Passwords stored as SHA-256 hashes in the users table.
```

---

## Dual Readiness Scoring

### What Are the Two Scores?

PRDs include **two independent readiness scores** in **Section 1 (Document Control)**:

#### Score 1: **SYS-Ready** (System Readiness)

Measures whether the PRD has sufficient product/business details for technical specification.

| Component | Weight | Measures |
|-----------|--------|----------|
| **Product Completeness** | 40% | All sections present, no placeholders |
| **Technical Readiness** | 30% | Constraints clear, FR depth, dependencies specified |
| **Business Alignment** | 20% | Goals defined, metrics measurable, value clear |
| **Traceability** | 10% | BRD refs complete, cross-refs valid |

#### Score 2: **EARS-Ready** (Executable ARtifacts Scorecard)

Measures whether the PRD has sufficient detail for formal EARS requirements (Layer 3).

| Component | Weight | Measures |
|-----------|--------|----------|
| **Timing Profiles** | 25% | Response times, performance reqs specified |
| **Boundary Values** | 25% | Min/max ranges, thresholds documented |
| **State Machines** | 25% | State transitions, conditions, error states clear |
| **Fallback Paths** | 15% | Error handling, recovery actions specified |
| **Threshold Registry** | 10% | KPIs defined, targets, SLAs specified |

### Score Format in Document Control

```markdown
| Field | Value |
|-------|-------|
| SYS-Ready Score | [DRAFT] 87% (Target: ≥90%) |
| EARS-Ready Score | [DRAFT] 84% (Target: ≥90%) |
| Profile | Standard (≥90% threshold) |
```

### Thresholds (v1.20.0)

| Profile | SYS-Ready | EARS-Ready | Use Case |
|---------|-----------|------------|----------|
| **MVP** | ≥85% | ≥85% | Early-stage, internal use |
| **Standard** | ≥90% | ≥90% | Production-ready |

---

## CLI Commands

### Basic Creation

```bash
# Create PRD from upstream BRD
ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01
```

### With Validation & Scoring

```bash
# Create + auto-validate + compute scores (v1.20.0+)
ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01 --validate

# Create + strict validation (warnings as errors)
ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01 --validate --strict
```

### With Model Selection

```bash
# Use Sonnet (faster, lower cost)
ucx --model sonnet create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01

# Use Opus (highest quality)
ucx --model opus create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01
```

### With Web Search

```bash
# Enable fact-checking, best practices research
ucx -W create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01

# Full CLI equivalent
ucx --enable-web-search create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01
```

### Post-Creation Validation

```bash
# Validate created PRD
ucx validate prd docs/02_PRD/PRD-01/

# Tier 1 only (fast, blocking checks)
ucx validate prd docs/02_PRD/PRD-01/ --tier1-only

# Strict mode (warnings treated as errors)
ucx validate prd docs/02_PRD/PRD-01/ --strict
```

---

## Python API Usage

```python
from ucx.api import UCXCreationAPI
from pathlib import Path

# Initialize
api = UCXCreationAPI()

# Create PRD
document = api.create(
    doc_type="prd",
    output_path=Path("docs/02_PRD/PRD-01"),
    from_upstream=Path("docs/01_BRD/BRD-01"),
    validate_after=True,  # NEW in v1.20.0
)

# Check scores
metadata = document.metadata
print(f"SYS-Ready: {metadata['sys_ready_score']}%")
print(f"EARS-Ready: {metadata['ears_ready_score']}%")

# Check validation status
if metadata.get('validation_status') == 'passed':
    print("✅ PRD passed Tier 1 validation")
else:
    print("⚠️ PRD has issues, run: ucx validate prd ...")
```

---

## Common Mistakes & Fixes

### Mistake 1: Section 10 with Placeholders

**❌ WRONG:**
```markdown
## Section 10: Customer-Facing Content

### 10.1 Product Positioning
[TBD: Add positioning statement]

### 10.2 Messaging Themes
[To be filled in later]
```

**✅ CORRECT:**
```markdown
## Section 10: Customer-Facing Content

### 10.1 Product Positioning
BeeLocal enables seamless cross-border remittance through mobile-first 
payment corridors that reduce transfer costs by 60% and settlement times 
to under 2 minutes.

### 10.2 Messaging Themes
| Theme | Audience | Message |
|-------|----------|---------|
| Speed | Urgent senders | Send in 2 minutes, not 2 days |
| Cost | Budget-conscious | Save up to 60% on fees |
| Trust | First-time users | Secure + 1M users trust us |
```

### Mistake 2: BDD/EARS Syntax in Section 8

**❌ WRONG (BDD syntax in PRD):**
```markdown
#### Scenario: Password Reset

Given the user is on the login page
When they click "Forgot Password"
Then they see the reset email form
And receive reset email within 5 minutes
```

**✅ CORRECT (PRD-level story):**
```markdown
#### PRD.01.09.03: User Can Reset Password

**As a** user who forgot password,  
**I want** to reset my password,  
**So that** I can regain access.

**Summary**: Users can initiate password reset from login page. 
They receive email with time-limited reset link (24 hours). 
Clicking link opens form to set new password.

**Product-Level Acceptance**:
- Reset link sent within 5 minutes
- Link valid for 24 hours
- New password stored securely
- Old password invalidated

**EARS Reference**: To be detailed in EARS-NN (Layer 3)
```

### Mistake 3: Wrong Element ID Format

**❌ WRONG:**
```markdown
FR-01: User can login
US-02: Reset password
Story-03: View history
Feature-Login-001: Email login
```

**✅ CORRECT:**
```markdown
PRD.01.01.01: (Functional Requirement)
PRD.01.09.02: (User Story)
PRD.01.09.03: (User Story)
PRD.01.22.01: (Feature Item)
```

### Mistake 4: Missing Layer Separation Note in Section 8

**❌ WRONG (no note):**
```markdown
## Section 8: User Stories

#### PRD.01.09.01: User Login
...
```

**✅ CORRECT (with note):**
```markdown
## Section 8: User Stories & User Roles

**Layer Separation Note**: This section contains PRD-level user stories
with role definitions, story titles, 2-3 sentence summaries, and 
product-level acceptance criteria.

Detailed WHEN-THE-SHALL formal requirements belong in EARS (Layer 3).
Executable Given-When-Then test scenarios belong in BDD (Layer 4).

#### PRD.01.09.01: User Login
...
```

### Mistake 5: Forward References to Non-Existent Documents

**❌ WRONG (referencing ADR that doesn't exist yet):**
```markdown
| Cart Service | BRD-01 §7.2 | See ADR-05 for architecture | ... |
```

**✅ CORRECT (use topic table, not ADR numbers):**
```markdown
| Cart Service | BRD-01 §7.2 | Microservice vs. Monolith | Performance, Cost | Sprint 3 |
```

---

## Validation & Post-Creation

### Automatic Validation (if `--validate` flag used)

After PRD creation, the system automatically:

1. **Runs Tier 1 validation** (blocking checks):
   - All 21 sections present
   - Section 10 has substantive content (min. 200 chars)
   - Element IDs use PRD.NN.TT.SS format
   - No forward references to non-existent layers
   - No TBD/TODO placeholders in Section 10

2. **Computes dual readiness scores**:
   - SYS-Ready: Product completeness assessment
   - EARS-Ready: Formal requirement readiness

3. **Injects scores into Document Control** (Section 1)

4. **Generates validation report**: `PRD-01.V_validation_report_v001.md`

### Validation Report Contents

```yaml
---
title: "PRD-01 Validation Report"
report_version: v001
validation_date: 2026-03-19T15:42:00
validator: UCX Framework v1.20.0
custom_fields:
  artifact_type: VALIDATION
  validated_document: PRD-01
  validation_score: 87.5
  status: PASS
  tier1_errors: 0
  tier2_warnings: 2
---

# PRD-01 Validation Report v001

## Executive Summary
PRD-01 passed Tier 1 validation with no blocking errors.

## Validation Score
- SYS-Ready: 87% (Target: ≥90%)
- EARS-Ready: 84% (Target: ≥90%)

## Tier 1 Findings (Core Checks)
✅ All 21 sections present
✅ Section 10 substantive content verified
✅ Element IDs valid (PRD.NN.TT.SS format)
...

## Recommended Next Steps
1. Address Section 20 timing profiles (needs detail)
2. Add boundary values to Section 20.2
3. Run full validation: `ucx validate prd docs/02_PRD/PRD-01/`
```

### Manual Validation (Anytime)

```bash
# Full validation (all tiers)
ucx validate prd docs/02_PRD/PRD-01/

# Tier 1 only (quick check)
ucx validate prd docs/02_PRD/PRD-01/ --tier1-only

# Strict mode
ucx validate prd docs/02_PRD/PRD-01/ --strict
```

---

## Best Practices

### 1. Start with a Quality BRD

PRD quality directly depends on upstream BRD quality. Ensure BRD has:
- Clear, measurable business goals
- Well-defined target users
- Specific problems being solved
- Business success metrics

### 2. Review Personas & Their Roles

Understand what each of the 7 personas contributes:
- **Product Owner** → Scope boundaries & MVP definition
- **UX Strategist** → User journeys & accessibility
- **Content Strategist** → Customer messaging (Section 10)
- **Tech Lead** → Technical feasibility assessment
- **QA Lead** → Testability & acceptance criteria
- **Architect** → System-level design decisions
- **Requirements Specialist** → Layer separation enforcement

### 3. Pay Special Attention to Section 10

Section 10 is the most critical section. Spend time on:
- **Positioning statement**: Concise, specific, customer-centric
- **Error messages**: Helpful, actionable, not blaming
- **Help text**: Clear for non-technical users
- **Tone & voice**: Consistent throughout

### 4. Follow Layer Separation in Section 8

Use the PRD as the **product definition layer**:
- User stories tell *what* users need and *why*
- EARS layer (L3) will define *how formally*
- BDD layer (L4) will define *how to test*

Section 8 user stories should NOT include:
- Given-When-Then test syntax
- WHEN-THE-SHALL formal syntax
- Technical implementation details

### 5. Complete Section 20 EARS Appendix

This section prepares for downstream EARS translation:
- **Timing profiles**: Response time SLAs
- **Boundary values**: Min/max ranges for parameters
- **State transitions**: Major state machines
- **Fallback paths**: Error handling and recovery

### 6. Use Section 18 for Traceability

Two traceability needs:
- **Upstream (Section 18.1)**: Show which BRD elements this PRD implements
- **Downstream (Section 18.2)**: Identify architectural decision topics (not specific ADR numbers)

---

## Related Documentation

- **[UNIFIED_CONTEXT_REVIEW.md](UNIFIED_CONTEXT_REVIEW.md)** — Review phase (UCR) for PRDs
- **[README.md](README.md)** — UCX overview and architecture
- **[PLAN-009_prd_creation.md](plans/PLAN-009_prd_creation.md)** — Detailed implementation plan
- **[PLAN-010_prd_validation.md](plans/PLAN-010_prd_validation.md)** — Validation system details
- **[CHANGELOG_v1.20.0.md](CHANGELOG/CHANGELOG_v1.20.0.md)** — v1.20.0 release notes

---

## Command Quick Reference

```bash
# Create PRD with validation
ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01 --validate

# Validate existing PRD
ucx validate prd docs/02_PRD/PRD-01/

# Review PRD with personas
ucx review prd docs/02_PRD/PRD-01/ --persona

# Quick validation (Tier 1 only)
ucx validate prd docs/02_PRD/PRD-01/ --tier1-only

# Show help
ucx create --help
ucx validate --help
```
