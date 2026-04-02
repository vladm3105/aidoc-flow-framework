# MCP CLI Reference

| Field | Value |
| --- | --- |
| Status | Active |
| Version | 1.3 |
| Date | 2026-03-27 |
| Scope | Implemented command contracts in `mcp_sdd/src/mcp_server/cli/main.py` |

---

## 1. Commands

| Command | Required Arguments | Optional Arguments | Output |
| --- | --- | --- | --- |
| init | --project | none | project UCX scaffold (personas, templates, schemas, prompts) under `docs/UCX/` |
| create-build | --project --persona --doc-type --layer --template | --sections-json --out | creation prompt artifacts (`creation_prompt.md`, `creation_sidecar.json`) |
| create | --project --persona --doc-type --layer --template --target | --sections-json --overwrite --out | final document artifact + creation diagnostics |
| review-build | --project --persona --doc-type --template and one of (--sections-json, --document) | --layer --unified --one-turn --no-resume --session-ttl --clean-memory --clean-reports --keep-versions --out | review prompt artifacts and control summary |
| review | same as review-build | same as review-build | alias for review-build |
| validate | --project --doc-type --layer --document | --tier1-only --strict --format {text,json} --out | validation report artifacts and status. Supports both .md and .yaml document formats. YAML documents receive cross-section validation and structure checks. |
| validate-fix | --project --doc-type --layer --document | --validation-report --out | `TYPE-NN_{slug}_validation.md` derived copy written alongside source, plus fix report |
| remediate | --project --doc-type --layer --document | --review-report --out | remediation report. Supports both .md and .yaml document formats. YAML documents receive cross-section validation and structure checks. |
| remediate-fix | --project --doc-type --layer --document | --remediation-report --out | `TYPE-NN_{slug}_remediated.md` derived copy (canonical base name), plus apply report |
| prescreen | --document | --out | prescreen candidate report |
| consistency | --target | --format {text,json} --out | artifact lineage and stage-consistency report. Supports both .md and .yaml document formats. YAML documents receive cross-section validation and structure checks. |
| preflight | --project | --context {create,review,remediate,any} --document --format {text,json} --out | runtime and environment readiness report |
| scan | --report-file | --out | category-count scan report |
| scoring show | --report-file | none | score payload |
| scoring validate | --report-file --threshold | none | threshold validation payload |
| scoring compare | --baseline-report-file --candidate-report-file | none | score delta payload |

---

## 2. Exit Code Semantics

| Condition | Exit Code |
| --- | --- |
| Command success | 0 |
| Validation failure (`validate`) | 1 |
| Blocking consistency failures (`consistency`) | 1 |
| Blocked preflight (`preflight`) | 1 |
| Score threshold failure (`scoring validate`) | 1 |
| Command runtime error (`consistency`, `preflight`) | 2 |
| CLI usage or parser failure | 2 |

---

## 3. Output Directory Semantics

Default output behavior:

- Document-aware commands (`create-build` with `--sections-json`, `review-build`, `validate`, `validate-fix`, `remediate`, `remediate-fix`) write artifacts directly into the target document folder.
- `create` writes the final source document artifact to `--target` and writes creation diagnostics to the target document folder unless `--out` is provided.
- Fallback when no document context is available uses `.ucx/<stage>` under project docs.

Stage mapping:

- create-build -> `creation`
- create -> `creation` (diagnostic artifacts only; final document always uses `--target`)
- review-build/review -> `review`
- validate/validate-fix -> `validate`
- remediate/remediate-fix -> `remediation`

Rule:

- if `--out` points to `.ucx`, CLI appends stage automatically.
- if `--out` points to a concrete directory (including a document folder), CLI writes artifacts there directly.

---

## 4. Validation Target Resolution

When `--document` points to a folder, MCP resolves the target artifact as follows:

| Command | Resolution |
| --- | --- |
| `validate`, `validate-fix`, `remediate` | Find single file matching `^[A-Z]+-\d+_.+\.md$` with no `_validation` or `_remediated` suffix — use as source. Fall back to full folder set if no unique match. |
| `remediate-fix` | Find single file matching `^[A-Z]+-\d+_.+_validation\.md$` — use as `_validation` copy input. Fall back to full folder set if no unique match. |

When `validate --document` points to a markdown file, MCP applies canonical source redirection across all layers:

- If the parent folder has exactly one canonical source artifact (`TYPE-NN_{slug}.md`), and the provided file is any other markdown artifact in that folder (index, appendix, glossary, section split, or similar), validation executes on the canonical source artifact only.
- If no unique canonical source exists, validation executes on the provided file input.

This behavior ensures validation remains monolith-first for hybrid document folders across all layer types.

**Output filename rules:**

- `validate-fix` always uses the source stem: `{slug}_validation.md`
- `remediate-fix` always uses the canonical base stem (stripping `_validation` if present): `{slug}_remediated.md`

This ensures derived copies never accumulate stage suffixes (e.g., `_validation_remediated.md` is never produced).

---

## 5. Derived Artifact Lineage

The 6-stage lifecycle produces this artifact chain (applies to all document layers):

```text
TYPE-NN_{slug}.md                      ← stage 1: create
  ↓
validation_report.json/.txt            ← stage 2: validate
  ↓
TYPE-NN_{slug}_validation.md           ← stage 3: validate-fix
  ↓
UCX_review_report_vNNN.md              ← stage 4: review
  ↓
UCX_remediation_report_vNNN.md         ← stage 5: remediate
  ↓
TYPE-NN_{slug}_remediated.md           ← stage 6: remediate-fix
```

Reserved filename suffixes:

- `_validation` — produced by `validate-fix` only
- `_remediated` — produced by `remediate-fix` only; always uses canonical base stem

---

## 6. Validation Control Contract

`validate` controls:

- `--tier1-only`: evaluate blocking tier1 checks only
- `--strict`: treat warnings as failures
- `--format json`: emit deterministic JSON status payload to stdout

Validation target resolution:

- If `--document` points to a file and a unique canonical source exists in the same folder, MCP validates the canonical source artifact.
- If `--document` points to a folder and a canonical source artifact (`TYPE-NN_slug.md`) exists, MCP validates that source artifact.
- Otherwise MCP validates the folder markdown set (for section-based documents).

Review source resolution (`review-build`/`review` with `--document`):

- Canonical main source is selected first when uniquely identifiable (`TYPE-NN_{slug}.md`).
- Appendix files are then included using filename signals (`appendix`, `appendices`, `.18_`, `.18.`, `.19_`, `.19.`).
- Existing `--sections-json` mode remains supported for explicit section payload workflows.

JSON status payload fields:

- `report_path`
- `summary_path`
- `tier1_only`
- `strict`
- `errors`
- `warnings`
- `passed`

---

## 7. Examples

Project initialization:

```bash
# Initialize project UCX scaffold (run once; idempotent)
mcp init --project /path/to/project
# Writes: docs/UCX/skills/personas/, prompts/templates/*, templates/layers/NN_TYPE/*

# Assemble LLM creation prompt for a BRD
mcp create-build --project /path/to/project --persona architect --doc-type brd \
  --layer 01_BRD --template UCC_PROMPT_BRD_PROJECT.md
# Writes: creation_prompt.md, creation_sidecar.json

# After LLM generates content, write the final source document
mcp create --project /path/to/project --persona architect --doc-type brd \
  --layer 01_BRD --template UCC_PROMPT_BRD_PROJECT.md \
  --target /path/to/docs/01_BRD/BRD-01_platform/BRD-01_platform.md
```

Full 6-stage lifecycle for a BRD document:

```bash
# Stage 1 — Create source document
mcp create --project /path/to/project --persona architect --doc-type brd --layer 01_BRD \
  --template UCC_PROMPT_BRD_PROJECT.md \
  --target /path/to/docs/01_BRD/BRD-01_platform/BRD-01_platform.md

# Stage 2 — Validate source
mcp validate --project /path/to/project --doc-type brd --layer 01_BRD \
  --document /path/to/docs/01_BRD/BRD-01_platform/BRD-01_platform.md \
  --format json

# Stage 3 — Produce _validation copy
mcp validate-fix --project /path/to/project --doc-type brd --layer 01_BRD \
  --document /path/to/docs/01_BRD/BRD-01_platform/ \
  --validation-report /path/to/validation_report.json
# → BRD-01_platform_validation.md written alongside source

# Stage 4 — Review _validation copy
mcp review --project /path/to/project --persona architect --doc-type brd \
  --layer 01_BRD --sections-json /path/to/sections.json

# Stage 4 alternative — Review document folder (auto main + appendices)
mcp review --project /path/to/project --persona architect --doc-type brd \
  --layer 01_BRD --template UCR_PROMPT_BRD_PROJECT.md \
  --document /path/to/docs/01_BRD/BRD-01_platform/

# Stage 5 — Remediation plan against _validation copy
mcp remediate --project /path/to/project --doc-type brd --layer 01_BRD \
  --document /path/to/docs/01_BRD/BRD-01_platform/ \
  --review-report /path/to/UCX_review_report_v001.md

# Stage 6 — Produce _remediated copy
mcp remediate-fix --project /path/to/project --doc-type brd --layer 01_BRD \
  --document /path/to/docs/01_BRD/BRD-01_platform/ \
  --remediation-report /path/to/remediation_report.json
# → BRD-01_platform_remediated.md written alongside source
```

Other commands:

```bash
mcp prescreen --document /path/to/docs/01_BRD
mcp consistency --target /path/to/docs/01_BRD/BRD-01_platform/
mcp preflight --project /path/to/project --context review --format json
mcp scan --report-file /path/to/validation_report.json
mcp scoring show --report-file /path/to/validation_report.json
mcp scoring validate --report-file /path/to/validation_report.json --threshold 90
mcp scoring compare --baseline-report-file /path/to/a.json --candidate-report-file /path/to/b.json
```
