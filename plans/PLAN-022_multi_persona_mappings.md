# PLAN-022: Multi-Persona Mappings for UCX Tools

**Status**: Completed
**Created**: 2026-04-02
**Updated**: 2026-04-02 (v6 — implementation complete, architecture review fixes applied)
**Scope**: mcp_sdd (UCX sub-framework) + framework-level documentation
**Complexity**: 4/5

---

## Problem Statement

UCX prompt templates define per-doctype persona sequences (3-13 personas per phase), but the runtime loads only a single persona `.md` file per tool invocation. The `persona` parameter is typed as `string` — no multi-persona support exists. This means the LLM receives detailed domain knowledge from one persona and must improvise the others from brief static text embedded in templates.

### Current State

| Component | Gap |
|-----------|-----|
| `tool_registry.py` | `persona` param is `string`, not `array` — affects 4 tools |
| `project_ucx_loader.py` | `load_project_persona_file()` loads one file |
| `context_builder.py` | `persona_text` is a single `str` field on both dataclasses |
| `context_engineering_contracts.py` | `PromptMetadataSidecar.persona` is a single `str` |
| `cli/main.py` | `--persona` is a single required string on 4 subcommands |
| `UCC_PROMPT_*.md` | Persona lists hardcoded as static markdown |
| `UCR_PROMPT_*.md` | Persona lists hardcoded as static markdown |
| `PERSONA_CATEGORY_MAP` | Only 7 of 15 personas mapped to categories |
| `discover_relevant_snippets()` | Accepts single persona for keyword lookup |
| Config files | No machine-readable persona-to-phase/doctype mapping exists |

### Name Mismatches Found

| Template Name | Actual `.md` File | Resolution |
|--------------|-------------------|------------|
| `DEVILS_ADVOCATE` | `chaos_engineer.md` | Use `chaos_engineer` |
| `INTEGRATION_EXPERT` | `integration_lead.md` | Use `integration_lead` |
| `CONTENT_STRATEGIST` | **none** | Create `content_strategist.md` |
| `ARCHITECT_FIXER` | **none** | Use base `architect.md` + remediation context |
| `AUDITOR_FIXER` | **none** | Use base `auditor.md` + remediation context |
| `QA_FIXER` | **none** | Use base `qa_lead.md` + remediation context |
| `INTEGRATION_FIXER` | **none** | Use base `integration_lead.md` + remediation context |
| `JUDGE` | **none** | Fold into `chairperson.md` |
| `CHAIRPERSON_EDITOR` | **none** | Fold into `chairperson.md` |

---

## Design

### Resolution Priority (2-tier, no legacy fallback)

```
Tool call with personas=["architect","auditor"]   -->  explicit override (highest)
            |
            v (not provided)
persona_mappings.yaml for phase+doctype           -->  project config default
```

No single `persona` string parameter. All persona resolution is list-based.

### New Config: `persona_mappings.yaml`

Location (canonical source): `mcp_sdd/skills/persona_mappings.yaml`
Location (project copy): `{project}/UCX/skills/persona_mappings.yaml`

```yaml
# UCX Persona Mappings v1.0
# Machine-readable persona sequences per phase and doctype.
# Projects customize after sdd_init.
#
# Resolution priority:
#   1. Tool call `personas` param (explicit override)
#   2. This file (project default)
#
# All names must match files in UCX/skills/personas/{name}.md

version: "1.0"

creation:
  brd:
    personas: [architect, product_owner, business_analyst, strategist, tech_lead]
    mode: sequential
  prd:
    personas: [product_owner, ux_strategist, content_strategist, tech_lead, qa_lead, architect, requirements_specialist]
    mode: sequential
  ears:
    personas: [requirements_specialist, tech_lead, qa_lead, chaos_engineer]
    mode: sequential
  bdd:
    personas: [qa_lead, tech_lead, chaos_engineer, operator]
    mode: sequential
  adr:
    personas: [architect, tech_lead, strategist, chaos_engineer, operator]
    mode: sequential
  sys:
    personas: [architect, tech_lead, operator, integration_lead]
    mode: sequential
  req:
    personas: [requirements_specialist, tech_lead, integration_lead]
    mode: sequential
  spec:
    personas: [tech_lead, architect, operator, integration_lead]
    mode: sequential
  ctr:
    personas: [architect, tech_lead, integration_lead]
    mode: sequential
  tspec:
    personas: [qa_lead, tech_lead, operator]
    mode: sequential

review:
  brd:
    personas: [architect, auditor, tech_lead, strategist, chaos_engineer, operator, integration_lead, product_owner, business_analyst, fact_checker, chairperson]
    mode: sequential
  prd:
    personas: [architect, auditor, tech_lead, strategist, chaos_engineer, operator, integration_lead, product_owner, qa_lead, ux_strategist]
    mode: sequential
  ears:
    personas: [requirements_specialist, tech_lead, qa_lead, chaos_engineer, integration_lead]
    mode: sequential
  bdd:
    personas: [qa_lead, tech_lead, chaos_engineer, operator, integration_lead, auditor]
    mode: sequential
  adr:
    personas: [architect, tech_lead, operator, auditor, strategist, chaos_engineer, integration_lead]
    mode: sequential
  sys:
    personas: [architect, tech_lead, qa_lead, chaos_engineer, integration_lead, operator]
    mode: sequential
  req:
    personas: [requirements_specialist, tech_lead, qa_lead, chaos_engineer, integration_lead]
    mode: sequential
  spec:
    personas: [tech_lead, architect, chaos_engineer, operator, integration_lead]
    mode: sequential
  ctr:
    personas: [integration_lead, tech_lead, architect, chaos_engineer, auditor]
    mode: sequential
  tspec:
    personas: [qa_lead, tech_lead, chaos_engineer, operator, integration_lead]
    mode: sequential

remediation:
  _default:
    personas: [architect, auditor, qa_lead, integration_lead, chaos_engineer, chairperson]
    mode: sequential
    loading: adaptive    # domain personas loaded only when findings match
```

### Tool Schema Change

Remove `persona: string`. Add `personas: array`:

```python
"personas": {
    "type": "array",
    "items": {"type": "string"},
    "description": "Persona list override. If omitted, loaded from persona_mappings.yaml for this phase+doctype.",
},
```

Applies to: `sdd_create`, `sdd_create_build`, `sdd_review`, `sdd_run_lifecycle`.

### CLI Argument Change

Replace `--persona` with `--personas` on all 4 subcommands:

```python
parser.add_argument(
    "--personas",
    nargs="+",
    default=None,
    help="Persona list override. If omitted, loaded from persona_mappings.yaml.",
)
```

Applies to: `review-build`, `review`, `create-build`, `create` subcommands in `cli/main.py`.

### Dataclass Changes

```python
@dataclass(frozen=True)
class PromptAssembly:
    prompt_text: str
    bundle: PromptBundle
    prompt_template_text: str
    persona_texts: list[str]       # individual persona contents
    persona_names: list[str]       # which personas were loaded

@dataclass(frozen=True)
class CreationAssembly:
    prompt_text: str
    bundle: PromptBundle
    prompt_template_text: str
    persona_texts: list[str]
    persona_names: list[str]
    layer_assets: dict[str, str]
    document_template_text: str | None
```

### PromptMetadataSidecar Change

```python
# In context_engineering_contracts.py
@dataclass
class PromptMetadataSidecar:
    personas: list[str]            # was: persona: str
    persona_count: int             # new: for token budget tracking
    # ... other fields unchanged
```

Validation: `if not metadata.personas: errors.append("personas is required")`
Serialization: `"personas": metadata.personas, "persona_count": metadata.persona_count`

### New Loader Functions

```python
def load_persona_mapping(*, project_root: Path) -> dict:
    """Load persona_mappings.yaml config."""
    ucx_root = validate_project_ucx_root(project_root)
    path = ucx_root / "skills" / "persona_mappings.yaml"
    if not path.exists():
        _raise_missing(project_root, [path])
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def load_multi_persona_files(
    *, project_root: Path, personas: list[str]
) -> list[tuple[str, str]]:
    """Load multiple persona .md files. Returns [(name, content), ...]."""
    return [
        (p, load_project_persona_file(project_root=project_root, persona=p))
        for p in personas
    ]
```

Note: `load_project_persona_file()` stays as an internal helper called by `load_multi_persona_files()`. Remove it from the public API re-export in `skills/__init__.py`.

### Persona Resolution Logic

```python
def _resolve_personas(
    project_root: Path,
    personas: list[str] | None,
    doc_type: str,
    phase: str,
) -> list[tuple[str, str]]:
    """Resolve persona list from explicit param or mapping config."""
    if not personas:
        mapping = load_persona_mapping(project_root=project_root)
        phase_map = mapping.get(phase)
        if not phase_map:
            raise PersonaMappingError(
                f"No persona mapping for phase '{phase}' in persona_mappings.yaml"
            )
        doc_map = phase_map.get(doc_type) or phase_map.get("_default")
        if not doc_map or "personas" not in doc_map:
            raise PersonaMappingError(
                f"No persona mapping for phase '{phase}', doctype '{doc_type}' "
                f"and no _default fallback in persona_mappings.yaml"
            )
        personas = doc_map["personas"]
    return load_multi_persona_files(project_root=project_root, personas=personas)
```

### YAML Schema Validation

`load_persona_mapping()` must validate the YAML structure after loading:

```python
def _validate_persona_mapping(mapping: dict, project_root: Path) -> None:
    """Validate persona_mappings.yaml structure and persona name references."""
    if "version" not in mapping:
        raise PersonaMappingError("Missing 'version' key in persona_mappings.yaml")
    for phase in ("creation", "review", "remediation"):
        phase_map = mapping.get(phase)
        if not phase_map:
            continue  # phase is optional
        for doc_type, config in phase_map.items():
            if not isinstance(config, dict) or "personas" not in config:
                raise PersonaMappingError(
                    f"Entry '{phase}.{doc_type}' missing 'personas' list"
                )
            personas = config["personas"]
            if not isinstance(personas, list) or not personas:
                raise PersonaMappingError(
                    f"Entry '{phase}.{doc_type}.personas' must be a non-empty list"
                )
            # Cross-reference: verify all persona names have .md files
            ucx_root = validate_project_ucx_root(project_root)
            for name in personas:
                path = ucx_root / "skills/personas" / f"{name}.md"
                if not path.exists():
                    raise PersonaMappingError(
                        f"Persona '{name}' in '{phase}.{doc_type}' has no file: {path}"
                    )
```

### `mode` Field Semantics

The `mode` field in `persona_mappings.yaml` is **metadata-only in v1.0**. It documents the intended collaboration pattern:

- `sequential` — personas enrich content in order (creation) or examine sequentially (review)
- Future: `parallel` — personas generate independent findings merged by chairperson

The runtime does NOT branch on `mode` in v1.0. All personas are loaded and injected into a single prompt regardless of mode. The field exists for:
1. Human documentation of the intended collaboration pattern
2. Future runtime support when multi-turn persona orchestration is implemented

No code reads `mode` in this release.

### PERSONA_CATEGORY_MAP — Complete Coverage (all 15 personas)

```python
PERSONA_CATEGORY_MAP: dict[str, tuple[str, ...]] = {
    "architect": ("functional", "quality", "technical", "integration"),
    "auditor": ("compliance", "risk", "quality", "integration"),
    "tech_lead": ("functional", "technical", "integration", "quality"),
    "chaos_engineer": ("risk", "quality", "operations", "integration"),
    "operator": ("operations", "quality", "technical", "risk"),
    "integration_lead": ("integration", "technical", "functional"),
    "chairperson": ("functional", "quality", "technical", "integration", "compliance", "risk", "operations"),
    # --- 8 personas added by PLAN-022 ---
    "product_owner": ("functional", "quality", "compliance"),
    "business_analyst": ("functional", "compliance", "quality"),
    "strategist": ("functional", "quality", "risk"),
    "requirements_specialist": ("functional", "technical", "compliance"),
    "ux_strategist": ("functional", "quality"),
    "qa_lead": ("functional", "technical", "quality", "risk"),
    "fact_checker": ("compliance", "quality", "functional"),
    "content_strategist": ("functional", "quality", "compliance"),
}
```

### Section Mapping — Union Categories

```python
def map_sections_for_personas(
    personas: list[str], sections: list[SourceSection]
) -> SectionMappingResult:
    """Union of all persona categories — include if ANY persona needs it."""
    all_categories: set[str] = set()
    for p in personas:
        all_categories.update(PERSONA_CATEGORY_MAP.get(p, ("functional", "technical")))
    # filter sections against union set
```

### Relevant Snippets — Union Keywords

```python
def discover_relevant_snippets(
    *,
    personas: list[str],
    skipped_sections: list[SourceSection],
    max_snippets: int = 5,
) -> list[RelevantSnippet]:
    """Find relevant snippets using union of all persona keywords."""
    keywords: set[str] = set()
    for p in personas:
        keywords.update(PERSONA_CATEGORY_MAP.get(p, ("functional", "technical")))
    # search skipped sections for keyword matches
```

### Prompt Assembly — Multi-Persona Block

```python
def _format_persona_block(persona_pairs: list[tuple[str, str]]) -> str:
    """Format multiple personas into a single prompt block."""
    if len(persona_pairs) == 1:
        return persona_pairs[0][1]
    parts = []
    for i, (name, content) in enumerate(persona_pairs, 1):
        parts.append(f"### Persona {i}: {name.upper()}\n\n{content.strip()}")
    return "\n\n---\n\n".join(parts)
```

### build_prompt_bundle() — Multi-Persona Metadata

```python
def build_prompt_bundle(
    *,
    personas: list[str],        # was: persona: str
    doc_type: str,
    sections: list[SourceSection],
    # ...
) -> PromptBundle:
    metadata = PromptMetadataSidecar(
        personas=personas,
        persona_count=len(personas),
        # ...
    )
```

### Token Budget Consideration

Loading 5 creation personas (~3-4KB each) adds ~15-20KB. Loading 11 review personas adds ~35-45KB. The context builder must:

- Add `persona_token_estimate: int` field to `PromptMetadataSidecar`
- Compute total persona tokens via `estimate_tokens()` (existing function in context_builder.py)
- Emit warning in bundle metadata sidecar when combined persona text exceeds 40KB:

```python
TOKEN_WARNING_THRESHOLD = 10_000  # ~40KB text

persona_tokens = estimate_tokens(combined_persona_text)
token_warning = None
if persona_tokens > TOKEN_WARNING_THRESHOLD:
    token_warning = (
        f"Combined persona text ({persona_tokens} tokens) exceeds "
        f"threshold ({TOKEN_WARNING_THRESHOLD}). Consider reducing persona count."
    )
```

- Warning appears in sidecar JSON as `"persona_token_warning": "..."` (null if under threshold)
- No runtime abort — warning is informational for prompt engineering debugging

### Remediation Persona Resolution

The `sdd_remediate`, `sdd_remediate_fix`, and `sdd_validate_fix` tools currently have no persona parameter. With `persona_mappings.yaml`, remediation tools gain persona support:

- Add optional `personas` array param to `sdd_remediate` and `sdd_remediate_fix` schemas
- `sdd_validate_fix` does NOT get personas — it runs deterministic validation, not LLM-driven review
- Resolution uses `remediation._default` from mapping when `personas` not provided
- `loading: adaptive` means the runner filters the persona list based on review report findings:

```python
MANDATORY_REMEDIATION_PERSONAS = {"chaos_engineer", "chairperson"}

def _filter_adaptive_personas(
    mapping_personas: list[str],
    review_report_categories: set[str],
) -> list[str]:
    """Filter domain personas by review findings; always keep mandatory."""
    result = []
    for p in mapping_personas:
        if p in MANDATORY_REMEDIATION_PERSONAS:
            result.append(p)  # always loaded
        else:
            persona_cats = set(PERSONA_CATEGORY_MAP.get(p, ()))
            if persona_cats & review_report_categories:
                result.append(p)  # findings match this persona's domain
    return result
```

- `chaos_engineer` and `chairperson` always load (mandatory fixers)
- Domain personas (architect, auditor, qa_lead, integration_lead) load only when findings exist in their categories

### Lifecycle Tool Persona Dispatch

`sdd_run_lifecycle` (tool_registry.py:720) delegates to `_handle_lifecycle_pipeline()` (line 883). The pipeline forwards ALL arguments (except `stages`) to each stage's `_dispatch()` call unchanged (line 901-904, 907). This means:

- The pipeline does NOT resolve personas per-phase itself
- It passes the raw `personas` param (or absence thereof) to each stage
- Each stage's dispatch handler calls `_resolve_personas()` independently, which reads the correct phase from `persona_mappings.yaml` based on the tool being called
- If `personas` is explicitly provided in the lifecycle call, the same list is forwarded to ALL stages (creation, review, remediation)
- If `personas` is omitted, each stage resolves its own list from the mapping based on its phase

No changes needed to `_handle_lifecycle_pipeline()` — the per-phase resolution happens naturally in each stage's handler.

### Additional Files with Persona References

3 source files reference `persona` but are NOT in the main modification path:

| File | Lines | Usage | Action Required |
|------|-------|-------|-----------------|
| `preflight/runner.py` | 156-162 | Checks `UCX/skills/personas/` directory exists | None — directory name unchanged |
| `remediation/review_parser.py` | 41 | `source_expert: str` on parsed findings | None — field name is `source_expert`, not `persona`; used as input by adaptive filter (Step 14b) |
| `reporting/contracts.py` | 430, 439-440 | Parses `persona` from legacy report filenames | Review only — legacy format may need `personas` key if downstream consumers change; low priority |

---

## Implementation Steps

### Step 1: Create `persona_mappings.yaml`
- **File**: `mcp_sdd/skills/persona_mappings.yaml` (new)
- **Action**: Create the canonical YAML config with all persona sequences extracted from prompt templates
- **Validation**: All persona names must match existing `.md` files (except `content_strategist` — Step 2)

### Step 2: Create `content_strategist.md` persona
- **File**: `mcp_sdd/skills/personas/content_strategist.md` (new)
- **Action**: Create persona definition for content strategy role (referenced by PRD creation)
- **Content**: Content strategy principles, information architecture, documentation standards, category tagging, scoring weights

### Step 3: Add loader functions and YAML validation
- **File**: `mcp_sdd/src/mcp_server/skills/project_ucx_loader.py`
- **Action**: Add `load_persona_mapping()`, `load_multi_persona_files()`, `_validate_persona_mapping()`
- **Action**: Add `PersonaMappingError` exception class
- **Action**: `load_persona_mapping()` calls `_validate_persona_mapping()` after YAML load — validates structure, required keys, persona name cross-references against `.md` files
- **Keep**: `load_project_persona_file()` as internal helper (called by `load_multi_persona_files()`)

### Step 4: Update public API re-export
- **File**: `mcp_sdd/src/mcp_server/skills/__init__.py`
- **Action**: Remove `load_project_persona_file` from public exports; add `load_persona_mapping` and `load_multi_persona_files`

### Step 5: Update `PromptMetadataSidecar`
- **File**: `mcp_sdd/src/mcp_server/models/context_engineering_contracts.py`
- **Action**: Replace `persona: str` with `personas: list[str]` + `persona_count: int`
- **Action**: Add `persona_token_estimate: int` field (computed by context builder)
- **Action**: Add `persona_token_warning: str | None` field (null if under threshold)
- **Action**: Update validation (`personas is required`, must be non-empty list)
- **Action**: Update serialization to emit `"personas"` array, `"persona_count"`, `"persona_token_estimate"`, `"persona_token_warning"`

### Step 6: Update dataclasses
- **File**: `mcp_sdd/src/mcp_server/prompts/context_builder.py`
- **Action**: Replace `persona_text: str` with `persona_texts: list[str]` + `persona_names: list[str]` on both `PromptAssembly` and `CreationAssembly`

### Step 7: Complete `PERSONA_CATEGORY_MAP` (all 15 personas)
- **File**: `mcp_sdd/src/mcp_server/prompts/context_builder.py`
- **Action**: Add 8 missing entries: `product_owner`, `business_analyst`, `strategist`, `requirements_specialist`, `ux_strategist`, `qa_lead`, `fact_checker`, `content_strategist`

### Step 8: Add persona resolution, formatting, and token warning functions
- **File**: `mcp_sdd/src/mcp_server/prompts/context_builder.py`
- **Action**: Add `_resolve_personas()` with descriptive `PersonaMappingError` on missing entries
- **Action**: Add `_format_persona_block()`
- **Action**: Add token budget warning logic: compute `persona_token_estimate` via `estimate_tokens()`, emit `persona_token_warning` if over `TOKEN_WARNING_THRESHOLD` (10,000 tokens / ~40KB)

### Step 9: Update `map_sections_for_persona` to `map_sections_for_personas`
- **File**: `mcp_sdd/src/mcp_server/prompts/context_builder.py`
- **Action**: Change signature to accept `personas: list[str]`, use union of all persona categories
- **Action**: Update callers in `assemble_project_review_prompt()` and `assemble_project_creation_prompt()`

### Step 10: Update `discover_relevant_snippets`
- **File**: `mcp_sdd/src/mcp_server/prompts/context_builder.py`
- **Action**: Change `persona: str` to `personas: list[str]`, use union of keywords from all personas
- **Action**: Update callers in both assembly functions

### Step 11: Update `build_prompt_bundle`
- **File**: `mcp_sdd/src/mcp_server/prompts/context_builder.py`
- **Action**: Change `persona: str` to `personas: list[str]` in signature and metadata construction

### Step 12: Update assembly functions
- **File**: `mcp_sdd/src/mcp_server/prompts/context_builder.py`
- **Action**: Update `assemble_project_creation_prompt()` — use `_resolve_personas()`, `_format_persona_block()`, populate `persona_texts` and `persona_names`
- **Action**: Update `assemble_project_review_prompt()` — same changes

### Step 13: Update `prompts/__init__.py` exports
- **File**: `mcp_sdd/src/mcp_server/prompts/__init__.py`
- **Action**: Replace `map_sections_for_persona` export with `map_sections_for_personas`

### Step 14: Update tool schemas and dispatch
- **File**: `mcp_sdd/src/mcp_server/tool_registry.py`
- **Action**: Replace `persona` (string, required) with `personas` (array, optional) on:
  - `sdd_create_build` (schema: line 239, required list: line 248, dispatch: line 737)
  - `sdd_create` (schema: line 258, required list: line 269, dispatch: line 762)
  - `sdd_review` (schema: line 279, required list: line 291, dispatch: line 796)
- **Action**: Update `sdd_run_lifecycle` (schema: line 224) — replace `persona` with `personas`. No dispatch change needed — `_handle_lifecycle_pipeline()` (line 883) forwards all arguments to stage handlers unchanged; per-phase resolution happens in each stage's `_resolve_personas()` call
- **Action**: Add optional `personas` (array) to `sdd_remediate` (line 313) and `sdd_remediate_fix` (line 331)
- **Note**: `sdd_validate_fix` (line 295) does NOT get personas — deterministic validation
- **Action**: Update dispatch handlers at lines 737, 762, 796 to extract `arguments.get("personas")` instead of `arguments["persona"]`
- **Action**: Update `sdd_remediate` dispatch (line 832) and `sdd_remediate_fix` dispatch (line 856) to extract `arguments.get("personas")`

### Step 14b: Implement adaptive remediation persona filtering
- **File**: `mcp_sdd/src/mcp_server/review/runner.py` (or new `remediation/runner.py`)
- **Action**: Add `_filter_adaptive_personas()` function that:
  - Parses the review report for finding category tags (`[CAT:architecture]`, `[CAT:compliance]`, etc.)
  - Extracts unique categories from findings
  - Filters `remediation._default.personas` to keep only personas whose `PERSONA_CATEGORY_MAP` categories overlap with finding categories
  - Always keeps mandatory personas (`chaos_engineer`, `chairperson`)
- **Action**: Wire into `sdd_remediate` dispatch — when `loading: adaptive` is set in mapping, apply filter before loading persona files

### Step 15: Update runner (3 functions)
- **File**: `mcp_sdd/src/mcp_server/review/runner.py`
- **Action**: Update `run_project_review_build()` (line 30): `persona: str` → `personas: list[str] | None`
- **Action**: Update `run_project_creation_build()` (line 101): `persona: str` → `personas: list[str] | None`
- **Action**: Update `run_project_creation_artifact()` (line 148): `persona: str` → `personas: list[str] | None`
- **Action**: Pass `personas` through to assembly functions in all three

### Step 16: Update CLI
- **File**: `mcp_sdd/src/mcp_server/cli/main.py`
- **Action**: Replace `--persona` (required string) with `--personas` (optional, `nargs="+"`) on 4 subcommands: `review-build` (line 41), `review` (line 65), `create-build` (line 86), `create` (line 102)
- **Action**: Update all handler functions to pass `args.personas` instead of `args.persona`

### Step 17: Add to scaffold
- **File**: `mcp_sdd/src/mcp_server/skills/scaffold.py`
- **Action**: Add `(Path("skills/persona_mappings.yaml"), Path("UCX/skills/persona_mappings.yaml"))` to `CANONICAL_SCAFFOLD_MAPPINGS`

### Step 18: Clean prompt templates
- **Files**: All `UCC_PROMPT_*.md` (11 files — includes `UCC_PROMPT_BRD_PROJECT.md`), `UCR_PROMPT_*.md` (10 files), and `UCRem_PROMPT_*.md` (10 files)
- **Total**: 31 prompt template files
- **Action**: Remove hardcoded persona lists and per-doctype persona sequences; replace with runtime injection note: `<!-- Personas injected at runtime from persona_mappings.yaml -->`
- **Action**: In `UCRem_PROMPT_*.md` files (10 files, 86 total persona references), remove hardcoded fixer persona lists and per-layer matrix references
- **Keep**: Collaboration protocol instructions (sequential enrichment, category tagging, output format)
- **Keep**: Phase-specific instructions (creation goals, review criteria, remediation procedures)

### Step 19: Update all tests

7 test files require changes:

#### 19a: `tests/unit/test_project_ucx_loader.py`
- Update `test_load_project_persona_file_reads_project_specific_persona` — test `load_multi_persona_files()` with multiple personas
- Add test for `load_persona_mapping()` — valid YAML, missing file, malformed YAML

#### 19b: `tests/unit/test_cli_main.py`
- Update all 7 test functions using `--persona architect` → `--personas architect tech_lead`
- Test that `--personas` accepts multiple values via `nargs="+"`

#### 19c: `tests/unit/test_review_runner.py`
- Update `run_project_review_build(persona="architect")` → `personas=["architect", "tech_lead"]`
- Update `run_project_creation_build(persona="architect")` → `personas=["architect", "tech_lead"]`
- Ensure multiple persona `.md` files are created in test fixtures

#### 19d: `tests/unit/test_scaffold_init.py`
- Add assertion: `(project_root / "UCX/skills/persona_mappings.yaml").exists()`
- Verify `persona_mappings.yaml` is scaffolded and not overwritten on re-scaffold

#### 19e: `tests/unit/test_reporting_contracts.py`
- Update `source_expert` references if they consume persona metadata

#### 19f: `tests/integration/test_creation_prompt_builder.py`
- Update all `persona="architect"` calls → `personas=["architect", "tech_lead"]`
- Assert `assembly.persona_names == ["architect", "tech_lead"]`
- Assert `len(assembly.persona_texts) == 2`
- Update sidecar assertions: `"personas": ["architect", "tech_lead"]`
- Update CLI integration tests: `--persona architect` → `--personas architect tech_lead`

#### 19g: `tests/integration/test_prompt_context_builder.py`
- Update `build_prompt_bundle(persona=...)` → `personas=[...]`
- Update `test_map_sections_for_persona_filters_by_semantic_category` → `map_sections_for_personas`
- Update sidecar assertion: `'"persona": "architect"'` → `'"personas": ["architect"]'`
- Update missing persona validation: `"persona is required"` → `"personas is required"`
- Add test: union category mapping with multiple personas includes all categories

#### 19h: New test file `tests/unit/test_persona_mappings.py`
- Test `_resolve_personas()` with explicit override
- Test `_resolve_personas()` with mapping config fallback
- Test `_resolve_personas()` with `_default` fallback for remediation
- Test all persona names in YAML resolve to existing `.md` files
- Test `_format_persona_block()` output with 1, 3, 11 personas

### Step 20: Update UCX architecture documentation

6 architecture files require updates:

#### 20a: `mcp_sdd/docs/architecture/MCP_PERSONA_DESIGN_GUIDE.md`
- Document multi-persona architecture and `persona_mappings.yaml` config format
- Update runtime source policy: single-load → multi-load via mapping
- Update persona output contract for multi-persona prompts
- Add complete persona taxonomy table (all 15 personas with category mappings)

#### 20b: `mcp_sdd/docs/architecture/MCP_CLI_REFERENCE.md`
- Replace `--persona` with `--personas` in all command signatures and examples
- Document `nargs="+"` behavior and interaction with `persona_mappings.yaml`

#### 20c: `mcp_sdd/docs/architecture/MCP_OPERATIONAL_FLOWS.md`
- Update creation and review workflow diagrams to show multi-persona loading
- Document `persona_mappings.yaml` in directory structure

#### 20d: `mcp_sdd/docs/architecture/MCP_OPERATOR_RUNBOOK.md`
- Update error handling section for multi-persona failures
- Document new `persona_mappings.yaml` troubleshooting

#### 20e: `mcp_sdd/docs/architecture/MCP_RUNTIME_ARCHITECTURE.md`
- Update runtime loading sequence to show multi-persona resolution
- Document 2-tier resolution priority (explicit param → mapping config)

#### 20f: `mcp_sdd/docs/architecture/MCP_UNIFIED_CONTEXT_FRAMEWORK.md`
- Update UCX framework description to reflect multi-persona as core capability
- Document `persona_mappings.yaml` as canonical persona config source

### Step 21: Update UCX specification documents

7 SPEC files reference persona and require contract updates:

#### 21a: `mcp_sdd/docs/specs/SPEC-002_mcp_review_scoring_handoff_identity_contracts.md` (11 refs)
- Update persona references in review findings contract: `persona: str` → `personas: list[str]`
- Update scoring handoff identity to carry `persona_names` list

#### 21b: `mcp_sdd/docs/specs/SPEC-003_mcp_creation_validation_profile_contracts.md`
- Update persona references in creation context contract

#### 21c: `mcp_sdd/docs/specs/SPEC-004_mcp_reporting_lineage_artifact_contracts.md`
- Update persona field in report lineage metadata

#### 21d: `mcp_sdd/docs/specs/SPEC-005_mcp_source_input_ingestion_contracts.md`
- Update persona reference in input parameter contracts

#### 21e: `mcp_sdd/docs/specs/SPEC-006_mcp_creation_flow_operational_contracts.md`
- Update persona parameter in creation flow operational contract

#### 21f: `mcp_sdd/docs/specs/SPEC-007_mcp_review_remediation_operational_contracts.md`
- Update persona parameter in review/remediation operational contract

#### 21g: `mcp_sdd/docs/specs/SPEC-001_mcp_core_architecture_workflow_contracts.md`
- Update persona reference in core architecture workflow

### Step 22: Update standalone persona definition files

These standalone persona reference files in prompt templates need updating to reflect that `persona_mappings.yaml` is now the authoritative source for persona sequences:

#### 22a: `mcp_sdd/prompts/templates/creation/UCC_PERSONAS.md`
- Add note that per-doctype persona sequences are now in `persona_mappings.yaml`
- Keep individual persona role descriptions as reference documentation
- Remove hardcoded per-doctype persona lists (now in YAML config)

#### 22b: `mcp_sdd/prompts/templates/remediation/UCRem_PERSONAS.md`
- Add note that remediation persona matrix is now in `persona_mappings.yaml` under `remediation._default`
- Keep fixer role descriptions as reference documentation
- Remove hardcoded per-layer persona matrix table (now in YAML config)

#### 22c: Mirror updates to UCX/ copies
- `UCX/prompts/templates/creation/UCC_PERSONAS.md` — mirror of 22a
- `UCX/prompts/templates/remediation/UCRem_PERSONAS.md` — mirror of 22b

### Step 23: Update README files

3 README files require updates:

#### 23a: `README.md` (project root)
- Add multi-persona support to UCX feature list
- Reference `persona_mappings.yaml` as new configuration artifact

#### 23b: `mcp_sdd/docs/README.md`
- Update UCX overview section to describe multi-persona architecture
- Add `persona_mappings.yaml` to directory structure listing
- Update tool parameter documentation (persona → personas)

#### 23c: `mcp_sdd/skills/README.md`
- Document `persona_mappings.yaml` purpose and format
- Update skills directory structure to include new config file
- Document how projects customize persona sequences after `sdd_init`
- Add `content_strategist.md` to persona file listing

### Step 24: Update SDD framework documentation

#### 24a: `ai_dev_ssd_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`
- Update UCX tool description to reflect multi-persona parameters
- Reference `persona_mappings.yaml` in UCX configuration section

#### 24b: `ai_dev_ssd_flow/REPORT_NAMING_STANDARDS.md`
- Update persona metadata field in report naming contract if applicable

### Step 25: UCX/ directory mirror sync

After all source changes, sync canonical `mcp_sdd/` assets to `UCX/` directory:

- `UCX/skills/persona_mappings.yaml` — copy from `mcp_sdd/skills/persona_mappings.yaml`
- `UCX/skills/personas/content_strategist.md` — copy from `mcp_sdd/skills/personas/content_strategist.md`
- `UCX/prompts/templates/creation/UCC_PROMPT_*.md` — mirror updated prompt templates
- `UCX/prompts/templates/review/UCR_PROMPT_*.md` — mirror updated prompt templates

Note: `sdd_init` scaffold handles this for new projects, but existing UCX/ copies in the framework repo must be manually synced.

### Step 26: Create mcp_sdd changelog entry

- **File**: `mcp_sdd/docs/CHANGELOG/CHANGELOG_v1.12.0.md` (new)
- **Version**: v1.12.0 (minor — new feature, no breaking external API since persona param was internal)
- **Content**:
  - **Summary**: Multi-persona mapping support via `persona_mappings.yaml`
  - **Added**:
    - `persona_mappings.yaml` — machine-readable per-doctype, per-phase persona sequences
    - `content_strategist.md` persona definition
    - `load_persona_mapping()`, `load_multi_persona_files()`, `_validate_persona_mapping()` loader functions
    - `PersonaMappingError` exception class with descriptive messages
    - `_resolve_personas()` 2-tier resolution (explicit param → mapping config)
    - `_filter_adaptive_personas()` for remediation domain filtering
    - `map_sections_for_personas()` union category mapping
    - `PERSONA_CATEGORY_MAP` expanded from 7 → 15 entries
    - Optional `personas` array param on `sdd_remediate` and `sdd_remediate_fix`
    - Token budget tracking: `persona_token_estimate`, `persona_token_warning` in sidecar
    - YAML schema validation at load time (structure, required keys, persona name cross-refs)
  - **Changed**:
    - Tool schemas: `persona` (string) → `personas` (array, optional) on `sdd_create`, `sdd_create_build`, `sdd_review`, `sdd_run_lifecycle`, `sdd_remediate`, `sdd_remediate_fix`
    - CLI: `--persona` → `--personas` (accepts multiple values)
    - `PromptMetadataSidecar`: `persona: str` → `personas: list[str]` + `persona_count: int` + token fields
    - `PromptAssembly` / `CreationAssembly`: `persona_text: str` → `persona_texts: list[str]` + `persona_names: list[str]`
    - Prompt templates: removed hardcoded persona lists from 31 creation/review/remediation templates
  - **Removed**:
    - Single `persona` string parameter on all tools and CLI
    - `load_project_persona_file()` from public API (kept as internal helper)
  - **Backward Compatibility**: Breaking for direct MCP tool callers using `persona` param — must migrate to `personas` array or omit to use mapping defaults
  - **Files changed**: ~111 files (listed in plan)

### Step 27: Update mcp_sdd roadmap

- **File**: `mcp_sdd/docs/ROADMAP.md`
- **Action**: Add v1.12.0 entry with multi-persona mapping milestone
- **Action**: Mark PLAN-022 as completed under current release cycle

### Step 28: Create framework changelog entry

- **File**: `changelog/CHANGELOG_v0.19.0.md` (new)
- **Version**: v0.19.0 (minor — UCX sub-framework feature)
- **Content**:
  - **Summary**: UCX v1.12.0 — multi-persona mapping support
  - **Changes**: Reference `mcp_sdd/docs/CHANGELOG/CHANGELOG_v1.12.0.md` for details
  - **UCX sub-framework**: `persona_mappings.yaml` config, 15-persona category map, multi-persona prompt assembly
  - **Documentation**: Updated architecture docs, specs, READMEs, SDD guide

### Step 29: Update framework roadmap

- **File**: `roadmap/ROADMAP.md`
- **Action**: Add v0.19.0 entry referencing UCX v1.12.0 multi-persona feature
- **Action**: Update timeline diagram and version table

---

## Validation Criteria

### Code & Runtime
- [ ] `sdd_create_build` for BRD loads all 5 creation personas from mapping
- [ ] `sdd_review` for BRD loads all 11 review personas from mapping
- [ ] `sdd_remediate` loads remediation personas from `_default` mapping
- [ ] `sdd_remediate` adaptive loading filters domain personas by review report categories
- [ ] `sdd_remediate_fix` accepts optional `personas` array param
- [ ] `sdd_run_lifecycle` resolves personas per-phase (creation/review/remediation mappings independently)
- [ ] Explicit `personas` param overrides `persona_mappings.yaml` on all tools
- [ ] Missing persona `.md` file raises `ProjectSkillsNotFound`
- [ ] Missing `persona_mappings.yaml` raises `ProjectSkillsNotFound`
- [ ] Malformed `persona_mappings.yaml` raises `PersonaMappingError` with descriptive message
- [ ] Invalid persona name in YAML (no matching `.md` file) caught at load time
- [ ] Missing phase or doctype in mapping (with no `_default`) raises `PersonaMappingError`
- [ ] `sdd_init` scaffolds `persona_mappings.yaml` to project `UCX/skills/`
- [ ] Bundle metadata sidecar includes `personas` array, `persona_count`, `persona_token_estimate`, `persona_token_warning`
- [ ] Token warning emitted when combined persona text exceeds 10,000 tokens (~40KB)
- [ ] All 15 persona names in YAML resolve to existing `.md` files
- [ ] Section union mapping includes categories from all loaded personas
- [ ] `discover_relevant_snippets` uses union keywords from all personas
- [ ] Prompt templates no longer contain hardcoded persona lists (31 creation/review/remediation templates cleaned)
- [ ] CLI `--personas` accepts multiple space-separated values
- [ ] `PERSONA_CATEGORY_MAP` covers all 15 personas
- [ ] `mode` field in YAML is metadata-only — not read by runtime in v1.0

### Tests
- [ ] All 7 existing test files pass after migration
- [ ] New `test_persona_mappings.py` covers resolution priority, formatting, YAML validation, error cases
- [ ] Test covers `PersonaMappingError` for missing phase, missing doctype, invalid persona name
- [ ] Test covers adaptive remediation persona filtering

### Documentation
- [ ] All 6 architecture docs updated to reflect multi-persona design
- [ ] All 7 SPEC files updated with `personas: list[str]` contract
- [ ] `UCC_PERSONAS.md` and `UCRem_PERSONAS.md` reference `persona_mappings.yaml` as authority
- [ ] 3 README files updated (root, mcp_sdd/docs, mcp_sdd/skills)
- [ ] SDD framework docs updated (`SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`, `REPORT_NAMING_STANDARDS.md`)
- [ ] UCX/ directory mirror synced with canonical mcp_sdd/ sources (33+ files)
- [ ] No stale `--persona` (singular) references remain in any documentation

### Changelog & Roadmap
- [ ] `mcp_sdd/docs/CHANGELOG/CHANGELOG_v1.12.0.md` created with full change summary
- [ ] `mcp_sdd/docs/ROADMAP.md` updated with v1.12.0 milestone
- [ ] `changelog/CHANGELOG_v0.19.0.md` created referencing UCX v1.12.0
- [ ] `roadmap/ROADMAP.md` updated with v0.19.0 entry

---

## Files Changed

### New Files (5)

| File | Step |
|------|------|
| `mcp_sdd/skills/persona_mappings.yaml` | 1 |
| `mcp_sdd/skills/personas/content_strategist.md` | 2 |
| `mcp_sdd/tests/unit/test_persona_mappings.py` | 19h |
| `mcp_sdd/docs/CHANGELOG/CHANGELOG_v1.12.0.md` | 26 |
| `changelog/CHANGELOG_v0.19.0.md` | 28 |

### Source Code (9 files, Steps 3-17)

| File | Action | Step |
|------|--------|------|
| `mcp_sdd/src/mcp_server/skills/project_ucx_loader.py` | Add 3 functions + error class, YAML validation | 3 |
| `mcp_sdd/src/mcp_server/skills/__init__.py` | Update public exports | 4 |
| `mcp_sdd/src/mcp_server/models/context_engineering_contracts.py` | persona → personas + token fields on sidecar | 5 |
| `mcp_sdd/src/mcp_server/prompts/context_builder.py` | Dataclasses, category map, assembly, section mapping, snippets, bundle, token warning | 6-12 |
| `mcp_sdd/src/mcp_server/prompts/__init__.py` | Update exports | 13 |
| `mcp_sdd/src/mcp_server/tool_registry.py` | Schema + dispatch on 6 tools (create, create_build, review, lifecycle, remediate, remediate_fix) | 14 |
| `mcp_sdd/src/mcp_server/review/runner.py` | Pass personas list + adaptive remediation filter | 14b, 15 |
| `mcp_sdd/src/mcp_server/cli/main.py` | --persona → --personas on 4 subcommands | 16 |
| `mcp_sdd/src/mcp_server/skills/scaffold.py` | Add mapping to scaffold | 17 |

### Prompt Templates (31 files + 4 persona refs, Step 18 + 22)

| File | Action | Step |
|------|--------|------|
| `mcp_sdd/prompts/templates/creation/UCC_PROMPT_*.md` (11 files, incl. BRD_PROJECT) | Remove hardcoded personas | 18 |
| `mcp_sdd/prompts/templates/review/UCR_PROMPT_*.md` (10 files) | Remove hardcoded personas | 18 |
| `mcp_sdd/prompts/templates/remediation/UCRem_PROMPT_*.md` (10 files) | Remove hardcoded fixer personas | 18 |
| `mcp_sdd/prompts/templates/creation/UCC_PERSONAS.md` | Reference persona_mappings.yaml | 22a |
| `mcp_sdd/prompts/templates/remediation/UCRem_PERSONAS.md` | Reference persona_mappings.yaml | 22b |
| `UCX/prompts/templates/creation/UCC_PERSONAS.md` | Mirror of 22a | 22c |
| `UCX/prompts/templates/remediation/UCRem_PERSONAS.md` | Mirror of 22b | 22c |

### Tests (8 files, Step 19)

| File | Action | Step |
|------|--------|------|
| `tests/unit/test_project_ucx_loader.py` | Multi-persona + mapping tests | 19a |
| `tests/unit/test_cli_main.py` | --personas in 7 tests | 19b |
| `tests/unit/test_review_runner.py` | Personas list in runner tests | 19c |
| `tests/unit/test_scaffold_init.py` | Assert persona_mappings.yaml scaffolded | 19d |
| `tests/unit/test_reporting_contracts.py` | Update persona metadata references | 19e |
| `tests/integration/test_creation_prompt_builder.py` | Multi-persona assertions + CLI tests | 19f |
| `tests/integration/test_prompt_context_builder.py` | Bundle, sidecar, section mapping tests | 19g |
| `tests/unit/test_persona_mappings.py` | **Create** — resolution, formatting, YAML validation | 19h |

### UCX Architecture Docs (6 files, Step 20)

| File | Action | Step |
|------|--------|------|
| `mcp_sdd/docs/architecture/MCP_PERSONA_DESIGN_GUIDE.md` | Multi-persona architecture, taxonomy | 20a |
| `mcp_sdd/docs/architecture/MCP_CLI_REFERENCE.md` | --personas in signatures | 20b |
| `mcp_sdd/docs/architecture/MCP_OPERATIONAL_FLOWS.md` | Workflow diagrams | 20c |
| `mcp_sdd/docs/architecture/MCP_OPERATOR_RUNBOOK.md` | Troubleshooting | 20d |
| `mcp_sdd/docs/architecture/MCP_RUNTIME_ARCHITECTURE.md` | Runtime loading sequence | 20e |
| `mcp_sdd/docs/architecture/MCP_UNIFIED_CONTEXT_FRAMEWORK.md` | Framework description | 20f |

### UCX Specification Docs (7 files, Step 21)

| File | Action | Step |
|------|--------|------|
| `mcp_sdd/docs/specs/SPEC-001_*_contracts.md` | Core architecture persona ref | 21g |
| `mcp_sdd/docs/specs/SPEC-002_*_contracts.md` | Review scoring persona contract (11 refs) | 21a |
| `mcp_sdd/docs/specs/SPEC-003_*_contracts.md` | Creation validation persona contract | 21b |
| `mcp_sdd/docs/specs/SPEC-004_*_contracts.md` | Reporting lineage persona field | 21c |
| `mcp_sdd/docs/specs/SPEC-005_*_contracts.md` | Source input persona ref | 21d |
| `mcp_sdd/docs/specs/SPEC-006_*_contracts.md` | Creation flow persona param | 21e |
| `mcp_sdd/docs/specs/SPEC-007_*_contracts.md` | Review/remediation persona param | 21f |

### README Files (3 files, Step 23)

| File | Action | Step |
|------|--------|------|
| `README.md` (project root) | Feature list update | 23a |
| `mcp_sdd/docs/README.md` | UCX overview, directory structure | 23b |
| `mcp_sdd/skills/README.md` | persona_mappings.yaml docs, content_strategist | 23c |

### SDD Framework Docs (2 files, Step 24)

| File | Action | Step |
|------|--------|------|
| `ai_dev_ssd_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` | UCX tool description | 24a |
| `ai_dev_ssd_flow/REPORT_NAMING_STANDARDS.md` | Persona metadata in reports | 24b |

### UCX/ Mirror Sync (5 file groups, Step 25)

| File | Action | Step |
|------|--------|------|
| `UCX/skills/persona_mappings.yaml` | Copy from mcp_sdd/skills/ | 25 |
| `UCX/skills/personas/content_strategist.md` | Copy from mcp_sdd/skills/personas/ | 25 |
| `UCX/prompts/templates/creation/UCC_PROMPT_*.md` (11 files) | Mirror updated templates | 25 |
| `UCX/prompts/templates/review/UCR_PROMPT_*.md` (10 files) | Mirror updated templates | 25 |
| `UCX/prompts/templates/remediation/UCRem_PROMPT_*.md` (10 files) | Mirror updated templates | 25 |

### Changelog & Roadmap (4 files, Steps 26-29)

| File | Action | Step |
|------|--------|------|
| `mcp_sdd/docs/CHANGELOG/CHANGELOG_v1.12.0.md` | **Create** — UCX release notes | 26 |
| `mcp_sdd/docs/ROADMAP.md` | Add v1.12.0 milestone | 27 |
| `changelog/CHANGELOG_v0.19.0.md` | **Create** — framework release notes | 28 |
| `roadmap/ROADMAP.md` | Add v0.19.0 entry | 29 |

### Totals

| Category | New | Modified | Total |
|----------|-----|----------|-------|
| Source code | 0 | 9 | 9 |
| Config (YAML) | 1 | 0 | 1 |
| Persona definitions | 1 | 0 | 1 |
| Prompt templates (creation) | 0 | 11 | 11 |
| Prompt templates (review) | 0 | 10 | 10 |
| Prompt templates (remediation) | 0 | 12 | 12 |
| Prompt persona refs | 0 | 4 | 4 |
| Tests | 1 | 7 | 8 |
| Architecture docs | 0 | 6 | 6 |
| Specification docs | 0 | 7 | 7 |
| README files | 0 | 3 | 3 |
| SDD framework docs | 0 | 2 | 2 |
| UCX mirror sync | 2 | 31+ | 33+ |
| Changelog | 2 | 0 | 2 |
| Roadmap | 0 | 2 | 2 |
| **Total** | **7** | **~104** | **~111** |

**Implementation steps**: 30 (Steps 1-14b, 15-19: code, Steps 20-25: documentation, Steps 26-29: changelog/roadmap).
