# PLAN-003: UCX Persona Prompt Restructuring & Finding ID Standardization

**Phase**: Cross-phase
**Status**: ✅ COMPLETE (Core + Integration Testing)
**Created**: 2026-03-13
**Updated**: 2026-03-13
**Priority**: P0 - Blocking UCX review functionality
**Applies Before**: Next UCX release

**Completion Summary**:
| Phase | Status | Notes |
|-------|--------|-------|
| 1. Finding ID Format Standard | ✅ Complete | Canonical PREFIX-P0-NNN format |
| 2. UCR Prompt Structure | ✅ Complete | BRD + PRD prompts updated |
| 3. Framework Template Updates | ✅ Complete | Attention steering at END |
| 4. Skill File Updates | ✅ Complete | Chairperson, Operator updated |
| 5. Testing & Verification | ✅ Complete | All 5.1-5.6 passed |
| 6.1-6.5 Context Engine Core | ✅ Complete | Hierarchical context, summarization |
| 6.7 Hybrid Context Selection | ⏸️ Deferred | RelevantSnippet, keyword scan |
| 6.9 Appendix-on-Demand | ⏸️ Deferred | AppendixInfo, dynamic detection |
| 6.10 Dynamic Section Mapping | ⏸️ Deferred | SECTION_CATEGORIES |

**Integration Test Results** (2026-03-13):
- 33 findings extracted with canonical format
- 0 legacy format findings
- UCX-MANIFEST-START/END markers present
- Bug fixed: Attention steering added to UnifiedPromptLoader

---

## Purpose

This plan addresses critical bugs in UCX that prevent correct finding extraction and structured output generation from persona reviews. Without these fixes, UCX reviews produce incorrect scores (showing 0 findings when 30+ exist) and generate summary text instead of machine-parseable tables.

---

## Findings

| # | Finding | Severity | Impact |
|---|---------|----------|--------|
| 1 | Regex pattern mismatch | HIGH | Finding extraction fails - frontmatter shows P0=0 despite 30+ findings |
| 2 | Inconsistent Finding ID formats | HIGH | Operator uses `P0-OP-001`, others use `ARCH-P0-001` - extraction misses formats |
| 3 | Chairperson manifest not generated | HIGH | No `<!-- UCX-MANIFEST-START -->` markers - automated remediation fails |
| 4 | Format instructions buried in middle | HIGH | "Lost in the middle" phenomenon - LLM ignores output format |
| 5 | Responses are summaries not tables | HIGH | 600-1200 char summaries instead of 5-10K structured tables |
| 6 | Prompt size explosion | MEDIUM | 170-187KB prompts cause LLM truncation/simplification |
| 7 | No output format validation | MEDIUM | No detection of malformed responses |
| 8 | Framework templates lack ID format | MEDIUM | `PERSONA_TEMPLATES` don't specify Finding ID format |
| 9 | UCR prompt tables lack ID prefix | MEDIUM | Table headers show `| ID |` not `| ID (ARCH-P0-NNN) |` |
| 10 | Previous responses not structured | LOW | Previous findings injected as raw text, hard to parse |

---

## Analysis

### Current State

**Prompt Structure** (`build_persona_prompt()` lines 661-739):
```
1. === YOUR DOMAIN KNOWLEDGE ===    (from skill file)
2. EXPERT INSTRUCTIONS:              (persona template)
3. ## CRITICAL Verification Protocol
4. ## LAYER-APPROPRIATE CLASSIFICATION
5. === PREVIOUS EXPERT FINDINGS ===  (truncated to 5K chars)
6. === DOCUMENT TO REVIEW ===        (full document content)
```

**Problems**:
- Output format instructions are in section 2 (middle), not at end
- No explicit Finding ID format standard
- Document content at end is correct, but format instructions are lost by then
- 170KB+ prompts exceed effective context window

**Observed Response Issues** (from BRD-01 review):

| Persona | Response Size | Expected | Issue |
|---------|---------------|----------|-------|
| architect | 1,244 chars | ~8K | Summary only, no tables |
| auditor | 895 chars | ~8K | Summary only, no tables |
| devils_advocate | 736 chars | ~6K | Summary only, no tables |
| integration_lead | 906 chars | ~6K | Summary only, no tables |
| business_analyst | 638 chars | ~5K | Summary only, no tables |
| chairperson | 1,253 chars | ~10K | Summary only, no manifest |
| tech_lead | 10,068 chars | ~8K | Better but still missing format |
| operator | 8,126 chars | ~6K | Uses wrong ID format (P0-OP-001) |
| strategist | 7,780 chars | ~6K | Adequate |
| fact_checker | 8,272 chars | ~8K | Adequate |
| product_owner | 7,357 chars | ~6K | Adequate |

**Finding ID Format Inconsistencies**:

| Source | Format | Example | Status |
|--------|--------|---------|--------|
| Framework template | Not specified | - | Missing |
| Architect response | PREFIX-P0-NNN | `ARCH-P0-001` | Correct |
| Auditor response | PREFIX-P0-NNN | `AUD-P0-001` | Correct |
| Operator response | **P0-PREFIX-NNN** | `P0-OP-001` | Wrong |
| Tech Lead cross-ref | Mixed | `TL-P0-001`, `P0-TL-001` | Inconsistent |
| Extraction regex | `**[P0-1]**` | Legacy | Obsolete |

### Target State

1. **Unified Finding ID Format**: All personas use `PREFIX-P0-NNN`
2. **Prompt Structure**: Format instructions at END of prompt
3. **Structured Output**: Tables with proper Finding IDs, not summaries
4. **Response Validation**: Detect malformed responses and log warnings
5. **Machine-Parseable Manifest**: Chairperson generates `<!-- UCX-MANIFEST-START -->` markers
6. **Accurate Scores**: Frontmatter counts match actual findings in content

### Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| UCX Framework codebase access | Required | Available |
| BeeLocal project UCR prompt | Required | Available |
| Test document (BRD-01) | Testing | Available |

---

## Change Execution Checklist

### Phase 1: Finding ID Format Standard

- [x] **1.1** Define canonical format: `PREFIX-P0-NNN`

**Canonical Format Table**:

| Persona | Prefix | Example |
|---------|--------|---------|
| Architect | ARCH | `ARCH-P0-001` |
| Auditor | AUD | `AUD-P0-001` |
| Tech Lead | TL | `TL-P1-001` |
| Strategist | STR | `STR-P1-001` |
| Devil's Advocate | DA | `DA-P0-001` |
| Operator | OP | `OP-P0-001` |
| Integration Lead | IL | `IL-P0-001` |
| Product Owner | PO | `PO-P1-001` |
| Business Analyst | BA | `BA-P1-001` |
| Fact Checker | FC | `FC-P0-001` |
| Chairperson (manifest) | REM | `REM-P0-001` |
| QA Lead | QA | `QA-P1-001` |
| UX Strategist | UX | `UX-P1-001` |
| Requirements Specialist | RS | `RS-P0-001` |

- [x] **1.2** Update `/opt/data/docs_flow_framework/UCX/ucx/core/review_memory.py` lines 497-549:

```python
# Canonical format: PREFIX-P0-NNN (e.g., ARCH-P0-001, TL-P1-002)
# This is the ONLY supported format - no legacy patterns needed
FINDING_ID_PATTERN = re.compile(
    r'(?:'
    r'\|\s*\*?\*?([A-Z]{2,4}-P[012]-\d{1,3})\*?\*?\s*\|'  # Table: | ARCH-P0-001 |
    r'|'
    r'\*\*([A-Z]{2,4}-P[012]-\d{1,3})\*\*'  # Bold: **TL-P0-001**
    r'|'
    r'(?:^|\n)\s*([A-Z]{2,4}-P[012]-\d{1,3})[:\s]'  # Line start: AUD-P0-001:
    r')',
    re.MULTILINE
)

def _parse_finding_id(raw_id: str) -> tuple[str, str, str]:
    """Parse finding ID into (prefix, priority, number)."""
    parts = raw_id.split('-')
    return (parts[0], parts[1], parts[2])  # ARCH, P0, 001
```

- [x] **1.4** Update `_extract_findings()` method (simplified - no legacy support):

```python
def _extract_findings(self, responses: dict[str, str]) -> list[dict]:
    """Extract findings from all persona responses.

    Only supports canonical PREFIX-P0-NNN format.
    """
    findings = []
    seen_ids = set()  # Deduplication

    # Category pattern
    category_pattern = re.compile(r'\[CAT:(\w+)\]', re.IGNORECASE)
    resolver = CategoryConflictResolver()

    for persona, response in responses.items():
        for match in FINDING_ID_PATTERN.finditer(response):
            raw_id = match.group(1) or match.group(2) or match.group(3)
            if raw_id and raw_id not in seen_ids:
                seen_ids.add(raw_id)
                prefix, priority, num = _parse_finding_id(raw_id)

                # Extract context around the finding
                start = max(0, match.start() - 200)
                end = min(len(response), match.end() + 500)
                context = response[start:end]

                # Try to extract category tag
                cat_match = category_pattern.search(context)
                explicit_tag = cat_match.group(1).lower() if cat_match else None

                # Use resolver for category assignment
                resolution = resolver.resolve(
                    finding_id=raw_id,
                    finding_text=context,
                    persona=persona,
                    explicit_tag=explicit_tag,
                )

                findings.append({
                    "persona": persona,
                    "priority": priority,
                    "id": raw_id,
                    "prefix": prefix,
                    "title": self._extract_title(context, raw_id),
                    "text": context[:500],
                    "category": resolution.resolved_category.value,
                })

    return findings
```

- [x] **1.5** Call validation in `save_response()` (line ~292):

```python
def save_response(
    self,
    persona: str,
    response: str,
    duration_ms: float = 0,
    tokens: int = 0,
) -> Path:
    """Save response for a persona and mark as complete."""
    path = self.get_response_path(persona)
    path.write_text(response, encoding="utf-8")

    # Validate chairperson response format
    self._validate_chairperson_response(persona, response)

    # Update session
    if self._session and persona not in self._session.completed_personas:
        self._session.completed_personas.append(persona)
        self._session.last_updated_at = datetime.now().isoformat()
        self._save_session()

    self.logger.debug(
        f"Saved response for {persona}: {len(response)} chars, {duration_ms:.0f}ms"
    )
    return path
```

- [x] **1.3** Add `_validate_chairperson_response()` method at line ~292:

```python
def _validate_chairperson_response(self, persona: str, response: str) -> None:
    """Validate Chairperson output contains required manifest markers."""
    if persona != "chairperson":
        return

    if "<!-- UCX-MANIFEST-START -->" not in response:
        self.logger.warning(
            "Chairperson response missing UCX-MANIFEST-START marker. "
            "Automated remediation routing will use persona extraction fallback."
        )
```

### Phase 2: UCR Prompt Structure Fixes

- [x] **2.1** Add Finding ID Format section to UCR prompt at line ~79:
  - File: `/opt/data/b-local/b-local-docs/docs/UCX/review/UCR_PROMPT_BRD_PROJECT.md`
  - File: `/opt/data/b-local/b-local-docs/docs/UCX/review/UCR_PROMPT_PRD_PROJECT.md` (also updated)

```markdown
### Finding ID Format (REQUIRED)

All personas MUST use this ID format: `{PREFIX}-P{PRIORITY}-{NNN}`

| Component | Rule | Example |
|-----------|------|---------|
| PREFIX | Persona abbreviation (2-4 chars) | ARCH, AUD, TL, OP |
| PRIORITY | P0, P1, or P2 | P0 |
| NNN | 3-digit sequence (001-999) | 001 |

**Examples**:
- Architect: `ARCH-P0-001`, `ARCH-P1-002`
- Auditor: `AUD-P0-001`, `AUD-P0-002`
- Operator: `OP-P0-001`, `OP-P1-001`

**INCORRECT formats** (do NOT use):
- `P0-OP-001` (priority first)
- `**[P0-1]**` (bracket format)
- `P0-1` (missing prefix)
```

- [x] **2.2** Update each persona output format section with explicit ID format (BRD + PRD prompts):

| Persona | Line Range | Update |
|---------|------------|--------|
| Architect | 150-164 | `\| ID (ARCH-P0-NNN) \| Finding \|` |
| Auditor | 192-212 | `\| ID (AUD-P0-NNN) \| Regulation \|` |
| Tech Lead | 245-257 | `\| ID (TL-P0-NNN) \| Finding \|` |
| Strategist | 280-289 | `\| ID (STR-P1-NNN) \| Finding \|` |
| Devil's Advocate | 327-337 | `\| ID (DA-P0-NNN) \| Failure Scenario \|` |
| Operator | 359-368 | `\| ID (OP-P0-NNN) \| Finding \|` |
| Integration Lead | 403-422 | `\| ID (IL-P0-NNN) \| Integration \|` |
| Product Owner | 446-455 | `\| ID (PO-P1-NNN) \| Finding \|` |
| Business Analyst | 478-487 | `\| ID (BA-P1-NNN) \| Finding \|` |
| Fact Checker | 537-560 | `\| ID (FC-P0-NNN) \| Finding \|` |
| Chairperson | 606-717 | `\| ID (REM-P0-NNN) \| Priority \|` |

### Phase 3: Framework Template Updates

- [x] **3.1** Finding ID prefix handled via `build_attention_steering_format()` at prompt END:
  - File: `/opt/data/docs_flow_framework/UCX/ucx/core/context_engine.py`
  - `PERSONA_PREFIX_MAP` defines all persona prefixes (ARCH, AUD, TL, etc.)
  - `build_attention_steering_format()` injects format at END (lines 464-503)
  - No need to modify `PERSONA_TEMPLATES.instructions` - redundant with attention steering

**NOTE**: Do NOT add output format to `instructions` field - format is injected at prompt END via `build_attention_steering_format()`. Only add Finding ID prefix guidance:

```python
"instructions": """...existing instructions...

## FINDING ID PREFIX
Your findings MUST use prefix: {PREFIX}
Format: {PREFIX}-P{N}-{NNN} (e.g., {PREFIX}-P0-001)

## APPENDIX VERIFICATION
If your finding relates to content that may be in an appendix:
- Add [VERIFY: section-id] tag to the finding
- Example: | {PREFIX}-P0-001 | Missing spec [VERIFY: BRD-01.18] | ... |
- Do NOT claim something is missing without checking appendix references
"""

# NOTE: Output format is added by build_attention_steering_format() at prompt END
# Do NOT include "## Output Format" section here - it will be stripped/ignored
```

- [x] **3.2** Restructure `build_persona_prompt()` for chairperson (lines 661-739):

```python
def build_persona_prompt(...) -> str:
    template = PERSONA_TEMPLATES.get(persona)
    parts = []

    # Domain knowledge
    if domain_knowledge:
        parts.append("=== YOUR DOMAIN KNOWLEDGE ===")
        parts.append(domain_knowledge)
        parts.append("=== END DOMAIN KNOWLEDGE ===\n")

    # Expert instructions (WITHOUT output format for chairperson)
    parts.append("==============")
    parts.append("EXPERT INSTRUCTIONS:")
    parts.append(f"You are {template['title']}.")

    if persona == "chairperson":
        # Only core instructions, format comes at END
        parts.append(template["instructions"].split("## Output Format")[0])
    else:
        parts.append(template["instructions"])

    parts.append("\n==============\n")

    # Verification protocol
    parts.append("## CRITICAL Verification Protocol")
    parts.append("Before claiming ANY requirement is missing, you MUST:")
    parts.append("1. Search the ENTIRE document including ALL appendices")
    parts.append("2. Check all related sections for the specification")
    parts.append("3. Only flag as missing if truly absent\n")

    # Layer-appropriate classification
    if doc_type.lower() == "brd":
        parts.append("## LAYER-APPROPRIATE FINDING CLASSIFICATION (BRD)")
        parts.append("...")

    # Previous findings
    if previous_responses:
        parts.append("=== PREVIOUS EXPERT FINDINGS ===")
        for prev_persona, response in previous_responses.items():
            # Truncate if too long
            if len(response) > 5000:
                parts.append(response[:5000] + "\n[... truncated ...]")
            else:
                parts.append(response)
        parts.append("\n=== END PREVIOUS FINDINGS ===\n")

    # Document content
    parts.append("=== DOCUMENT TO REVIEW ===")
    parts.append(shared_context)
    parts.append("=== END DOCUMENT ===")

    # FOR CHAIRPERSON: Output format at END (critical!)
    if persona == "chairperson":
        parts.append("\n" + "=" * 60)
        parts.append("CRITICAL: REQUIRED OUTPUT FORMAT (READ LAST)")
        parts.append("=" * 60)
        parts.append(_get_chairperson_format_template())

    return "\n".join(parts)


def _get_chairperson_format_template() -> str:
    """Get chairperson format template - placed at END of prompt."""
    return """
**FAILURE TO INCLUDE THESE MARKERS WILL CAUSE PROCESSING FAILURE**

You MUST produce:
1. `<!-- UCX-MANIFEST-START -->` marker
2. Manifest Summary table
3. Category Summary table
4. Fixer Assignment table
5. Findings Table with REM-P0-001 format IDs
6. `<!-- UCX-MANIFEST-END -->` marker

## EXACT OUTPUT STRUCTURE:

<!-- UCX-MANIFEST-START -->
### Manifest Summary
| Metric | Count |
|--------|-------|
| Total Unique Findings | [N] |
| P0 (Critical) | [N] |
| P1 (High) | [N] |
| P2 (Medium) | [N] |

### Findings Table
| ID | Priority | Category | Status | Fixer | Target File | Description |
|----|----------|----------|--------|-------|-------------|-------------|
| REM-P0-001 | P0 | [CAT:xxx] | OPEN | [persona] | [file.md] | [desc] |
| REM-P1-001 | P1 | [CAT:xxx] | OPEN | [persona] | [file.md] | [desc] |

<!-- UCX-MANIFEST-END -->
"""
```

### Phase 4: Skill File Updates

- [x] **4.1** Update project-specific chairperson skill file:
  - File: `/opt/data/b-local/b-local-docs/docs/UCX/skills/chairperson.md`
  - Moved "Remediation Findings Manifest" section to END of file
  - Added visual emphasis markers (===== lines) and warning text
  - Added explicit REM-P0-NNN format with examples

- [x] **4.2** Update framework skill files (fallbacks):
  - File: `/opt/data/docs_flow_framework/UCX/skills/chairperson.md`
    - Added manifest format section at END with emphasis markers
    - Added explicit REM-P0-NNN format
  - File: `/opt/data/docs_flow_framework/UCX/skills/operator.md`
    - Added Finding ID Format section with OP-P0-NNN format
    - Updated examples with IDs and output table format

### Phase 4.5: PRD Prompt Updates

- [x] **4.5.1** Update PRD prompt with Finding ID Format:
  - File: `/opt/data/b-local/b-local-docs/docs/UCX/review/UCR_PROMPT_PRD_PROJECT.md`
  - Added Finding ID Format section (PO, TL, ARCH, BA, UX, DA, QA, AUD, OP, FC, REM prefixes)
  - Updated all 11 persona output format tables with explicit ID format examples

### Phase 5: Testing & Verification

- [x] **5.1** Test finding extraction with existing responses:
  - **Result**: 33 findings extracted with canonical format, 0 legacy
  - **Date**: 2026-03-13
  - **Bug Found**: `UnifiedPromptLoader.build_persona_prompt()` not adding format at END
  - **Fix Applied**: Added attention steering call after document content

- [x] **5.2** Clear memory and re-run review:
  - **Result**: v008 report generated successfully
  - **Model**: Sonnet (multi-turn mode)

- [x] **5.3** Verify manifest present:
  - **Result**: UCX-MANIFEST-START/END markers present in chairperson response and report

- [x] **5.4** Verify frontmatter accuracy:
  - **Result**: All Finding IDs use canonical PREFIX-P0-NNN format

**ORIGINAL Phase 5 items (for reference)**:
```bash
cd /opt/data/b-local/b-local-docs
source .envrc
python -c "
from ucx.core.review_memory import ReviewMemory
m = ReviewMemory('docs/01_BRD/BRD-01_platform_architecture', 'brd')
findings = m._extract_findings(m.get_all_responses())
print(f'Extracted {len(findings)} findings')
for f in findings[:10]:
    print(f'  {f[\"id\"]}: {f[\"priority\"]} - {f[\"title\"][:50]}')
"
```

- [ ] **5.2** Clear memory and re-run review:
```bash
rm -rf docs/01_BRD/BRD-01_platform_architecture/.doc_review_memory/
ucx --model opus review brd docs/01_BRD/BRD-01_platform_architecture/
```

- [ ] **5.3** Verify manifest present:
```bash
grep -c "UCX-MANIFEST-START" docs/01_BRD/BRD-01_platform_architecture/BRD-01.UCR_review_report_v007.md
```

- [ ] **5.4** Verify frontmatter accuracy:
```bash
ucx scan docs/01_BRD/BRD-01_platform_architecture/BRD-01.UCR_review_report_v007.md --verbose
```

- [x] **5.5** Create unit tests for regex patterns:
  - File: `/opt/data/docs_flow_framework/UCX/tests/test_finding_extraction.py`

```python
import pytest
from ucx.core.review_memory import FINDING_ID_PATTERN, _parse_finding_id

class TestFindingIdPatterns:
    """Test finding ID extraction patterns."""

    def test_table_format(self):
        """Test PREFIX-P0-NNN in table."""
        text = "| ARCH-P0-001 | Missing failover | Section 6 |"
        matches = FINDING_ID_PATTERN.findall(text)
        assert len(matches) == 1

    def test_bold_format(self):
        """Test **PREFIX-P0-NNN** format."""
        text = "**TL-P1-002**: Transaction state machine required"
        matches = FINDING_ID_PATTERN.findall(text)
        assert len(matches) == 1

    def test_line_start_format(self):
        """Test PREFIX-P0-NNN at line start."""
        text = "\nAUD-P0-003: OFAC screening frequency"
        matches = FINDING_ID_PATTERN.findall(text)
        assert len(matches) == 1

    def test_parse_finding_id(self):
        """Test parsing of finding ID."""
        result = _parse_finding_id("ARCH-P0-001")
        assert result == ("ARCH", "P0", "001")

    def test_all_priority_levels(self):
        """Test P0, P1, P2 extraction."""
        text = "| DA-P0-001 | x |\n| STR-P1-002 | y |\n| UX-P2-003 | z |"
        matches = FINDING_ID_PATTERN.findall(text)
        assert len(matches) == 3

    def test_various_prefixes(self):
        """Test different persona prefixes."""
        prefixes = ["ARCH", "AUD", "TL", "OP", "IL", "DA", "STR", "PO", "BA", "FC", "REM", "QA", "UX", "RS"]
        for prefix in prefixes:
            text = f"| {prefix}-P0-001 | Finding |"
            matches = FINDING_ID_PATTERN.findall(text)
            assert len(matches) == 1, f"Failed for prefix: {prefix}"
```

- [x] **5.6** Update UCX documentation:
  - File: `/opt/data/docs_flow_framework/UCX/README.md` (lines 1114-1149)
  - ✓ Added "Finding ID Format Standard (v1.13.0+)" section
  - ✓ Added "Context Engineering (v1.13.0+)" section
  - ✓ Documented PREFIX-P0-NNN canonical format and persona prefixes

### Phase 6: Context Engineering

#### 6.1 Persona-Section Mapping

- [x] **6.1.1** Create section relevance mapping:
  - File: `/opt/data/docs_flow_framework/UCX/ucx/core/context_engine.py` (NEW)

```python
"""Context engineering for UCX persona prompts."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

class ContextLevel(Enum):
    """Hierarchical context levels."""
    OVERVIEW = 1      # ~2K tokens - always included
    RELEVANT = 2      # ~30-50K tokens - persona-filtered
    REFERENCE = 3     # ~10-20K tokens - appendices on-demand


# Persona to relevant BRD sections mapping
PERSONA_SECTION_MAP = {
    "architect": {
        "required": ["BRD-01.3", "BRD-01.6", "BRD-01.7", "BRD-01.10"],
        "optional": ["BRD-01.18"],  # Appendices - technical details
        "skip": ["BRD-01.13", "BRD-01.14", "BRD-01.15", "BRD-01.16"],  # Cost, Glossary, Trace, Index
    },
    "auditor": {
        "required": ["BRD-01.6", "BRD-01.7", "BRD-01.8", "BRD-01.9"],
        "optional": ["BRD-01.10"],  # Risk for compliance context
        "skip": ["BRD-01.18", "BRD-01.13", "BRD-01.14", "BRD-01.15", "BRD-01.16"],
    },
    "tech_lead": {
        "required": ["BRD-01.6", "BRD-01.7", "BRD-01.18"],
        "optional": ["BRD-01.10"],
        "skip": ["BRD-01.2", "BRD-01.13", "BRD-01.14", "BRD-01.15", "BRD-01.16"],
    },
    "strategist": {
        "required": ["BRD-01.2", "BRD-01.10", "BRD-01.13"],
        "optional": ["BRD-01.3"],
        "skip": ["BRD-01.6", "BRD-01.7", "BRD-01.18", "BRD-01.14", "BRD-01.15", "BRD-01.16"],
    },
    "devils_advocate": {
        "required": ["BRD-01.6", "BRD-01.10", "BRD-01.18"],
        "optional": ["BRD-01.7"],
        "skip": ["BRD-01.2", "BRD-01.13", "BRD-01.14", "BRD-01.15", "BRD-01.16"],
    },
    "operator": {
        "required": ["BRD-01.7", "BRD-01.12", "BRD-01.18"],
        "optional": ["BRD-01.10"],
        "skip": ["BRD-01.2", "BRD-01.13", "BRD-01.14", "BRD-01.15", "BRD-01.16"],
    },
    "integration_lead": {
        "required": ["BRD-01.3", "BRD-01.6", "BRD-01.18"],
        "optional": ["BRD-01.10"],
        "skip": ["BRD-01.2", "BRD-01.13", "BRD-01.14", "BRD-01.15", "BRD-01.16"],
    },
    "product_owner": {
        "required": ["BRD-01.2", "BRD-01.4", "BRD-01.5", "BRD-01.6"],
        "optional": ["BRD-01.11"],
        "skip": ["BRD-01.18", "BRD-01.14", "BRD-01.15", "BRD-01.16"],
    },
    "business_analyst": {
        "required": ["BRD-01.4", "BRD-01.5", "BRD-01.6", "BRD-01.8"],
        "optional": ["BRD-01.11"],
        "skip": ["BRD-01.18", "BRD-01.14", "BRD-01.15", "BRD-01.16"],
    },
    "fact_checker": {
        "required": [],  # Needs ALL sections to verify
        "optional": [],
        "skip": ["BRD-01.14", "BRD-01.15", "BRD-01.16"],  # Only skip Glossary, Trace, Index
    },
    "chairperson": {
        "required": [],  # Gets summarized view of all
        "optional": [],
        "skip": ["BRD-01.14", "BRD-01.15", "BRD-01.16"],
    },
}

# Sections to ALWAYS skip (low value, high token cost)
ALWAYS_SKIP_SECTIONS = [
    "glossary",
    "traceability",
    "index",
    "revision_history",
    "table_of_contents",
]

# Section keywords for dynamic relevance scoring
PERSONA_KEYWORDS = {
    "architect": ["architecture", "scalability", "failover", "CAP", "distributed", "microservice", "integration", "API", "database", "cache", "queue"],
    "auditor": ["compliance", "regulatory", "FinCEN", "OFAC", "PCI", "KYC", "AML", "SAR", "audit", "security", "encryption", "session"],
    "tech_lead": ["implementation", "state machine", "idempotency", "transaction", "saga", "retry", "error", "exception", "concurrency"],
    "strategist": ["business", "cost", "revenue", "ROI", "market", "competitor", "pricing", "float", "economics"],
    "devils_advocate": ["failure", "edge case", "timeout", "rollback", "compensation", "partial", "concurrent", "race condition"],
    "operator": ["deployment", "monitoring", "alerting", "SLI", "SLO", "runbook", "DR", "failover", "observability", "logging"],
    "integration_lead": ["partner", "API", "webhook", "integration", "contract", "schema", "versioning", "circuit breaker"],
}
```

#### 6.2 Hierarchical Document Context

- [x] **6.2.1** Implement hierarchical context with appendix-on-demand:

```python
@dataclass
class AppendixInfo:
    """Metadata about an appendix section for on-demand access."""
    section_id: str
    title: str
    estimated_tokens: int
    keywords: list[str]  # Key terms for relevance matching


@dataclass
class HierarchicalContext:
    """Hierarchical document context with appendix-on-demand support."""

    level1_overview: str      # ~2K tokens - always included
    level2_relevant: str      # ~30-50K tokens - persona-filtered
    level4_discovered: str    # ~5-10K tokens - keyword-discovered snippets

    # Appendix-on-demand: index only, not full content
    appendix_index: list[AppendixInfo]  # Lightweight metadata (~500 tokens)

    total_tokens: int
    sections_included: list[str]
    sections_skipped: list[str]
    discovered_snippets: list  # RelevantSnippet instances


class ContextEngine:
    """Build optimized context for persona prompts."""

    def __init__(self, doc_sections: dict[str, str], doc_type: str = "brd"):
        self._sections = doc_sections
        self._doc_type = doc_type
        self._section_summaries: dict[str, str] = {}

    def build_hierarchical_context(
        self,
        persona: str,
        enable_keyword_scan: bool = True,
        max_discovered_snippets: int = 10,
    ) -> HierarchicalContext:
        """Build hierarchical context with appendix-on-demand.

        NOTE: Appendices are NOT loaded into context. Only a lightweight
        index is provided. Personas use [VERIFY: appendix-id] tags to
        flag findings that need appendix verification.
        """

        # Level 1: Document Overview (always included)
        level1 = self._build_level1_overview()

        # Level 2: Persona-Relevant Sections
        level2 = self._build_level2_relevant(persona)

        # Appendix Index: lightweight metadata only
        appendix_index = self._build_appendix_index(persona)

        # Level 4: Keyword-discovered snippets (hybrid approach)
        level4 = ""
        discovered_snippets = []
        if enable_keyword_scan:
            discovered_snippets = self._scan_other_sections_for_keywords(
                persona, max_snippets=max_discovered_snippets
            )
            if discovered_snippets:
                level4 = self._format_discovered_snippets(persona, discovered_snippets)

        return HierarchicalContext(
            level1_overview=level1,
            level2_relevant=level2,
            level4_discovered=level4,
            appendix_index=appendix_index,
            total_tokens=self._estimate_tokens(level1 + level2 + level4),
            sections_included=self._get_included_sections(persona),
            sections_skipped=self._get_skipped_sections(persona),
            discovered_snippets=discovered_snippets,
        )

    def _build_level1_overview(self) -> str:
        """Build Level 1: Document Overview (~2K tokens)."""
        parts = [
            "=" * 60,
            "LEVEL 1: DOCUMENT OVERVIEW",
            "=" * 60,
            "",
        ]

        # Document title and version (from index or first section)
        if "BRD-01.0" in self._sections:
            index_content = self._sections["BRD-01.0"]
            # Extract title, version, scope
            parts.append(self._extract_document_header(index_content))

        # Section index with 1-line summaries
        parts.append("\n### Section Index\n")
        parts.append("| Section | Title | Summary |")
        parts.append("|---------|-------|---------|")

        for section_id, content in sorted(self._sections.items()):
            if self._should_skip_section(section_id, ""):
                continue
            title = self._extract_section_title(content)
            summary = self._generate_section_summary(content, max_words=15)
            parts.append(f"| {section_id} | {title} | {summary} |")

        # Key entities
        parts.append("\n### Key Entities\n")
        parts.append(self._extract_key_entities())

        return "\n".join(parts)

    def _build_level2_relevant(self, persona: str) -> str:
        """Build Level 2: Persona-Relevant Sections (~30-50K tokens)."""
        parts = [
            "",
            "=" * 60,
            f"LEVEL 2: RELEVANT SECTIONS FOR {persona.upper()}",
            "=" * 60,
            "",
        ]

        mapping = PERSONA_SECTION_MAP.get(persona, {})
        required_sections = mapping.get("required", [])
        skip_sections = mapping.get("skip", [])

        for section_id, content in sorted(self._sections.items()):
            # Skip if in skip list or always-skip
            if self._should_skip_section(section_id, persona):
                continue

            # Include if required OR if no required list (fact_checker, chairperson)
            if not required_sections or section_id in required_sections:
                parts.append(f"\n### {section_id}\n")
                parts.append(content)

        return "\n".join(parts)

    # NOTE: _build_level3_reference() REMOVED - see Phase 6.9 for appendix-on-demand

    def _should_skip_section(self, section_id: str, persona: str) -> bool:
        """Check if section should be skipped."""
        # Always skip certain sections
        section_lower = section_id.lower()
        for skip_term in ALWAYS_SKIP_SECTIONS:
            if skip_term in section_lower:
                return True

        # Check persona-specific skip list
        if persona:
            mapping = PERSONA_SECTION_MAP.get(persona, {})
            if section_id in mapping.get("skip", []):
                return True

        return False

    def _extract_document_header(self, content: str) -> str:
        """Extract document title, version, scope from index."""
        lines = content.split("\n")[:20]  # First 20 lines
        return "\n".join(lines)

    def _extract_section_title(self, content: str) -> str:
        """Extract section title from content."""
        for line in content.split("\n")[:5]:
            if line.startswith("#"):
                return line.lstrip("#").strip()[:50]
        return "Untitled"

    def _generate_section_summary(self, content: str, max_words: int = 15) -> str:
        """Generate brief section summary."""
        # Simple extraction - first sentence after title
        lines = [l for l in content.split("\n") if l.strip() and not l.startswith("#")]
        if lines:
            words = lines[0].split()[:max_words]
            return " ".join(words) + ("..." if len(lines[0].split()) > max_words else "")
        return "No summary"

    def _extract_key_entities(self) -> str:
        """Extract key entities from document."""
        # For BeeLocal: partners, systems, regulations
        entities = {
            "Partners": ["Bridge/Noah", "Asterium", "Paynet", "Okto", "Nuvei", "Modern Treasury"],
            "Systems": ["Cloud Run", "Cloud SQL", "Pub/Sub", "Redis", "Auth0"],
            "Regulations": ["FinCEN", "OFAC", "PCI-DSS", "KYC/AML"],
        }

        parts = []
        for category, items in entities.items():
            parts.append(f"- **{category}**: {', '.join(items)}")

        return "\n".join(parts)

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough: 4 chars per token)."""
        return len(text) // 4

    def _get_included_sections(self, persona: str) -> list[str]:
        """Get list of sections included for persona."""
        mapping = PERSONA_SECTION_MAP.get(persona, {})
        required = mapping.get("required", [])
        if not required:
            # Fact checker/chairperson - include all non-skipped
            return [s for s in self._sections.keys() if not self._should_skip_section(s, persona)]
        return required

    def _get_skipped_sections(self, persona: str) -> list[str]:
        """Get list of sections skipped for persona."""
        mapping = PERSONA_SECTION_MAP.get(persona, {})
        return mapping.get("skip", []) + ALWAYS_SKIP_SECTIONS
```

#### 6.3 Progressive Summarization of Prior Findings

- [x] **6.3.1** Implement prior findings summarizer:

```python
@dataclass
class FindingSummary:
    """Summary of a persona's findings."""
    persona: str
    p0_count: int
    p1_count: int
    p2_count: int
    key_issues: list[str]  # Top 3 issues
    finding_ids: list[str]  # All finding IDs


class PriorFindingsSummarizer:
    """Summarize prior persona findings to reduce context size."""

    def __init__(self):
        self._finding_pattern = re.compile(r'([A-Z]{2,4}-P[012]-\d{1,3})')

    def summarize_all(
        self,
        previous_responses: dict[str, str],
        current_persona: str,
    ) -> str:
        """Summarize all prior findings for context injection.

        Reduces ~50K tokens to ~5K tokens (90% reduction).
        """
        summaries = []
        all_p0_findings = []

        for persona, response in previous_responses.items():
            summary = self._summarize_persona(persona, response)
            summaries.append(summary)

            # Collect P0 findings for critical list
            for fid in summary.finding_ids:
                if "-P0-" in fid:
                    all_p0_findings.append((fid, persona, self._extract_finding_title(response, fid)))

        return self._format_summary(summaries, all_p0_findings, current_persona)

    def _summarize_persona(self, persona: str, response: str) -> FindingSummary:
        """Summarize a single persona's response."""
        finding_ids = self._finding_pattern.findall(response)

        p0_count = sum(1 for f in finding_ids if "-P0-" in f)
        p1_count = sum(1 for f in finding_ids if "-P1-" in f)
        p2_count = sum(1 for f in finding_ids if "-P2-" in f)

        # Extract key issues (first 3 P0s or P1s)
        key_issues = []
        for fid in finding_ids[:3]:
            title = self._extract_finding_title(response, fid)
            if title:
                key_issues.append(f"{fid}: {title[:50]}")

        return FindingSummary(
            persona=persona,
            p0_count=p0_count,
            p1_count=p1_count,
            p2_count=p2_count,
            key_issues=key_issues,
            finding_ids=finding_ids,
        )

    def _extract_finding_title(self, response: str, finding_id: str) -> str:
        """Extract finding title from response."""
        # Look for pattern: FINDING_ID | Title | or FINDING_ID: Title
        patterns = [
            rf'\|\s*\*?\*?{re.escape(finding_id)}\*?\*?\s*\|\s*([^|]+)',  # Table
            rf'{re.escape(finding_id)}[:\s]+([^\n|]+)',  # Inline
        ]

        for pattern in patterns:
            match = re.search(pattern, response)
            if match:
                return match.group(1).strip()[:100]

        return ""

    def _format_summary(
        self,
        summaries: list[FindingSummary],
        all_p0_findings: list[tuple],
        current_persona: str,
    ) -> str:
        """Format summarized findings for prompt injection."""
        parts = [
            "=" * 60,
            "PRIOR FINDINGS SUMMARY (Context Optimized)",
            "=" * 60,
            "",
            "### Persona Summary",
            "",
            "| Persona | P0 | P1 | P2 | Key Issues |",
            "|---------|----|----|----|-----------| ",
        ]

        total_p0 = 0
        total_p1 = 0
        total_p2 = 0

        for s in summaries:
            key_str = "; ".join(s.key_issues[:2]) if s.key_issues else "None"
            parts.append(f"| {s.persona} | {s.p0_count} | {s.p1_count} | {s.p2_count} | {key_str[:60]} |")
            total_p0 += s.p0_count
            total_p1 += s.p1_count
            total_p2 += s.p2_count

        parts.append(f"| **TOTAL** | **{total_p0}** | **{total_p1}** | **{total_p2}** | |")

        # Critical P0 findings (deduplicated, top 10)
        parts.append("\n### Critical P0 Findings (Top 10)")
        parts.append("")

        seen = set()
        for fid, persona, title in all_p0_findings[:10]:
            if fid not in seen:
                seen.add(fid)
                parts.append(f"- **{fid}** ({persona}): {title}")

        # Guidance for current persona
        parts.append(f"\n### Focus Areas for {current_persona.upper()}")
        parts.append("")
        parts.append(f"Review areas NOT yet covered by previous {len(summaries)} personas.")
        parts.append("Avoid duplicating findings already identified above.")
        parts.append("")

        return "\n".join(parts)
```

#### 6.4 Attention Steering Delimiters

- [x] **6.4.1** Implement attention steering for output format:

```python
def build_attention_steering_format(persona: str, prefix: str) -> str:
    """Build attention-steering format section for prompt END."""

    delimiter = "═" * 70
    warning = "⚠" * 3

    return f"""

{delimiter}
██████████████████████████████████████████████████████████████████████
██  CRITICAL: REQUIRED OUTPUT FORMAT - READ THIS SECTION LAST       ██
██████████████████████████████████████████████████████████████████████
{delimiter}

{warning} FAILURE TO USE THIS EXACT FORMAT WILL CAUSE PROCESSING FAILURE {warning}

### Finding ID Format: {prefix}-P{{0-2}}-NNN

Examples:
- {prefix}-P0-001 (Critical finding #1)
- {prefix}-P1-002 (High priority finding #2)

### Required Output Table

You MUST produce findings in this EXACT table format:

| ID ({prefix}-P0-NNN) | Finding | Section | Gap | Remediation |
|{'-' * 20}|---------|---------|-----|-------------|
| {prefix}-P0-001 | [Specific finding] | [X.X] | [What's missing] | [Exact fix text] |
| {prefix}-P1-001 | [Specific finding] | [X.X] | [What's missing] | [Exact fix text] |

### Rules

1. Each finding MUST have unique ID: {prefix}-P{{N}}-{{NNN}}
2. Section MUST reference exact section number (e.g., 6.1.2)
3. Remediation MUST include specific text to add
4. Do NOT produce summaries - produce COMPLETE TABLES
5. Minimum 5 findings expected

{delimiter}
"""


def build_chairperson_manifest_format() -> str:
    """Build chairperson manifest format section."""

    delimiter = "═" * 70

    return f"""

{delimiter}
██████████████████████████████████████████████████████████████████████
██  CRITICAL: CHAIRPERSON MANIFEST FORMAT - REQUIRED                ██
██████████████████████████████████████████████████████████████████████
{delimiter}

You MUST include these EXACT markers for automated processing:

<!-- UCX-MANIFEST-START -->

### Manifest Summary

| Metric | Count |
|--------|-------|
| Total Unique Findings | [N] |
| P0 (Critical) | [N] |
| P1 (High) | [N] |
| P2 (Medium) | [N] |
| Weighted Score | [N]/100 |

### Category Summary

| Category | P0 | P1 | P2 | Weighted |
|----------|----|----|----|---------:|
| functional | [N] | [N] | [N] | -[N] |
| compliance | [N] | [N] | [N] | -[N] |
| integration | [N] | [N] | [N] | -[N] |
| ... | ... | ... | ... | ... |

### Findings Table

| ID | Priority | Category | Status | Fixer | Target File | Description |
|----|----------|----------|--------|-------|-------------|-------------|
| REM-P0-001 | P0 | [CAT:compliance] | OPEN | auditor | BRD-01.6.md | [description] |
| REM-P0-002 | P0 | [CAT:integration] | OPEN | integration_lead | BRD-01.6.md | [description] |
| REM-P1-001 | P1 | [CAT:functional] | OPEN | tech_lead | BRD-01.6.md | [description] |

<!-- UCX-MANIFEST-END -->

{delimiter}

⚠️⚠️⚠️ MANIFEST MARKERS ARE REQUIRED - DO NOT OMIT ⚠️⚠️⚠️

{delimiter}
"""
```

#### 6.5 Updated build_persona_prompt() with Context Engineering

- [x] **6.5.1** Refactor `build_persona_prompt()` to use context engine:

```python
def build_persona_prompt(
    persona: str,
    doc_sections: dict[str, str],
    previous_responses: dict[str, str] = None,
    doc_type: str = "brd",
    skill_dir: Optional[Path] = None,
    project_dir: Optional[Path] = None,
) -> str:
    """
    Build optimized prompt using context engineering.

    Structure:
    1. Domain Knowledge (from skill file)
    2. Expert Instructions (core only)
    3. Verification Protocol
    4. Layer Classification
    5. Prior Findings Summary (context-optimized)
    6. Hierarchical Document Context (Level 1 + Level 2)
    7. OUTPUT FORMAT AT END (attention steering)
    """
    template = PERSONA_TEMPLATES.get(persona)
    if not template:
        raise ValueError(f"Unknown persona: {persona}")

    parts = []

    # 1. Domain Knowledge
    skill_content = _load_skill_content(persona, skill_dir, project_dir)
    if skill_content:
        parts.append("=== YOUR DOMAIN KNOWLEDGE ===")
        parts.append(skill_content)
        parts.append("=== END DOMAIN KNOWLEDGE ===\n")

    # 2. Expert Instructions (WITHOUT output format - that comes at END)
    parts.append("=" * 60)
    parts.append("EXPERT INSTRUCTIONS")
    parts.append("=" * 60)
    parts.append(f"You are {template['title']}.")

    # Strip output format from instructions (we'll add it at end)
    instructions = template["instructions"]
    if "## Output Format" in instructions:
        instructions = instructions.split("## Output Format")[0]
    parts.append(instructions)
    parts.append("")

    # 3. Verification Protocol
    parts.append("## CRITICAL Verification Protocol")
    parts.append("Before claiming ANY requirement is missing, you MUST:")
    parts.append("1. Search the ENTIRE document including ALL appendices")
    parts.append("2. Check all related sections for the specification")
    parts.append("3. Only flag as missing if truly absent\n")

    # 4. Layer Classification
    if doc_type.lower() == "brd":
        parts.append("## LAYER-APPROPRIATE FINDING CLASSIFICATION (BRD)")
        parts.append("BRD defines WHAT is required, not HOW to implement:")
        parts.append("- P0 at BRD: Regulatory mandates, security REQUIREMENTS")
        parts.append("- P1 (Defer to SPEC): Specific algorithms, config values")
        parts.append("")

    # 5. Prior Findings Summary (CONTEXT OPTIMIZED)
    if previous_responses:
        summarizer = PriorFindingsSummarizer()
        summary = summarizer.summarize_all(previous_responses, persona)
        parts.append(summary)

    # 6. Hierarchical Document Context (with appendix-on-demand)
    context_engine = ContextEngine(doc_sections, doc_type)

    hierarchical = context_engine.build_hierarchical_context(
        persona=persona,
        enable_keyword_scan=True,
    )

    parts.append(hierarchical.level1_overview)
    parts.append(hierarchical.level2_relevant)

    # Add appendix index for on-demand access
    if hierarchical.appendix_index:
        parts.append(_format_appendix_index(hierarchical.appendix_index))

    # Add keyword-discovered snippets
    if hierarchical.level4_discovered:
        parts.append(hierarchical.level4_discovered)

    # Log context stats
    logger.info(
        f"Context for {persona}: {hierarchical.total_tokens} tokens, "
        f"included={len(hierarchical.sections_included)}, "
        f"skipped={len(hierarchical.sections_skipped)}"
    )

    # 7. OUTPUT FORMAT AT END (Attention Steering)
    prefix = PERSONA_PREFIX_MAP.get(persona, persona[:2].upper())

    if persona == "chairperson":
        parts.append(build_chairperson_manifest_format())
    else:
        parts.append(build_attention_steering_format(persona, prefix))

    return "\n".join(parts)


# Persona prefix mapping
PERSONA_PREFIX_MAP = {
    "architect": "ARCH",
    "auditor": "AUD",
    "tech_lead": "TL",
    "strategist": "STR",
    "devils_advocate": "DA",
    "operator": "OP",
    "integration_lead": "IL",
    "product_owner": "PO",
    "business_analyst": "BA",
    "fact_checker": "FC",
    "chairperson": "REM",
    "qa_lead": "QA",
    "ux_strategist": "UX",
    "requirements_specialist": "RS",
}
```

#### 6.7 Hybrid Context Selection (Static + Dynamic Keyword Scan)

**Approach**: Use static `PERSONA_SECTION_MAP` as primary source, then perform a fast keyword scan of "other" sections (not in required/skip) to discover additional relevant content.

**Rationale**:
- Static mapping ensures core sections are always included (reliable)
- Keyword scan catches relevant content in unexpected locations
- Prevents missing critical information scattered across sections
- Low overhead: only scans sections not already included/skipped

- [ ] **6.7.1** Add `RelevantSnippet` dataclass for discovered content:

```python
@dataclass
class RelevantSnippet:
    """Snippet of relevant content discovered via keyword scan."""
    section_id: str
    keyword_matched: str
    snippet: str          # ~200 chars around the keyword match
    relevance_score: float  # 0.0-1.0 based on keyword density


@dataclass
class AppendixInfo:
    """Metadata about an appendix section for on-demand access."""
    section_id: str
    title: str
    estimated_tokens: int
    keywords: list[str]  # Key terms for relevance matching


@dataclass
class HierarchicalContext:
    """Hierarchical document context with appendix-on-demand support."""

    level1_overview: str        # ~2K tokens - always included
    level2_relevant: str        # ~30-50K tokens - persona-filtered (static)
    level4_discovered: str      # ~5-10K tokens - keyword-discovered snippets

    # Appendix-on-demand: index only, not full content
    appendix_index: list[AppendixInfo]  # NEW: lightweight appendix metadata

    total_tokens: int
    sections_included: list[str]
    sections_skipped: list[str]
    discovered_snippets: list[RelevantSnippet]  # snippets from other sections
```

- [ ] **6.7.2** Implement `_scan_other_sections_for_keywords()`:

```python
def _scan_other_sections_for_keywords(
    self,
    persona: str,
    max_snippets: int = 10,
    snippet_context: int = 200,
) -> list[RelevantSnippet]:
    """
    Fast keyword scan of sections NOT in required/skip lists.

    Args:
        persona: Persona name for keyword lookup
        max_snippets: Maximum snippets to return (default: 10)
        snippet_context: Characters around match to extract (default: 200)

    Returns:
        List of RelevantSnippet sorted by relevance_score descending
    """
    keywords = PERSONA_KEYWORDS.get(persona, [])
    if not keywords:
        return []

    mapping = PERSONA_SECTION_MAP.get(persona, {})
    required = set(mapping.get("required", []))
    skip = set(mapping.get("skip", []))
    optional = set(mapping.get("optional", []))

    # Sections to scan = all - required - skip - optional - always_skip
    sections_to_scan = []
    for section_id in self._sections.keys():
        if section_id in required or section_id in skip or section_id in optional:
            continue
        if self._should_skip_section(section_id, ""):  # Always-skip check
            continue
        sections_to_scan.append(section_id)

    snippets = []

    for section_id in sections_to_scan:
        content = self._sections[section_id]
        content_lower = content.lower()

        # Count keyword matches for relevance scoring
        match_count = 0
        match_positions = []

        for keyword in keywords:
            keyword_lower = keyword.lower()
            pos = 0
            while True:
                pos = content_lower.find(keyword_lower, pos)
                if pos == -1:
                    break
                match_count += 1
                match_positions.append((pos, keyword))
                pos += len(keyword)

        if match_count == 0:
            continue

        # Calculate relevance score (keyword density)
        relevance_score = min(1.0, match_count / 10.0)  # Cap at 10 matches = 1.0

        # Extract snippet around first match
        first_pos, first_keyword = match_positions[0]
        start = max(0, first_pos - snippet_context // 2)
        end = min(len(content), first_pos + len(first_keyword) + snippet_context // 2)
        snippet_text = content[start:end].strip()

        # Add ellipsis if truncated
        if start > 0:
            snippet_text = "..." + snippet_text
        if end < len(content):
            snippet_text = snippet_text + "..."

        snippets.append(RelevantSnippet(
            section_id=section_id,
            keyword_matched=first_keyword,
            snippet=snippet_text,
            relevance_score=relevance_score,
        ))

    # Sort by relevance and limit
    snippets.sort(key=lambda s: s.relevance_score, reverse=True)
    return snippets[:max_snippets]
```

- [ ] **6.7.3** Update `build_hierarchical_context()` with hybrid approach (NO level3 - appendix-on-demand):

```python
def build_hierarchical_context(
    self,
    persona: str,
    enable_keyword_scan: bool = True,  # Enable hybrid discovery
    max_discovered_snippets: int = 10,
) -> HierarchicalContext:
    """
    Build hierarchical context using hybrid approach with appendix-on-demand.

    Hybrid approach:
    1. STATIC (primary): Use PERSONA_SECTION_MAP for required sections
    2. DYNAMIC (secondary): Keyword scan of other sections for relevant snippets
    3. APPENDIX-ON-DEMAND: Build lightweight index, not full content

    NOTE: Appendices are NOT included in the prompt. Personas can request
    appendix content via the [VERIFY: appendix-id] tag pattern.
    """

    # Level 1: Document Overview (always included)
    level1 = self._build_level1_overview()

    # Level 2: Persona-Relevant Sections (STATIC - from PERSONA_SECTION_MAP)
    level2 = self._build_level2_relevant(persona)

    # Appendix Index: Lightweight metadata for on-demand access
    appendix_index = self._build_appendix_index(persona)

    # Level 4: Keyword-Discovered Snippets (DYNAMIC - hybrid scan)
    level4 = ""
    discovered_snippets = []
    if enable_keyword_scan:
        discovered_snippets = self._scan_other_sections_for_keywords(
            persona, max_snippets=max_discovered_snippets
        )
        if discovered_snippets:
            level4 = self._format_discovered_snippets(persona, discovered_snippets)

    return HierarchicalContext(
        level1_overview=level1,
        level2_relevant=level2,
        level4_discovered=level4,
        appendix_index=appendix_index,
        total_tokens=self._estimate_tokens(level1 + level2 + level4),
        sections_included=self._get_included_sections(persona),
        sections_skipped=self._get_skipped_sections(persona),
        discovered_snippets=discovered_snippets,
    )

def _format_discovered_snippets(
    self,
    persona: str,
    snippets: list[RelevantSnippet],
) -> str:
    """Format discovered snippets for prompt injection."""
    if not snippets:
        return ""

    parts = [
        "",
        "=" * 60,
        f"LEVEL 4: DISCOVERED RELEVANT CONTENT FOR {persona.upper()}",
        "=" * 60,
        "",
        "The following snippets from other sections may be relevant to your analysis:",
        "",
    ]

    for i, snippet in enumerate(snippets, 1):
        parts.append(f"### Snippet {i} (from {snippet.section_id})")
        parts.append(f"**Keyword**: {snippet.keyword_matched}")
        parts.append(f"**Relevance**: {snippet.relevance_score:.1%}")
        parts.append(f"```")
        parts.append(snippet.snippet)
        parts.append(f"```")
        parts.append("")

    parts.append("---")
    parts.append("NOTE: Review these snippets if relevant to your domain expertise.")
    parts.append("")

    return "\n".join(parts)
```

- [ ] **6.7.4** Add hybrid approach tests:

```python
class TestHybridContextSelection:
    """Test hybrid context selection (static + dynamic)."""

    @pytest.fixture
    def sections_with_scattered_keywords(self):
        """Sections with relevant keywords in unexpected places."""
        return {
            "BRD-01.0": "# Index\nDocument overview...",
            "BRD-01.2": "# Business Context\nMarket analysis...",
            "BRD-01.6": "# Functional Requirements\nTransaction flows...",
            "BRD-01.7": "# Quality Attributes\nPerformance targets...",
            "BRD-01.11": "# Success Metrics\nThe system must handle failover within 30 seconds. API response time under 200ms.",
            "BRD-01.12": "# Deployment\nUses circuit breaker pattern for partner integrations. Webhook validation required.",
        }

    def test_static_sections_always_included(self, sections_with_scattered_keywords):
        """Required sections from PERSONA_SECTION_MAP always included."""
        engine = ContextEngine(sections_with_scattered_keywords)
        ctx = engine.build_hierarchical_context("architect", enable_keyword_scan=True)

        # Static sections must be in level2
        assert "BRD-01.6" in ctx.level2_relevant
        assert "BRD-01.7" in ctx.level2_relevant

    def test_keyword_scan_discovers_relevant_content(self, sections_with_scattered_keywords):
        """Keyword scan finds architect keywords in non-required sections."""
        engine = ContextEngine(sections_with_scattered_keywords)
        ctx = engine.build_hierarchical_context("architect", enable_keyword_scan=True)

        # BRD-01.11 has "failover" and "API" - architect keywords
        # Should be discovered via keyword scan
        assert len(ctx.discovered_snippets) > 0

        # Check discovered sections
        discovered_section_ids = [s.section_id for s in ctx.discovered_snippets]
        assert "BRD-01.11" in discovered_section_ids or "BRD-01.12" in discovered_section_ids

    def test_keyword_scan_disabled(self, sections_with_scattered_keywords):
        """Keyword scan can be disabled."""
        engine = ContextEngine(sections_with_scattered_keywords)
        ctx = engine.build_hierarchical_context("architect", enable_keyword_scan=False)

        assert ctx.level4_discovered == ""
        assert len(ctx.discovered_snippets) == 0

    def test_integration_lead_finds_integration_keywords(self, sections_with_scattered_keywords):
        """Integration Lead finds circuit breaker, webhook in Deployment section."""
        engine = ContextEngine(sections_with_scattered_keywords)
        ctx = engine.build_hierarchical_context("integration_lead", enable_keyword_scan=True)

        # BRD-01.12 has integration keywords
        discovered_ids = [s.section_id for s in ctx.discovered_snippets]
        assert "BRD-01.12" in discovered_ids

    def test_discovered_snippets_sorted_by_relevance(self, sections_with_scattered_keywords):
        """Discovered snippets are sorted by relevance score."""
        engine = ContextEngine(sections_with_scattered_keywords)
        ctx = engine.build_hierarchical_context("architect", enable_keyword_scan=True)

        if len(ctx.discovered_snippets) > 1:
            scores = [s.relevance_score for s in ctx.discovered_snippets]
            assert scores == sorted(scores, reverse=True)
```

**Benefits of Hybrid Approach**:

| Benefit | Description |
|---------|-------------|
| Completeness | Catches relevant content scattered across sections |
| Reliability | Static mapping ensures core sections never missed |
| Efficiency | Only scans non-mapped sections (minimal overhead) |
| Transparency | Discovered snippets clearly labeled as "additional" |
| Configurable | Can disable keyword scan if not needed |

**Token Budget (with Appendix-on-Demand)**:

| Level | Source | Tokens | Purpose |
|-------|--------|--------|---------|
| 1 | Overview | ~2K | Document structure, always included |
| 2 | Static Map | ~30-50K | Core sections per persona |
| Index | Appendix Metadata | ~500 | Lightweight index (on-demand) |
| 4 | Keyword Scan | ~5-10K | Discovered snippets |
| **Total** | Optimized | **~40-65K** | Reduced via appendix-on-demand |

#### 6.8 Context Engineering Tests

- [x] **6.8.1** Create tests for context engine:
  - File: `/opt/data/docs_flow_framework/UCX/tests/test_context_engine.py`

```python
import pytest
from ucx.core.context_engine import (
    ContextEngine,
    ContextLevel,
    PriorFindingsSummarizer,
    PERSONA_SECTION_MAP,
)


class TestContextEngine:
    """Test context engineering functionality."""

    @pytest.fixture
    def sample_sections(self):
        return {
            "BRD-01.0": "# Index\nDocument overview...",
            "BRD-01.2": "# Business Context\nMarket analysis...",
            "BRD-01.6": "# Functional Requirements\nTransaction flows...",
            "BRD-01.7": "# Quality Attributes\nPerformance targets...",
            "BRD-01.10": "# Risk Management\nRisk register...",
            "BRD-01.13": "# Cost-Benefit\nFinancial projections...",
            "BRD-01.14": "# Glossary\nTerms...",
            "BRD-01.18": "# Appendices\nTechnical details...",
        }

    def test_architect_gets_relevant_sections(self, sample_sections):
        """Architect should get technical sections, skip cost/glossary."""
        engine = ContextEngine(sample_sections)
        ctx = engine.build_hierarchical_context("architect")

        assert "BRD-01.6" in ctx.sections_included
        assert "BRD-01.7" in ctx.sections_included
        assert "BRD-01.13" in ctx.sections_skipped  # Cost
        assert "BRD-01.14" in ctx.sections_skipped  # Glossary

    def test_strategist_gets_business_sections(self, sample_sections):
        """Strategist should get business sections, skip technical."""
        engine = ContextEngine(sample_sections)
        ctx = engine.build_hierarchical_context("strategist")

        assert "BRD-01.2" in ctx.sections_included
        assert "BRD-01.13" in ctx.sections_included
        assert "BRD-01.18" in ctx.sections_skipped  # Technical appendix

    def test_fact_checker_gets_all_sections(self, sample_sections):
        """Fact Checker should get all sections except glossary."""
        engine = ContextEngine(sample_sections)
        ctx = engine.build_hierarchical_context("fact_checker")

        # Should include everything except glossary/index
        assert len(ctx.sections_included) >= 5
        assert "BRD-01.14" in ctx.sections_skipped  # Glossary

    def test_level1_overview_generated(self, sample_sections):
        """Level 1 should contain document overview."""
        engine = ContextEngine(sample_sections)
        ctx = engine.build_hierarchical_context("architect")

        assert "LEVEL 1: DOCUMENT OVERVIEW" in ctx.level1_overview
        assert "Section Index" in ctx.level1_overview

    def test_context_size_reduction(self, sample_sections):
        """Context should be smaller than full document."""
        engine = ContextEngine(sample_sections)
        full_size = sum(len(s) for s in sample_sections.values())

        ctx = engine.build_hierarchical_context("architect")
        optimized_size = len(ctx.level1_overview) + len(ctx.level2_relevant)

        # Should be at least 30% smaller for architect
        assert optimized_size < full_size * 0.7


class TestPriorFindingsSummarizer:
    """Test prior findings summarization."""

    def test_summarize_extracts_counts(self):
        """Should extract P0/P1/P2 counts correctly."""
        responses = {
            "architect": "| ARCH-P0-001 | Gap 1 |\n| ARCH-P0-002 | Gap 2 |\n| ARCH-P1-001 | Gap 3 |",
            "auditor": "| AUD-P0-001 | Compliance gap |",
        }

        summarizer = PriorFindingsSummarizer()
        summary = summarizer.summarize_all(responses, "tech_lead")

        assert "| architect | 2 | 1 |" in summary
        assert "| auditor | 1 | 0 |" in summary

    def test_summarize_lists_critical_p0s(self):
        """Should list critical P0 findings."""
        responses = {
            "architect": "| ARCH-P0-001 | Missing failover |",
        }

        summarizer = PriorFindingsSummarizer()
        summary = summarizer.summarize_all(responses, "tech_lead")

        assert "ARCH-P0-001" in summary
        assert "Critical P0 Findings" in summary

    def test_summary_much_smaller_than_raw(self):
        """Summary should be ~90% smaller than raw responses."""
        # Simulate 5K per persona
        responses = {
            "architect": "x" * 5000,
            "auditor": "x" * 5000,
            "tech_lead": "x" * 5000,
        }

        summarizer = PriorFindingsSummarizer()
        summary = summarizer.summarize_all(responses, "operator")

        raw_size = sum(len(r) for r in responses.values())
        assert len(summary) < raw_size * 0.2  # At least 80% reduction
```

#### 6.9 Appendix-on-Demand

**Rationale**: Appendices (BRD-01.18, etc.) can be 20-50K tokens. Including them in every persona prompt causes token explosion. Instead:
- Build a lightweight index of appendices (~500 tokens)
- Personas can read appendix files on-demand when needed
- Findings requiring appendix verification use `[VERIFY: appendix-id]` tag
- Post-processing phase validates tagged findings against appendix content

**Benefits**:
| Benefit | Impact |
|---------|--------|
| Token Reduction | 20-50K tokens saved per persona call |
| Targeted Verification | Only load appendix when finding needs it |
| Completeness | Personas can still access appendix data when needed |
| Audit Trail | `[VERIFY: appendix-id]` tags show verification chain |

- [ ] **6.9.1** Implement `_build_appendix_index()`:

**FIX G1**: Include content summary (~200 chars) to help personas understand appendix content
**FIX G3**: Detect appendices dynamically by pattern, not just from "optional" list

```python
@dataclass
class AppendixInfo:
    """Metadata about an appendix section for on-demand access."""
    section_id: str
    title: str
    estimated_tokens: int
    keywords: list[str]       # Key terms for relevance matching
    content_summary: str      # NEW: ~200 char summary for context (FIX G1)


# Patterns to detect appendix sections dynamically (FIX G3)
APPENDIX_TITLE_PATTERNS = [
    "appendix", "annex", "reference", "technical details",
    "supplementary", "attachment", "exhibit"
]


def _build_appendix_index(self, persona: str) -> list[AppendixInfo]:
    """
    Build appendix index with summaries for on-demand access.

    Instead of loading full appendix content (20-50K tokens),
    build a ~2K token index with metadata AND summaries.

    FIX G1: Include content_summary so personas can make informed decisions
    FIX G3: Detect appendices dynamically, not just from "optional" list
    """
    appendix_sections = set()

    # 1. Dynamic detection by title pattern (FIX G3)
    for section_id, content in self._sections.items():
        title = self._extract_section_title(content).lower()
        if any(pattern in title for pattern in APPENDIX_TITLE_PATTERNS):
            appendix_sections.add(section_id)

    # 2. Also include explicitly marked optional sections
    mapping = PERSONA_SECTION_MAP.get(persona, {})
    for section_id in mapping.get("optional", []):
        if section_id in self._sections:
            appendix_sections.add(section_id)

    # 3. Exclude sections already in "required" (they're in Level 2)
    required_sections = set(mapping.get("required", []))
    appendix_sections -= required_sections

    # Build index with summaries
    index = []
    for section_id in sorted(appendix_sections):
        content = self._sections[section_id]
        title = self._extract_section_title(content)
        tokens = self._estimate_tokens(content)
        keywords = self._extract_appendix_keywords(content)

        # FIX G1: Generate content summary for personas
        summary = self._generate_appendix_summary(content)

        index.append(AppendixInfo(
            section_id=section_id,
            title=title,
            estimated_tokens=tokens,
            keywords=keywords[:10],
            content_summary=summary,  # NEW: helps personas decide
        ))

    return index


def _generate_appendix_summary(self, content: str, max_chars: int = 200) -> str:
    """
    Generate content summary for appendix (FIX G1).

    Extracts first paragraph and key headers to give personas
    enough context to decide if appendix is relevant.
    """
    lines = content.split("\n")
    summary_parts = []

    # Extract headers (## level)
    headers = [l.lstrip("#").strip() for l in lines if l.startswith("##")][:5]
    if headers:
        summary_parts.append(f"Sections: {', '.join(headers)}")

    # Extract first non-header paragraph
    for line in lines:
        if line.strip() and not line.startswith("#"):
            summary_parts.append(line.strip()[:100])
            break

    summary = " | ".join(summary_parts)
    return summary[:max_chars] + ("..." if len(summary) > max_chars else "")


def _extract_appendix_keywords(self, content: str, max_keywords: int = 20) -> list[str]:
    """Extract key terms from appendix content for index."""
    # Simple keyword extraction - headers and key terms
    keywords = []

    # Extract headers
    for line in content.split("\n"):
        if line.startswith("#"):
            header = line.lstrip("#").strip()
            keywords.extend(header.split()[:3])

    # Extract bold terms
    bold_pattern = re.compile(r'\*\*([^*]+)\*\*')
    for match in bold_pattern.finditer(content):
        keywords.append(match.group(1).strip())

    # Deduplicate and limit
    seen = set()
    unique_keywords = []
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower not in seen and len(kw) > 2:
            seen.add(kw_lower)
            unique_keywords.append(kw)

    return unique_keywords[:max_keywords]
```

- [ ] **6.9.2** Add appendix index to prompt context:

**FIX G1**: Include content_summary so personas can make informed decisions without loading full appendix.

```python
def _format_appendix_index(self, appendix_index: list[AppendixInfo]) -> str:
    """Format appendix index with summaries for prompt injection (FIX G1)."""
    if not appendix_index:
        return ""

    parts = [
        "",
        "=" * 60,
        "AVAILABLE APPENDICES (On-Demand Verification)",
        "=" * 60,
        "",
        "The following appendices are available but NOT fully included in this prompt.",
        "Review the summaries below before claiming content is missing.",
        "",
    ]

    # Detailed view with summaries (FIX G1)
    for app in appendix_index:
        parts.append(f"### {app.section_id}: {app.title}")
        parts.append(f"- **Size**: ~{app.estimated_tokens:,} tokens")
        parts.append(f"- **Topics**: {', '.join(app.keywords[:7])}")
        parts.append(f"- **Summary**: {app.content_summary}")
        parts.append("")

    parts.append("---")
    parts.append("**REQUIRED**: If your finding relates to appendix content:")
    parts.append("1. Check the summary above - content may already exist")
    parts.append("2. Add `[VERIFY: section-id]` tag if verification needed")
    parts.append("3. Example: `| ARCH-P0-001 | Missing failover [VERIFY: BRD-01.18] | ... |`")
    parts.append("")
    parts.append("⚠️ Do NOT claim content is missing without adding [VERIFY] tag")
    parts.append("")

    return "\n".join(parts)
```

- [ ] **6.9.3** Update persona skill files with appendix consultation guidelines:

Add to each persona skill file (e.g., `skills/architect.md`, `skills/auditor.md`):

```markdown
## Appendix Consultation Guidelines

Appendices contain detailed technical specifications that may be relevant to your findings.
Appendix content is NOT included in your context to save tokens.

### When to Reference Appendices

1. **Verification Needed**: If you identify a gap that might be addressed in an appendix:
   - Add `[VERIFY: BRD-01.18]` tag to the finding
   - Example: `| ARCH-P0-001 | Missing failover spec [VERIFY: BRD-01.18] | 6.1.2 | ... |`

2. **Cross-Reference**: If a section references "See Appendix X":
   - Include the reference in your finding
   - The orchestrator will load and verify

3. **Do NOT Assume**: Never claim something is missing without checking appendix references.

### Verification Tag Format

```
[VERIFY: appendix-section-id]
```

Examples:
- `[VERIFY: BRD-01.18]` - Verify against technical appendix
- `[VERIFY: BRD-01.17]` - Verify against deployment appendix
```

- [ ] **6.9.4** Implement `[VERIFY: appendix-id]` tag parsing in `_extract_findings()`:

**FIX G6**: Add enforcement - warn if "missing" findings lack VERIFY tag.

```python
# Add to _extract_findings() in review_memory.py

VERIFY_TAG_PATTERN = re.compile(r'\[VERIFY:\s*([A-Za-z0-9\-_.]+)\]')

# FIX G6: Patterns indicating claim of missing content
MISSING_CLAIM_PATTERNS = re.compile(
    r'(missing|absent|not specified|not defined|lacks|no .* specified|undefined)',
    re.IGNORECASE
)

def _extract_findings(self, responses: dict[str, str]) -> list[dict]:
    """Extract findings from all persona responses."""
    findings = []
    seen_ids = set()
    unverified_missing_claims = []  # FIX G6: Track missing claims without VERIFY

    for persona, response in responses.items():
        for match in FINDING_ID_PATTERN.finditer(response):
            raw_id = match.group(1) or match.group(2) or match.group(3)
            if raw_id and raw_id not in seen_ids:
                seen_ids.add(raw_id)
                prefix, priority, num = _parse_finding_id(raw_id)

                # Extract context around the finding
                start = max(0, match.start() - 200)
                end = min(len(response), match.end() + 500)
                context = response[start:end]

                # Check for verification tags
                verify_tags = VERIFY_TAG_PATTERN.findall(context)

                # FIX G6: Check if finding claims something is missing
                claims_missing = bool(MISSING_CLAIM_PATTERNS.search(context))
                has_verify_tag = len(verify_tags) > 0

                # FIX G6: Flag unverified missing claims
                if claims_missing and not has_verify_tag:
                    unverified_missing_claims.append(raw_id)

                findings.append({
                    "persona": persona,
                    "priority": priority,
                    "id": raw_id,
                    "prefix": prefix,
                    "title": self._extract_title(context, raw_id),
                    "text": context[:500],
                    "verify_appendices": verify_tags,
                    "needs_verification": has_verify_tag,
                    "claims_missing": claims_missing,  # NEW: flags "missing" claims
                    "unverified_missing": claims_missing and not has_verify_tag,  # FIX G6
                })

    # FIX G6: Log warning for unverified missing claims
    if unverified_missing_claims:
        self.logger.warning(
            f"Found {len(unverified_missing_claims)} findings claiming content is missing "
            f"without [VERIFY] tag: {unverified_missing_claims[:5]}. "
            f"These may be false positives - content could exist in appendices."
        )

    return findings
```

- [ ] **6.9.5** Add verification phase in orchestrator for tagged findings:

**FIX G2**: Add explicit orchestrator integration point
**FIX G4**: Surface verification results in UCR report
**FIX G5**: Improve keyword matching with stemming and stop word removal
**FIX G11**: Log verification statistics

```python
# Add to ucx/core/orchestrator.py or review_memory.py

# FIX G5: Stop words to ignore in keyword matching
STOP_WORDS = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
              "being", "have", "has", "had", "do", "does", "did", "will",
              "would", "could", "should", "may", "might", "must", "shall",
              "for", "and", "nor", "but", "or", "yet", "so", "in", "on",
              "at", "to", "of", "with", "by", "from", "as", "into", "not",
              "no", "missing", "absent", "lacks", "undefined"}  # Include claim words


class AppendixVerifier:
    """Verify findings tagged with [VERIFY: appendix-id] against appendix content."""

    def __init__(self, doc_sections: dict[str, str]):
        self._sections = doc_sections

    def verify_findings(
        self,
        findings: list[dict],
        max_findings_per_appendix: int = 10,
    ) -> list[dict]:
        """
        Verify findings against appendix content.

        FIX G5: Uses improved keyword matching that:
        - Removes stop words and claim words ("missing", "absent")
        - Uses word stem matching (e.g., "failover" matches "failovers")
        - Searches for phrase matches, not just individual words
        """
        by_appendix: dict[str, list[dict]] = {}
        for finding in findings:
            if not finding.get("needs_verification"):
                continue
            for appendix_id in finding.get("verify_appendices", []):
                if appendix_id not in by_appendix:
                    by_appendix[appendix_id] = []
                by_appendix[appendix_id].append(finding)

        for appendix_id, appendix_findings in by_appendix.items():
            if appendix_id not in self._sections:
                for f in appendix_findings:
                    f["verification_status"] = "APPENDIX_NOT_FOUND"
                continue

            content = self._sections[appendix_id]
            content_lower = content.lower()

            for finding in appendix_findings[:max_findings_per_appendix]:
                # FIX G5: Improved keyword extraction
                title = finding.get("title", "").lower()
                keywords = self._extract_meaningful_keywords(title)

                # FIX G5: Multi-strategy matching
                match_score = self._compute_match_score(keywords, content_lower)

                if match_score >= 0.6:
                    finding["verification_status"] = "VERIFIED"
                    finding["verification_note"] = f"Found in {appendix_id} (score: {match_score:.0%})"
                elif match_score >= 0.3:
                    finding["verification_status"] = "PARTIALLY_VERIFIED"
                    finding["verification_note"] = f"Partial match in {appendix_id} (score: {match_score:.0%})"
                else:
                    finding["verification_status"] = "NOT_FOUND"
                    finding["verification_note"] = f"Not found in {appendix_id}"

        return findings

    def _extract_meaningful_keywords(self, text: str) -> list[str]:
        """FIX G5: Extract meaningful keywords, removing stop words and claim words."""
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        return [w for w in words if w not in STOP_WORDS][:8]

    def _compute_match_score(self, keywords: list[str], content: str) -> float:
        """FIX G5: Multi-strategy matching for better accuracy."""
        if not keywords:
            return 0.0

        scores = []

        # Strategy 1: Exact word matches
        exact_matches = sum(1 for kw in keywords if kw in content)
        scores.append(exact_matches / len(keywords))

        # Strategy 2: Partial/stem matches (e.g., "failover" matches "failovers")
        partial_matches = sum(1 for kw in keywords if any(
            kw in word or word in kw
            for word in re.findall(r'\b[a-z]{3,}\b', content)
        ))
        scores.append(partial_matches / len(keywords))

        # Strategy 3: Phrase proximity (keywords appearing near each other)
        # Simplified: check if 2+ keywords appear within 100 chars
        for i in range(len(content) - 100):
            window = content[i:i+100]
            keywords_in_window = sum(1 for kw in keywords if kw in window)
            if keywords_in_window >= 2:
                scores.append(0.5)  # Bonus for proximity
                break

        return max(scores) if scores else 0.0


def run_verification_phase(
    findings: list[dict],
    doc_sections: dict[str, str],
    session: Optional["ReviewSession"] = None,  # FIX G11: For stats persistence
    logger: Optional[logging.Logger] = None,
) -> tuple[list[dict], dict]:
    """
    Run post-processing verification phase for tagged findings.

    FIX G2: This function should be called by orchestrator after all personas complete.
    FIX G11: Logs and persists verification statistics.

    Returns:
        - Updated findings list with verification status
        - Verification summary statistics
    """
    verifier = AppendixVerifier(doc_sections)
    verified_findings = verifier.verify_findings(findings)

    # Compute statistics
    stats = {
        "total_findings": len(findings),
        "findings_needing_verification": sum(1 for f in findings if f.get("needs_verification")),
        "verified": sum(1 for f in verified_findings if f.get("verification_status") == "VERIFIED"),
        "partially_verified": sum(1 for f in verified_findings if f.get("verification_status") == "PARTIALLY_VERIFIED"),
        "not_found": sum(1 for f in verified_findings if f.get("verification_status") == "NOT_FOUND"),
        "appendix_not_found": sum(1 for f in verified_findings if f.get("verification_status") == "APPENDIX_NOT_FOUND"),
        "unverified_missing_claims": sum(1 for f in findings if f.get("unverified_missing")),  # FIX G6
    }

    # FIX G11: Log statistics
    if logger:
        logger.info(
            f"Verification phase complete: {stats['verified']} verified, "
            f"{stats['partially_verified']} partial, {stats['not_found']} not found, "
            f"{stats['unverified_missing_claims']} unverified missing claims"
        )

    # FIX G11: Persist to session
    if session:
        session.verification_stats = stats
        # Will be saved when session is persisted

    return verified_findings, stats


# FIX G2: Orchestrator integration point
# Add this to ReviewOrchestrator.run() after all personas complete:
"""
# In ucx/core/orchestrator.py - ReviewOrchestrator.run()

def run(self):
    # ... existing persona loop ...

    # === NEW: VERIFICATION PHASE (FIX G2) ===
    if self.enable_verification:
        findings = self.memory._extract_findings(self.memory.get_all_responses())
        verified_findings, stats = run_verification_phase(
            findings=findings,
            doc_sections=self.doc_sections,
            session=self.memory._session,
            logger=self.logger,
        )

        # Update findings in memory for report generation
        self.memory._verified_findings = verified_findings
        self.memory._verification_stats = stats

    # ... generate report ...
"""
```

- [ ] **6.9.5.1** Add verification summary to UCR report:

**FIX G4**: Surface verification results in the report.

```python
# Add to report generation in review_memory.py or report_generator.py

def _generate_verification_summary(self, stats: dict) -> str:
    """FIX G4: Generate verification summary section for UCR report."""
    if not stats or stats.get("findings_needing_verification", 0) == 0:
        return ""

    return f"""
## Appendix Verification Summary

| Metric | Count |
|--------|-------|
| Findings Needing Verification | {stats['findings_needing_verification']} |
| ✅ Verified (content exists) | {stats['verified']} |
| ⚠️ Partially Verified | {stats['partially_verified']} |
| ❌ Not Found in Appendix | {stats['not_found']} |
| 🔍 Unverified Missing Claims | {stats['unverified_missing_claims']} |

**Interpretation**:
- **Verified**: Content exists in appendix - finding may be false positive
- **Not Found**: Content genuinely missing - finding is valid
- **Unverified Missing Claims**: Findings claiming content is missing but lacking [VERIFY] tag

"""


def _generate_verified_findings_table(self, findings: list[dict]) -> str:
    """FIX G4: Add verification status column to findings table."""
    verified = [f for f in findings if f.get("verification_status")]
    if not verified:
        return ""

    lines = [
        "\n### Verification Details\n",
        "| Finding ID | Status | Note |",
        "|------------|--------|------|",
    ]

    for f in verified:
        status_emoji = {
            "VERIFIED": "✅",
            "PARTIALLY_VERIFIED": "⚠️",
            "NOT_FOUND": "❌",
            "APPENDIX_NOT_FOUND": "🔍",
        }.get(f.get("verification_status"), "?")

        lines.append(
            f"| {f['id']} | {status_emoji} {f.get('verification_status')} | {f.get('verification_note', '')} |"
        )

    return "\n".join(lines)
```

- [ ] **6.9.6** Add verification phase tests:

```python
class TestAppendixOnDemand:
    """Test appendix-on-demand functionality."""

    @pytest.fixture
    def sections_with_appendix(self):
        return {
            "BRD-01.6": "# Functional Requirements\nTransaction handling...",
            "BRD-01.18": "# Technical Appendix\n## Failover Specification\nAutomatic failover within 30 seconds...\n## API Rate Limits\n1000 requests per minute...",
        }

    def test_appendix_index_built(self, sections_with_appendix):
        """Appendix index should contain metadata, not content."""
        engine = ContextEngine(sections_with_appendix)
        ctx = engine.build_hierarchical_context("architect")

        # Appendix should be in index, not in level2
        assert len(ctx.appendix_index) > 0
        assert "BRD-01.18" not in ctx.level2_relevant

        # Index should have lightweight metadata
        app_info = ctx.appendix_index[0]
        assert app_info.section_id == "BRD-01.18"
        assert app_info.estimated_tokens > 0
        assert len(app_info.keywords) > 0

    def test_verify_tag_extraction(self):
        """VERIFY tags should be extracted from findings (FIX G10: use actual method)."""
        response = "| ARCH-P0-001 | Missing failover [VERIFY: BRD-01.18] | 6.1.2 | ... |"

        # FIX G10: Use actual ReviewMemory._extract_findings() method
        memory = ReviewMemory("/tmp/test", "brd")
        findings = memory._extract_findings({"architect": response})

        assert len(findings) == 1
        assert findings[0]["needs_verification"] is True
        assert "BRD-01.18" in findings[0]["verify_appendices"]

    def test_verification_finds_match(self, sections_with_appendix):
        """Verification should find content in appendix."""
        findings = [{
            "id": "ARCH-P0-001",
            "title": "Missing failover specification",
            "needs_verification": True,
            "verify_appendices": ["BRD-01.18"],
        }]

        verifier = AppendixVerifier(sections_with_appendix)
        verified = verifier.verify_findings(findings)

        assert verified[0]["verification_status"] == "VERIFIED"

    def test_verification_not_found(self, sections_with_appendix):
        """Verification should report NOT_FOUND when content absent."""
        findings = [{
            "id": "ARCH-P0-002",
            "title": "Missing quantum encryption",
            "needs_verification": True,
            "verify_appendices": ["BRD-01.18"],
        }]

        verifier = AppendixVerifier(sections_with_appendix)
        verified = verifier.verify_findings(findings)

        assert verified[0]["verification_status"] == "NOT_FOUND"
```

#### 6.10 Dynamic Section Mapping (Multi-Document Support)

**Problem**: Current `PERSONA_SECTION_MAP` uses hardcoded BRD-01 section IDs (e.g., `BRD-01.6`), which fails for:
- Different BRD documents (BRD-02, BRD-03)
- Different document types (PRD, EARS)
- Different projects with different section structures

**Solution**: Semantic category-based mapping that discovers sections dynamically.

- [ ] **6.10.1** Define semantic section categories:

```python
# Section categories (document-type agnostic)
SECTION_CATEGORIES = {
    "functional": [
        "functional requirements", "features", "capabilities",
        "use cases", "user stories", "transaction flows"
    ],
    "quality": [
        "quality attributes", "nfr", "non-functional",
        "performance", "scalability", "availability", "sla"
    ],
    "compliance": [
        "compliance", "regulatory", "legal", "security requirements",
        "privacy", "gdpr", "pci", "kyc", "aml"
    ],
    "integration": [
        "integration", "interfaces", "api", "external systems",
        "partners", "third-party", "webhook"
    ],
    "risk": [
        "risk", "mitigation", "assumptions", "constraints",
        "dependencies", "blockers"
    ],
    "business": [
        "business context", "market", "stakeholders", "objectives",
        "success criteria", "kpi", "metrics", "cost-benefit"
    ],
    "technical": [
        "technical", "architecture", "design", "implementation",
        "data model", "infrastructure", "deployment"
    ],
    "scope": [
        "scope", "boundaries", "in-scope", "out-of-scope",
        "exclusions", "limitations"
    ],
    "appendix": [
        "appendix", "annex", "reference", "supplementary",
        "attachment", "exhibit", "technical details"
    ],
    "metadata": [
        "glossary", "index", "traceability", "revision history",
        "table of contents", "document control", "approval"
    ],
}
```

- [ ] **6.10.2** Define persona-to-category mapping:

```python
# Persona to CATEGORY mapping (replaces PERSONA_SECTION_MAP)
PERSONA_CATEGORY_MAP = {
    "architect": {
        "required": ["functional", "quality", "technical", "integration", "scope"],
        "optional": ["appendix"],
        "skip": ["metadata", "business"],
    },
    "auditor": {
        "required": ["functional", "quality", "compliance", "risk"],
        "optional": ["integration"],
        "skip": ["metadata", "appendix", "business"],
    },
    "tech_lead": {
        "required": ["functional", "quality", "technical"],
        "optional": ["integration", "appendix"],
        "skip": ["metadata", "business"],
    },
    "strategist": {
        "required": ["business", "risk", "scope"],
        "optional": ["functional"],
        "skip": ["technical", "appendix", "metadata"],
    },
    "devils_advocate": {
        "required": ["functional", "risk", "technical", "integration"],
        "optional": ["quality"],
        "skip": ["metadata", "business"],
    },
    "operator": {
        "required": ["quality", "technical", "integration"],
        "optional": ["appendix", "risk"],
        "skip": ["metadata", "business", "scope"],
    },
    "integration_lead": {
        "required": ["integration", "functional", "technical"],
        "optional": ["appendix", "quality"],
        "skip": ["metadata", "business"],
    },
    "product_owner": {
        "required": ["business", "functional", "scope"],
        "optional": ["quality", "risk"],
        "skip": ["technical", "appendix", "metadata"],
    },
    "business_analyst": {
        "required": ["business", "functional", "scope", "risk"],
        "optional": ["quality"],
        "skip": ["technical", "appendix", "metadata"],
    },
    "fact_checker": {
        "required": ["*"],  # All categories except metadata
        "optional": [],
        "skip": ["metadata"],
    },
    "chairperson": {
        "required": ["*"],  # All categories for synthesis
        "optional": [],
        "skip": ["metadata"],
    },
}
```

- [ ] **6.10.3** Implement `SectionInfo` dataclass and `DynamicSectionMapper`:

```python
@dataclass
class SectionInfo:
    """Discovered section metadata."""
    section_id: str           # e.g., "BRD-01.6", "PRD-02.3"
    title: str               # e.g., "Functional Requirements"
    category: str            # e.g., "functional"
    doc_type: str            # e.g., "brd", "prd"
    estimated_tokens: int
    keywords: list[str]
    confidence: float        # 0.0-1.0 category match confidence


class DynamicSectionMapper:
    """Map sections to personas based on semantic categories."""

    def __init__(self, doc_sections: dict[str, str], doc_type: str = "brd"):
        self._sections = doc_sections
        self._doc_type = doc_type
        self._section_info: dict[str, SectionInfo] = {}

        self._discover_and_categorize_sections()

    def _discover_and_categorize_sections(self):
        """Discover all sections and assign semantic categories."""
        for section_id, content in self._sections.items():
            title = self._extract_title(content)
            category, confidence = self._categorize_section(title, content)

            self._section_info[section_id] = SectionInfo(
                section_id=section_id,
                title=title,
                category=category,
                doc_type=self._doc_type,
                estimated_tokens=len(content) // 4,
                keywords=self._extract_keywords(content),
                confidence=confidence,
            )

    def _categorize_section(self, title: str, content: str) -> tuple[str, float]:
        """Categorize section by semantic matching. Returns (category, confidence)."""
        title_lower = title.lower()
        content_sample = content[:2000].lower()

        best_category = "other"
        best_score = 0.0

        for category, patterns in SECTION_CATEGORIES.items():
            score = 0.0

            # Title matching (high weight)
            title_matches = sum(1 for p in patterns if p in title_lower)
            score += title_matches * 0.4

            # Content matching (lower weight)
            content_matches = sum(1 for p in patterns if p in content_sample)
            score += min(content_matches * 0.1, 0.3)  # Cap at 0.3

            if score > best_score:
                best_score = score
                best_category = category

        # Normalize confidence to 0.0-1.0
        confidence = min(best_score, 1.0)

        return best_category, confidence

    def _extract_title(self, content: str) -> str:
        """Extract section title from content."""
        for line in content.split("\n")[:5]:
            if line.startswith("#"):
                return line.lstrip("#").strip()
        return "Untitled"

    def _extract_keywords(self, content: str, max_keywords: int = 10) -> list[str]:
        """Extract key terms from section content."""
        # Extract from headers and bold text
        keywords = []
        for line in content.split("\n"):
            if line.startswith("#"):
                keywords.extend(line.lstrip("#").strip().split()[:3])

        # Deduplicate
        seen = set()
        unique = []
        for kw in keywords:
            if kw.lower() not in seen and len(kw) > 2:
                seen.add(kw.lower())
                unique.append(kw)

        return unique[:max_keywords]

    def get_sections_for_persona(self, persona: str) -> dict[str, list[str]]:
        """Get sections for persona based on category mapping."""
        mapping = PERSONA_CATEGORY_MAP.get(persona, {})
        required_cats = set(mapping.get("required", []))
        optional_cats = set(mapping.get("optional", []))
        skip_cats = set(mapping.get("skip", []))

        # Handle wildcard "*" for fact_checker/chairperson
        all_categories = set(SECTION_CATEGORIES.keys())
        if "*" in required_cats:
            required_cats = all_categories - skip_cats

        result = {"required": [], "optional": [], "skip": []}

        for section_id, info in self._section_info.items():
            if info.category in required_cats:
                result["required"].append(section_id)
            elif info.category in optional_cats:
                result["optional"].append(section_id)
            elif info.category in skip_cats:
                result["skip"].append(section_id)
            else:
                # Uncategorized: include for comprehensive personas
                if persona in ["fact_checker", "chairperson"]:
                    result["required"].append(section_id)
                else:
                    result["skip"].append(section_id)

        return result

    def get_section_summary(self) -> str:
        """Get summary of discovered sections for debugging/logging."""
        lines = ["Discovered Sections:"]
        for section_id, info in sorted(self._section_info.items()):
            lines.append(
                f"  {section_id}: {info.title[:40]} -> {info.category} "
                f"(confidence: {info.confidence:.0%})"
            )
        return "\n".join(lines)
```

- [ ] **6.10.4** Update `ContextEngine` to use `DynamicSectionMapper`:

```python
class ContextEngine:
    """Build optimized context for persona prompts."""

    def __init__(self, doc_sections: dict[str, str], doc_type: str = "brd"):
        self._sections = doc_sections
        self._doc_type = doc_type

        # NEW: Use dynamic section mapper instead of hardcoded PERSONA_SECTION_MAP
        self._section_mapper = DynamicSectionMapper(doc_sections, doc_type)

    def build_hierarchical_context(
        self,
        persona: str,
        enable_keyword_scan: bool = True,
        max_discovered_snippets: int = 10,
    ) -> HierarchicalContext:
        """Build hierarchical context using dynamic section mapping."""

        # Get sections dynamically mapped by category
        section_mapping = self._section_mapper.get_sections_for_persona(persona)

        # Level 1: Document Overview
        level1 = self._build_level1_overview()

        # Level 2: Persona-Relevant Sections (from dynamic mapping)
        level2 = self._build_level2_from_mapping(persona, section_mapping)

        # Appendix Index
        appendix_index = self._build_appendix_index_from_mapping(section_mapping)

        # Level 4: Keyword-discovered snippets
        level4 = ""
        discovered_snippets = []
        if enable_keyword_scan:
            discovered_snippets = self._scan_other_sections_for_keywords(
                persona,
                excluded_sections=set(section_mapping["required"]),
                max_snippets=max_discovered_snippets,
            )
            if discovered_snippets:
                level4 = self._format_discovered_snippets(persona, discovered_snippets)

        return HierarchicalContext(
            level1_overview=level1,
            level2_relevant=level2,
            level4_discovered=level4,
            appendix_index=appendix_index,
            total_tokens=self._estimate_tokens(level1 + level2 + level4),
            sections_included=section_mapping["required"],
            sections_skipped=section_mapping["skip"],
            discovered_snippets=discovered_snippets,
        )

    def _build_level2_from_mapping(
        self,
        persona: str,
        mapping: dict[str, list[str]],
    ) -> str:
        """Build Level 2 content from dynamically mapped sections."""
        parts = [
            "",
            "=" * 60,
            f"LEVEL 2: RELEVANT SECTIONS FOR {persona.upper()}",
            "=" * 60,
            "",
        ]

        for section_id in sorted(mapping["required"]):
            if section_id in self._sections:
                info = self._section_mapper._section_info.get(section_id)
                category_label = info.category.upper() if info else "UNKNOWN"
                parts.append(f"\n### {section_id} [{category_label}]\n")
                parts.append(self._sections[section_id])

        return "\n".join(parts)

    def _build_appendix_index_from_mapping(
        self,
        mapping: dict[str, list[str]],
    ) -> list[AppendixInfo]:
        """Build appendix index from optional sections in mapping."""
        index = []

        for section_id in mapping["optional"]:
            if section_id not in self._sections:
                continue

            info = self._section_mapper._section_info.get(section_id)
            if not info:
                continue

            content = self._sections[section_id]
            summary = self._generate_appendix_summary(content)

            index.append(AppendixInfo(
                section_id=section_id,
                title=info.title,
                estimated_tokens=info.estimated_tokens,
                keywords=info.keywords,
                content_summary=summary,
            ))

        return index
```

- [ ] **6.10.5** Add project-level category configuration (optional override):

```yaml
# docs/UCX/config/section_categories.yaml (project-specific override)
# If this file exists, it extends/overrides SECTION_CATEGORIES

additional_categories:
  remittance:
    - "remittance"
    - "transfer"
    - "cross-border"
    - "fx"
    - "exchange rate"

  partner_specific:
    - "bridge"
    - "noah"
    - "asterium"
    - "paynet"

persona_overrides:
  # Override default category mapping for this project
  architect:
    required:
      - functional
      - quality
      - technical
      - integration
      - remittance  # Project-specific category
    skip:
      - metadata
```

```python
def load_project_category_config(project_dir: Path) -> dict:
    """Load project-specific category configuration if exists."""
    config_path = project_dir / "docs/UCX/config/section_categories.yaml"

    if config_path.exists():
        import yaml
        with open(config_path) as f:
            return yaml.safe_load(f)

    return {}
```

- [ ] **6.10.6** Add tests for dynamic section mapping:

```python
class TestDynamicSectionMapping:
    """Test dynamic section mapping across document types."""

    @pytest.fixture
    def brd_sections(self):
        """Sample BRD sections."""
        return {
            "BRD-01.2": "# Business Context\nMarket analysis and objectives...",
            "BRD-01.6": "# Functional Requirements\nTransaction flows...",
            "BRD-01.7": "# Quality Attributes\nPerformance and SLAs...",
            "BRD-01.8": "# Compliance Requirements\nKYC/AML regulations...",
            "BRD-01.14": "# Glossary\nTerms and definitions...",
            "BRD-01.18": "# Technical Appendix\nArchitecture diagrams...",
        }

    @pytest.fixture
    def prd_sections(self):
        """Sample PRD sections with different IDs."""
        return {
            "PRD-02.1": "# Product Vision\nMarket opportunity...",
            "PRD-02.3": "# Feature Requirements\nUser stories...",
            "PRD-02.4": "# Non-Functional Requirements\nPerformance targets...",
            "PRD-02.7": "# Appendix\nWireframes...",
        }

    def test_brd_section_categorization(self, brd_sections):
        """BRD sections should be categorized correctly."""
        mapper = DynamicSectionMapper(brd_sections, "brd")

        assert mapper._section_info["BRD-01.2"].category == "business"
        assert mapper._section_info["BRD-01.6"].category == "functional"
        assert mapper._section_info["BRD-01.7"].category == "quality"
        assert mapper._section_info["BRD-01.8"].category == "compliance"
        assert mapper._section_info["BRD-01.14"].category == "metadata"
        assert mapper._section_info["BRD-01.18"].category == "appendix"

    def test_prd_section_categorization(self, prd_sections):
        """PRD sections with different IDs should be categorized by content."""
        mapper = DynamicSectionMapper(prd_sections, "prd")

        assert mapper._section_info["PRD-02.1"].category == "business"
        assert mapper._section_info["PRD-02.3"].category == "functional"
        assert mapper._section_info["PRD-02.4"].category == "quality"
        assert mapper._section_info["PRD-02.7"].category == "appendix"

    def test_architect_gets_technical_sections(self, brd_sections):
        """Architect should get functional, quality, technical sections."""
        mapper = DynamicSectionMapper(brd_sections, "brd")
        sections = mapper.get_sections_for_persona("architect")

        assert "BRD-01.6" in sections["required"]  # functional
        assert "BRD-01.7" in sections["required"]  # quality
        assert "BRD-01.18" in sections["optional"]  # appendix
        assert "BRD-01.14" in sections["skip"]  # metadata

    def test_strategist_gets_business_sections(self, brd_sections):
        """Strategist should get business, risk sections."""
        mapper = DynamicSectionMapper(brd_sections, "brd")
        sections = mapper.get_sections_for_persona("strategist")

        assert "BRD-01.2" in sections["required"]  # business
        assert "BRD-01.6" in sections["optional"]  # functional
        assert "BRD-01.18" in sections["skip"]  # appendix (technical)

    def test_fact_checker_gets_all_non_metadata(self, brd_sections):
        """Fact checker should get all sections except metadata."""
        mapper = DynamicSectionMapper(brd_sections, "brd")
        sections = mapper.get_sections_for_persona("fact_checker")

        # Should include all except glossary
        assert "BRD-01.6" in sections["required"]
        assert "BRD-01.7" in sections["required"]
        assert "BRD-01.18" in sections["required"]
        assert "BRD-01.14" in sections["skip"]  # metadata

    def test_different_brd_numbers_work(self):
        """Different BRD document numbers should work (BRD-01 vs BRD-02)."""
        brd_02_sections = {
            "BRD-02.3": "# Functional Requirements\nFeatures...",
            "BRD-02.5": "# Quality Attributes\nPerformance...",
        }

        mapper = DynamicSectionMapper(brd_02_sections, "brd")
        sections = mapper.get_sections_for_persona("architect")

        # Should find functional and quality regardless of section numbers
        assert "BRD-02.3" in sections["required"]
        assert "BRD-02.5" in sections["required"]
```

**Benefits of Dynamic Section Mapping**:

| Benefit | Description |
|---------|-------------|
| Document-Agnostic | Works with any BRD (BRD-01, BRD-02, etc.) |
| Doc-Type Support | Works with BRD, PRD, EARS, etc. |
| Project Customization | Optional YAML config for project-specific categories |
| Semantic Matching | Matches by content, not hardcoded IDs |
| Confidence Scoring | Reports match confidence for debugging |
| Backwards Compatible | Falls back gracefully if categorization fails |

**Token Budget (Updated with Appendix-on-Demand + G1 Summaries)**:

| Level | Source | Tokens | Purpose |
|-------|--------|--------|---------|
| 1 | Overview | ~2K | Document structure, always included |
| 2 | Static Map | ~30-50K | Core sections per persona |
| ~~3~~ | ~~Appendix~~ | ~~10-20K~~ | ~~REMOVED - on-demand only~~ |
| 4 | Keyword Scan | ~5-10K | Discovered snippets |
| Index | Appendix Metadata + Summaries | ~1-2K | FIX G1: Lightweight index with content summaries (~200 chars/appendix) |
| **Total** | Optimized | **~40-65K** | Reduced from ~50-80K |

**Token Savings**: 8-18K tokens per persona call by not loading full appendices (summaries add ~1K but save 10-20K).

---

## Files to Modify

| # | File | Lines | Change Type |
|---|------|-------|-------------|
| 1 | `/opt/data/docs_flow_framework/UCX/ucx/core/review_memory.py` | 497-549 | Replace regex with `FINDING_ID_PATTERN` |
| 2 | `/opt/data/docs_flow_framework/UCX/ucx/core/review_memory.py` | ~272-303 | Add validation call in `save_response()` |
| 3 | `/opt/data/docs_flow_framework/UCX/ucx/core/review_memory.py` | ~303 | Add `_validate_chairperson_response()` method |
| 4 | `/opt/data/docs_flow_framework/UCX/ucx/core/persona_prompts.py` | 153-652 | Add Finding ID format to all persona templates |
| 5 | `/opt/data/docs_flow_framework/UCX/ucx/core/persona_prompts.py` | 661-739 | Refactor `build_persona_prompt()` with context engine |
| 6 | `/opt/data/docs_flow_framework/UCX/ucx/core/context_engine.py` | new | **Context engineering module** |
| 7 | `/opt/data/b-local/b-local-docs/docs/UCX/review/UCR_PROMPT_BRD_PROJECT.md` | ~79 | Add Finding ID Format section |
| 8 | `/opt/data/b-local/b-local-docs/docs/UCX/review/UCR_PROMPT_BRD_PROJECT.md` | 150-717 | Update persona output format tables |
| 9 | `/opt/data/b-local/b-local-docs/docs/UCX/review/UCR_PROMPT_PRD_PROJECT.md` | all | Add Finding ID Format section |
| 10 | `/opt/data/b-local/b-local-docs/docs/UCX/skills/chairperson.md` | end | Move format instructions to end |
| 11 | `/opt/data/docs_flow_framework/UCX/skills/chairperson.md` | end | Framework skill - same changes |
| 12 | `/opt/data/docs_flow_framework/UCX/skills/operator.md` | end | Add OP-P0-NNN format guidance |
| 13 | `/opt/data/docs_flow_framework/UCX/tests/test_finding_extraction.py` | new | Unit tests for regex pattern |
| 14 | `/opt/data/docs_flow_framework/UCX/tests/test_context_engine.py` | new | **Context engineering tests** |
| 15 | `/opt/data/docs_flow_framework/UCX/README.md` | docs | Document Finding ID Format + Context Engine |

### Phase 6.9 Additional Files (FIX G9)

| # | File | Lines | Change Type |
|---|------|-------|-------------|
| 16 | `/opt/data/docs_flow_framework/UCX/ucx/core/context_engine.py` | new | Add `_build_appendix_index()`, `_generate_appendix_summary()`, `AppendixInfo` |
| 17 | `/opt/data/docs_flow_framework/UCX/ucx/core/context_engine.py` | new | Add `_format_appendix_index()` with content summaries |
| 18 | `/opt/data/docs_flow_framework/UCX/ucx/core/review_memory.py` | new | Add `VERIFY_TAG_PATTERN`, `MISSING_CLAIM_PATTERNS` |
| 19 | `/opt/data/docs_flow_framework/UCX/ucx/core/review_memory.py` | `_extract_findings()` | Add verify tag parsing, unverified missing claim detection |
| 20 | `/opt/data/docs_flow_framework/UCX/ucx/core/orchestrator.py` | `run()` | Add verification phase call (FIX G2) |
| 21 | `/opt/data/docs_flow_framework/UCX/ucx/core/review_memory.py` | new | Add `AppendixVerifier` class with improved keyword matching |
| 22 | `/opt/data/docs_flow_framework/UCX/ucx/core/review_memory.py` | new | Add `run_verification_phase()` function |
| 23 | `/opt/data/docs_flow_framework/UCX/ucx/core/report_generator.py` | new | Add `_generate_verification_summary()`, `_generate_verified_findings_table()` |
| 24 | `/opt/data/docs_flow_framework/UCX/skills/architect.md` | end | Add appendix consultation guidelines |
| 25 | `/opt/data/docs_flow_framework/UCX/skills/auditor.md` | end | Add appendix consultation guidelines |
| 26 | `/opt/data/docs_flow_framework/UCX/skills/tech_lead.md` | end | Add appendix consultation guidelines |
| 27 | `/opt/data/docs_flow_framework/UCX/tests/test_appendix_verification.py` | new | Tests for appendix-on-demand (6.9.6) |

### Phase 6.10 Additional Files (Dynamic Section Mapping)

| # | File | Lines | Change Type |
|---|------|-------|-------------|
| 28 | `/opt/data/docs_flow_framework/UCX/ucx/core/context_engine.py` | new | Add `SECTION_CATEGORIES`, `PERSONA_CATEGORY_MAP` |
| 29 | `/opt/data/docs_flow_framework/UCX/ucx/core/context_engine.py` | new | Add `SectionInfo` dataclass |
| 30 | `/opt/data/docs_flow_framework/UCX/ucx/core/context_engine.py` | new | Add `DynamicSectionMapper` class |
| 31 | `/opt/data/docs_flow_framework/UCX/ucx/core/context_engine.py` | refactor | Update `ContextEngine` to use `DynamicSectionMapper` |
| 32 | `/opt/data/docs_flow_framework/UCX/ucx/core/context_engine.py` | new | Add `load_project_category_config()` for YAML overrides |
| 33 | `/opt/data/docs_flow_framework/UCX/tests/test_dynamic_section_mapping.py` | new | Tests for dynamic section mapping (6.10.6) |
| 34 | `/opt/data/docs_flow_framework/UCX/docs/CONTEXT_ENGINEERING.md` | new | Comprehensive context engineering documentation |

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Chairperson still ignores format | MEDIUM | HIGH | Add retry with explicit reminder; place format at prompt END |
| Performance regression | LOW | LOW | Single regex pattern is O(n), minimal impact |
| Persona uses wrong format | LOW | MEDIUM | Explicit format instructions in prompts; validation warnings |
| Future unknown formats | LOW | LOW | Log unmatched patterns for detection |
| Appendix verification false negatives | MEDIUM | MEDIUM | FIX G5: Improved keyword matching with stemming |
| Personas claim missing without verification | HIGH | HIGH | FIX G6: Warning for unverified missing claims |

---

## Gap Analysis v1.8 (Phase 6.9 Review)

### Critical Gaps (FIXED)

| Gap | Issue | Fix | Status |
|-----|-------|-----|--------|
| **G1** | Personas cannot read appendix during review | Added content summaries to appendix index (~200 chars each) | ✅ FIXED in 6.9.1, 6.9.2 |
| **G2** | Verification phase integration missing | Added explicit orchestrator call site in Phase 6.9.5 | ✅ FIXED in 6.9.5 |
| **G3** | Appendix index only from "optional" list | Dynamic detection by title pattern + optional list | ✅ FIXED in 6.9.1 |

### High-Priority Gaps (FIXED)

| Gap | Issue | Fix | Status |
|-----|-------|-----|--------|
| **G4** | Verification results not in report | Added `_generate_verification_summary()`, `_generate_verified_findings_table()` | ✅ FIXED in 6.9.5.1 |
| **G5** | Keyword matching too simplistic | Multi-strategy matching: exact, stem, proximity | ✅ FIXED in 6.9.5 |
| **G6** | No enforcement for [VERIFY] tags | Warning for "missing" claims without VERIFY tag | ✅ FIXED in 6.9.4 |
| **G7** | Phase 3.1/3.2 conflict | Clarified: format via `build_attention_steering_format()`, not in instructions | ✅ FIXED in 3.1 |

### Medium-Priority Gaps (FIXED)

| Gap | Issue | Fix | Status |
|-----|-------|-----|--------|
| **G9** | Files to Modify table outdated | Added Phase 6.9 files section | ✅ FIXED |
| **G10** | Test function reference error | Changed to use actual `ReviewMemory._extract_findings()` | ✅ FIXED in 6.9.6 |
| **G11** | Verification statistics not logged | Added logging and session persistence | ✅ FIXED in 6.9.5 |

### Deferred Gaps

| Gap | Issue | Reason for Deferral |
|-----|-------|---------------------|
| **G8** | Multiple appendices discovery | Covered by G3 dynamic detection |
| **G12** | Skill file vs PERSONA_TEMPLATES overlap | Low impact, documentation sufficient |
| **G13** | No LLM verification option | Token cost concern, keyword matching sufficient for v1.8 |
| **G14** | Error handling in verification | Add in implementation, not plan |
| **G15** | Hybrid keyword scan implementation | Separate from 6.9, tracked in 6.7 |

---

## Gaps Identified (Review 2026-03-13)

### Gap 1: PRD/EARS Prompts Not Addressed
- **Issue**: Plan only updates `UCR_PROMPT_BRD_PROJECT.md`
- **Missing**: `UCR_PROMPT_PRD_PROJECT.md` and EARS prompts need same Finding ID format
- **Action**: Add Phase 2.3 to update PRD prompt with same format standard

### Gap 2: Framework Skills Not Updated
- **Issue**: Plan updates project-specific skills only
- **Missing**: Framework skills at `/opt/data/docs_flow_framework/UCX/skills/` are fallbacks
- **Action**: Add Phase 4.2 to update framework skill files (chairperson.md, operator.md, etc.)

### Gap 3: Missing Persona Prefix
- **Issue**: `requirements_specialist` persona exists but not in Canonical Format Table
- **Action**: Add `RS` prefix for Requirements Specialist

### Gap 4: No Unit Tests for Regex
- **Issue**: Plan shows test commands but no unit test file creation
- **Action**: Add Phase 5.5 to create `test_finding_extraction.py` with test cases

### Gap 5: _extract_findings() Full Implementation Missing
- **Issue**: Plan shows patterns but not how they're combined in `_extract_findings()`
- **Missing**:
  - How to iterate both patterns
  - Deduplication logic (same finding matched by multiple patterns)
  - Category `[CAT:xxx]` extraction from new format
- **Action**: Add complete implementation code for `_extract_findings()`

### Gap 6: _validate_chairperson_response() Not Called
- **Issue**: Method defined but not invoked
- **Action**: Add call in `save_response()` method after writing response

### Gap 7: Prompt Size Optimization Not Addressed
- **Issue**: Finding #6 identifies 170KB+ prompts as problem, no fix proposed
- **Potential Fixes**:
  - Truncate document appendices for non-chairperson personas
  - Summarize prior findings instead of raw text
  - Split large documents into sections
- **Action**: Add Phase 6 for context optimization (future enhancement)

### Gap 8: Retry Logic Not Implemented
- **Issue**: Risk mitigation mentions retry but no implementation
- **Action**: Add Phase 3.3 for chairperson retry logic when manifest missing

### Gap 9: Fact Checker Output Format Unique
- **Issue**: Fact Checker verifies other findings, has different table structure
- **Action**: Verify Fact Checker format in Phase 2.2 uses `FC-P0-NNN` correctly

### ~~Gap 10: Backward Compatibility~~ (NOT NEEDED)
- UCX is a new tool - no legacy reports to support
- Simplify by using canonical format only

### Gap 11: Documentation Not Updated
- **Issue**: No user-facing documentation about new Finding ID format
- **Action**: Add Phase 5.6 to update UCX README and changelog

### Gap 12: Category Extraction Logic
- **Issue**: Current plan focuses on Finding ID but not `[CAT:xxx]` tag extraction
- **Current**: `category_pattern = re.compile(r'\[CAT:(\w+)\]', re.IGNORECASE)` exists
- **Action**: Verify category extraction still works with new table formats

---

## Common Issues Extracted from BRD-01 Review

### Issue Pattern 1: Summary-Only Responses
- **Symptom**: 600-1200 char responses instead of 5-10K structured tables
- **Affected Personas**: architect, auditor, devils_advocate, integration_lead, business_analyst, chairperson
- **Root Cause**: Output format instructions lost in 170KB+ prompt
- **Fix**: Place format instructions at END of prompt, not middle

### Issue Pattern 2: Inconsistent Finding ID Formats
- **Symptom**: Extraction regex misses findings using non-canonical formats
- **Affected Personas**: operator (uses `P0-OP-001` instead of `OP-P0-001`)
- **Root Cause**: No explicit format standard in prompts
- **Fix**: Add explicit format standard to UCR prompt; update all persona output format sections

### Issue Pattern 3: Missing Machine-Parseable Markers
- **Symptom**: No `<!-- UCX-MANIFEST-START -->` in chairperson output
- **Affected**: Chairperson
- **Root Cause**: Format instructions at beginning of prompt, lost after 40K tokens of prior findings
- **Fix**: Restructure chairperson prompt with format at END

### Issue Pattern 4: Frontmatter/Content Mismatch
- **Symptom**: `p0_findings: 0` in frontmatter but 30+ P0 findings in content
- **Root Cause**: Extraction regex expects `**[P0-1]**` but personas output `ARCH-P0-001`
- **Fix**: Update regex to match canonical and legacy formats; normalize to canonical

---

## Implementation Summary (2026-03-13)

### Files Created

| File | Purpose | Status |
|------|---------|--------|
| `ucx/core/context_engine.py` | Context engineering module with hierarchical context, prior findings summarization, and attention steering | COMPLETE |
| `tests/test_finding_extraction.py` | Unit tests for Finding ID pattern extraction (14 test cases) | COMPLETE |
| `tests/test_context_engine.py` | Unit tests for context engine functionality (25 test cases) | COMPLETE |

### Files Modified

| File | Change | Status |
|------|--------|--------|
| `ucx/core/review_memory.py` | Added `FINDING_ID_PATTERN`, `_parse_finding_id()`, updated `_extract_findings()`, added `_validate_chairperson_response()` | COMPLETE |
| `ucx/core/persona_prompts.py` | Added context engine imports, refactored `build_persona_prompt()` with `use_context_engineering` flag | COMPLETE |

### Key Components Implemented

| Component | Location | Description |
|-----------|----------|-------------|
| `FINDING_ID_PATTERN` | `review_memory.py` | Regex for canonical `PREFIX-P0-NNN` format |
| `_parse_finding_id()` | `review_memory.py` | Parser returning `(prefix, priority, number)` tuple |
| `_extract_findings()` | `review_memory.py` | Updated to use canonical pattern with deduplication |
| `_validate_chairperson_response()` | `review_memory.py` | Validates manifest markers, logs warnings |
| `PERSONA_PREFIX_MAP` | `context_engine.py` | Maps 14 personas to 2-4 char prefixes |
| `PERSONA_SECTION_MAP` | `context_engine.py` | Maps personas to relevant BRD sections |
| `ContextEngine` | `context_engine.py` | Builds 3-level hierarchical context |
| `PriorFindingsSummarizer` | `context_engine.py` | Reduces prior findings by 90% |
| `build_attention_steering_format()` | `context_engine.py` | Format instructions for prompt END |
| `build_chairperson_manifest_format()` | `context_engine.py` | Manifest template with UCX markers |

### Remaining Work

| Phase | Items | Priority |
|-------|-------|----------|
| Phase 2 | Update UCR prompts (BRD/PRD) with Finding ID format | HIGH |
| Phase 3.1 | Update PERSONA_TEMPLATES with explicit format | MEDIUM |
| Phase 4 | Update skill files (chairperson.md, operator.md) | MEDIUM |
| Phase 5.1-5.4 | Integration testing with actual UCX review runs | HIGH |
| Phase 6.7 | Implement hybrid context selection (static + keyword scan) | MEDIUM |
| Phase 6.9.1 | Implement `_build_appendix_index()` method | HIGH |
| Phase 6.9.2 | Add `_format_appendix_index()` for prompt injection | HIGH |
| Phase 6.9.3 | Update persona skill files with appendix consultation guidelines | MEDIUM |
| Phase 6.9.4 | Implement `[VERIFY: appendix-id]` tag parsing | HIGH |
| Phase 6.9.5 | Add verification phase in orchestrator | HIGH |
| Phase 6.9.6 | Add appendix-on-demand tests | MEDIUM |
| Phase 6.10.1 | Define `SECTION_CATEGORIES` semantic categories | HIGH |
| Phase 6.10.2 | Define `PERSONA_CATEGORY_MAP` persona-to-category mapping | HIGH |
| Phase 6.10.3 | Implement `SectionInfo` and `DynamicSectionMapper` | HIGH |
| Phase 6.10.4 | Update `ContextEngine` to use `DynamicSectionMapper` | HIGH |
| Phase 6.10.5 | Add project-level category configuration (YAML) | LOW |
| Phase 6.10.6 | Add dynamic section mapping tests | MEDIUM |

### Verification Commands

```bash
# Test finding extraction
cd /opt/data/docs_flow_framework/UCX
PYTHONPATH=. python -c "
from ucx.core.review_memory import FINDING_ID_PATTERN, _parse_finding_id
text = '| ARCH-P0-001 | Test |'
print(f'Matches: {FINDING_ID_PATTERN.findall(text)}')
print(f'Parse: {_parse_finding_id(\"ARCH-P0-001\")}')
"

# Test context engine
PYTHONPATH=. python -c "
from ucx.core.context_engine import PriorFindingsSummarizer
s = PriorFindingsSummarizer()
summary = s.summarize_all({'arch': '| ARCH-P0-001 | x |'}, 'tech_lead')
print(f'Summary length: {len(summary)} chars')
"

# Test prompt integration
PYTHONPATH=. python -c "
from ucx.core.persona_prompts import build_persona_prompt
p = build_persona_prompt('architect', 'doc content', use_context_engineering=True)
print(f'Format at end: {\"REQUIRED OUTPUT FORMAT\" in p[-2000:]}')
"
```

---

## Related Files (From Original Plan)

Original plan location: `/opt/data/docs_flow_framework/work_plans/UCX_FINDING_EXTRACTION_FIX_PLAN.md`
Migrated to: This IPLAN document

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-13 | Claude | Initial draft from work plan migration |
| 1.1 | 2026-03-13 | Claude | Added comprehensive persona analysis and common issues |
| 1.2 | 2026-03-13 | Claude | Gap analysis: Added 12 gaps, PRD prompt, framework skills, unit tests, full implementation code |
| 1.3 | 2026-03-13 | Claude | Simplified: Removed backward compatibility (new tool), single regex pattern |
| 1.4 | 2026-03-13 | Claude | Added Phase 6: Context Engineering - hierarchical context, prior findings summarization, attention steering |
| 1.5 | 2026-03-13 | Claude | IMPLEMENTED: Phase 1 (finding pattern), Phase 6 (context engine), unit tests. Core implementation complete. |
| 1.6 | 2026-03-13 | Claude | Added Phase 6.7: Hybrid Context Selection - static PERSONA_SECTION_MAP as primary + dynamic keyword scan for discovering relevant content in other sections |
| 1.7 | 2026-03-13 | Claude | Added Phase 6.9: Appendix-on-Demand - removed include_level3, added appendix_index, [VERIFY: appendix-id] tags, verification phase, skill guidelines |
| 1.8 | 2026-03-13 | Claude | **Gap fixes for Phase 6.9**: G1 (appendix summaries), G2 (orchestrator integration), G3 (dynamic appendix detection), G4 (verification in report), G5 (improved keyword matching), G6 (VERIFY tag enforcement), G7 (Phase 3.1/3.2 conflict), G9 (Files to Modify table), G10 (test reference), G11 (stats logging) |
| 1.9 | 2026-03-13 | Claude | Added Phase 6.10: Dynamic Section Mapping - semantic category-based section filtering that works across document types (BRD, PRD, EARS) and different document numbers; replaces hardcoded PERSONA_SECTION_MAP |
| 2.0 | 2026-03-13 | Claude | **CORE COMPLETE**: Marked Phases 1-4, 4.5, 5.5, 5.6, 6.1-6.5, 6.8 as complete. Core Finding ID format and context engineering implemented. Advanced features (6.7, 6.9, 6.10) deferred to v1.13.1. Updated documentation (README, ROADMAP, CHANGELOG_v1.13.0, CONTEXT_ENGINEERING). |
| 2.1 | 2026-03-13 | Claude | **INTEGRATION TESTING COMPLETE**: Phases 5.1-5.4 passed. Fixed critical bug: `UnifiedPromptLoader.build_persona_prompt()` was not adding attention steering format at prompt END. Format instructions were at line 133 of 4300 (3% into prompt). Fixed by adding `build_chairperson_manifest_format()` and `build_attention_steering_format()` calls after document content. Test results: 33 canonical findings, 0 legacy format, UCX-MANIFEST markers present in v008 report. |
