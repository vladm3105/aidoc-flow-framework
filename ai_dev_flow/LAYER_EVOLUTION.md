---
title: "Layer Evolution Guide"
tags:
  - framework-guide
  - layer-management
  - shared-architecture
custom_fields:
  document_type: guide
  priority: shared
  development_status: active
---

# SDD Framework Layer Evolution Guide

**Version**: 1.0
**Last Updated**: 2025-12-29
**Purpose**: Procedures for adding, modifying, or deprecating layers in the SDD framework

---

## Overview

The SDD Framework uses a 15-layer document hierarchy (Layers 0-14). This guide documents the procedures and files that must be updated when evolving the layer structure.

**Authoritative Source**: `LAYER_REGISTRY.yaml` is the single source of truth for layer definitions.

---

## Adding a New Layer

### Step 1: Update LAYER_REGISTRY.yaml

Add the new layer entry in the `layers` array:

```yaml
- number: 13
  artifact: NEWTYPE
  name: "New Layer Name"
  folder: NEWTYPE/
  extensions: [.md]
  required_tags: [brd, prd, ears, bdd, adr, sys, req, spec, tasks]
  can_reference: [BRD, PRD, EARS, BDD, ADR, SYS, REQ, IMPL, CTR, SPEC, TASKS]
  error_prefix: NEWTYPE
  optional: false
  description: "Layer 13 - Description of purpose"
```

### Step 2: Create Layer Directory

```bash
mkdir -p docs/NEWTYPE
```

### Step 3: Create Layer Template

Create `NEWTYPE/NEWTYPE-TEMPLATE.md` following existing template patterns.

### Step 4: Create Layer README

Create `NEWTYPE/README.md` documenting layer purpose and usage.

### Step 5: Create Validation Script

Create `scripts/validate_newtype.sh` or `scripts/validate_newtype.py` for layer-specific validation.

---

## Files Requiring Manual Updates

Until registry integration is complete, these files contain hardcoded layer definitions:

| File | Content Type | Update Required |
|------|--------------|-----------------|
| `scripts/validate_cross_document.py` | `LAYER_CONFIG` dict (line ~83) | Add layer entry with number, folder, tags |
| `scripts/validate_all.py` | Layer type imports | Add new validator import and call |
| `VALIDATION_STANDARDS.md` | Layer tables | Update validator tables |
| `AI_ASSISTANT_RULES.md` | Layer references | Update Rule 14 layer diagram |
| `TRACEABILITY.md` | Layer mappings | Add layer to traceability rules |
| `index.md` | Layer overview | Update layer listing |
| `METADATA_TAGGING_GUIDE.md` | Tag requirements | Add tag requirements for new layer |
| `ID_NAMING_STANDARDS.md` | ID patterns | Add ID pattern for new layer |

---

## Deprecating a Layer

### Step 1: Mark as Deprecated in Registry

```yaml
- number: N
  artifact: TYPE
  # ... other fields ...
  deprecated: true
  deprecated_date: "2025-XX-XX"
  replacement: "NEWTYPE"  # if applicable
```

### Step 2: Update Validation Scripts

Modify validators to emit warnings for deprecated layer usage.

### Step 3: Create Migration Guide

Document migration path for existing documents using deprecated layer.

### Step 4: Set Sunset Date

Communicate timeline for complete removal (recommend 6-12 months).

---

## Modifying Existing Layers

### Changing Required Tags

1. Update `required_tags` in `LAYER_REGISTRY.yaml`
2. Run `python scripts/sync_layer_config.py --check` to identify affected files
3. Update hardcoded definitions in affected scripts
4. Update documentation

### Changing ID Patterns

1. Update `id_patterns` in `LAYER_REGISTRY.yaml`
2. Update `ID_NAMING_STANDARDS.md`
3. Update validation regex in affected scripts

---

## Registry Integration Roadmap

### Phase 1: Registry Creation (Complete)

- [x] Create `LAYER_REGISTRY.yaml`
- [x] Document all 15 layers

### Phase 2: Validation Tools (Future)

- [ ] Create `scripts/sync_layer_config.py`
- [ ] Integrate registry with `validate_cross_document.py`
- [ ] Integrate registry with `validate_all.py`

### Phase 3: Full Integration (Future)

- [ ] Remove all hardcoded layer definitions from scripts
- [ ] Auto-generate documentation from registry
- [ ] Implement registry version migration

---

## Validation Commands

```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('LAYER_REGISTRY.yaml'))"

# Validate registry against files (when sync script available)
python scripts/sync_layer_config.py --check

# Generate consistency report
python scripts/sync_layer_config.py --report
```

---

## Related Documents

- `LAYER_REGISTRY.yaml` - Authoritative layer definitions
- `VALIDATION_STANDARDS.md` - Validation error codes and behaviors
- `AI_ASSISTANT_RULES.md` - Layer validation rules (Rules 14-17)
- `TRACEABILITY.md` - Cross-layer reference requirements
