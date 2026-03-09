# UCX Framework: How to Use

This guide covers practical usage of the UCX (Unified Context) Framework.

---

## Prerequisites

- Python 3.10+
- UCX package installed in venv
- Project structure with `docs/` directory

### Installation

```bash
# Activate the shared venv
source /opt/data/docs_flow_framework/.venv/bin/activate

# Verify UCX is installed
ucx --version
```

### LLM Provider Setup

UCX uses **LiteLLM** for multi-provider LLM support:

```bash
# Anthropic (default)
export ANTHROPIC_API_KEY="sk-ant-..."

# Or use other providers
export OPENAI_API_KEY="sk-..."
export OPENROUTER_API_KEY="sk-or-..."
```

---

## Phase 1: UCC (Creation)

### CLI Usage

```bash
# Create a BRD from reference documents
ucx create brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/

# Create a PRD from upstream BRD
ucx create prd docs/02_PRD/PRD-01 --from-upstream docs/01_BRD/BRD-01

# Use specific template
ucx create brd docs/01_BRD/BRD-01 --template BRD-MVP-TEMPLATE.md

# Multi-file output (index + sections)
ucx create brd docs/01_BRD/BRD-01_platform --multi-file
```

### Python API

```python
from ucx import UCCPhase, UCXConfig
from pathlib import Path

config = UCXConfig(model="opus")
ucc = UCCPhase(config)

doc = ucc.create(
    doc_type="brd",
    output_path=Path("docs/01_BRD/BRD-01"),
    from_ref=Path("docs/00_REF/"),
)
```

### Options

| CLI Option | Python Parameter | Description |
|------------|------------------|-------------|
| `--from-ref <dir>` | `from_ref=` | Load reference documents |
| `--from-upstream <path>` | `from_upstream=` | Load upstream artifact |
| `--template <file>` | `template=` | Use specific template |
| `--multi-file` | `multi_file=True` | Multi-file output |

### Environment Variables

```bash
UCX_MODEL=opus          # LLM model (opus, sonnet, haiku, or LiteLLM format)
UCX_API_BASE=           # Custom API endpoint (for proxies, Ollama, etc.)
```

### Multi-File Output

For large documents (BRD, SYS), use multi-file mode:

```bash
ucx create brd docs/01_BRD/BRD-01_platform --multi-file
```

Generates:
- `BRD-01.0_index.md`
- `BRD-01.1_executive_summary.md`
- `BRD-01.2_business_context.md`
- etc.

---

## Phase 2: UCR (Review)

### CLI Usage

```bash
# Review a document folder
ucx review brd docs/01_BRD/BRD-01_platform/

# Review a single file
ucx review prd docs/02_PRD/PRD-01.md

# Validate structure only (no AI review)
ucx validate brd docs/01_BRD/BRD-01.md
```

### Python API

```python
from ucx import UCRPhase, UCXConfig
from pathlib import Path

config = UCXConfig(model="opus", min_score=90)
ucr = UCRPhase(config)

result = ucr.review(
    doc_type="brd",
    doc_path=Path("docs/01_BRD/BRD-01.md"),
)

print(f"Score: {result.score}")
print(f"Findings: {len(result.findings)}")
```

### Review Flow

1. **Validation Phase**: Automated schema/structure checks
2. **Content Review Phase**: Multi-persona analysis
3. **Output**: Unified report with P0/P1/P2 findings

### Understanding Findings

| Priority | Meaning | Action |
|----------|---------|--------|
| **P0** | Critical - blocking | Must fix before approval |
| **P1** | High - should fix | Fix before release |
| **P2** | Medium - consider | Optional improvement |

### Remediation Table

The review output includes a remediation table for UCRem:

```markdown
| ID | Priority | Target File | Section | Fix | Persona |
|----|----------|-------------|---------|-----|---------|
| P0-1 | P0 | file.md | 3.1 | Add X | Auditor |
```

---

## Phase 3: UCRem (Remediation)

### CLI Usage

```bash
# Generate fix proposals from review
ucx remediate brd docs/01_BRD/BRD-01.md --review-report docs/01_BRD/BRD_UCR_REVIEW.md
```

### Python API

```python
from ucx import UCRemPhase, UCXConfig
from pathlib import Path

config = UCXConfig(model="opus")
ucrem = UCRemPhase(config)

fixes = ucrem.generate_fixes(
    review_report=Path("docs/01_BRD/BRD_UCR_REVIEW.md"),
    doc_path=Path("docs/01_BRD/BRD-01.md"),
)

for fix in fixes:
    print(f"{fix.fix_id}: {fix.confidence} - {fix.target_section}")
```

### Fix Confidence Levels

| Level | Description | Action |
|-------|-------------|--------|
| `auto-safe` | Deterministic fix | Apply automatically |
| `auto-assisted` | Template with [TODO] | Apply, complete placeholders |
| `manual-required` | Needs human decision | Create task, don't auto-apply |

### UCRem Output

```yaml
fix_id: FIX-P0-01
source_finding: P0-1
confidence: auto-safe
target_file: "file.md"
target_section: "3.1"
fix_type: add_text
fix_action:
  position: after
  anchor: "existing text"
  text: |
    New text to insert.
```

---

## Full Workflow (Autopilot)

### CLI Usage

```bash
# Run full autopilot cycle
ucx autopilot brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/

# With iteration limits
ucx autopilot brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/ --max-iterations 3
```

### Python API

```python
from ucx import UCXAutopilot, UCXConfig
from pathlib import Path

config = UCXConfig(
    model="opus",
    max_iterations=3,
    min_score=90,
)
pilot = UCXAutopilot(config)

result = pilot.run(
    doc_type="brd",
    target=Path("docs/01_BRD/BRD-01"),
    from_ref=Path("docs/00_REF/"),
)

if result.is_success:
    print(f"Success! Score: {result.score}")
else:
    print(f"Needs manual review. Score: {result.score}")
```

### Claude Skills (Alternative)

```bash
# Via Claude skill
/doc-brd-autopilot BRD-01 --from-ref ./docs/00_REF/
```

---

## LiteLLM Multi-Provider Support

UCX supports multiple LLM providers via LiteLLM:

### Model Aliases

| Alias | Full Model ID |
|-------|---------------|
| `opus` | `anthropic/claude-opus-4-5-20251101` |
| `sonnet` | `anthropic/claude-sonnet-4-20250514` |
| `haiku` | `anthropic/claude-3-5-haiku-20241022` |

### Using Other Providers

```bash
# OpenAI
UCX_MODEL="openai/gpt-4o" ucx review brd docs/01_BRD/BRD-01.md

# Azure OpenAI
export AZURE_API_KEY="..."
export AZURE_API_BASE="https://your-resource.openai.azure.com"
UCX_MODEL="azure/gpt-4" ucx review brd docs/01_BRD/BRD-01.md

# Local Ollama
UCX_MODEL="ollama/llama3" UCX_API_BASE="http://localhost:11434" ucx review brd docs/01_BRD/BRD-01.md

# OpenRouter
export OPENROUTER_API_KEY="sk-or-..."
UCX_MODEL="openrouter/openai/gpt-4o-mini" ucx review brd docs/01_BRD/BRD-01.md
```

### Python API with LiteLLM

```python
from ucx import UCXConfig
from ucx.ai import LiteLLMClient

# Use OpenAI
config = UCXConfig(model="openai/gpt-4o")

# Use local Ollama
config = UCXConfig(model="ollama/llama3", api_base="http://localhost:11434")

# Direct client usage
client = LiteLLMClient(model="openai/gpt-4o")
response = client.generate("Analyze this requirement...")
```

---

## Troubleshooting

### "ucx: command not found"

Activate the venv:
```bash
source /opt/data/docs_flow_framework/.venv/bin/activate
```

### "No API key found"

Set provider-specific API key:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# or
export OPENAI_API_KEY="sk-..."
```

### Large documents timeout

Use multi-file mode or increase timeout:
```bash
ucx create brd docs/01_BRD/BRD-01 --multi-file
```

### Import errors

Reinstall UCX:
```bash
pip install -e /opt/data/docs_flow_framework/UCX
```

---

## Best Practices

### 1. Always Review Before Approval

Even after fixes, run UCR again to verify.

### 2. Use Project-Specific Prompts

Generic prompts miss domain-specific requirements.

### 3. Don't Skip Validation

Schema validation catches structural issues early.

### 4. Be Conservative with Auto-Apply

When in doubt, use `manual-required`.

### 5. Choose Appropriate Models

- `opus`: High-stakes documents (BRD, PRD, ADR)
- `sonnet`: Standard documents (REQ, SPEC)
- `haiku`: Quick validation, simple fixes

---

## See Also

- [README.md](../README.md) - Package overview
- [SKILL_INDEX.md](../SKILL_INDEX.md) - Claude skill integration
- [UNIFIED_CONTEXT_FRAMEWORK.md](UNIFIED_CONTEXT_FRAMEWORK.md) - Framework overview
- [PERSONA_DESIGN_GUIDE.md](PERSONA_DESIGN_GUIDE.md) - Creating personas
