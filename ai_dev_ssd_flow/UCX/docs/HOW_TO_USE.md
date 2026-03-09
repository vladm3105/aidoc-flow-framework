# UCx Framework: How to Use

This guide covers practical usage of the UCx (Unified Context) Framework.

---

## Prerequisites

- Claude CLI installed (`claude` command available)
- Framework UCX at `/opt/data/docs_flow_framework/ai_dev_ssd_flow/UCX/`
- Project structure with `docs/` directory

---

## Phase 1: UCC (Creation)

### Basic Usage

```bash
# Create a BRD from reference documents
./docs/UCX/creation/run_ucc.sh brd ./docs/01_BRD/ --from-ref ./docs/00_REF/

# Create a PRD from upstream BRD
./docs/UCX/creation/run_ucc.sh prd ./docs/02_PRD/ --from-upstream ./docs/01_BRD/

# Use specific template
./docs/UCX/creation/run_ucc.sh brd ./docs/01_BRD/ --template BRD-MVP-TEMPLATE.md
```

### Options

| Option | Description |
|--------|-------------|
| `--from-ref <dir>` | Load reference documents from directory |
| `--from-upstream <path>` | Load upstream artifact |
| `--template <file>` | Use specific template |
| `--multi-file` | Generate multi-file output (index + sections) |

### Environment Variables

```bash
UCC_MODEL=opus          # Claude model (default: opus)
UCC_LOAD_SKILLS=true    # Load persona skills (default: true)
UCC_PROMPT_DIR=./       # Custom prompt directory
```

### Multi-File Output

For large documents (BRD, SYS), use multi-file mode:

```bash
./run_ucc.sh brd ./docs/01_BRD/BRD-01_platform/ --multi-file
```

Generates:
- `BRD-01.0_index.md`
- `BRD-01.1_executive_summary.md`
- `BRD-01.2_business_context.md`
- etc.

---

## Phase 2: UCR (Review)

### Basic Usage

```bash
# Review a document folder
./docs/UCX/review/run_ucr.sh brd ./docs/01_BRD/BRD-01_platform/

# Review a single file
./docs/UCX/review/run_ucr.sh prd ./docs/02_PRD/PRD-01.md

# Specify output file
./docs/UCX/review/run_ucr.sh brd ./docs/01_BRD/ ./reports/BRD_review.md
```

### Review Flow

1. **Validation Phase**: Automated schema/structure checks
2. **Content Review Phase**: Multi-persona analysis
3. **Output**: Unified report with P0/P1/P2 findings

### Options

| Option | Description |
|--------|-------------|
| Output file | Third argument (optional) |

### Environment Variables

```bash
UCR_MODEL=opus           # Claude model (default: opus)
UCR_LOAD_SKILLS=true     # Load persona skills (default: true)
UCR_SKIP_VALIDATE=false  # Skip validation phase (default: false)
```

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

### Basic Usage

```bash
# Generate fix proposals from review
./docs/UCX/remediation/run_ucrem.sh ./docs/01_BRD/BRD_UCR_REVIEW.md ./docs/01_BRD/
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

### Applying Fixes

For `auto-safe` fixes:
```bash
# Apply automatically (script reads UCRem output)
./apply_fixes.sh ./UCRem_REPORT.md ./docs/01_BRD/
```

For `auto-assisted` fixes:
- Apply the template
- Search for `[TODO]` placeholders
- Complete manually

For `manual-required` fixes:
- Create task for domain expert
- Do not auto-apply

---

## Full Workflow (Autopilot)

### Using Autopilot Skills

```bash
# Via Claude skill
/doc-brd-autopilot BRD-01 --from-ref ./docs/00_REF/
```

### Manual Orchestration

```bash
# 1. Create
./run_ucc.sh brd ./output/ --from-ref ./refs/

# 2. Review
./run_ucr.sh brd ./output/

# 3. Check findings
cat ./output/BRD_UCR_REVIEW.md | grep "P0-\|P1-"

# 4. If findings exist, generate fixes
./run_ucrem.sh ./output/BRD_UCR_REVIEW.md ./output/

# 5. Apply auto-safe fixes
# (manual step or script)

# 6. Re-review
./run_ucr.sh brd ./output/

# 7. Repeat until clean
```

---

## Project-Specific Prompts

### Creating Project Prompts

1. Copy framework prompt:
   ```bash
   cp UCR_PROMPT_BRD.md UCR_PROMPT_BRD_PROJECT.md
   ```

2. Add project context:
   - Domain terminology
   - Compliance requirements
   - Technical constraints
   - Project personas

### Naming Convention

| Pattern | Priority |
|---------|----------|
| `*_PROJECT.md` | Highest |
| `*_BEELOCAL.md` | Project-specific |
| `*.md` | Framework default |

---

## Troubleshooting

### "No UCR prompt found"

Check prompt directory:
```bash
ls $UCR_PROMPT_DIR/UCR_PROMPT_*.md
```

### "claude CLI not found"

Install Claude CLI or run manually:
```bash
cat input.md | claude -p --model opus > output.md
```

### Large documents timeout

Split into smaller sections or use multi-file mode:
```bash
./run_ucc.sh brd ./output/ --multi-file
```

### Skills not loading

Verify skill directory exists:
```bash
ls ./docs/UCX/skills/
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

### 5. Document Custom Personas

Keep project personas documented for consistency.

---

## See Also

- `UNIFIED_CONTEXT_FRAMEWORK.md` - Framework overview
- `PERSONA_DESIGN_GUIDE.md` - Creating personas
- `../SKILL_INDEX.md` - Claude skill integration
