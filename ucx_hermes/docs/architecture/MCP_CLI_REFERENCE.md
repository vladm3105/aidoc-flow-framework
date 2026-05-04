# MCP CLI Reference

| Field | Value |
| --- | --- |
| Status | Active |
| Version | 2.1 |
| Date | 2026-05-04 |
| Scope | Implemented command contracts in `ucx_hermes/src/mcp_server/cli/main.py` |

---

## 1. Commands

| Command | Required Arguments | Optional Arguments | Output |
| --- | --- | --- | --- |
| init | --project | --update --update-mappings | project UCX scaffold (personas, templates, schemas, prompts) under `UCX/`. With `--update`: sync stale files (protects persona_mappings.yaml). With `--update-mappings`: also reset persona_mappings.yaml. |
| personas-show | --project | --phase --doc-type --format {text,json} | persona assignments table (phase → doctype → persona list) |
| personas-set | --project --phase --doc-type --personas | none | update persona list for a phase+doctype, validate persona files exist |
| personas-diff | --project | --format {text,json} | comparison of project persona mappings vs framework defaults |
| env-show | --project | --format {text,json} | project .env keys without values, blocked system vars, key count |
| get-project | (none) | (none) | resolved default project from `SDD_DEFAULT_PROJECT` env var |
| create-build | --project --doc-type --layer --template | --personas --sections-json --out | creation prompt artifacts (`creation_prompt.txt`, `creation_prompt_sidecar.json`, `creation_prompt_inspection.json`) |
| create | --project --doc-type --layer --template --target | --personas --sections-json --overwrite --out | final document artifact + creation diagnostics |
| review-build | --project --doc-type --template and one of (--sections-json, --document) | --personas --layer --unified --one-turn --review-mode {prompt_only,saga_parallel} --max-parallel-branches --branch-timeout-seconds --max-branch-retries --retry-backoff-seconds --saga-resume --no-resume --session-ttl --clean-memory --clean-reports --keep-versions --out | review prompt artifacts (`review_prompt.txt`, `review_prompt_sidecar.json`, `review_prompt_inspection.json`) and control summary. Document mode supports `.md`, `.yaml`, `.yml` files with YAML-first precedence. In `saga_parallel`, runtime emits saga journal/status summaries and applies bounded branch scheduling/retry controls. |
| review | same as review-build | same as review-build | alias for review-build |
| validate | --project --doc-type --layer --document | --tier1-only --strict --format {text,json} --out | validation report artifacts and status. Supports both .md and .yaml document formats. YAML documents receive cross-section validation and structure checks. |
| validate-fix | --project --doc-type --layer --document | --validation-report --out | **DEPRECATED** — alias for `validate`. Use `validate` instead. When validation errors are found, `validate` produces the `_validated` derived copy and fix report automatically. |
| remediate | --project --doc-type --layer --document | --fix --review-report --remediation-report --out | remediation findings report (`{DOC_ID}.ucx.remediate.json/.txt`). With `--fix`: also produces `{DOC_ID}.ucx.remediate_fix.json/.txt`, versioned derived copy `TYPE-NN_{slug}_remediate_v{N}.{ext}`, and `remediation_quality` metrics. `--remediation-report` supplies a pre-existing report to the fix flow. In pipeline mode, auto-validates derived copy post-fix. Supports both .md and .yaml document formats. |
| remediate-fix | (deprecated) | (deprecated) | **DEPRECATED** — alias for `remediate --fix`. Use `remediate --fix` instead. |
| clean | --project --document | --stages {validate,review,remediate,creation,all} --keep N --dry-run --apply --out | prune obsolete stage artifacts (`_validated`, `_remediate_copy`, `_remediate_v{N}`, reports) from document folders. `--dry-run` lists candidates; `--apply` performs deletion. |
| prescreen | --document | --out | prescreen candidate report |
| consistency | --target | --format {text,json} --out | artifact lineage and stage-consistency report. Supports both .md and .yaml document formats. YAML documents receive cross-section validation and structure checks. |
| validate-links | --target | --workspace-root --format {text,json} --out | markdown link validation report (file links + anchors) |
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

- Document-aware lifecycle commands write artifacts to `<document_dir>/.ucx/<stage>` by default.
- `create` writes the final source document artifact to `--target` and writes creation diagnostics to `<target_dir>/.ucx/creation` unless `--out` is provided.
- Fallback when no document context is available uses `<project>/docs/.ucx/<stage>`.

Stage mapping:

- create-build -> `creation`
- create -> `creation` (diagnostic artifacts only; final document always uses `--target`)
- review-build/review -> `review`
- validate -> `validate`
- remediate/remediate --fix -> `remediation`

Rule:

- if `--out` points to `.ucx`, CLI appends stage automatically.
- if `--out` points to a concrete directory (including a document folder), CLI writes artifacts there directly.

---

## 4. Validation Target Resolution

When `--document` points to a folder, MCP resolves the target artifact as follows:

| Command | Resolution |
| --- | --- |
| `validate`, `remediate` | Find single file matching `^[A-Z]+-\d+_.+\.(md\|yaml\|yml)$` with no `_validated`, `_remediate_copy`, or `_remediate_v{N}` stem suffix — use as source. Fall back to full folder set if no unique match. |
| `remediate --fix` | Find single file matching `^[A-Z]+-\d+_.+_validated\.` (`.md`, `.yaml`, `.yml`) — use as `_validated` copy input. Fall back to full folder set if no unique match. |

When `validate --document` points to a markdown file, MCP applies canonical source redirection across all layers:

- If the parent folder has exactly one canonical source artifact (`TYPE-NN_{slug}.md`), and the provided file is any other markdown artifact in that folder (index, appendix, glossary, section split, or similar), validation executes on the canonical source artifact only.
- If no unique canonical source exists, validation executes on the provided file input.

This behavior ensures validation remains monolith-first for hybrid document folders across all layer types.

**Output filename rules:**

- `validate` (when errors found) uses the source stem and extension: `{slug}_validated.{ext}`
- `remediate --fix` uses the canonical base stem and extension with versioning: `{slug}_remediate_v{N}.{ext}`

This ensures derived copies never accumulate stage suffixes (e.g., `_validated_remediate_v1.md` is never produced).

---

## 5. Derived Artifact Lineage

The 5-stage lifecycle produces this artifact chain (applies to all document layers):

```text
TYPE-NN_{slug}.md                      ← stage 1: create
  ↓
{DOC_ID}.ucx.validate.json/.txt        ← stage 2: validate
TYPE-NN_{slug}_validated.{ext}         ← stage 2: validate (when errors found)
{DOC_ID}.ucx.validate_fix.json/.txt    ← stage 2: validate (when errors found)
  ↓
review_prompt.txt/.sidecar/.inspection ← stage 3: review
  ↓
{DOC_ID}.ucx.remediate.json/.txt       ← stage 4: remediate
  ↓
{DOC_ID}.ucx.remediate_fix.json/.txt   ← stage 5: remediate --fix
TYPE-NN_{slug}_remediate_v{N}.{ext}    ← stage 5: remediate --fix
```

Reserved filename suffixes:

- `_validated` — produced by `validate` when errors are found
- `_remediate_v{N}` — produced by `remediate --fix` only; always uses canonical base stem
- `_remediate_copy` — legacy compatibility suffix (read-only compatibility)

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

- Document collection scans for `.md`, `.yaml`, and `.yml` files. Legacy files (`_LEGACY` in stem) are excluded.
- Canonical main source is identified by matching `^[A-Z]+-\d+_.+\.(md|yaml|yml)$`, excluding appendix files.
- YAML-first precedence: when both `.yaml` and `.md` canonical sources exist, `.yaml` is selected.
- Appendix files are included using filename signals (`appendix`, `appendices` in name).
- Existing `--sections-json` mode remains supported for explicit section payload workflows.

Review mode controls:

- `--review-mode prompt_only` is default and implemented.
- `--review-mode saga_parallel` is implemented as saga journal/reducer scaffolding.
- Saga control flags (`--max-parallel-branches`, `--branch-timeout-seconds`, `--max-branch-retries`, `--retry-backoff-seconds`, `--saga-resume`) are applied by runtime and recorded in `review_controls.json`.

JSON status payload fields:

- `report_path`
- `summary_path`
- `tier1_only`
- `strict`
- `errors`
- `warnings`
- `is_valid`
- `passed`
- `fix_generated`

---

## 7. Persona Resolution

The `--personas` argument accepts zero or more space-separated persona identifiers (`nargs="+"`). It is optional on all commands that accept it.

**Resolution behavior**:

1. If `--personas` is provided on the command line, those personas are used (highest priority).
2. If `--personas` is omitted, the runtime looks up `persona_mappings.yaml` using the `(doc_type, phase)` pair.
3. If neither source provides personas, the command raises `PersonaMappingError`.

**MCP tool schema** (for programmatic callers):

```json
{
  "personas": {
    "type": "array",
    "items": {"type": "string"},
    "description": "Optional list of persona identifiers. Defaults to persona_mappings.yaml lookup."
  }
}
```

---

## 8. Examples

Project initialization:

```bash
# Initialize project UCX scaffold (run once; idempotent)
mcp init --project /path/to/project
# Writes: UCX/skills/personas/, prompts/templates/*, templates/layers/NN_TYPE/*

# Sync stale templates/prompts with framework source (protects persona_mappings.yaml)
mcp init --project /path/to/project --update

# Also reset persona_mappings.yaml to framework defaults
mcp init --project /path/to/project --update --update-mappings

# Assemble LLM creation prompt for a BRD (personas resolved from persona_mappings.yaml)
mcp create-build --project /path/to/project --doc-type brd \
  --layer 01_BRD --template UCC_PROMPT_BRD_PROJECT.md
# Writes: creation_prompt.txt, creation_prompt_sidecar.json, creation_prompt_inspection.json

# Explicit persona override (space-separated, optional)
mcp create-build --project /path/to/project --personas architect strategist --doc-type brd \
  --layer 01_BRD --template UCC_PROMPT_BRD_PROJECT.md

# After LLM generates content, write the final source document
mcp create --project /path/to/project --doc-type brd \
  --layer 01_BRD --template UCC_PROMPT_BRD_PROJECT.md \
  --target /path/to/docs/01_BRD/BRD-01_platform/BRD-01_platform.md
```

Full 5-stage lifecycle for a BRD document:

```bash
# Stage 1 — Create source document (personas from persona_mappings.yaml)
mcp create --project /path/to/project --doc-type brd --layer 01_BRD \
  --template UCC_PROMPT_BRD_PROJECT.md \
  --target /path/to/docs/01_BRD/BRD-01_platform/BRD-01_platform.md

# Stage 2 — Validate source (produces _validated copy + fix report when errors found)
mcp validate --project /path/to/project --doc-type brd --layer 01_BRD \
  --document /path/to/docs/01_BRD/BRD-01_platform/BRD-01_platform.md \
  --format json
# → BRD-01.ucx.validate.json/.txt always
# → BRD-01_platform_validated.md + BRD-01.ucx.validate_fix.json/.txt when errors found

# Stage 3 — Review prompt assembly (personas from persona_mappings.yaml)
mcp review --project /path/to/project --doc-type brd \
  --layer 01_BRD --sections-json /path/to/sections.json
# → review_prompt.txt + review_prompt_sidecar.json + review_prompt_inspection.json

# Stage 3 alternative — Review document folder with explicit personas
mcp review --project /path/to/project --personas architect auditor chairperson --doc-type brd \
  --layer 01_BRD --template UCR_PROMPT_BRD_PROJECT.md \
  --document /path/to/docs/01_BRD/BRD-01_platform/

# Stage 4 — Remediation plan against _validated copy
mcp remediate --project /path/to/project --doc-type brd --layer 01_BRD \
  --document /path/to/docs/01_BRD/BRD-01_platform/ \
  --review-report /path/to/external_review_report.md
# → BRD-01.ucx.remediate.json/.txt

# Stage 5 — Produce versioned remediated copy
mcp remediate --fix --project /path/to/project --doc-type brd --layer 01_BRD \
  --document /path/to/docs/01_BRD/BRD-01_platform/ \
  --remediation-report /path/to/remediation_report.json
# → BRD-01.ucx.remediate_fix.json/.txt + BRD-01_platform_remediate_v1.md
```

Persona management:

```bash
# Show all persona assignments for a project
mcp personas-show --project /path/to/project

# Show creation phase only, JSON format
mcp personas-show --project /path/to/project --phase creation --format json

# Show specific doctype
mcp personas-show --project /path/to/project --phase review --doc-type brd

# Update BRD creation personas
mcp personas-set --project /path/to/project --phase creation --doc-type brd \
  --personas architect product_owner business_analyst

# Compare project against framework defaults
mcp personas-diff --project /path/to/project

# Show project .env keys (without values)
mcp env-show --project /path/to/project

# Show project .env keys in JSON
mcp env-show --project /path/to/project --format json

# Show resolved default project
mcp get-project

# With SDD_DEFAULT_PROJECT set, --project is optional:
export SDD_DEFAULT_PROJECT=/path/to/project
mcp preflight --context any
mcp env-show
```

Other commands:

```bash
mcp prescreen --document /path/to/docs/01_BRD
mcp consistency --target /path/to/docs/01_BRD/BRD-01_platform/
mcp validate-links --target /path/to/docs --format json
mcp preflight --project /path/to/project --context review --format json
mcp clean --project /path/to/project --document /path/to/docs/01_BRD/BRD-01_platform --dry-run
mcp scan --report-file /path/to/validation_report.json
mcp scoring show --report-file /path/to/validation_report.json
mcp scoring validate --report-file /path/to/validation_report.json --threshold 90
mcp scoring compare --baseline-report-file /path/to/a.json --candidate-report-file /path/to/b.json
```
