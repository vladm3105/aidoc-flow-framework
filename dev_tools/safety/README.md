# Runtime Safety (Guardrails)

Automated validation for Agent outputs using **Guardrails AI**.

## Usage

```bash
# Validate that output contains only digits
python validator.py --input "12345" --regex "^[0-9]+$"

# Validate JSON
python validator.py --input '{"key": "value"}' --json
```

## Integration
Import `validator.py` in your agent code to wrap LLM calls.
