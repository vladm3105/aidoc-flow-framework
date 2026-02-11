# Autopilot Workflow Guide

**Purpose**: Document autopilot workflow including source directories, template usage, and auto-generated files.

---

## Source Directories

### BRD Autopilot Input Sources

The `doc-brd-autopilot` skill uses reference documents as input sources (Layer 1 entry point):

| Priority | Source | Location | Content Type |
|----------|--------|----------|--------------|
| 1 | Reference Documents | `docs/00_REF/` | Technical specs, gap analysis, architecture |
| 2 | Reference Documents (alt) | `REF/` | Alternative location |
| 3 | Existing Documentation | `docs/` or `README.md` | Project context |
| 4 | User Prompts | Interactive | Business context, objectives (fallback) |

### Other Autopilots

All other autopilots require upstream documents to exist:

| Autopilot | Upstream Required | Source |
|-----------|-------------------|--------|
| `doc-prd-autopilot` | BRD | `docs/01_BRD/BRD-NN_*` |
| `doc-ears-autopilot` | PRD | `docs/02_PRD/PRD-NN_*` |
| `doc-bdd-autopilot` | EARS | `docs/03_EARS/EARS-NN_*` |
| `doc-adr-autopilot` | BRD | `docs/01_BRD/BRD-NN_*` |
| `doc-sys-autopilot` | ADR | `docs/05_ADR/ADR-NN_*` |
| `doc-req-autopilot` | SYS | `docs/06_SYS/SYS-NN_*` |
| `doc-ctr-autopilot` | REQ | `docs/07_REQ/REQ-NN_*` |
| `doc-spec-autopilot` | REQ+CTR | `docs/07_REQ/` + `docs/08_CTR/` |
| `doc-tspec-autopilot` | SPEC | `docs/09_SPEC/SPEC-NN_*` |
| `doc-tasks-autopilot` | SPEC+TSPEC | `docs/09_SPEC/` + `docs/10_TSPEC/` |

---

## Auto-Generated Index Files

### BRD Layer Auto-Generated Files

The BRD autopilot automatically creates/updates these files:

| File | Purpose | Auto-Created | Auto-Updated |
|------|---------|--------------|--------------|
| `docs/01_BRD/BRD-00_index.md` | Master BRD registry | Yes (if missing) | Yes (on each BRD) |
| `docs/01_BRD/BRD-00_GLOSSARY.md` | Master glossary | Yes (if missing) | No (manual updates) |

### Index Update Logic

After generating each BRD:
1. Read existing `BRD-00_index.md`
2. Parse Document Registry table
3. Add or update entry for new BRD
4. Update Statistics section
5. Update `last_updated` timestamp

---

## Template Usage

The Autopilot workflow uses **YAML templates exclusively** for all artifact generation.

### YAML Template Path Mapping

| Layer | Artifact | YAML Template | MD Template (Reference Only) |
|-------|----------|---------------|---------------------------|
| 1 | BRD | `01_BRD/BRD-MVP-TEMPLATE.yaml` | `BRD-MVP-TEMPLATE.md` |
| 2 | PRD | `02_PRD/PRD-MVP-TEMPLATE.yaml` | `PRD-MVP-TEMPLATE.md` |
| 3 | EARS | `03_EARS/EARS-MVP-TEMPLATE.yaml` | `EARS-MVP-TEMPLATE.md` |
| 5 | ADR | `05_ADR/ADR-MVP-TEMPLATE.yaml` | `ADR-MVP-TEMPLATE.md` |
| 6 | SYS | `06_SYS/SYS-MVP-TEMPLATE.yaml` | `SYS-MVP-TEMPLATE.md` |
| 7 | REQ | `07_REQ/REQ-MVP-TEMPLATE.yaml` | `REQ-MVP-TEMPLATE.md` |
| 8 | CTR | `08_CTR/CTR-MVP-TEMPLATE.yaml` | `CTR-MVP-TEMPLATE.md` |
| 9 | SPEC | `09_SPEC/SPEC-MVP-TEMPLATE.yaml` | N/A (already YAML) |
| 10 | TSPEC | `10_TSPEC/TSPEC-MVP-TEMPLATE.yaml` | N/A (already YAML) |
| 11 | TASKS | `11_TASKS/TASKS-MVP-TEMPLATE.yaml` | `TASKS-TEMPLATE.md` |

### Why YAML Templates Only?

The Autopilot workflow exclusively uses YAML templates for these reasons:

#### 1. Performance

| Operation | MD Template | YAML Template | Improvement |
|-----------|-------------|---------------|-------------|
| Parse single doc | ~50ms | ~10ms | 5x faster |
| Parse 100 docs | ~5s | ~1s | 5x faster |
| Extract traceability | Regex (complex) | Key access (direct) | 3x faster |
| Validate schema | After parse | During parse | Earlier errors |

#### 2. Clarity

- YAML keys are explicitly named (no parsing interpretation needed)
- Markdown headings/tables require regex with edge cases
- Nested structures are clear in YAML, ambiguous in MD

#### 3. Type Safety

- YAML validates against schema during load
- Markdown validates after parsing (separate step)
- Earlier error detection = faster feedback loop

#### 4. Direct Mapping

- YAML `dict` → Python `dict` (zero transformation)
- Markdown → Python requires custom parsing logic
- Less code = fewer bugs

### Template Loading Pattern

Autopilot should load templates using this pattern:

```python
import yaml
from pathlib import Path

def load_autopilot_template(artifact_type: str, layer_dir: str) -> dict:
    """
    Load YAML template for Autopilot.

    Priority:
    1. Load {artifact}-MVP-TEMPLATE.yaml
    2. If not found, raise error (YAML templates required for Autopilot)

    Note: Never load MD templates for Autopilot workflow.

    Args:
        artifact_type: Artifact type (e.g., "REQ", "TASKS")
        layer_dir: Layer directory (e.g., "07_REQ")

    Returns:
        dict: Template structure

    Raises:
        FileNotFoundError: If YAML template doesn't exist
    """
    yaml_template = f"ai_dev_flow/{layer_dir}/{artifact_type}-MVP-TEMPLATE.yaml"
    template_path = Path(yaml_template)

    if not template_path.exists():
        raise FileNotFoundError(
            f"YAML template required for Autopilot: {yaml_template}\n"
            f"See DUAL_MVP_TEMPLATES_ARCHITECTURE.md for explanation."
        )

    with open(template_path) as f:
        return yaml.safe_load(f)

# Example usage
req_template = load_autopilot_template("REQ", "07_REQ")
tasks_template = load_autopilot_template("TASKS", "11_TASKS")
```

### Human Reference

For understanding artifact structure, reviewing examples, or learning the framework:
- **See `{artifact}-MVP-TEMPLATE.md`** (MD template) - narrative explanations, rich formatting
- **See `DUAL_MVP_TEMPLATES_ARCHITECTURE.md`** - complete comparison of formats, authority hierarchy, and when to use each.

### Important Notes

- **Autopilot never loads MD templates** - YAML only
- **If YAML template missing**: Raise error, don't fallback to MD
- **Validation**: Use existing validators (format detection internal)
- **Schema**: Single schema validates both MD and YAML documents

---

## Additional Autopilot Documentation

For complete Autopilot usage, execution modes, and configuration, see:
- **`MVP_AUTOPILOT.md`** - Core Autopilot guide with layer-by-layer behavior
- **`HOW_TO_USE_AUTOPILOT.md`** - Quick start guide for local development
- **`MVP_GITHUB_CICD_INTEGRATION_PLAN.md`** - GitHub Actions CI/CD integration

## Autopilot Mode Detection

Autopilot skills automatically detect whether to generate or review based on document existence:

### Document Exists vs Missing

| Upstream | Target | Mode | Phases Run |
|----------|--------|------|------------|
| Missing | Missing | **ERROR** | Abort - create upstream first |
| Exists | Missing | **Generate** | Full pipeline (Phases 1-6) |
| Exists | Exists | **Review/Fix** | Phase 5 only (review cycle) |

### Generate Mode (Target Missing)

Full 6-phase pipeline:

1. **Phase 1**: Dependency Analysis - Find upstream docs, validate `@ref:` targets
2. **Phase 2**: Readiness Validation - Check upstream score, verify prerequisites
3. **Phase 3**: Document Generation - Load template, generate all sections
4. **Phase 4**: Validation - Run `doc-TYPE-validator`, calculate readiness score
5. **Phase 5**: Review & Fix Cycle - Run `doc-TYPE-reviewer` → `doc-TYPE-fixer` until score ≥ threshold
6. **Phase 6**: Summary - Update index, generate completion report

### Review/Fix Mode (Target Exists)

Abbreviated pipeline (Phase 5 only):

1. Run `doc-TYPE-reviewer` → Generate review report
2. If score < threshold → Run `doc-TYPE-fixer` → Apply fixes
3. Re-run reviewer until PASS or max iterations

### Force Regeneration

Use `--regenerate` flag to force full regeneration (archives existing):

```bash
/doc-prd-autopilot BRD-01 --regenerate
# Archives existing PRD-01, generates fresh PRD-01 (Phases 1-6)
```

---

## Tiered Drift Handling

When upstream documents change, autopilot applies tiered auto-merge:

| Change % | Tier | Action |
|----------|------|--------|
| < 5% | Tier 1 | Auto-merge additions, patch version (1.0→1.0.1) |
| 5-15% | Tier 2 | Auto-merge with changelog, minor version (1.0→1.1) |
| > 15% | Tier 3 | Archive existing, regenerate, major version (1.x→2.0) |

**No Deletion Policy**: Upstream deletions mark content as `[DEPRECATED]` rather than removing.

---

## Related Documentation

- **`DUAL_MVP_TEMPLATES_ARCHITECTURE.md`** - Complete explanation of dual-format architecture
- **`MVP_WORKFLOW_GUIDE.md`** - MVP workflow documentation
- **Layer-specific schemas** - Each `XX_MVP_SCHEMA.yaml` validates both formats
- **Skill Documentation**: `.claude/skills/doc-{type}-autopilot/SKILL.md`
