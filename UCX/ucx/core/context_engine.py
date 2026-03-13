"""Context engineering for UCX persona prompts.

This module implements hierarchical document context and attention steering
to reduce prompt sizes from ~170KB to ~60-80KB while improving LLM adherence
to output format requirements.

Key components:
- PERSONA_SECTION_MAP: Static mapping of which sections each persona needs
- ContextEngine: Builds three-level hierarchical context (Overview/Relevant/Reference)
- PriorFindingsSummarizer: Reduces prior findings from ~50K to ~5K tokens (90% reduction)
- Attention steering functions: Place format instructions at END of prompt

Reference: PLAN-003_persona_prompt_restructuring.md
"""

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from ucx.utils.logging import get_logger

logger = get_logger(__name__)


class ContextLevel(Enum):
    """Hierarchical context levels."""
    OVERVIEW = 1      # ~2K tokens - always included
    RELEVANT = 2      # ~30-50K tokens - persona-filtered
    REFERENCE = 3     # ~10-20K tokens - appendices on-demand


# Persona prefix mapping for Finding IDs
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


@dataclass
class HierarchicalContext:
    """Three-level hierarchical document context."""

    level1_overview: str      # ~2K tokens - always included
    level2_relevant: str      # ~30-50K tokens - persona-filtered
    level3_reference: str     # ~10-20K tokens - appendices on-demand

    total_tokens: int
    sections_included: list[str]
    sections_skipped: list[str]


@dataclass
class FindingSummary:
    """Summary of a persona's findings."""
    persona: str
    p0_count: int
    p1_count: int
    p2_count: int
    key_issues: list[str]  # Top 3 issues
    finding_ids: list[str]  # All finding IDs


class ContextEngine:
    """Build optimized context for persona prompts."""

    def __init__(self, doc_sections: dict[str, str], doc_type: str = "brd"):
        self._sections = doc_sections
        self._doc_type = doc_type
        self._section_summaries: dict[str, str] = {}

    def build_hierarchical_context(
        self,
        persona: str,
        include_level3: bool = False,
    ) -> HierarchicalContext:
        """Build three-level hierarchical context for a persona."""

        # Level 1: Document Overview (always included)
        level1 = self._build_level1_overview()

        # Level 2: Persona-Relevant Sections
        level2 = self._build_level2_relevant(persona)

        # Level 3: Reference Appendices (optional)
        level3 = ""
        if include_level3:
            level3 = self._build_level3_reference(persona)

        return HierarchicalContext(
            level1_overview=level1,
            level2_relevant=level2,
            level3_reference=level3,
            total_tokens=self._estimate_tokens(level1 + level2 + level3),
            sections_included=self._get_included_sections(persona),
            sections_skipped=self._get_skipped_sections(persona),
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
        index_keys = [k for k in self._sections.keys() if "0" in k or "index" in k.lower()]
        if index_keys:
            index_content = self._sections[index_keys[0]]
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

    def _build_level3_reference(self, persona: str) -> str:
        """Build Level 3: Reference Appendices (~10-20K tokens)."""
        parts = [
            "",
            "=" * 60,
            "LEVEL 3: REFERENCE APPENDICES",
            "=" * 60,
            "",
        ]

        mapping = PERSONA_SECTION_MAP.get(persona, {})
        optional_sections = mapping.get("optional", [])

        for section_id in optional_sections:
            if section_id in self._sections:
                parts.append(f"\n### {section_id} (Reference)\n")
                parts.append(self._sections[section_id])

        return "\n".join(parts)

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
        # This can be made dynamic by scanning the document
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


def build_attention_steering_format(persona: str, prefix: str) -> str:
    """Build attention-steering format section for prompt END."""

    delimiter = "=" * 70

    return f"""

{delimiter}
======================================================================
==  CRITICAL: REQUIRED OUTPUT FORMAT - READ THIS SECTION LAST       ==
======================================================================
{delimiter}

WARNING: FAILURE TO USE THIS EXACT FORMAT WILL CAUSE PROCESSING FAILURE

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

    delimiter = "=" * 70

    return f"""

{delimiter}
======================================================================
==  CRITICAL: CHAIRPERSON MANIFEST FORMAT - REQUIRED                ==
======================================================================
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

WARNING: MANIFEST MARKERS ARE REQUIRED - DO NOT OMIT

{delimiter}
"""
