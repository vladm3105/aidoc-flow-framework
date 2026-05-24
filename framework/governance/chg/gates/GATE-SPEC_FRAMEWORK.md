---
title: "GATE-SPEC: Framework Specification Gate"
tags:
  - change-management
  - gate-system
  - framework-governance
  - shared-architecture
custom_fields:
  document_type: gate-definition
  artifact_type: CHG
  gate_number: SPEC
  layer_range: "meta"
  layer_names: ["framework-spec"]
---

# GATE-SPEC: Framework Specification Gate (meta)

> **Position**: Orthogonal to the artifact cascade — governs the `framework/`
> spec itself, not a project's artifacts.
> **Change Sources**: Spec (a change to `framework/` templates, governance,
> registry, or `VERSION`).
> **Purpose**: Validate changes to the shared specification both platforms
> consume, before they ripple to every consumer.

## 1. Purpose & Scope

The five artifact gates (GATE-01/03/06/08/CODE) govern changes to **artifact
instances** flowing down a project's BRD→Code chain. GATE-SPEC is different in
kind: it governs changes to the **shared contract that defines the layers** —
the templates, governance rules, registry, and version under `framework/`.

GATE-SPEC is therefore a **meta gate**, *orthogonal* to the artifact cascade. Its
"cascade" is not L1→Code; it is: **a spec change forces every platform to
re-declare `FRAMEWORK_SPEC_VERSION` and re-pass the shared conformance suite.**
This is the "Process" role described in `docs/PROJECT.md` §6 — a `framework/`
spec change has multiple downstream consumers and real breaking-change risk,
which is exactly the formal-gate scenario CHG exists for.

### 1.1 What GATE-SPEC governs

| Target | Examples |
|--------|----------|
| Templates | `framework/layers/<NN>_<X>/*-TEMPLATE.yaml`, index templates |
| Governance | `framework/governance/*` (rules, standards, the CHG overlay itself) |
| Registry | `framework/registry/LAYER_REGISTRY.yaml` |
| Version | `framework/VERSION` |

A change is routed to GATE-SPEC by its **target** (it edits `framework/`), not by
which artifact layer it resembles. Per-platform internal development (a platform's authoring
wording or runtime code) is **not** a spec change — it is an ordinary platform
PR (`docs/PROJECT.md` §6), and does not enter GATE-SPEC.

## 2. Entry Criteria

| Criterion | Required | Validation |
|-----------|----------|------------|
| Spec target identified | Yes | The change edits `framework/` (template / governance / registry / VERSION) |
| Justification documented | Yes | `change_description.why` + `.trigger` — a promotion cites the motivating `.aidoc/learnings.md` / profile signal |
| SemVer impact classified | Yes | `change_control.semver_impact` ∈ {major, minor, patch} |
| Change level proposed | Yes | ≥ C2 (a spec change is never C1 — it reaches ≥2 consumers); `major` ⇒ C3 |
| Both-platform reach acknowledged | Yes | The change updates both platforms' `FRAMEWORK_SPEC_VERSION` and they re-pass conformance |

### 2.1 Pre-Gate Checklist

```markdown
- [ ] Change edits framework/ (templates / governance / registry / VERSION)
- [ ] change_description.why and .trigger populated (provenance for a promotion)
- [ ] semver_impact set (major | minor | patch)
- [ ] change_level proposed (>= C2; major => C3)
- [ ] CHANGELOG.md entry drafted
- [ ] For C3: both platform owners notified
```

## 3. Validation Checklist

The checks split three ways by enforcer (ROADMAP CHG-D1): each platform's
**record validator** reads the CHG record (E001–E004); **continuous integration
(CI)** runs the diff-aware + suite checks (E005–E008); the **human** approval is
the platform's protected-branch review. The validator never grants approval.

### 3.1 Error Checks (Blocking)

| Check ID | Description | Enforcer | Validation |
|----------|-------------|----------|------------|
| GATE-SPEC-E001 | Spec change must carry provenance/justification | record (validator) | `change_description.why` and `.trigger` non-empty |
| GATE-SPEC-E002 | SemVer impact declared; `major` must be C3 | record (validator) | `semver_impact` ∈ {major,minor,patch}; if `major` then `change_level == C3` |
| GATE-SPEC-E003 | A framework-spec change is never C1 | record (validator) | `change_level` ≥ C2 |
| GATE-SPEC-E004 | C3 spec change requires human approval | record (validator) | C3 ⇒ `gate_approval.gate == GATE-SPEC` + non-null `approver` |
| GATE-SPEC-E005 | `framework/VERSION` must bump when `framework/**` changes | CI (diff-aware) | VERSION changed in the PR diff |
| GATE-SPEC-E006 | Platform spec versions match the framework | CI (conformance) | both `FRAMEWORK_SPEC_VERSION` == `framework/VERSION` |
| GATE-SPEC-E007 | Shared conformance suite passes | CI (conformance) | `tests/conformance` green |
| GATE-SPEC-E008 | `CHANGELOG.md` updated | CI (diff-aware) | CHANGELOG changed in the PR diff |

> **E002 mapping (one-directional):** `major` ⇒ C3 (required). `minor` / `patch`
> may be C2 — an additive change (a new optional knob, a new gate) reaches both
> platforms yet is not breaking, so it does not force C3. Only a breaking change
> escalates.

### 3.2 Warning Checks (Non-Blocking)

| Check ID | Description | Recommendation |
|----------|-------------|----------------|
| GATE-SPEC-W001 | `major` (breaking) change without a per-platform migration note | Add a migration note for each platform |
| GATE-SPEC-W002 | Change touches only one platform's conformance (parity drift) | Confirm both platforms track the new spec version |

## 4. Approval Workflow

### 4.1 Approval Matrix

| Change Level | Required Approvers | SLA |
|--------------|-------------------|-----|
| **C2** | Framework maintainer + 1 platform owner | 2 business days |
| **C3** (breaking) | Framework maintainer + **both** platform owners | 5 business days |
| **Emergency** | Not a typical spec path — a spec change is not a production hotfix; handle out-of-band and document | n/a |

The validator **prepares and verifies** the approval form; a **human** signs. It
must never mark a spec change "approved" — the human gate is the platform's
protected-branch review (required reviewers on `framework/**`).

### 4.2 Approval Form

For C2/C3, complete `templates/GATE_APPROVAL_FORM.md` with the change summary,
the affected `framework/` targets, the SemVer impact, the per-platform
conformance result, the risk/rollback sections, and the approver rows for the
level. Signature fields stay blank for the human.

## 5. Exit Criteria

| Criterion | C2 | C3 |
|-----------|----|----|
| All E-level checks pass (E001–E008) | Yes | Yes |
| W-level checks addressed | Review | Must address |
| Provenance complete | Yes | Yes |
| SemVer impact classified | Yes | Yes |
| Both `FRAMEWORK_SPEC_VERSION` re-declared + conformance green | Yes | Yes |
| Human approval obtained per matrix | Yes | Yes |
| Rollback plan documented | Yes | Yes |
| Per-platform migration note (for `major`) | n/a | Yes |

### 5.1 Exit Checklist

```markdown
- [ ] GATE-SPEC-E001..E004 pass (record-level)
- [ ] GATE-SPEC-E005..E008 pass (CI: VERSION bump, FSV match, suite green, CHANGELOG)
- [ ] GATE-SPEC-W001..W002 reviewed
- [ ] CHG document created (>= C2)
- [ ] Human approval obtained per matrix (branch protection)
- [ ] Both platforms re-declare FRAMEWORK_SPEC_VERSION; conformance green
- [ ] Ready to merge
```

## 6. Routing Rules

GATE-SPEC does **not** route into the artifact cascade — it has no GATE-03/06/08
successor, because it changes the spec, not a project's artifacts. After
GATE-SPEC passes:

| Scenario | Next Step |
|----------|-----------|
| Spec change merged | Both platforms adopt the new `framework/VERSION` (update `FRAMEWORK_SPEC_VERSION`, re-run conformance) |
| Platform must adapt its authoring engine / runtime to the new spec | Ordinary platform PR (not CHG) |

```
        CHANGE TO framework/ (template / governance / registry / VERSION)
                                  │
                              GATE-SPEC
                 (provenance · semver · >=C2 · human approval
                  · VERSION bump · FSV match · suite green · CHANGELOG)
                                  │
                               PASSED
                                  │
              both platforms re-declare FRAMEWORK_SPEC_VERSION
                    and re-pass the shared conformance suite
```

## 7. Error Catalog

### 7.1 GATE-SPEC Error Codes

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-SPEC-E001 | Provenance | Missing justification | Populate `change_description.why` + `.trigger`; cite the motivating signal |
| GATE-SPEC-E002 | Classification | SemVer impact undeclared or `major` not C3 | Set `semver_impact`; escalate a breaking change to C3 |
| GATE-SPEC-E003 | Classification | Spec change classified C1 | Reclassify ≥ C2 — a spec change reaches multiple consumers |
| GATE-SPEC-E004 | Approval | C3 missing human gate approval | Obtain + record `gate_approval` (gate GATE-SPEC + approver) |
| GATE-SPEC-E005 | Versioning | `framework/VERSION` not bumped | Bump `framework/VERSION` per `semver_impact` |
| GATE-SPEC-E006 | Conformance | Platform spec versions out of sync | Update both `FRAMEWORK_SPEC_VERSION` to match |
| GATE-SPEC-E007 | Conformance | Conformance suite failing | Fix the spec or the platform; never weaken a check |
| GATE-SPEC-E008 | Documentation | `CHANGELOG.md` not updated | Add a changelog entry for the spec change |
| GATE-SPEC-W001 | Migration | Breaking change without a per-platform migration note | Add a migration note for each platform |
| GATE-SPEC-W002 | Parity | One-platform conformance drift | Confirm both platforms track the new version |

### 7.2 Common Resolutions

```markdown
## GATE-SPEC-E001 Resolution
Add to the CHG document:

change_description:
  why: "[Why the spec must change — the rule/template/registry gap it closes]"
  trigger: "[What surfaced it — e.g. learnings entry LRN-NN across N projects]"

## GATE-SPEC-E002 Resolution
Set the SemVer impact and align the level:

change_control:
  semver_impact: minor   # major | minor | patch ; major => change_level: C3
  change_level: C2
```

---

**Related Documents**:

- [GATE_INTERACTION_DIAGRAM.md](./GATE_INTERACTION_DIAGRAM.md)
- [GATE_ERROR_CATALOG.md](./GATE_ERROR_CATALOG.md)
- [../README.md](../README.md) — CHG overview & source routing
- [../../../../docs/PROJECT.md](../../../../docs/PROJECT.md) §6 — change management roles
- [../templates/GATE_APPROVAL_FORM.md](../templates/GATE_APPROVAL_FORM.md)
