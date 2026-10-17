# Implementation Plan: Comprehensive Stale Documentation & Specification Remediation

## Document Control

| Field | Value |
|---|---|
| Version | 1.1 |
| Status | Approved |
| Last Updated | 2026-10-17 |
| Author | Framework Maintainer |
| Framework Version | 0.96.0 |
| Linked Issue | #1004 |
| Authority | [CHG_REQUEST_FLOWS.md](../framework/governance/CHG_REQUEST_FLOWS.md), [WORKTREE_FLOW.md](../framework/governance/WORKTREE_FLOW.md), [LINT_RULES.md](../framework/governance/LINT_RULES.md), [GATE-SPEC_FRAMEWORK.md](../framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md) |

---

## 1. Objective

Remediate systemic documentation staleness, retired gate requirements, architectural naming lag, and catalog divergence across [`framework/`](../framework/) and [`docs/`](../docs/).

Following the ratification of Change Requests **CHG-94** through **CHG-113**, multiple foundational architectural shifts occurred:

1. **Three-Tier Layer Architecture & SDD-GRAPH v2.0:** Transitioned from the legacy Dual-Template paradigm to the Three-Tier Architecture (Tier 1 `*-SWF-TEMPLATE.yaml` State Machine, Tier 2 `*-GRAPH-TEMPLATE.yaml` Property Graph Data Plane, Tier 3 compiled Markdown `.md`, and standard declarative `*-TEMPLATE.yaml`).
2. **Binary Topological Validation (BTV):** Formally retired qualitative heuristic readiness scoring (`>=90/100`) in favor of deterministic mathematical DAG integrity (`BTV PASS` / `FAIL`).
3. **Monolithic Register Retirement:** Frozen `framework/CHANGELOG.md` (CHG-94) and `framework/governance/DECISIONS.md` (CHG-95) as read-only tombstones, retiring `GATE-SPEC-E008`.
4. **Closed 5-Step Layer Lifecycle & Review Sagas:** Codified mandatory in-situ author remediation loops (`RemediateLayerDraft`), formal gate verification (`VerifyLayerCloseoutGate`), baseline sealing (`SealLayerDocumentBaseline`), and CloudEvent handoff emission across layer workflows (`SWF-L008`, `SWF-L009`, `sdd-layer-orchestration.sw.yaml`).
5. **Forbidden Symlinks & Workstation Parity:** Banned raw symlinks in consumer repos, standardizing `docs/sdd/graph/` and `.aidoc/Taskfile.yml`.

This plan establishes a phased, structured remediation ensuring complete consistency between framework specifications, governance gates, layer READMEs, and actual repo ground truth while strictly respecting repository PR sizing, worktree isolation, and conformance invariants.

---

## 2. Scope

### In Scope

1. **Framework Core Guides & Quick References**:
   - `framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`: Update Dual-Template section to Three-Tier Architecture; document SDD-GRAPH v2.0 property graph plane and 5-step closed lifecycle.
   - `framework/QUICK_REFERENCE.md`: Add `*-GRAPH-TEMPLATE.yaml` and `*-SWF-TEMPLATE.yaml` across all 10 layers; replace legacy `Target: >=90/100` table with deterministic BTV PASS criteria.
   - `framework/README.md`: Retire `CHANGELOG.md` E008 entry; update layout description with Three-Tier Architecture and layer template distribution.
   - `framework/AI_ASSISTANT_RULES.md`: Reconcile Section 14–22 template selection rules with Section 181 Three-Tier Model.
   - `AGENTS.md`: Update automated CHG validation list to explicitly include `CHG-L019` (`GOV-023`), `SWF-L008`, and `SWF-L009`.

2. **Governance Core, Gates & Catalogs**:
   - `framework/governance/DOC_GOVERNANCE_CORE.md`: Modernize `## Template Policy` to codify the Three-Tier Architecture.
   - `framework/governance/README.md`: Remove `CHANGELOG.md updated` and `DECISIONS.md GD entry` obligations; add missing `sdd-layer-orchestration.sw.yaml` and `iplan-execution.sw.yaml` to workflow catalog table; list `CHG-GRAPH-TEMPLATE.yaml`.
   - `framework/governance/DEFINITION_OF_DONE.md`: Remove `CHANGELOG updated` and platform `FRAMEWORK_SPEC_VERSION` requirements; update readiness score to BTV PASS.
   - `framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md` and `framework/playbooks/09_CHG/gate_spec_change.md`: Remove `- [ ] CHANGELOG.md entry drafted` and dead E008 references.
   - `framework/governance/chg/README.md` & `framework/layers/09_CHG/README.md`: Synchronize both files byte-identically, adding `CHG-GRAPH-TEMPLATE.yaml` and `CHG-SWF-TEMPLATE.yaml` to their templates table.
   - `framework/governance/REVIEW_REMEDIATION_FLOW.md`: Replace heuristic `>=90/100` scoring with BTV PASS and reflect integrated 5-step closed review sagas.
   - `framework/governance/ID_NAMING_STANDARDS.md`: Document `slice_id` and SDD-GRAPH v2.0 node ID standards.
   - `framework/registry/LAYER_REGISTRY.yaml`: Remove obsolete comment referencing platform `FRAMEWORK_SPEC_VERSION`.

3. **Layer Documentation Harmonization**:
   - Update `framework/layers/02_PRD/README.md` through `10_EVAL/README.md`: Standardize `## Three-Tier Architecture & Dual-Template Selection Matrix` section (preserving the substring `Dual-template` to satisfy conformance tests `test_spec_workflow.py` and `test_tdd_workflow.py`) and document Tier 3 compiled Markdown projections (matching `01_BRD/README.md` and `framework/layers/README.md`).

4. **Workstation Standards, Runbooks & Pattern Guides**:
   - `framework/governance/aidoc/UPGRADE-RUNBOOK.md`: Remove canon `CHANGELOG.md` reading step; replace symlink re-targeting with sanctioned pinned copy / submodule flows.
   - `docs/STARTUP_HANDOFF.md`: Replace `--kind symlink` instruction with `--kind pin` or submodule; remove `../framework/CHANGELOG.md` pointer; update `audit_threshold` guidance.
   - `docs/FEDERATED_READ_LAKE_PATTERN.md`: Scrub hardcoded `/home/ya/devd/*` path to `$WORKSPACE/*`.
   - `docs/PROJECT.md` and `docs/REPO_STRUCTURE.md`: Reconcile historical changelog text with tombstone reality.

5. **Governance Vehicle, Sizing & Conformance**:
   - Manage PR surface cap: Execute as either Option A (Split PRs: PR 1 Governance for `AGENTS.md` and plan, PR 2 Non-governance Docs-Only for framework files) or Option B (Single PR with in-session Founder OK).
   - Pre-modification archive: Archive original versions of touched framework files to `framework/archive/CHG-114/` before modification.
   - Author authorizing Change Request `framework/archive/CHG-114/CHG-114.yaml` (Class C2 Spec, DIR2C) and `IPLAN-114.yaml`.
   - Bump `framework/VERSION` and execute `hooks/sync-version-refs.sh`.
   - Provision dedicated per-task worktree per `WORKTREE_FLOW.md`.
   - Commit with mandatory OPS-0065 audit-trail line.

### Out of Scope

- Introducing new runtime platform dependencies or breaking engine neutrality (forbidden by D-0013 / GD-13).
- Modifying YAML schemas or changing existing node IDs in ratified `*-GRAPH-TEMPLATE.yaml` and `*-SWF-TEMPLATE.yaml` files.
- Resurrecting legacy platform repositories or example corpuses.

---

## 3. PR Sizing & Governance Strategy

Per [`AGENTS.md §Governance PRs`](../AGENTS.md), touching `AGENTS.md` or plan files qualifies a PR as a **Governance PR**, which imposes a strict limit of **$\le 3$ doc surfaces**:

- **Option A (Recommended Default — Two Sequential PRs):**
  1. **PR 1: Governance PR (`feature/chg-114-governance-agreement`)**:
     - Touches only `AGENTS.md` (adding `CHG-L019`, `SWF-L008`, `SWF-L009`) and `plans/STALE-DOCS-REMEDIATION-PLAN.md` ($\le 3$ surfaces).
     - Merges into `dev` cleanly without triggering surface cap violations.
  2. **PR 2: Non-Governance Docs-Only PR (`feature/chg-114-stale-docs-remediation`)**:
     - Executes Phases 1 through 5 across the remaining 25+ documentation files and `framework/archive/CHG-114/`.
     - Non-governance (docs-only) PRs have **no surface cap**.
- **Option B (Single Unified PR with Founder OK):**
  - If executed in a single PR, an in-session Founder OK must be recorded in the PR body and commit message:
    `Self-review skipped per founder OK — Governance PR surface cap carve-out for comprehensive doc remediation batch (CHG-114)`

---

## 4. Phased Implementation Plan

### Phase 1: Core Guides & Quick Reference Alignment

1. **`framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`**:
   - Replace Section `## Dual-Template Architecture` with `## Three-Tier Architecture & Dual-Template Selection Matrix (Tier 1 SWF, Tier 2 GRAPH, Tier 3 MD, and Declarative Alternative)`.
   - Document the 5-step closed layer lifecycle (authoring, review saga, in-situ remediation, gate verification, baseline sealing, CloudEvent handoff).
2. **`framework/QUICK_REFERENCE.md`**:
   - Expand `## Templates` table to include `*-GRAPH-TEMPLATE.yaml` and `*-SWF-TEMPLATE.yaml`.
   - Replace the `## Readiness Gates` table (`>=90/100`) with deterministic `Binary Topological Validation (BTV PASS)`.
3. **`framework/README.md` & `framework/AI_ASSISTANT_RULES.md`**:
   - Update `framework/README.md` lines 74 and 82–88: remove `CHANGELOG.md (E008)` document-of-record claim, update layer folder description to reflect the Three-Tier Model.
   - Update `framework/AI_ASSISTANT_RULES.md` lines 14–22: reconcile `Dual-Template Selection` with Section 181 `The Three-Tier Layer Model`.
4. **`AGENTS.md`**:
   - Update `Automated CHG validation` list to explicitly include `CHG-L019` (`GOV-023`), `SWF-L008`, and `SWF-L009`.

### Phase 2: Governance Core, Gates & Catalogs Remediation

1. **`framework/governance/DOC_GOVERNANCE_CORE.md`**:
   - Re-specify `## Template Policy` to codify the Three-Tier Architecture, referencing `*-GRAPH-TEMPLATE.yaml` (SDD-GRAPH v2.0) and `*-SWF-TEMPLATE.yaml`.
2. **`framework/governance/README.md`**:
   - Remove `CHANGELOG.md updated` and `DECISIONS.md GD entry` obligations from the framework self-changes table.
   - Update the CNCF Serverless Workflows table to include `sdd-layer-orchestration.sw.yaml` and `iplan-execution.sw.yaml`, bringing the listed catalog count to parity with the 32 workflows on disk.
   - Add `CHG-GRAPH-TEMPLATE.yaml` to the Governance Templates table.
3. **`framework/governance/chg/README.md` & `framework/layers/09_CHG/README.md` (Byte-Identity Mirror)**:
   - Simultaneously update both mirrors to list `CHG-GRAPH-TEMPLATE.yaml` and `CHG-SWF-TEMPLATE.yaml`, preserving exact byte identity per `test_readme_copies_identical.py`.
4. **`framework/governance/DEFINITION_OF_DONE.md`**:
   - Remove `CHANGELOG updated` and `every platform's FRAMEWORK_SPEC_VERSION re-declared` from Section "Change-level".
   - Replace `readiness score meets the layer gate threshold` with `passes Binary Topological Validation (BTV PASS)`.
5. **`framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md` & `framework/playbooks/09_CHG/gate_spec_change.md`**:
   - Remove `- [ ] CHANGELOG.md entry drafted` checkboxes and purge legacy E008 warnings.
6. **`framework/governance/REVIEW_REMEDIATION_FLOW.md`**:
   - Modernize Section 21–64: replace qualitative `>=90/100` scoring terminology with deterministic `BTV PASS`.
   - Note integration of review sagas into layer SWF state machines per CHG-111 and CHG-112.
7. **`framework/governance/ID_NAMING_STANDARDS.md`**:
   - Add a dedicated subsection defining `slice_id` naming patterns (`INIT-NN_<slug>`, `<LAYER>-NN_slice`) and SDD-GRAPH v2.0 typed node ID tokens (`SEED-<slug>`, `MODULE-NN`, `BRD.NN.SS.xxxx`, etc.).
8. **`framework/registry/LAYER_REGISTRY.yaml`**:
   - Remove line 35 comment referring to retired platforms re-declaring `FRAMEWORK_SPEC_VERSION`.

### Phase 3: Layer README Harmonization (02_PRD through 10_EVAL)

1. For each layer README in `framework/layers/02_PRD/README.md` through `framework/layers/10_EVAL/README.md`:
   - Replace legacy `## Dual-Template Architecture` section headings with:
     `## Three-Tier Architecture & Dual-Template Selection Matrix`
     (strictly preserving the substring `Dual-template` to satisfy conformance tests `test_spec_workflow.py:167` and `test_tdd_workflow.py:160`).
   - Document Tier 1 (`*-SWF-TEMPLATE.yaml`), Tier 2 (`*-GRAPH-TEMPLATE.yaml`), Tier 3 compiled Markdown, and the standard declarative template alternative, aligning with `01_BRD/README.md` and `framework/layers/README.md`.

### Phase 4: Workstation, Runbooks & Project Documentation Scrubbing

1. **`framework/governance/aidoc/UPGRADE-RUNBOOK.md`**:
   - Remove Step 1 bullet instructing reading `canon CHANGELOG.md`.
   - Update Step 2 to remove symlink instructions, aligning with `BOOTSTRAP.md` §3 and `AIDOC_WORKSTATION_STANDARD.md` §8.
2. **`docs/STARTUP_HANDOFF.md`**:
   - In Step 1, remove `--kind symlink` example, replacing it with the standard `--kind pin` or git submodule command.
   - Update Step 2 `audit_threshold` description to reference BTV validation rather than numeric score floors.
   - In Section Historical Archive, clarify that `framework/CHANGELOG.md` is a frozen tombstone and point to GitHub Releases / Change Requests.
3. **`docs/FEDERATED_READ_LAKE_PATTERN.md`**:
   - Scrub `/home/ya/devd/*` on line 165 to generic `$WORKSPACE/*`.
4. **`docs/PROJECT.md` & `docs/REPO_STRUCTURE.md`**:
   - Annotate root and framework `CHANGELOG.md` references as historical tombstones.

### Phase 5: Verification, Conformance & Governance Vehicles

1. **Worktree Provisioning**:

   ```bash
   git worktree add ../aidoc-framework-chg-114 -b feature/chg-114-stale-docs-remediation origin/dev
   cd ../aidoc-framework-chg-114
   ```

2. **Pre-Modification Archiving**:
   - Copy original versions of all modified framework files into `framework/archive/CHG-114/` prior to editing.
3. **Governance Vehicles**:
   - Author authorizing Change Request `framework/archive/CHG-114/CHG-114.yaml` (Class C2 Spec, DIR2C).
   - Author Implementation Plan `framework/archive/CHG-114/IPLAN-114.yaml`.
4. **Version Bump & Fan-out**:
   - Bump `framework/VERSION` (e.g. `0.96.0 → 0.96.1`).
   - Run `bash hooks/sync-version-refs.sh`.
5. **Quality Gates & Conformance Verification**:
   - Run `python3 sdd_doc_lint/chg_lint.py framework/archive/CHG-114/CHG-114.yaml` (assert clean).
   - Run `python3 -m sdd_doc_lint.swf_lint framework/governance/workflows/` (assert clean).
   - Run `python3 -m unittest discover -s tests/conformance -v` (assert 100% pass).
   - Run `python3 .agents/skills/verified-planning/check_plan.py plans/STALE-DOCS-REMEDIATION-PLAN.md`.
6. **Commit & Push Audit-Trail**:
   - Commit changes with mandatory body phrase:
     `Multi-agent self-review per OPS-0065 (planner, reviewer, architect): PASS`
   - Push to origin and open PR to `dev`.
7. **Cleanup Order Guard**:
   - After squash-merge into `dev`, execute order guard:
     `git worktree remove ../aidoc-framework-chg-114` *before* deleting branch `feature/chg-114-stale-docs-remediation`.

---

## Claim ledger

| # | Claim | Symbol | Citation |
|---|---|---|---|
| 1 | `framework/README.md` lists CHANGELOG.md as document of record for spec changes under retired E008 | `CHANGELOG.md` | framework/README.md:74 |
| 2 | `framework/governance/README.md` lists CHANGELOG.md update as mandatory for framework self-changes | `archive-tier-only repairs exempt` | framework/governance/README.md:147 |
| 3 | `framework/governance/README.md` requires GD entry in DECISIONS.md for significant decisions | `for significant decisions` | framework/governance/README.md:153 |
| 4 | `GATE-SPEC_FRAMEWORK.md` pre-gate checklist still contains CHANGELOG.md entry drafted checkbox | `- [ ] CHANGELOG.md entry drafted` | framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md:92 |
| 5 | `gate_spec_change.md` playbook still contains CHANGELOG.md entry drafted checkbox | `- [ ] CHANGELOG.md entry drafted` | framework/playbooks/09_CHG/gate_spec_change.md:149 |
| 6 | `UPGRADE-RUNBOOK.md` directs reading canon CHANGELOG.md entry for new version | `The canon` | framework/governance/aidoc/UPGRADE-RUNBOOK.md:30 |
| 7 | `DEFINITION_OF_DONE.md` change-level criteria mandates platforms re-declare FRAMEWORK_SPEC_VERSION | `every platform's` | framework/governance/DEFINITION_OF_DONE.md:42 |
| 8 | `LAYER_REGISTRY.yaml` comments that platforms re-declare framework_version in FRAMEWORK_SPEC_VERSION | `platforms re-declare in FRAMEWORK_SPEC_VERSION` | framework/registry/LAYER_REGISTRY.yaml:35 |
| 9 | `QUICK_REFERENCE.md` readiness gates table still lists numeric target >=90/100 | `\| PRD-Ready \| >=90/100 \| BRD objectives, requirements, scope complete \|` | framework/QUICK_REFERENCE.md:56 |
| 10 | `SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` section header still specifies Dual-Template Architecture | `## Dual-Template Architecture: Standard vs. Workflow-Driven SDD` | framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md:82 |
| 11 | `DOC_GOVERNANCE_CORE.md` template policy still codifies Dual-Template Architecture only | `Dual-Template Architecture (GD-51 through GD-61)` | framework/governance/DOC_GOVERNANCE_CORE.md:57 |
| 12 | `AI_ASSISTANT_RULES.md` top template section still specifies Dual-Template Selection | `Dual-Template Selection (GD-51 through GD-61)` | framework/AI_ASSISTANT_RULES.md:16 |
| 13 | `BOOTSTRAP.md` strictly bans raw filesystem symlinks in version control | `Raw filesystem symlinks in version control are strictly forbidden` | framework/governance/aidoc/BOOTSTRAP.md:55 |
| 14 | `STARTUP_HANDOFF.md` quickstart step 1 still provides a symlink installation command | `--kind symlink --shared /path/to/framework` | docs/STARTUP_HANDOFF.md:40 |
| 15 | `FEDERATED_READ_LAKE_PATTERN.md` leaks developer workstation path /home/ya/devd/* | `/home/ya/devd/*` | docs/FEDERATED_READ_LAKE_PATTERN.md:165 |
| 16 | `AGENTS.md` automated CHG validation list stops at CHG-L018 | `Automated CHG validation` | AGENTS.md:140 |
| 17 | `02_PRD/README.md` templates table lists PRD-TEMPLATE.yaml | `PRD-TEMPLATE.yaml` | framework/layers/02_PRD/README.md:41 |
| 18 | `framework/governance/README.md` workflow catalog header table | `\| Workflow File \| Layer / Domain \| Governs \|` | framework/governance/README.md:78 |
| 19 | `AGENTS.md` caps governance PRs touching working agreements or plans at <=3 doc surfaces | `cap it at ≤3 doc surfaces` | AGENTS.md:203 |
| 20 | `test_spec_workflow.py` asserts Dual-template substring presence in layer 06 documentation | `self.assertIn("Dual-template", content)` | tests/conformance/test_spec_workflow.py:167 |

---

## Review log

### Pass 1

- **Date**: 2026-10-17T18:05:00Z
- **Reviewer**: AI Architectural Reviewer
- **Findings**:
  1. *Scope Completeness*: Verified that all claims in the Claim Ledger resolve to existing lines and exact symbols in the codebase.
  2. *Cross-Layer Parity*: Noted that layers 02_PRD through 10_EVAL require consistent adoption of the Three-Tier Architecture section header and Tier 3 compiled markdown description to match Layer 01 and the root layers README. Added explicitly to Phase 3.
  3. *Workflow Catalog*: Identified that `sdd-layer-orchestration.sw.yaml` and `iplan-execution.sw.yaml` were omitted from `framework/governance/README.md`, leaving it at 29 instead of 32 workflows. Added to Phase 2.
- **Resolution**: Integrated all findings into Phase 2 and Phase 3 deliverables.

### Pass 2

- **Date**: 2026-10-17T18:15:00Z
- **Reviewer**: Adversarial Governance & Conformance Lens
- **Findings**:
  1. *Governance PR Sizing Blocker*: Bundling `AGENTS.md` into the same PR with 25+ documentation files converts the PR into a Governance PR, which violates the $\le 3$ doc surface cap (`AGENTS.md:203`).
  2. *Conformance Test Failure Risk*: Conformance tests (`test_spec_workflow.py:167` and `test_tdd_workflow.py:160`) assert `self.assertIn("Dual-template", content)`. Replacing the section header with a plain "Three-Tier Architecture" without retaining "Dual-template" will break the tests.
  3. *Missing VERSION Bump & Fan-out*: Normative framework edits require a version bump in `framework/VERSION` and running `hooks/sync-version-refs.sh`.
  4. *Missing Pre-Modification Archiving*: GATE-SPEC mandates copying original files into `framework/archive/CHG-114/` before modification.
  5. *Commit Audit Trail Omission*: Pre-push hook requires the literal OPS-0065 review phrase in the commit message body.
  6. *Worktree Flow Omission*: Missing worktree provisioning and §3.8 order guard (`worktree remove` before branch delete).
  7. *CHG README Mirror Byte-Identity*: `framework/governance/chg/README.md` and `framework/layers/09_CHG/README.md` must be updated simultaneously to satisfy `test_readme_copies_identical.py`.
- **Resolution**: Added Section 3 (PR Sizing & Governance Strategy with Option A/B), updated Phase 3 to mandate the composite `Three-Tier Architecture & Dual-Template Selection Matrix` title, and expanded Phase 5 with archiving, version bump, worktree commands, commit audit trail, and mirror identity rules.

### Pass 3

- **Date**: 2026-10-17T18:22:00Z
- **Reviewer**: Independent Fresh-Context Evaluator
- **Findings**: No remaining findings. All 7 identified gaps from Pass 2 are resolved in the specification. Claim ledger expanded to 20 verified citations, covering the governance PR cap and test assertion invariants. Deterministic gate passes cleanly.
- **Status**: Ready
