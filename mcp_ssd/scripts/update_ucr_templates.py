#!/usr/bin/env python3
"""Update UCR prompt templates with SDD-compliant output format."""

import re
from pathlib import Path

# Document type to layer mapping
DOC_LAYERS = {
    "BRD": 1,
    "PRD": 2,
    "EARS": 3,
    "BDD": 4,
    "ADR": 5,
    "SYS": 6,
    "REQ": 7,
    "CTR": 8,
    "SPEC": 9,
    "TSPEC": 10,
}

OLD_PATTERN = r'''---

## Final Synthesis

After all persona reviews, produce the consolidated report:

```markdown
# PERSONA REVIEW REPORT: \[.*?\]

> \*\*Target Document\*\*:.*?
> \*\*Review Date\*\*:.*?
> \*\*Method\*\*:.*?
> \*\*Personas Applied\*\*:.*?

## 1\. Executive Summary

\* \*\*Recommendation\*\*:.*?
\* \*\*Statistics\*\*:.*?
\* \*\*Blocking Issues\*\*:.*?

\*Synthesis\*:.*?

## 2\. Critical Findings \(P0\)

\| ID \| Finding.*?

## 3\. High Priority Findings \(P1\)

\| ID \| Finding.*?

## 4\. Required Remediations

\| ID \| Priority.*?
\| R1.*?

## 5\. Enhancement Recommendations \(P2\)

\| ID \| Finding.*?

## 6\. Items Verified as Present

\| Item \| Location.*?

## 7\. Alternative Solutions.*?

\[Only if.*?\]
```

---

## Document to Review

\[PASTE.*?\]'''

def get_new_format(doc_type: str) -> str:
    """Generate SDD-compliant output format for a document type."""
    layer = DOC_LAYERS.get(doc_type, 1)
    doc_type_lower = doc_type.lower()

    return f'''---

## Final Synthesis

After all persona reviews, produce the consolidated report with **SDD-compliant format**:

```markdown
---
title: "UCR Review Report: [{doc_type} Document ID]"
tags:
  - ucr-review
  - {doc_type_lower}-review
  - layer-{layer}-artifact
  - quality-assurance
custom_fields:
  document_type: ucr-review-report
  source_artifact_type: {doc_type}
  source_artifact_id: "[{doc_type}-XX]"
  layer: {layer}
  review_method: unified-context-review
  personas_applied: 9
  schema_version: "1.0"
  last_updated: "[YYYY-MM-DDTHH:MM:SS]"
  downstream_ready_score: "[SCORE]/100"
  findings_p0: [COUNT]
  findings_p1: [COUNT]
  findings_p2: [COUNT]
---

# UCR Review Report: [{doc_type} Document ID]

## 0. Document Control

| Item | Details |
|------|---------|
| **Source Document** | [{doc_type}-XX] (Version X.X) |
| **Review Date** | [YYYY-MM-DDTHH:MM:SS] |
| **Review Method** | UCR (Unified Context Review) |
| **Personas Applied** | 9 (Architect, Auditor, Tech Lead, Strategist, Devil's Advocate, Operator, Integration Lead, Product Owner, Business Analyst) |
| **Reviewer** | UCX Framework v1.4.x |
| **Status** | [Draft / Final] |
| **Downstream-Ready Score** | [SCORE]/100 |

### Review Summary

| Metric | Value |
|--------|-------|
| **Recommendation** | [✅ PROCEED / ⚠️ REMEDIATION REQUIRED / 🚨 FUNDAMENTAL REDESIGN] |
| **P0 Critical Findings** | [COUNT] |
| **P1 High Findings** | [COUNT] |
| **P2 Medium Findings** | [COUNT] |
| **Total Remediations** | [COUNT] |

---

## 1. Executive Summary

**Recommendation**: [PROCEED / REMEDIATION REQUIRED / FUNDAMENTAL REDESIGN]

**Statistics**:
- **P0 Critical**: [COUNT] findings
- **P1 High**: [COUNT] findings
- **P2 Medium**: [COUNT] findings
- **Total**: [COUNT] findings

**Blocking Issues** (Must resolve before downstream artifacts):
1. [P0-1 summary]
2. [P0-2 summary]
...

**Synthesis**:
[Paragraph summarizing document viability and critical gaps]

---

## 2. Critical Findings (P0)

| ID | Finding | Expert | Section | Impact |
|----|---------|--------|---------|--------|

---

## 3. High Priority Findings (P1)

| ID | Finding | Expert | Section | Impact |
|----|---------|--------|---------|--------|

---

## 4. Required Remediations

| ID | Priority | Target File | Section | Remediation Text | Source |
|----|----------|-------------|---------|------------------|--------|
| R1 | P0 | `exact_filename.md` | X.X | "Exact text to add" | Expert |

---

## 5. Enhancement Recommendations (P2)

| ID | Finding | Expert | Value Add |
|----|---------|--------|-----------|

---

## 6. Items Verified as Present

| Item | Location | Exact Specification |
|------|----------|---------------------|

---

## 7. Alternative Solutions (If Fundamental Redesign)

[Only if P0 issues indicate architectural problems]

---

## 8. Per-Persona Detailed Analysis

[Include detailed output from each persona with findings, verified items, and remediations]
```

---

## Document to Review

[PASTE {doc_type} DOCUMENT CONTENT BELOW THIS LINE]'''


def update_template(template_path: Path) -> bool:
    """Update a single UCR template with SDD-compliant format."""
    # Extract doc type from filename
    match = re.search(r'UCR_PROMPT_(\w+)\.md', template_path.name)
    if not match:
        return False

    doc_type = match.group(1)
    if doc_type not in DOC_LAYERS:
        print(f"Unknown doc type: {doc_type}")
        return False

    content = template_path.read_text()

    # Check if already updated
    if "SDD-compliant format" in content:
        print(f"Already updated: {template_path.name}")
        return False

    # Find and replace the Final Synthesis section
    # Use a simpler approach - find the section boundaries
    old_start = "## Final Synthesis\n\nAfter all persona reviews, produce the consolidated report:"
    old_end = "[PASTE"

    if old_start not in content:
        print(f"Pattern not found in: {template_path.name}")
        return False

    # Find the section
    start_idx = content.find(old_start)
    end_marker = content.find(old_end, start_idx)

    if end_marker == -1:
        print(f"End marker not found in: {template_path.name}")
        return False

    # Find the end of the line with [PASTE
    end_idx = content.find("\n", end_marker)
    if end_idx == -1:
        end_idx = len(content)

    # Get the prefix (everything before Final Synthesis)
    prefix = content[:start_idx].rstrip()

    # Get the new format
    new_format = get_new_format(doc_type)

    # Combine
    new_content = prefix + "\n\n" + new_format.lstrip() + "\n"

    # Write back
    template_path.write_text(new_content)
    print(f"Updated: {template_path.name}")
    return True


def main():
    """Update all UCR templates."""
    templates_dir = Path("/opt/data/docs_flow_framework/UCX/ucx/prompts/templates/ucr")

    updated = 0
    for template_path in templates_dir.glob("UCR_PROMPT_*.md"):
        # Skip BRD - already updated manually
        if "BRD" in template_path.name:
            print(f"Skipping (already done): {template_path.name}")
            continue

        if update_template(template_path):
            updated += 1

    print(f"\nTotal updated: {updated}")


if __name__ == "__main__":
    main()
