# SDD v3.2 Framework Location & Known Quirks

## Framework Root

```
framework/
```

## Key Reference Files

| File | Purpose |
|------|---------|
| LAYER_REGISTRY.yaml | Authoritative layer definitions, doc type metadata, c4 mapping |
| ID_NAMING_STANDARDS.md | Document ID, element ID, tag, and file naming conventions |
| TRACEABILITY.md | Cumulative tag chain, readiness gates, upstream/downstream rules |
| THRESHOLD_NAMING_RULES.md | Threshold key format, category rules, boundary conventions (900+ lines) |
| AI_ASSISTANT_RULES.md | Template usage rules, what NOT to reference (v2 cut layers), TDD enforcement |
| QUICK_REFERENCE.md | One-page summary of layers, templates, gates |
| TESTING_STRATEGY_TDD.md | TDD integration guidance |
| DIAGRAM_STANDARDS.md | Mermaid diagram conventions |
| README.md | Framework overview, directory structure, quick start |

## Layer Folders

```
01_BRD/  02_PRD/  03_EARS/  04_BDD/  05_ADR/  06_SPEC/  07_TDD/  08_IPLAN/  CHG/
```

Templates: `0N_TYPE/TYPE-TEMPLATE.yaml` (e.g., `01_BRD/BRD-TEMPLATE.yaml`)

## Known Framework Quirks (Discovered & Fixed)

1. **Element ID regex was broken** — LAYER_REGISTRY.yaml pattern `^[A-Z]+\.\d{2,}\.\d{2,}\.\d{2,}$` rejected hex hashes (only accepted decimal digits). Fixed to `^[A-Z]+\.\d{2,}\.\d{2,}\.[a-f0-9]{4,8}$` to accept valid IDs like `BRD.01.07.a7f3`.

2. **BRD filename conflict** — ID_NAMING_STANDARDS.md said `BRD-01.yaml` but BRD-TEMPLATE.yaml says `BRD-01.yaml` is INVALID. Must use slug suffix: `BRD-01_kyc_onboarding.yaml` (feature) or `BRD-01_platform_architecture.yaml` (platform). Updated ID_NAMING_STANDARDS.md to document this. Non-BRD docs use plain `{TYPE}-NN.yaml`.

3. **BDD-Ready gate** — QUICK_REFERENCE.md omits `spec_trace links` from the BDD-Ready criteria, but TRACEABILITY.md and the BDD-TEMPLATE.yaml both include it. The sdd-orchestrator skill correctly includes `spec_trace links` — trust the skill over QUICK_REFERENCE.md.

## Threshold Tag Format

`@threshold: {DOC_TYPE}.{DOC_NUM}.{category.subcategory.attribute}`

Examples: `@threshold: PRD.01.kyc.l1.daily`, `@threshold: ADR.15.circuit.failure.count`

Defined in source docs (BRD/PRD/ADR), referenced from downstream docs (EARS/BDD/SPEC/TDD/IPLAN).

## ADR Dual Role

ADR can both DEFINE technical thresholds AND REFERENCE business/product thresholds from BRD/PRD. Documented in THRESHOLD_NAMING_RULES.md Section 1.2.

## What NOT to Reference (per AI_ASSISTANT_RULES.md)

See `framework/AI_ASSISTANT_RULES.md` for the authoritative rules on obsolete layer types, cuts, and template generation rules.

## 4. UCX sdd_validate Template Collision Bug

The UCX `sdd_validate` tool discovers ALL YAML files in the project when scanning
the target layer directory and/or `UCX/templates/` tree. If any file contains
template placeholder data (e.g., `id: ADR-NN`, unquoted `>`, `>=`, broken block
mappings), the validator WILL parse it and fail with a YAML error — even when
the target document itself is clean.

**Symptoms**:

```
sdd_validate(document=ADR-01.yaml, layer=05_ADR)
→ YAMLError: while parsing a block mapping
  in "<unicode string>", line 20, column 1:
    id: ADR-NN
    ^
  expected <block end>, but found '<block mapping start>'
```

**Root cause**: The validator scans these locations:

- The target layer directory (`0N_TYPE/`)
- `UCX/templates/` (top-level template set)
- `UCX/templates/layers/0N_TYPE/` (layer-specific templates)

Any YAML file with `ADR-NN` or other template placeholders in any of these paths
will trigger false parse failures.

**Workaround**: Before validation, move ALL ADR template files out of the
project tree entirely:

```bash
# Move all template copies to /tmp
find /opt/data/tradegent_covered_calls -name "ADR-TEMPLATE*" \
  -exec mv {} /tmp/ \; 2>/dev/null
# Validate
sdd_validate(document=ADR-01.yaml, layer=05_ADR)
# Restore templates
mv /tmp/ADR-TEMPLATE*.yaml /opt/data/tradegent_covered_calls/05_ADR/
```

**Note**: `yaml.safe_load()` on the target document will succeed while
`sdd_validate` fails — this is the diagnostic signature. If the document parses
cleanly in Python but the validator rejects it, check for template files in the
project tree with broken YAML.

This is distinct from the **filename heuristic bug** (quirk in main orchestrator
SKILL.md) which misclassifies files as Markdown based on name patterns. The
template collision bug affects ANY valid YAML document if a template file exists
nearby.

## Development Completion Rule (from AI_ASSISTANT_RULES.md)

See `framework/AI_ASSISTANT_RULES.md` for authoritative development completion and IPLAN completion criteria.
