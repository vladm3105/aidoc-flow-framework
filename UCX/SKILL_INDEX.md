# UCX Skill Index

This document maps Claude Skills to the UCX framework phases.

---

## Overview

The UCX framework provides three phases that map to existing Claude Skills:

| UCX Phase | Purpose | Python API | CLI |
|-----------|---------|------------|-----|
| **UCC** | Document Creation | `UCCPhase.create()` | `ucx create` |
| **UCR** | Document Review | `UCRPhase.review()` | `ucx review` |
| **UCRem** | Document Remediation | `UCRemPhase.generate_fixes()` | `ucx remediate` |
| **Autopilot** | Full Workflow | `UCXAutopilot.run()` | `ucx autopilot` |

---

## Skill Mapping by Layer

### Layer 1: BRD (Business Requirements)

| Claude Skill | UCX Phase | Python API | CLI |
|--------------|-----------|------------|-----|
| `/doc-brd` | UCC | `UCCPhase.create("brd", ...)` | `ucx create brd` |
| `/doc-brd-audit` | UCR | `UCRPhase.review("brd", ...)` | `ucx review brd` |
| `/doc-brd-fixer` | UCRem | `UCRemPhase.generate_fixes(...)` | `ucx remediate brd` |
| `/doc-brd-autopilot` | All | `UCXAutopilot.run("brd", ...)` | `ucx autopilot brd` |

### Layer 2: PRD (Product Requirements)

| Claude Skill | UCX Phase | Python API | CLI |
|--------------|-----------|------------|-----|
| `/doc-prd` | UCC | `UCCPhase.create("prd", ...)` | `ucx create prd` |
| `/doc-prd-audit` | UCR | `UCRPhase.review("prd", ...)` | `ucx review prd` |
| `/doc-prd-fixer` | UCRem | `UCRemPhase.generate_fixes(...)` | `ucx remediate prd` |
| `/doc-prd-autopilot` | All | `UCXAutopilot.run("prd", ...)` | `ucx autopilot prd` |

### Layer 3: EARS (Formal Requirements)

| Claude Skill | UCX Phase | Python API | CLI |
|--------------|-----------|------------|-----|
| `/doc-ears` | UCC | `UCCPhase.create("ears", ...)` | `ucx create ears` |
| `/doc-ears-audit` | UCR | `UCRPhase.review("ears", ...)` | `ucx review ears` |
| `/doc-ears-fixer` | UCRem | `UCRemPhase.generate_fixes(...)` | `ucx remediate ears` |
| `/doc-ears-autopilot` | All | `UCXAutopilot.run("ears", ...)` | `ucx autopilot ears` |

### Layer 4: BDD (Behavior Scenarios)

| Claude Skill | UCX Phase | Python API | CLI |
|--------------|-----------|------------|-----|
| `/doc-bdd` | UCC | `UCCPhase.create("bdd", ...)` | `ucx create bdd` |
| `/doc-bdd-audit` | UCR | `UCRPhase.review("bdd", ...)` | `ucx review bdd` |
| `/doc-bdd-fixer` | UCRem | `UCRemPhase.generate_fixes(...)` | `ucx remediate bdd` |
| `/doc-bdd-autopilot` | All | `UCXAutopilot.run("bdd", ...)` | `ucx autopilot bdd` |

### Layer 5: ADR (Architecture Decisions)

| Claude Skill | UCX Phase | Python API | CLI |
|--------------|-----------|------------|-----|
| `/doc-adr` | UCC | `UCCPhase.create("adr", ...)` | `ucx create adr` |
| `/doc-adr-audit` | UCR | `UCRPhase.review("adr", ...)` | `ucx review adr` |
| `/doc-adr-fixer` | UCRem | `UCRemPhase.generate_fixes(...)` | `ucx remediate adr` |
| `/doc-adr-autopilot` | All | `UCXAutopilot.run("adr", ...)` | `ucx autopilot adr` |

### Layer 6: SYS (System Requirements)

| Claude Skill | UCX Phase | Python API | CLI |
|--------------|-----------|------------|-----|
| `/doc-sys` | UCC | `UCCPhase.create("sys", ...)` | `ucx create sys` |
| `/doc-sys-audit` | UCR | `UCRPhase.review("sys", ...)` | `ucx review sys` |
| `/doc-sys-fixer` | UCRem | `UCRemPhase.generate_fixes(...)` | `ucx remediate sys` |
| `/doc-sys-autopilot` | All | `UCXAutopilot.run("sys", ...)` | `ucx autopilot sys` |

### Layer 7: REQ (Atomic Requirements)

| Claude Skill | UCX Phase | Python API | CLI |
|--------------|-----------|------------|-----|
| `/doc-req` | UCC | `UCCPhase.create("req", ...)` | `ucx create req` |
| `/doc-req-audit` | UCR | `UCRPhase.review("req", ...)` | `ucx review req` |
| `/doc-req-fixer` | UCRem | `UCRemPhase.generate_fixes(...)` | `ucx remediate req` |
| `/doc-req-autopilot` | All | `UCXAutopilot.run("req", ...)` | `ucx autopilot req` |

### Layer 8: CTR (Data Contracts)

| Claude Skill | UCX Phase | Python API | CLI |
|--------------|-----------|------------|-----|
| `/doc-ctr` | UCC | `UCCPhase.create("ctr", ...)` | `ucx create ctr` |
| `/doc-ctr-audit` | UCR | `UCRPhase.review("ctr", ...)` | `ucx review ctr` |
| `/doc-ctr-fixer` | UCRem | `UCRemPhase.generate_fixes(...)` | `ucx remediate ctr` |
| `/doc-ctr-autopilot` | All | `UCXAutopilot.run("ctr", ...)` | `ucx autopilot ctr` |

### Layer 9: SPEC (Technical Specification)

| Claude Skill | UCX Phase | Python API | CLI |
|--------------|-----------|------------|-----|
| `/doc-spec` | UCC | `UCCPhase.create("spec", ...)` | `ucx create spec` |
| `/doc-spec-audit` | UCR | `UCRPhase.review("spec", ...)` | `ucx review spec` |
| `/doc-spec-fixer` | UCRem | `UCRemPhase.generate_fixes(...)` | `ucx remediate spec` |
| `/doc-spec-autopilot` | All | `UCXAutopilot.run("spec", ...)` | `ucx autopilot spec` |

### Layer 10: TSPEC (Test Specification)

| Claude Skill | UCX Phase | Python API | CLI |
|--------------|-----------|------------|-----|
| `/doc-tspec` | UCC | `UCCPhase.create("tspec", ...)` | `ucx create tspec` |
| `/doc-tspec-audit` | UCR | `UCRPhase.review("tspec", ...)` | `ucx review tspec` |
| `/doc-tspec-fixer` | UCRem | `UCRemPhase.generate_fixes(...)` | `ucx remediate tspec` |
| `/doc-tspec-autopilot` | All | `UCXAutopilot.run("tspec", ...)` | `ucx autopilot tspec` |

---

## Python API Examples

### Creation (UCC)

```python
from ucx import UCCPhase, UCXConfig

config = UCXConfig(model="opus")
ucc = UCCPhase(config)

doc = ucc.create(
    doc_type="brd",
    output_path=Path("docs/01_BRD/BRD-01"),
    from_ref=Path("docs/00_REF/"),
)
```

### Review (UCR)

```python
from ucx import UCRPhase, UCXConfig

config = UCXConfig(model="opus", min_score=90)
ucr = UCRPhase(config)

result = ucr.review(
    doc_type="brd",
    doc_path=Path("docs/01_BRD/BRD-01.md"),
)

print(f"Score: {result.score}, Findings: {result.findings}")
```

### Remediation (UCRem)

```python
from ucx import UCRemPhase, UCXConfig

config = UCXConfig(model="opus")
ucrem = UCRemPhase(config)

fixes = ucrem.generate_fixes(
    review_report=Path("docs/01_BRD/BRD_UCR_REVIEW.md"),
    doc_path=Path("docs/01_BRD/BRD-01.md"),
)

for fix in fixes:
    print(f"{fix.fix_id}: {fix.confidence} - {fix.target_section}")
```

### Autopilot

```python
from ucx import UCXAutopilot, UCXConfig

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

---

## CLI Examples

```bash
# Activate venv first
source /opt/data/docs_flow_framework/.venv/bin/activate

# Creation
ucx create brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/

# Review
ucx review brd docs/01_BRD/BRD-01.md

# Remediation
ucx remediate brd docs/01_BRD/BRD-01.md --review-report docs/01_BRD/BRD_UCR_REVIEW.md

# Full autopilot
ucx autopilot brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/ --max-iterations 3

# Validate structure only
ucx validate brd docs/01_BRD/BRD-01.md
```

---

## Environment Variables

```bash
# Model selection
export UCX_MODEL="opus"          # opus, sonnet, haiku

# Autopilot settings
export UCX_MAX_ITER="3"          # Max review/fix cycles
export UCX_MIN_SCORE="90"        # Minimum passing score

# Drift monitoring
export UCX_SKIP_DRIFT="false"    # Skip drift cache

# Logging
export UCX_LOG_LEVEL="INFO"      # DEBUG, INFO, WARNING, ERROR
```

---

## Deprecated

The following standalone validator skills are deprecated - validation is integrated into UCR:

- `/doc-{type}-validator` → Use `/doc-{type}-audit` or `ucx review`

Legacy shell scripts in this directory are deprecated:
- `run_ucx_autopilot.sh` → Use `ucx autopilot`
- `creation/run_ucc.sh` → Use `ucx create`
- `review/run_ucr.sh` → Use `ucx review`
- `remediation/run_ucrem.sh` → Use `ucx remediate`

---

## See Also

- [README.md](README.md) - Full documentation
- [ucx/skills/personas/](ucx/skills/personas/) - Persona definitions
- [ucx/prompts/templates/](ucx/prompts/templates/) - Prompt templates
