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

**Version**: 1.0
**Purpose**: Streamlined workflow for rapid Minimum Viable Product (MVP) development using AI Dev Flow.
**Target Audience**: AI Assistants and small teams (2-10 people) building early-stage products.

---

## 🚀 The MVP Track

The **MVP Track** offers a faster, lighter alternative to the standard 16-layer framework while maintaining full traceability and compliance.

### Key Differences vs Standard Flow

| Feature | Standard Flow | MVP Track |
|---------|---------------|-----------|
| **Templates** | Full multi-section templates | **Streamlined, single-file MVP templates** |
| **BRD Layer** | Detailed strategy & finance | **Hypothesis & Core Validation** |
| **Requirements** | BRD → PRD → EARS → REQ | **BRD → PRD → REQ** (EARS merged into PRD) |
| **Validation** | Strict, full compliance | **Focus on active documents & links** |
| **Time-to-Code** | 1-2 Weeks (Planning) | **1-2 Days (Planning)** |

---

## ⚡ 5-Step MVP Workflow

### Step 1: Business Hypothesis (BRD)
**Artifact**: `BRD/BRD-MVP-TEMPLATE.md`
- **Goal**: Define the *one* core problem and *one* solution hypothesis.
- **AI Prompt**: "Create an MVP BRD for [Project]. Focus on validating [Hypothesis] with 5-10 core features."

### Step 2: Core Product Definition (PRD)
**Artifact**: `PRD/PRD-MVP-TEMPLATE.md`
- **Goal**: List the 5-15 "Must Have" features.
- **Changes**: 
    - Skip detailed user indices.
    - Merge "EARS" requirements into User Stories if simple.
- **AI Prompt**: "Create an MVP PRD based on BRD-01. List only P1 features needed for launch."

### Step 3: lean Architecture (ADR & SYS)
**Artifacts**: `ADR/ADR-MVP-TEMPLATE.md`, `SYS/SYS-MVP-TEMPLATE.md`
- **Goal**: Make "Good Enough" technical decisions.
- **ADR**: Only document *irreversible* decisions (e.g., Cloud Provider, Language, Database). Skip minor choices.
- **SYS**: Define high-level system boundary and 3-5 core quality attributes (e.g., "Must handle 100 concurrent users").

### Step 4: Atomic Requirements (REQ)
**Artifact**: `REQ/REQ-MVP-TEMPLATE.md`
- **Goal**: Atomic, testable units for code generation.
- **Streamlining**: 
    - Use broader requirements where possible.
    - Focus on "Happy Path" and critical errors only.

### Step 5: Spec & Code (SPEC -> CODE)
**Artifact**: Standard `SPEC` (YAML) and `TASKS`.
- **Goal**: Generate code.
- **Note**: The SPEC/TASKS layers remain standard to ensure the AI coding assistant has precise instructions.

---

## 📅 MVP Kickoff Schedule (Day 1-2)

Accelerated timeline for getting to code by Day 3.

### Day 1: Definition & Design
1. **Morning**: 
   - Initialize project.
   - Generate `BRD-01` (MVP).
   - Generate `PRD-01` (MVP).
2. **Afternoon**:
   - Generate `ADR-01` (Tech Stack).
   - Generate `SYS-01` (System Baseline).

### Day 2: Requirements & Specs
1. **Morning**:
   - Generate `REQ` documents (Batch generation).
   - Validate links (`scripts/validate_links.py`).
2. **Afternoon**:
   - Generate `SPEC` files (YAML).
   - Generate `TASKS`.
   - **Start Coding**.

---

## 🛠️ Validation for MVP

When using the MVP track, run validation with awareness:

1. **Use Specific Scripts**:
   - Traceability is still strictly enforced.
   - Use `scripts/validate_links.py` frequently.

2. **Ignore "Missing Section" Warnings**:
   - MVP templates intentionally omit sections found in full templates.
   - If `validate_brd.py` complains about missing "Financial Analysis", **ignore it**.
   - **Green Flag**: As long as Traceability Links (@brd, @req) are valid, you are good.

---

## 🔄 Migration to Full Framework

See the "Migration" section at the bottom of every MVP template when you are ready to scale.

1. **Trigger**: Product market fit achieved, team grows >10, or compliance audit needed.
2. **Action**: Create new `BRD-02`, `PRD-02` using the **FULL templates**.
3. **Traceability**: Link new full documents to original MVP ones as "Supersedes".

---
