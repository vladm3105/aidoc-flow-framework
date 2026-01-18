---
title: "MVP Development Workflow"
tags:
  - framework-guide
  - mvp-workflow
custom_fields:
  document_type: guide
  priority: high
  development_status: active
---

# MVP Development Workflow Guide

**Version**: 2.0
**Purpose**: Streamlined workflow for rapid Minimum Viable Product (MVP) development using AI Dev Flow.
**Target Audience**: AI Assistants and small teams (2-10 people) building early-stage products.

> **🎯 MVP-ONLY FRAMEWORK**
>
> As of v2.0, the framework uses MVP templates exclusively.
> Full templates have been deprecated and archived in `archived/` subdirectories.
>
> See [LAYER_REGISTRY.yaml](./LAYER_REGISTRY.yaml) for `template` field definitions.

Note: Some examples in this guide show a portable `docs/` root. In this repository, artifact folders live under `ai_dev_flow/` without the `docs/` prefix. Use zero-padded paths (e.g., `01_BRD`, `02_PRD`). Run commands from the repo root, e.g., `python3 ai_dev_flow/scripts/validate_prd.py ai_dev_flow/02_PRD`. For the automation-focused flow, see `ai_dev_flow/SDD_AUTOMATION_WORKFLOW.md`.

Important MVP note: MVP artifacts are single, flat files. Split only when a document is too large for AI assistants to handle in one file; otherwise ignore `DOCUMENT_SPLITTING_RULES.md` for MVP.

---

## 🚀 The MVP Track

The **MVP Track** offers a faster, lighter alternative to the standard 15-layer framework while maintaining full traceability and compliance.

### Key Differences vs Standard Flow

| Feature | Standard Flow | MVP Track |
|---------|---------------|-----------|
| **Templates** | Full multi-section templates | **Streamlined, single-file MVP templates** |
| **File Structure** | May use document splitting rules | **Single flat files; no splitting** |
| **BRD Layer** | Detailed strategy & finance | **Hypothesis & Core Validation** |
| **Requirements** | BRD → PRD → EARS → REQ | **BRD → PRD → EARS → REQ** (Streamlined) |
| **Validation** | Strict, full compliance | **Focus on active documents & links** |
| **Time-to-Code** | 1-2 Weeks (Planning) | **1-2 Days (Planning)** |

---

## 🔄 The 6-Step Universal Verification Loop

For **EVERY** step in the workflow below (BRD, PRD, etc.), follow this exact micro-workflow:

1.  **PLAN**: Create/Update `X-00_index.md` & `X-00_required_documents_list.md`.
2.  **PRE-CHECK**: Run `python3 ai_dev_flow/scripts/validate_documentation_paths.py --root ai_dev_flow` (verify planning docs exist for the layer).
3.  **SETUP**: Load `X_CREATION_RULES.md` + `X-MVP-TEMPLATE.md`. See also: [`ID_NAMING_STANDARDS.md`](./ID_NAMING_STANDARDS.md). Note: MVP uses flat files only; do not use document splitting rules.
4.  **GENERATE**: Create the file (e.g., `X-01.md`).
5.  **VALIDATE**: Run single-file validator (e.g., `validate_brd.py`). Fix errors.
6.  **CORPUS CHECK**: Once all files in *required list* are done, run full corpus validation.

---

## ⚡ 7-Step MVP Workflow

### Step 1: Business Hypothesis (BRD) — **Day 1 (Morning)**
**Artifacts**: `01_BRD/BRD-MVP-TEMPLATE.md`, `BRD_CREATION_RULES.md`
1.  **Plan**: Edit `BRD-00_index.md`. Create `BRD-00_required_documents_list.md` (List: BRD-01).
2.  **Pre-Check**: Verify index/required lists structure; run `python3 ai_dev_flow/scripts/validate_documentation_paths.py --root ai_dev_flow`.
3.  **Generate**: "Create BRD-01 using BRD-MVP-TEMPLATE. Focus on Hypothesis."
4.  **Validate**: `python3 ai_dev_flow/scripts/validate_brd.py ai_dev_flow/01_BRD`
5.  **Corpus Validation**: `python3 ai_dev_flow/scripts/validate_all.py ai_dev_flow --layer BRD`

### Step 2: Core Product Definition (PRD) — **Day 1 (Morning)**
**Artifacts**: `02_PRD/PRD-MVP-TEMPLATE.md`, `PRD_CREATION_RULES.md`
1.  **Plan**: Edit `PRD-00_index.md`. Create `PRD-00_required_documents_list.md` (List: PRD-01).
2.  **Pre-Check**: Ensure `BRD-01` exists; verify PRD index/required list; run `python3 ai_dev_flow/scripts/validate_documentation_paths.py --root ai_dev_flow`.
3.  **Generate**: "Create PRD-01 using PRD-MVP-TEMPLATE. List P1 features."
4.  **Validate**: `python3 ai_dev_flow/scripts/validate_prd.py ai_dev_flow/02_PRD`
5.  **Corpus Validation**: `python3 ai_dev_flow/scripts/validate_links.py --docs-dir ai_dev_flow` (check traceability)

### Step 3: Logic Mapping (EARS) — **Day 1 (Afternoon)**
**Artifacts**: `03_EARS/EARS-MVP-TEMPLATE.md`, `EARS_CREATION_RULES.md`
1.  **Plan**: Edit `EARS-00_index.md`, `EARS-00_required_documents_list.md`.
2.  **Pre-Check**: Ensure `PRD-01` exists; verify EARS index/required list; run `python3 ai_dev_flow/scripts/validate_documentation_paths.py --root ai_dev_flow`.
3.  **Generate**: "Create EARS-01. Map PRD features to MVP Logic."
4.  **Validate**: `python3 ai_dev_flow/scripts/validate_ears.py --path ai_dev_flow/03_EARS`
5.  **Corpus Validation**: `python3 ai_dev_flow/scripts/validate_all.py ai_dev_flow --layer EARS`

### Step 4: Critical Scenarios (BDD) — **Day 1 (Late Afternoon)**
**Artifacts**: `04_BDD/BDD-MVP-TEMPLATE.feature`, `BDD_CREATION_RULES.md`
1.  **Plan**: Edit `BDD-00_index.md` (one per suite), `required_documents_list`.
2.  **Pre-Check**: Ensure `EARS-01` exists; verify BDD index/required list; run `python3 ai_dev_flow/scripts/validate_documentation_paths.py --root ai_dev_flow`.
3.  **Generate**: "Create `BDD-01_checkout.feature`. Include Happy Path + Critical Error Path scenarios."
4.  **Validate**: `python3 ai_dev_flow/scripts/validate_bdd.py ai_dev_flow/04_BDD`
5.  **Corpus Validation**: Verify Gherkin syntax across suite.

### Step 5: Lean Architecture (ADR & SYS) — **Day 2 (Morning)**
**Artifacts**: MVP Templates for 05_ADR/SYS.
1.  **Plan**: Identify *irreversible* decisions (ADR) and System Boundary (SYS).
2.  **Pre-Check**: Ensure upstream docs exist (`BRD-01`, `PRD-01`, `EARS-01`); verify `ADR-00_index.md` and `SYS-00_index.md` + required lists; run `python3 ai_dev_flow/scripts/validate_documentation_paths.py --root ai_dev_flow`.
3.  **Generate**: `ADR-01` (Tech Stack), `SYS-01` (System Spec).
4.  **Validate**:
    - `python3 ai_dev_flow/scripts/validate_adr.py ai_dev_flow/05_ADR`
    - `python3 ai_dev_flow/scripts/validate_sys.py ai_dev_flow/06_SYS`
5.  **Corpus Validation**: `python3 ai_dev_flow/scripts/validate_all.py ai_dev_flow --layer ADR --layer SYS`

### Step 6: Atomic Requirements (REQ) — **Day 2 (Mid-Day)**
**Artifacts**: `07_REQ/REQ-MVP-TEMPLATE.md`, `REQ_CREATION_RULES.md`
1.  **Plan**: List all required REQ files in `REQ-00_required_documents_list.md`.
2.  **Pre-Check**: Ensure upstream docs exist (`ADR-01`, `SYS-01`); verify REQ index/required list; run `python3 ai_dev_flow/scripts/validate_documentation_paths.py --root ai_dev_flow`.
3.  **Generate**: Batch creation of atomic requirements.
4.  **Validate** (per file):
    - `find ai_dev_flow/07_REQ -name 'REQ-*.md' -exec bash ai_dev_flow/scripts/validate_req_template.sh {} \;`
5.  **Corpus Validation**: `python3 ai_dev_flow/scripts/validate_requirement_ids.py --directory ai_dev_flow/07_REQ` (unique IDs)

### Step 7: Spec & Code (SPEC -> TASKS) — **Day 2 (Afternoon)**
**Artifacts**: Standard `SPEC` (YAML), `TASKS`.
1.  **Plan**: Map REQs to Specs.
2.  **Pre-Check**: Ensure required REQ files exist; verify any 10_SPEC/TASKS index/required lists used; run `python3 ai_dev_flow/scripts/validate_documentation_paths.py --root ai_dev_flow`.
3.  **Generate**: Specs and Task Lists.
4.  **Validate**: `python3 ai_dev_flow/scripts/validate_spec.py ai_dev_flow/10_SPEC`.
5.  **Corpus Validation**: `python3 ai_dev_flow/scripts/validate_links.py --docs-dir ai_dev_flow` (final pre-code check).

---

## 🔁 MVP-to-Production Loop

Create an MVP, fix defects, promote to production, add features as a new MVP based on the current product, fix defects, and repeat. Use MVP templates by default; split files only when size blocks AI assistants.

## 🛠️ Validation for MVP

When using the MVP track, run validation with awareness:

1. **Use Specific Scripts**:
   - Traceability is still strictly enforced.
   - Use `python3 ai_dev_flow/scripts/validate_links.py --docs-dir ai_dev_flow` frequently.
   - Optional cross-checks:
     - Forward refs: `python3 ai_dev_flow/scripts/validate_forward_references.py ai_dev_flow`
     - Cross-doc: `python3 ai_dev_flow/scripts/validate_cross_document.py --all --strict`

2. **Ignore "Missing Section" Warnings**:
   - MVP templates intentionally omit sections found in full templates.
   - If `validate_brd.py` complains about missing "Financial Analysis", **ignore it**.
   - **Green Flag**: As long as Traceability Links (@brd, @req) are valid, you are good.

3. **Use MVP Validator Profile**:
   - Set `custom_fields.template_profile: mvp` in MVP template frontmatter to relax non-critical checks to warnings during drafting.
   - Use the full profile (omit `template_profile` or set `full`) for strict/enterprise runs.

```yaml
---
custom_fields:
  template_profile: mvp
---
```

---

## 🔄 Migration to Full Framework

See the "Migration" section at the bottom of every MVP template when you are ready to scale.

1. **Trigger**: Product market fit achieved, team grows >10, or compliance audit needed.
2. **Action**: Create new `BRD-02`, `PRD-02` using the **FULL templates**.
3. **Traceability**: Link new full documents to original MVP ones as "Supersedes".

---

### Primary Workflow Command (Autopilot)

**The recommended way to run the entire MVP workflow:**

```bash
# Start new project
python3 ai_dev_flow/scripts/mvp_autopilot.py --root ai_dev_flow --intent "My MVP Idea" --auto-fix

# Resume existing project (Generate missing files + Validate)
python3 ai_dev_flow/scripts/mvp_autopilot.py --root ai_dev_flow --resume --auto-fix

# Validate only (no new files)
python3 ai_dev_flow/scripts/mvp_autopilot.py --root ai_dev_flow --resume --skip-validate
```

### Manual Validation Commands (Debugging)

- **Orchestrator (All)**: `python3 ai_dev_flow/scripts/validate_all.py ai_dev_flow --all --report markdown`
- **Plan Check**: `python3 ai_dev_flow/scripts/validate_documentation_paths.py --root ai_dev_flow`
- **BRD**: `python3 ai_dev_flow/scripts/validate_brd.py ai_dev_flow/01_BRD`
- **PRD**: `python3 ai_dev_flow/scripts/validate_prd.py ai_dev_flow/02_PRD`
- **EARS**: `python3 ai_dev_flow/scripts/validate_ears.py --path ai_dev_flow/03_EARS`
- **BDD**: `python3 ai_dev_flow/scripts/validate_bdd.py ai_dev_flow/04_BDD`
- **ADR**: `python3 ai_dev_flow/scripts/validate_adr.py ai_dev_flow/05_ADR`
- **SYS**: `python3 ai_dev_flow/scripts/validate_sys.py ai_dev_flow/06_SYS`
- **SPEC**: `python3 ai_dev_flow/scripts/validate_spec.py ai_dev_flow/10_SPEC`

- **Links**: `python3 ai_dev_flow/scripts/validate_links.py --docs-dir ai_dev_flow`
