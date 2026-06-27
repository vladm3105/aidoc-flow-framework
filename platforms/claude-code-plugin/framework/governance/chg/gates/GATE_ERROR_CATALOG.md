---
title: "Gate Error Catalog"
tags:
  - change-management
  - gate-system
  - error-codes
  - shared-architecture
custom_fields:
  document_type: reference
  artifact_type: CHG
---

# Gate Error Catalog

Complete catalog of all error and warning codes across the Change Management gate system (5 artifact gates + the GATE-SPEC meta gate) for the SDD framework.

## 1. Error Code Format

```
GATE-NN-SNNN

Where:
  NN   = Gate number (01, 03, 06, 08, CODE, SPEC)
  S    = Severity (E=Error, W=Warning, I=Info)
  NNN  = Sequential number within gate and severity
```

> GATE-SPEC is the **meta** gate — it governs changes to the `framework/` spec
> itself, orthogonal to the artifact-cascade gates below. See
> `GATE-SPEC_FRAMEWORK.md`.

## 2. GATE-01: Business/Product Errors (L1-L2)

### 2.1 Blocking Errors (E)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-01-E001 | Documentation | BRD change must have business justification | Add "Business Justification" section with measurable impact |
| GATE-01-E002 | Traceability | PRD change must link to BRD objective | Add `@brd:` tag with valid BRD reference |
| GATE-01-E003 | Classification | Breaking change missing C3 classification | Escalate change level to C3 |
| GATE-01-E004 | Approval | No stakeholder approval for C3 change | Obtain and document stakeholder signature |

### 2.2 Warnings (W)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-01-W001 | Scope | Large scope (>5 layers) without C3 | Consider elevating to C3 or phased implementation |
| GATE-01-W002 | Approval | Missing stakeholder sign-off for C2 | Obtain Product Owner approval |
| GATE-01-W003 | Planning | Cascade affects >8 artifacts | Create phased implementation plan |

## 3. GATE-03: Requirements & Architecture Errors (L3-L5)

### 3.1 Blocking Errors (E)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-03-E001 | Structure | ADR must document context, decision, consequences | Add Context, Decision, Consequences sections |
| GATE-03-E002 | Security | External change missing security review | Complete security assessment |
| GATE-03-E003 | Syntax | EARS must follow WHEN-THE-SHALL syntax | Fix WHEN-THE-SHALL-WITHIN format |
| GATE-03-E004 | Syntax | BDD must have Given-When-Then format | Fix Given-When-Then structure |
| GATE-03-E005 | Traceability | EARS missing necessary-upstream tag (@prd) | Add the required upstream tag |
| GATE-03-E006 | Traceability | BDD missing necessary-upstream tag (@ears) | Add the required upstream tag |
| GATE-03-E007 | Traceability | ADR missing necessary-upstream tags (@ears @bdd) | Add the 2 required upstream tags |
| GATE-03-E008 | Security | External-source change cites neither a CVE/advisory nor an N/A reason | Add `CVE-YYYY-NNNN`/advisory ref, or `no advisory applies: <reason>` |

### 3.2 Warnings (W)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-03-W001 | Documentation | External security change without CVE reference | Add CVE-YYYY-NNNN reference |
| GATE-03-W002 | Completeness | ADR alternatives section missing | Document considered alternatives |
| GATE-03-W003 | Coverage | BDD missing edge case coverage | Add boundary condition scenarios |
| GATE-03-W004 | Coverage | EARS missing boundary value coverage | Add boundary condition specifications |

## 4. GATE-06: Design & Test Errors (L6-L7)

### 4.1 Blocking Errors (E)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-06-E001 | Readiness | SPEC TDD-Ready score < 90% | Complete missing sections, clarify ambiguities |
| GATE-06-E002 | Coverage | TDD missing BDD scenario coverage | Add test case definitions for all BDD scenarios |
| GATE-06-E003 | Consistency | TDD/SPEC misalignment | Synchronize TDD test contracts with SPEC interfaces |
| GATE-06-E004 | Process | SPEC change without TDD update | Update TDD with test cases for changed interfaces |

### 4.2 Warnings (W)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-06-W001 | Performance | Algorithm change without performance baseline | Document current performance metrics |
| GATE-06-W002 | Complexity | SPEC implementation complexity > 4 | Consider decomposition |

## 5. GATE-08: IPLAN Errors (L8)

### 5.1 Blocking Errors (E)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-08-E001 | Completeness | IPLAN file manifest incomplete | Add missing files to manifest |
| GATE-08-E002 | Order | Test files not before implementation files | Reorder manifest: tests first |
| GATE-08-E003 | Traceability | IPLAN missing @spec/@tdd tags | Add upstream traceability tags |
| GATE-08-E004 | Handoff | Session handoff protocol missing | Document state variables and resume protocol |

### 5.2 Warnings (W)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-08-W001 | Size | File manifest exceeds 20 files | Split into multiple IPLANS |
| GATE-08-W002 | Contracts | Shared interface without implementation contract | Define contract for multi-session work |
| GATE-08-W003 | Rollback | No rollback procedure defined | Add revert steps |

## 6. GATE-CODE: Implementation Errors

### 6.1 Blocking Errors (E)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-CODE-E001 | Analysis | Root cause analysis must be completed | Add RCA section with 5-Whys analysis |
| GATE-CODE-E002 | Layer | Fix must be at correct layer (not symptom masking) | Trace to actual problem layer |
| GATE-CODE-E003 | Testing | Code must pass TDD test suite | Fix code to pass TDD test cases |
| GATE-CODE-E004 | Review | Code review required for C2/C3 changes | Complete review process |

### 6.2 Warnings (W)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-CODE-W001 | Performance | Performance regression without baseline | Benchmark before and after |
| GATE-CODE-W002 | Quality | Build warning introduced | Fix or document rationale |
| GATE-CODE-W003 | Debt | Technical debt without tracking ticket | Create follow-up issue |

## 6b. GATE-SPEC: Framework Specification Errors (meta)

Governs changes to the `framework/` spec (templates, governance, registry,
VERSION). Split by enforcer: E001–E004 are validated from the CHG record (each
platform's record validator); E005–E008 are enforced by continuous integration
(diff-aware checks + the conformance suite); the human approval half is the
platform's protected-branch review.

### 6b.1 Blocking Errors (E)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-SPEC-E001 | Provenance | Spec change missing justification | Populate `change_description.why` + `.trigger`; cite the motivating signal |
| GATE-SPEC-E002 | Classification | SemVer impact undeclared, or `major` not classified C3 | Set `semver_impact`; escalate a breaking change to C3 |
| GATE-SPEC-E003 | Classification | Spec change classified C1 | Reclassify ≥ C2 — a spec change reaches multiple consumers |
| GATE-SPEC-E004 | Approval | C3 spec change missing human gate approval | Record `gate_approval` (gate GATE-SPEC + approver); a human signs |
| GATE-SPEC-E005 | Versioning | `framework/VERSION` not bumped when `framework/**` changed | Bump `framework/VERSION` per `semver_impact` |
| GATE-SPEC-E006 | Conformance | Platform `FRAMEWORK_SPEC_VERSION` out of sync | Update both to match `framework/VERSION` |
| GATE-SPEC-E007 | Conformance | Shared conformance suite failing | Fix the spec or the platform; never weaken a check |
| GATE-SPEC-E008 | Documentation | `CHANGELOG.md` not updated | Add a changelog entry for the spec change |

### 6b.2 Warnings (W)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-SPEC-W001 | Migration | `major` change without a per-platform migration note | Add a migration note for each platform |
| GATE-SPEC-W002 | Parity | Change touches only one platform's conformance | Confirm both platforms track the new spec version |
| GATE-SPEC-W003 | Security | Agent-facing spec change without a `SECURITY_REVIEW.md` assessment | Run the security review (injection/abuse surface) for the changed guidance |

## 7. Emergency Bypass Errors

### 7.1 Blocking Errors (E)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| EMG-E001 | Authorization | Emergency not authorized by incident commander | Obtain authorization |
| EMG-E002 | Classification | Non-critical issue using emergency bypass | Use standard gate process |
| EMG-E003 | Documentation | Emergency stub not created | Create CHG-EMG-{timestamp}.yaml |
| EMG-E004 | Timeline | Post-mortem not completed within 48 hours | Complete POST_MORTEM-{CHG-ID}.md |
| EMG-E005 | Closure | Emergency CHG not closed | Complete all closure requirements |

### 7.2 Warnings (W)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| EMG-W001 | Documentation | Emergency stub missing incident reference | Add incident ticket number |
| EMG-W002 | Follow-up | Preventive measure CHG not created | Create follow-up CHG |
| EMG-W003 | Review | Post-mortem missing root cause | Complete 5-Whys analysis |

## 8. Cross-Gate Errors

### 8.1 Routing Errors

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| ROUTE-E001 | Routing | Invalid gate entry for change source | Route to correct gate per source |
| ROUTE-E002 | Cascade | Skipped mandatory gate | Pass all required gates in sequence |
| ROUTE-E003 | Approval | Missing upstream gate approval | Complete upstream gate first |
| ROUTE-E004 | Classification | Change level mismatch across gates | Maintain consistent level |

### 8.2 Validation Errors

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| VAL-E001 | Schema | CHG document fails schema validation | Fix YAML structure |
| VAL-E002 | Structure | Required section missing | Add missing section |
| VAL-E003 | Traceability | Broken cross-reference | Fix or remove invalid reference |
| VAL-E004 | Status | Invalid status transition | Follow status workflow |

## 9. Error Resolution Quick Reference

### 9.1 Most Common Errors

| Error | Frequency | Quick Fix |
|-------|-----------|-----------|
| GATE-03-E007 | High | Add 4 traceability tags to ADR |
| GATE-06-E001 | High | Improve SPEC TDD-Ready score |
| GATE-CODE-E001 | Medium | Add RCA section |
| GATE-01-E003 | Medium | Escalate breaking change to C3 |

### 9.2 Resolution Templates

```markdown
## GATE-03-E007 Resolution
Add all 4 upstream traceability tags:

@brd: BRD-XXX
@prd: PRD-XXX
@ears: EARS-XXX
@bdd: BDD-XXX

## GATE-CODE-E001 Resolution
Add Root Cause Analysis section:

### Root Cause Analysis
**5-Whys Analysis**:
1. Why? [First-level cause]
2. Why? [Second-level cause]
3. Why? [Third-level cause]
4. Why? [Fourth-level cause]
5. Why? [Root cause]

**Root Cause Layer**: L[N] - [Layer Name]
**Fix Approach**: [How this fix addresses root cause]
```

---

**Related Documents**:
- [GATE-01_BUSINESS_PRODUCT.md](./GATE-01_BUSINESS_PRODUCT.md)
- [GATE-03_REQUIREMENTS_ARCHITECTURE.md](./GATE-03_REQUIREMENTS_ARCHITECTURE.md)
- [GATE-06_DESIGN_TEST.md](./GATE-06_DESIGN_TEST.md)
- [GATE-08_IPLAN.md](./GATE-08_IPLAN.md)
- [GATE-CODE_IMPLEMENTATION.md](./GATE-CODE_IMPLEMENTATION.md)
- [GATE-SPEC_FRAMEWORK.md](./GATE-SPEC_FRAMEWORK.md)
- [GATE_INTERACTION_DIAGRAM.md](./GATE_INTERACTION_DIAGRAM.md)
