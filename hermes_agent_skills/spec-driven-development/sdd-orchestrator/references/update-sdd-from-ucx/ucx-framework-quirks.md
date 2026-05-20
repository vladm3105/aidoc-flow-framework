# UCX Framework Quirks — Known Bugs and Safe Workarounds

Discovered during Hermes ↔ UCX sync operations. Last updated: 2026-05-06

## 1. Unquoted @-keys in YAML Templates

**Files affected**: BRD-TEMPLATE, EARS-TEMPLATE, BDD-TEMPLATE, ADR-TEMPLATE

**Problem**: Keys like `@brd:`, `@prd:`, `@ears:`, `@depends:`, `@threshold:` are bare tokens starting with `@`. YAML parsers throw:

```
YAMLError: while scanning for the next token
found character '@' that cannot start any token
```

**Workaround**: Quote the key in UCX source:

```yaml
# WRONG (breaks parse)
@brd: "BRD.01.05.xxxx"

# RIGHT
"@brd": "BRD.01.05.xxxx"
```

**Current state**: Sync script flags but does not auto-fix. Fix upstream in UCX repo and re-sync.

---

## 2. ADR-TEMPLATE Structural YAML Bug

**File**: `ucx_flow_v3/05_ADR/ADR-TEMPLATE.yaml`

**Problem**: Line ~308 contains `implementation_assessment:` at wrong indentation level, causing:

```
expected <block end>, but found '<block mapping start>'
```

**Workaround**: Fix indent in UCX source. No Hermes-side workaround possible without diverging from canonical upstream.

**Current state**: Blocks `yaml.safe_load()` validation. Sync script returns exit code 1 when this file is included.

---

## 3. Legacy ID Patterns in v2 Artifacts

**Directory**: `ai_dev_ssd_flow_v2/`

**Problem**: Contains `REQ-TEMPLATE.yaml`, `SYS-TEMPLATE.yaml`, `CTR-TEMPLATE.yaml`, `TSPEC-TEMPLATE.yaml`, `TASKS-TEMPLATE.yaml` with flat IDs like `REQ-001`. These are v2 format and must NOT be referenced in v3.2 documents.

**Mitigation**: Sync script ignores `ai_dev_ssd_flow_v2/` entirely. Legacy ID scanner checks all synced templates.

---

## 4. EARS Template Section 01-06 Ordering Discrepancy

**History**: During initial sync, the EARS template was partially overwritten via `patch` from an `offset`/`limit` view. This deleted Section 01 (Ubiquitous Requirements), nested `requirements` under `traceability`, duplicated Section 06, and corrupted the file.

**Lesson**: Never `patch` a file you read via pagination. Always `write_file` the entire file if the full contents were not read.

---

## 5. Hermes Skills ↔ UCX Source Drift

**Observation**: After running `update-sdd-from-ucx`, 6 of 9 templates and 6 of 9 reference files showed hash differences vs UCX canonical versions. This means project-level templates (copied from UCX at some point) have diverged over time.

**Recommendation**: Run `update-sdd-from-ucx` periodically. Check `STALE` entries in the report. If a template is stale, regenerate downstream documents from the new template rather than hand-migrating old documents.

---

## Verification Commands

```bash
# Check all templates for unquoted @-keys
python3 -c "import re; [print(f) for f in __import__('pathlib').Path('.').rglob('*.yaml') if any(re.search(r'^\s+@\w+:', l) for l in f.read_text().splitlines())]"

# Validate a single template
python3 -c "import yaml; yaml.safe_load(open('BRD-TEMPLATE.yaml'))" && echo OK || echo FAIL
```
