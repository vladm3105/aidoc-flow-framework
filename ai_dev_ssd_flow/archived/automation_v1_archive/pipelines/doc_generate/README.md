# Multi-Agent Document Generation Pipeline

> ## ⚠️ DEPRECATED
>
> **This pipeline is deprecated as of 2026-03-09.**
>
> Replaced by: **UCC (Unified Context Creation)**
> ```
> /opt/data/docs_flow_framework/ai_dev_ssd_flow/UCX/creation/run_ucc.sh
> ```
>
> UCC provides:
> - Multi-persona authoring with skill injection
> - Simpler single-pass architecture
> - Integrated with UCR/UCRem workflow
>
> See `../../DEPRECATED.md` for migration guide.

---

## Overview
The `run_generate.sh` pipeline is a 5-step orchestration script that uses an AI Expert Board to collaboratively author SDD-compliant framework documents (BRD, PRD, ADR, BDD, etc.).

Instead of relying on a single AI context window to write an entire complex document, this pipeline divides the work among multiple domain-specific personas, enforces strict template bounds via an independent Judge, and acts strictly on framework structure.

## The 5-Step Process
1. **Shared Context Assembly**: The orchestrator injects strict framework rules (`LAYER_REGISTRY`, `VALIDATION_STANDARDS`, and layer-specific `doc-*/SKILL.md` instructions). It optionally ingests an upstream document (like a BRD when authoring a PRD).
2. **Drafters**: Domain expert personas drafted in `generate.<type>.yaml` write specific sections of the document concurrently (e.g., QA Lead writes Acceptance Criteria, Tech Lead writes Constraints).
3. **Assembler**: The Chairperson persona compiles the independent drafts into a cohesive Version 1 (V1) draft matching the required framework structure.
4. **Judge**: A completely isolated, impartial LLM (often configured to a different base model, e.g. from Claude to GPT-4o) audits the V1 Draft purely on framework formatting, schema precision, and numbering standards.
5. **Final Editor**: The Chairperson takes the V1 Draft AND the Judge's audit critique to heavily self-edit, outputting an absolute perfect compliance-ready markdown document.

## Usage

```bash
run_generate.sh --type <doc_type> --outdir <output_dir> [options]
```

### Required Arguments
* `--type`: The document layer target (`brd`, `prd`, `adr`, `bdd`). This instructs the script to dynamically load `generate.<type>.yaml` and `.claude/skills/doc-<type>/SKILL.md`.
* `--outdir`: The directory target for the resulting `GENERATED_<TYPE>.md` and the `.generation_memory` debugging workspace.

### Optional Context Arguments
* `--upstream`: Passes an upstream dependency into the shared context. **Critical Note**: Always pass the parent layer when generating a child document (e.g. `--upstream docs/01_BRD/BRD-01.md` when `--type prd`).
* `--topic`: Passes unstructured raw input (such as meeting notes, feature request tickets, or a raw text idea) for the board to build upon.
* `--dry-run`: Will parse all YAML blocks and pipeline variables without making LLM API calls.

## Example Configuration & Execution

```bash
# Generate a new PRD located in /tmp, utilizing the parent BRD-01 as the source truth.
bash automation/pipelines/doc_generate/run_generate.sh \
  --type prd \
  --outdir /tmp/feature_prd \
  --upstream docs/01_BRD/BRD-01.md
```

## Adding New Targets
To enable this pipeline for a new document type (e.g., `EARS`):
1. Create `ai_dev_ssd_flow/AI_EXPERTS/generate.ears.yaml`
2. Define the independent drafters, the Chairperson assembler, the Judge, and the Editor blocks.
3. Ensure you have defined a `doc-ears/SKILL.md` to enforce exact layout requirements.
