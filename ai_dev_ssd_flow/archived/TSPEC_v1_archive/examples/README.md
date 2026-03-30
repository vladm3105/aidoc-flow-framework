---
title: "TSPEC Examples"
tags:
  - examples
  - layer-10-artifact
custom_fields:
  document_type: examples-readme
  artifact_type: TSPEC
  layer: 10
  development_status: active
---

# TSPEC Examples

## Overview

This directory contains example TSPEC documents demonstrating best practices for each test type.

## Example Documents

| File | Test Type | Description |
|------|-----------|-------------|
| `UTEST-01_auth_service.md` | Unit Test | Unit test specs for authentication service |
| `ITEST-01_auth_service.md` | Integration Test | Integration test specs for auth API |
| `STEST-01_auth_service.md` | Smoke Test | Post-deployment smoke tests |
| `FTEST-01_auth_service.md` | Functional Test | Functional behavior tests |
| `PTEST-01_api_performance.md` | Performance Test | API load and stress tests |
| `SECTEST-01_auth_security.md` | Security Test | Authentication security tests |

## Usage

These examples demonstrate:

1. **Proper ID formatting** - `TSPEC.NN.TT.SS` format
2. **Traceability tags** - Required upstream references
3. **Quality gate compliance** - Meeting threshold requirements
4. **Test case structure** - I/O tables, pseudocode, validation

## Running Validation

```bash
# Validate example documents
cd scripts/
python validate_utest.py ../examples/UTEST-01_auth_service.md --verbose
python validate_itest.py ../examples/ITEST-01_auth_service.md --verbose
python validate_stest.py ../examples/STEST-01_auth_service.md --verbose
python validate_ftest.py ../examples/FTEST-01_auth_service.md --verbose
python validate_ptest.py ../examples/PTEST-01_api_performance.md --verbose
python validate_sectest.py ../examples/SECTEST-01_auth_security.md --verbose
```

## See Also

- [UTEST-MVP-TEMPLATE.md](../UTEST/UTEST-MVP-TEMPLATE.md)
- [ITEST-MVP-TEMPLATE.md](../ITEST/ITEST-MVP-TEMPLATE.md)
- [STEST-MVP-TEMPLATE.md](../STEST/STEST-MVP-TEMPLATE.md)
- [FTEST-MVP-TEMPLATE.md](../FTEST/FTEST-MVP-TEMPLATE.md)
- [PTEST-MVP-TEMPLATE.md](../PTEST/PTEST-MVP-TEMPLATE.md)
- [SECTEST-MVP-TEMPLATE.md](../SECTEST/SECTEST-MVP-TEMPLATE.md)
