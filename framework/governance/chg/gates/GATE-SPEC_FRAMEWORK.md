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

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-09-07 |
| Author | Framework Maintainer |
| Framework Version | 0.61.6 |


> **Position**: Orthogonal to the artifact cascade — governs the `framework/`
> spec itself, not a project's artifacts.
> **Change Sources**: Spec (a change to `framework/` templates, governance,
> registry, or `VERSION`).
> **Purpose**: Validate changes to the shared specification all consumers
> share, before they ripple to every consumer.

## 1. Purpose & Scope

The five artifact gates (GATE-01/03/06/08/CODE) govern changes to **artifact
instances** flowing down a project's BRD→Code chain. GATE-SPEC is different in
kind: it governs changes to the **shared contract that defines the layers** —
the templates, governance rules, registry, and version under `framework/`.

GATE-SPEC is therefore a **meta gate**, *orthogonal* to the artifact cascade. Its
"cascade" is not L1→Code; it is: **a spec change forces every consumer to
re-adopt the new `framework/VERSION` and re-pass the shared conformance suite.**
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

A change is routed to GATE-SPEC by its **target** (it edits normative
`framework/` files), not by which artifact layer it resembles. Downstream
internal development (a consumer's authoring wording or runtime code) is
**not** a spec change — it is an ordinary consumer PR, and does not enter
GATE-SPEC.

### 1.2 Scope: the frozen archive tier

Edits confined to `framework/archive/**` are **not** spec changes (#725).
They repair frozen history (dangling citations, snapshot gaps) without
touching any normative rule, template, playbook, or consumer-visible surface,
so they carry no `framework/VERSION` bump, no `CHANGELOG.md` entry, and no
GATE-SPEC approval obligation on their own. A change set that touches
normative `framework/` files alongside archive files is a spec change, and
the full gate applies.

## 2. Entry Criteria

| Criterion | Required | Validation |
|-----------|----------|------------|
| Spec target identified | Yes | The change edits `framework/` (template / governance / registry / VERSION) |
| Justification documented | Yes | `change_description.why` + `.trigger` — a promotion cites the motivating `.aidoc/project/governance/SELF_LEARNING.md` / profile signal |
| SemVer impact classified | Yes | `change_control.semver_impact` ∈ {major, minor, patch} |
| Change level proposed | Yes | ≥ C2 (a spec change is never C1 — it reaches ≥2 consumers); `major` ⇒ C3 |
| Consumer reach acknowledged | Yes | In-repo spec-version pins stay re-declared and the shared conformance suite stays green |

### 2.1 Pre-Gate Checklist

```markdown
- [ ] Change edits framework/ (templates / governance / registry / VERSION)
- [ ] change_description.why and .trigger populated (provenance for a promotion)
- [ ] semver_impact set (major | minor | patch)
- [ ] change_level proposed (>= C2; major => C3)
- [ ] CHANGELOG.md entry drafted
- [ ] For C3: downstream consumers notified (migration note per consumer)
```

## 3. Validation Checklist

The checks split three ways by enforcer (ROADMAP CHG-D1): the **record
validator** reads the CHG record (E001–E004); **continuous integration
(CI)** runs the diff-aware + suite checks (E005–E008); the **human** approval is
protected-branch review. The validator never grants approval.

### 3.1 Error Checks (Blocking)

| Check ID | Description | Enforcer | Validation |
|----------|-------------|----------|------------|
| GATE-SPEC-E001 | Spec change must carry provenance/justification | record (validator) | `change_description.why` and `.trigger` non-empty |
| GATE-SPEC-E002 | SemVer impact declared; `major` must be C3 | record (validator) | `semver_impact` ∈ {major,minor,patch}; if `major` then `change_level == C3` |
| GATE-SPEC-E003 | A framework-spec change is never C1 | record (validator) | `change_level` ≥ C2 |
| GATE-SPEC-E004 | C3 spec change requires human approval | record (validator) | C3 ⇒ `gate_approval.gate == GATE-SPEC` + non-null `approver` |
| GATE-SPEC-E005 | `framework/VERSION` must bump when normative `framework/**` changes (archive-tier-only edits exempt — §1.2) | CI (diff-aware) | VERSION changed in the PR diff |
| GATE-SPEC-E006 | Spec-version pins match the framework | CI (conformance) | in-repo `framework_version` pins re-declared (`sync-version-refs` clean), conformance green |
| GATE-SPEC-E007 | Shared conformance suite passes | CI (conformance) | `tests/conformance` green |
| GATE-SPEC-E008 | `CHANGELOG.md` updated (archive-tier-only edits exempt — §1.2) | CI (diff-aware) | CHANGELOG changed in the PR diff |

> **E002 mapping (one-directional):** `major` ⇒ C3 (required). `minor` / `patch`
> may be C2 — an additive change (a new optional knob, a new gate) reaches all
> consumers yet is not breaking, so it does not force C3. Only a breaking change
> escalates.

### 3.2 Warning Checks (Non-Blocking)

| Check ID | Description | Recommendation |
|----------|-------------|----------------|
| GATE-SPEC-W001 | `major` (breaking) change without a per-consumer migration note | Add a migration note for each consumer |
| GATE-SPEC-W002 | Change adopted by only a subset of consumers (parity drift) | Confirm all consumers track the new spec version |
| GATE-SPEC-W003 | Agent-facing spec change (template/governance guidance) without a recorded `SECURITY_REVIEW.md` assessment | Run the `SECURITY_REVIEW.md` checklist — a spec change reaches every consumer, so injected/unsafe guidance has the widest blast radius |
| GATE-SPEC-W004 | CHG touches documents with `framework_version` older than the new `framework/VERSION` but `version_action` is null | Set `version_action` to `upgrade` or `keep` with justification — stale framework_version is acceptable only when the schema is compatible |

## 4. Approval Workflow

### 4.1 Approval Matrix

| Change Level | Required Approvers | SLA |
|--------------|-------------------|-----|
| **C2** | Framework maintainer + 1 reviewer | 2 business days |
| **C3** (breaking) | Framework maintainer + **2** reviewers | 5 business days |
| **Emergency** | Not a typical spec path — a spec change is not a production hotfix; handle out-of-band and document |

The validator **prepares and verifies** the approval form; a **human** signs. It
must never mark a spec change "approved" — the human gate is
protected-branch review (required reviewers on `framework/**`).

### 4.2 Approval Form

For C2/C3, complete `templates/GATE_APPROVAL_FORM.md` with the change summary,
the affected `framework/` targets, the SemVer impact, the conformance result,
the risk/rollback sections, and the approver rows for the
level. Signature fields stay blank for the human.

## 5. Exit Criteria

| Criterion | C2 | C3 |
|-----------|----|----|
| All E-level checks pass (E001–E008) | Yes | Yes |
| W-level checks addressed | Review | Must address |
| Provenance complete | Yes | Yes |
| SemVer impact classified | Yes | Yes |
| Spec-version pins re-declared + conformance green | Yes | Yes |
| Human approval obtained per matrix | Yes | Yes |
| Rollback plan documented | Yes | Yes |
| Per-consumer migration note (for `major`) | n/a | Yes |

### 5.1 Exit Checklist

```markdown
- [ ] GATE-SPEC-E001..E004 pass (record-level)
- [ ] GATE-SPEC-E005..E008 pass (CI: VERSION bump, pins match, suite green, CHANGELOG)
- [ ] GATE-SPEC-W001..W003 reviewed (W003: SECURITY_REVIEW.md for agent-facing changes)
- [ ] CHG document created (>= C2)
- [ ] Human approval obtained per matrix (branch protection)
- [ ] Spec-version pins re-declared; conformance green
- [ ] Ready to merge
```

## 6. Routing Rules

GATE-SPEC does **not** route into the artifact cascade — it has no GATE-03/06/08
successor, because it changes the spec, not a project's artifacts. After
GATE-SPEC passes:

| Scenario | Next Step |
|----------|-----------|
| Spec change merged | Downstream consumers adopt the new `framework/VERSION` (update their spec-version pin, re-run conformance) |
| Consumer must adapt its authoring engine / runtime to the new spec | Ordinary consumer PR (not CHG) |

```
        CHANGE TO framework/ (template / governance / registry / VERSION)
                                  │
                              GATE-SPEC
                 (provenance · semver · >=C2 · human approval
                  · VERSION bump · pins match · suite green · CHANGELOG)
                                  │
                               PASSED
                                  │
              consumers re-adopt the new framework/VERSION
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
| GATE-SPEC-E005 | Versioning | `framework/VERSION` not bumped | Bump `framework/VERSION` per `semver_impact` (archive-tier-only repairs exempt — §1.2) |
| GATE-SPEC-E006 | Conformance | Spec-version pins out of sync | Re-declare in-repo pins (`bash hooks/sync-version-refs.sh`) and re-run conformance |
| GATE-SPEC-E007 | Conformance | Conformance suite failing | Fix the spec; never weaken a check |
| GATE-SPEC-E008 | Documentation | `CHANGELOG.md` not updated | Add a changelog entry for the spec change (archive-tier-only repairs exempt — §1.2) |
| GATE-SPEC-W001 | Migration | Breaking change without a per-consumer migration note | Add a migration note for each consumer |
| GATE-SPEC-W002 | Parity | Consumer adoption drift | Confirm all consumers track the new version |
| GATE-SPEC-W003 | Security | Agent-facing spec change without a `SECURITY_REVIEW.md` assessment | Run the security review (injection/abuse surface) for the changed guidance |
| GATE-SPEC-W004 | Versioning | CHG touches documents with stale `framework_version` without setting `version_action` | Set `version_action: upgrade` or `version_action: keep` with justification |

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
