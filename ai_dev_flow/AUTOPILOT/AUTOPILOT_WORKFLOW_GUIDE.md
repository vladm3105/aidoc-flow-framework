# Autopilot Workflow Guide

**Purpose**: Document YAML-only template usage for Autopilot workflow

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
| 10 | TASKS | `11_TASKS/TASKS-MVP-TEMPLATE.yaml` | `TASKS-TEMPLATE.md` |

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

## Related Documentation

- **`DUAL_MVP_TEMPLATES_ARCHITECTURE.md`** - Complete explanation of dual-format architecture
- **`MVP_WORKFLOW_GUIDE.md`** - MVP workflow documentation
- **Layer-specific schemas** - Each `XX_MVP_SCHEMA.yaml` validates both formats
