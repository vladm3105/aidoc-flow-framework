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

v1.19.0: Updated to support hash-based finding IDs (PLAN-008).
"""

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from ucx.utils.logging import get_logger
from ucx.utils.finding_hash import (
    DUAL_FORMAT_FINDING_PATTERN,
    is_legacy_finding_id,
    is_hash_finding_id,
)

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
    "chaos_engineer": "CE",  # Renamed from devils_advocate (v1.14.3)
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
    "chaos_engineer": {  # Renamed from devils_advocate (v1.14.3)
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
    "qa_lead": {  # Added v1.14.3
        "required": ["BRD-01.4", "BRD-01.5", "BRD-01.6", "BRD-01.8"],
        "optional": ["BRD-01.7", "BRD-01.10"],
        "skip": ["BRD-01.18", "BRD-01.13", "BRD-01.14", "BRD-01.15", "BRD-01.16"],
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


# Section keywords for dynamic relevance scoring (Phase 6.7)
PERSONA_KEYWORDS = {
    "architect": ["architecture", "scalability", "failover", "CAP", "distributed", "microservice", "integration", "API", "database", "cache", "queue"],
    "auditor": ["compliance", "regulatory", "FinCEN", "OFAC", "PCI", "KYC", "AML", "SAR", "audit", "security", "encryption", "session"],
    "tech_lead": ["implementation", "state machine", "idempotency", "transaction", "saga", "retry", "error", "exception", "concurrency"],
    "strategist": ["business", "cost", "revenue", "ROI", "market", "competitor", "pricing", "float", "economics"],
    "chaos_engineer": ["failure", "edge case", "timeout", "rollback", "compensation", "partial", "concurrent", "race condition", "chaos", "fault injection"],
    "operator": ["deployment", "monitoring", "alerting", "SLI", "SLO", "runbook", "DR", "failover", "observability", "logging"],
    "integration_lead": ["partner", "API", "webhook", "integration", "contract", "schema", "versioning", "circuit breaker"],
    "product_owner": ["stakeholder", "user story", "acceptance", "feature", "priority", "roadmap", "mvp", "backlog"],
    "business_analyst": ["process", "workflow", "requirement", "use case", "actor", "scenario", "constraint"],
    "fact_checker": ["consistency", "reference", "cross-check", "verify", "validate", "accuracy"],
    "qa_lead": ["test", "testability", "coverage", "BDD", "Gherkin", "acceptance criteria", "quality", "verification", "validation", "edge case"],
}


# ============================================================================
# Phase 6.10: Dynamic Section Mapping
# ============================================================================

# Semantic section categories (document-type agnostic)
SECTION_CATEGORIES = {
    "functional": [
        "functional requirements", "features", "capabilities",
        "use cases", "user stories", "transaction flows", "functional"
    ],
    "quality": [
        "quality attributes", "nfr", "non-functional",
        "performance", "scalability", "availability", "sla", "quality"
    ],
    "compliance": [
        "compliance", "regulatory", "legal", "security requirements",
        "privacy", "gdpr", "pci", "kyc", "aml", "fincen", "ofac"
    ],
    "integration": [
        "integration", "interfaces", "api", "external systems",
        "partners", "third-party", "webhook", "partner"
    ],
    "risk": [
        "risk", "mitigation", "assumptions", "constraints",
        "dependencies", "blockers", "risk management"
    ],
    "business": [
        "business context", "market", "stakeholders", "objectives",
        "success criteria", "kpi", "metrics", "cost-benefit", "business"
    ],
    "technical": [
        "technical", "architecture", "design", "implementation",
        "data model", "infrastructure", "deployment", "system design"
    ],
    "scope": [
        "scope", "boundaries", "in-scope", "out-of-scope",
        "exclusions", "limitations", "project scope"
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


# Persona to CATEGORY mapping (replaces hardcoded PERSONA_SECTION_MAP for new docs)
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
    "chaos_engineer": {  # Renamed from devils_advocate (v1.14.3)
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
    "qa_lead": {  # Added v1.14.3
        "required": ["functional", "quality", "scope"],
        "optional": ["technical", "risk"],
        "skip": ["metadata", "appendix", "business"],
    },
}


# ============================================================================
# Phase 6.9: Appendix-on-Demand
# ============================================================================

# Patterns to detect appendix sections dynamically
APPENDIX_TITLE_PATTERNS = [
    "appendix", "annex", "reference", "technical details",
    "supplementary", "attachment", "exhibit"
]


@dataclass
class HierarchicalContext:
    """Four-level hierarchical document context (v1.13.1+)."""

    level1_overview: str      # ~2K tokens - always included
    level2_relevant: str      # ~30-50K tokens - persona-filtered
    level3_reference: str     # ~10-20K tokens - appendices on-demand
    level4_discovered: str = ""  # Phase 6.7: keyword-discovered snippets

    total_tokens: int = 0
    sections_included: list[str] = None
    sections_skipped: list[str] = None

    # Phase 6.7: Hybrid keyword scan results
    discovered_snippets: list = None  # list[RelevantSnippet]

    # Phase 6.9: Appendix index for on-demand access
    appendix_index: list = None  # list[AppendixInfo]

    def __post_init__(self):
        if self.sections_included is None:
            self.sections_included = []
        if self.sections_skipped is None:
            self.sections_skipped = []
        if self.discovered_snippets is None:
            self.discovered_snippets = []
        if self.appendix_index is None:
            self.appendix_index = []


@dataclass
class RelevantSnippet:
    """Snippet discovered via keyword scan (Phase 6.7)."""
    section_id: str
    content: str
    keywords_matched: list[str]
    relevance_score: float


@dataclass
class AppendixInfo:
    """Metadata about an appendix section for on-demand access (Phase 6.9)."""
    section_id: str
    title: str
    estimated_tokens: int
    keywords: list[str]
    content_summary: str  # ~200 chars for context


@dataclass
class SectionInfo:
    """Discovered section metadata (Phase 6.10)."""
    section_id: str
    title: str
    category: str
    doc_type: str
    estimated_tokens: int
    keywords: list[str]
    confidence: float  # Category match confidence 0.0-1.0


@dataclass
class FindingSummary:
    """Summary of a persona's findings."""
    persona: str
    p0_count: int
    p1_count: int
    p2_count: int
    key_issues: list[str]  # Top 3 issues
    finding_ids: list[str]  # All finding IDs


# ============================================================================
# Phase 6.10: Dynamic Section Mapper
# ============================================================================

class DynamicSectionMapper:
    """Map sections to personas based on semantic categories (Phase 6.10).

    Replaces hardcoded PERSONA_SECTION_MAP with dynamic category-based mapping
    that works across document types (BRD-01, BRD-02, PRD, EARS).
    """

    def __init__(self, doc_sections: dict[str, str], doc_type: str = "brd"):
        self._sections = doc_sections
        self._doc_type = doc_type
        self._section_info: dict[str, SectionInfo] = {}

        self._discover_and_categorize_sections()

    def _discover_and_categorize_sections(self) -> None:
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

    def get_section_info(self, section_id: str) -> Optional[SectionInfo]:
        """Get info for a specific section."""
        return self._section_info.get(section_id)


class ContextEngine:
    """Build optimized context for persona prompts (v1.13.1+).

    Supports:
    - Phase 6.7: Hybrid keyword scan for discovering relevant content
    - Phase 6.9: Appendix-on-demand with lightweight index
    - Phase 6.10: Dynamic section mapping based on semantic categories
    """

    def __init__(
        self,
        doc_sections: dict[str, str],
        doc_type: str = "brd",
        use_dynamic_mapping: bool = True,
    ):
        self._sections = doc_sections
        self._doc_type = doc_type
        self._section_summaries: dict[str, str] = {}
        self._use_dynamic_mapping = use_dynamic_mapping

        # Phase 6.10: Initialize dynamic section mapper
        if use_dynamic_mapping:
            self._section_mapper = DynamicSectionMapper(doc_sections, doc_type)
        else:
            self._section_mapper = None

    def build_hierarchical_context(
        self,
        persona: str,
        include_level3: bool = False,
        enable_keyword_scan: bool = True,
        max_discovered_snippets: int = 10,
        include_appendix_index: bool = True,
    ) -> HierarchicalContext:
        """Build four-level hierarchical context for a persona (v1.13.1+).

        Levels:
        1. Document Overview (~2K tokens) - always included
        2. Persona-Relevant Sections (~30-50K tokens) - via dynamic mapping
        3. Reference Appendices (~10-20K tokens) - optional, on-demand
        4. Keyword-Discovered Snippets (~5-10K tokens) - Phase 6.7

        Args:
            persona: Persona name
            include_level3: Include full reference appendices (not recommended)
            enable_keyword_scan: Enable Phase 6.7 hybrid keyword discovery
            max_discovered_snippets: Max snippets from keyword scan
            include_appendix_index: Include Phase 6.9 appendix index

        Returns:
            HierarchicalContext with all levels and metadata
        """
        # Get section mapping (dynamic or static)
        if self._use_dynamic_mapping and self._section_mapper:
            section_mapping = self._section_mapper.get_sections_for_persona(persona)
        else:
            section_mapping = self._get_static_section_mapping(persona)

        # Level 1: Document Overview (always included)
        level1 = self._build_level1_overview()

        # Level 2: Persona-Relevant Sections (from mapping)
        level2 = self._build_level2_from_mapping(persona, section_mapping)

        # Level 3: Reference Appendices (optional - not recommended for size)
        level3 = ""
        if include_level3:
            level3 = self._build_level3_reference(persona)

        # Phase 6.7: Level 4 - Keyword-discovered snippets
        level4 = ""
        discovered_snippets = []
        if enable_keyword_scan:
            excluded = set(section_mapping["required"]) | set(section_mapping["optional"])
            discovered_snippets = self._scan_other_sections_for_keywords(
                persona,
                excluded_sections=excluded,
                max_snippets=max_discovered_snippets,
            )
            if discovered_snippets:
                level4 = self._format_discovered_snippets(persona, discovered_snippets)

        # Phase 6.9: Appendix index for on-demand access
        appendix_index = []
        if include_appendix_index:
            appendix_index = self._build_appendix_index(persona, section_mapping)

        total_content = level1 + level2 + level3 + level4
        if appendix_index:
            total_content += self._format_appendix_index(appendix_index)

        return HierarchicalContext(
            level1_overview=level1,
            level2_relevant=level2,
            level3_reference=level3,
            level4_discovered=level4,
            total_tokens=self._estimate_tokens(total_content),
            sections_included=section_mapping["required"],
            sections_skipped=section_mapping["skip"],
            discovered_snippets=discovered_snippets,
            appendix_index=appendix_index,
        )

    def _get_static_section_mapping(self, persona: str) -> dict[str, list[str]]:
        """Get section mapping from static PERSONA_SECTION_MAP (fallback)."""
        mapping = PERSONA_SECTION_MAP.get(persona, {})
        return {
            "required": mapping.get("required", []),
            "optional": mapping.get("optional", []),
            "skip": mapping.get("skip", []),
        }

    def _build_level2_from_mapping(
        self,
        persona: str,
        mapping: dict[str, list[str]],
    ) -> str:
        """Build Level 2 content from mapped sections (Phase 6.10)."""
        parts = [
            "",
            "=" * 60,
            f"LEVEL 2: RELEVANT SECTIONS FOR {persona.upper()}",
            "=" * 60,
            "",
        ]

        for section_id in sorted(mapping["required"]):
            if section_id in self._sections:
                # Get category label if using dynamic mapper
                category_label = ""
                if self._section_mapper:
                    info = self._section_mapper.get_section_info(section_id)
                    if info:
                        category_label = f" [{info.category.upper()}]"

                parts.append(f"\n### {section_id}{category_label}\n")
                parts.append(self._sections[section_id])

        return "\n".join(parts)

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

    # ========================================================================
    # Phase 6.7: Hybrid Keyword Scan
    # ========================================================================

    def _scan_other_sections_for_keywords(
        self,
        persona: str,
        excluded_sections: set[str],
        max_snippets: int = 10,
    ) -> list[RelevantSnippet]:
        """Scan non-mapped sections for persona-relevant keywords (Phase 6.7).

        Discovers relevant content scattered in sections NOT already included
        via the static/dynamic section mapping.

        Args:
            persona: Persona name
            excluded_sections: Sections already included (skip these)
            max_snippets: Maximum number of snippets to return

        Returns:
            List of RelevantSnippet sorted by relevance score
        """
        persona_keywords = PERSONA_KEYWORDS.get(persona, [])
        if not persona_keywords:
            return []

        snippets = []

        for section_id, content in self._sections.items():
            # Skip already-included sections
            if section_id in excluded_sections:
                continue

            # Skip always-skip sections
            if self._should_skip_section(section_id, persona):
                continue

            # Scan for keyword matches
            content_lower = content.lower()
            matched_keywords = [
                kw for kw in persona_keywords
                if kw.lower() in content_lower
            ]

            if matched_keywords:
                # Calculate relevance score (more matches = higher score)
                relevance_score = len(matched_keywords) / len(persona_keywords)

                # Extract relevant snippet (first 500 chars around first match)
                snippet_content = self._extract_keyword_snippet(
                    content, matched_keywords[0]
                )

                snippets.append(RelevantSnippet(
                    section_id=section_id,
                    content=snippet_content,
                    keywords_matched=matched_keywords,
                    relevance_score=relevance_score,
                ))

        # Sort by relevance and limit
        snippets.sort(key=lambda s: s.relevance_score, reverse=True)
        return snippets[:max_snippets]

    def _extract_keyword_snippet(
        self,
        content: str,
        keyword: str,
        context_chars: int = 500,
    ) -> str:
        """Extract snippet around keyword match."""
        content_lower = content.lower()
        keyword_lower = keyword.lower()

        pos = content_lower.find(keyword_lower)
        if pos == -1:
            return content[:context_chars]

        start = max(0, pos - context_chars // 2)
        end = min(len(content), pos + context_chars // 2)

        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        return snippet

    def _format_discovered_snippets(
        self,
        persona: str,
        snippets: list[RelevantSnippet],
    ) -> str:
        """Format discovered snippets for prompt injection (Phase 6.7)."""
        if not snippets:
            return ""

        parts = [
            "",
            "=" * 60,
            f"LEVEL 4: DISCOVERED CONTENT FOR {persona.upper()}",
            "=" * 60,
            "",
            "The following content was discovered via keyword scan in sections",
            "not typically mapped to your persona. Review for additional insights.",
            "",
        ]

        for snippet in snippets:
            keywords_str = ", ".join(snippet.keywords_matched[:5])
            parts.append(f"### {snippet.section_id} (Keywords: {keywords_str})")
            parts.append(f"Relevance: {snippet.relevance_score:.0%}")
            parts.append("")
            parts.append(snippet.content)
            parts.append("")

        return "\n".join(parts)

    # ========================================================================
    # Phase 6.9: Appendix-on-Demand
    # ========================================================================

    def _build_appendix_index(
        self,
        persona: str,
        section_mapping: dict[str, list[str]],
    ) -> list[AppendixInfo]:
        """Build appendix index with summaries for on-demand access (Phase 6.9).

        Instead of loading full appendix content (20-50K tokens),
        build a ~500 token index with metadata AND summaries.

        Args:
            persona: Persona name
            section_mapping: Current section mapping

        Returns:
            List of AppendixInfo for appendices
        """
        appendix_sections = set()

        # 1. Dynamic detection by title pattern
        for section_id, content in self._sections.items():
            title = self._extract_section_title(content).lower()
            if any(pattern in title for pattern in APPENDIX_TITLE_PATTERNS):
                appendix_sections.add(section_id)

        # 2. Also include explicitly marked optional sections
        for section_id in section_mapping.get("optional", []):
            if section_id in self._sections:
                appendix_sections.add(section_id)

        # 3. Exclude sections already in "required" (they're in Level 2)
        required_sections = set(section_mapping.get("required", []))
        appendix_sections -= required_sections

        # Build index with summaries
        index = []
        for section_id in sorted(appendix_sections):
            content = self._sections[section_id]
            title = self._extract_section_title(content)
            tokens = self._estimate_tokens(content)
            keywords = self._extract_appendix_keywords(content)
            summary = self._generate_appendix_summary(content)

            index.append(AppendixInfo(
                section_id=section_id,
                title=title,
                estimated_tokens=tokens,
                keywords=keywords[:10],
                content_summary=summary,
            ))

        return index

    def _generate_appendix_summary(self, content: str, max_chars: int = 200) -> str:
        """Generate content summary for appendix (Phase 6.9).

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

    def _extract_appendix_keywords(
        self,
        content: str,
        max_keywords: int = 20,
    ) -> list[str]:
        """Extract key terms from appendix content for index."""
        keywords = []

        # Extract from headers
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

    def _format_appendix_index(self, appendix_index: list[AppendixInfo]) -> str:
        """Format appendix index for prompt injection (Phase 6.9)."""
        if not appendix_index:
            return ""

        parts = [
            "",
            "=" * 60,
            "AVAILABLE APPENDICES (On-Demand Verification)",
            "=" * 60,
            "",
            "The following appendices are available but NOT fully included.",
            "Review the summaries below before claiming content is missing.",
            "",
        ]

        # Detailed view with summaries
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


class PriorFindingsSummarizer:
    """Summarize prior persona findings to reduce context size.

    v1.19.0: Updated to support both legacy (REM-P1-001) and
    hash-based (P1-a7f3) finding ID formats.
    """

    def __init__(self):
        # Dual-format pattern supports both legacy and hash IDs
        # Legacy: ARCH-P0-001, REM-P1-002, etc.
        # Hash: P0-a7f3, P1-b2c1, etc.
        self._finding_pattern = re.compile(
            r'((?:[A-Z]{2,4}-)?P[012]-(?:[a-f0-9]{4,8}|\d{1,3}))',
            re.IGNORECASE,
        )

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


def build_attention_steering_format(persona: str, prefix: str, use_hash_ids: bool = True) -> str:
    """Build attention-steering format section for prompt END.

    Args:
        persona: Persona name
        prefix: Finding ID prefix (e.g., "ARCH", "AUD")
        use_hash_ids: If True, use new hash-based ID format (v1.19.0+).
                      If False, use legacy sequential format.
    """
    delimiter = "=" * 70

    if use_hash_ids:
        # New hash-based format (v1.19.0+)
        id_format = "P{0-2}-AUTO"
        id_note = "NOTE: Use P{N}-AUTO placeholder. System auto-generates hash IDs."
        examples = f"""- P0-AUTO (Critical finding - hash auto-generated)
- P1-AUTO (High priority finding - hash auto-generated)"""
        table_header = f"| ID (P0-xxxx) | Finding | Section | Gap | Remediation |"
        table_row1 = "| P0-AUTO | [Specific finding] | [X.X] | [What's missing] | [Exact fix text] |"
        table_row2 = "| P1-AUTO | [Specific finding] | [X.X] | [What's missing] | [Exact fix text] |"
        rule1 = "1. Use P{N}-AUTO for IDs (system generates hash IDs like P1-a7f3)"
    else:
        # Legacy sequential format
        id_format = f"{prefix}-P{{0-2}}-NNN"
        id_note = ""
        examples = f"""- {prefix}-P0-001 (Critical finding #1)
- {prefix}-P1-002 (High priority finding #2)"""
        table_header = f"| ID ({prefix}-P0-NNN) | Finding | Section | Gap | Remediation |"
        table_row1 = f"| {prefix}-P0-001 | [Specific finding] | [X.X] | [What's missing] | [Exact fix text] |"
        table_row2 = f"| {prefix}-P1-001 | [Specific finding] | [X.X] | [What's missing] | [Exact fix text] |"
        rule1 = f"1. Each finding MUST have unique ID: {prefix}-P{{N}}-{{NNN}}"

    return f"""

{delimiter}
======================================================================
==  CRITICAL: REQUIRED OUTPUT FORMAT - READ THIS SECTION LAST       ==
======================================================================
{delimiter}

WARNING: FAILURE TO USE THIS EXACT FORMAT WILL CAUSE PROCESSING FAILURE

### Finding ID Format: {id_format}

{id_note}

Examples:
{examples}

### Required Output Table

You MUST produce findings in this EXACT table format:

{table_header}
|{'-' * 20}|---------|---------|-----|-------------|
{table_row1}
{table_row2}

### Rules

{rule1}
2. Section MUST reference exact section number (e.g., 6.1.2)
3. Remediation MUST include specific text to add
4. Do NOT produce summaries - produce COMPLETE TABLES
5. Minimum 5 findings expected

{delimiter}
"""


def build_chairperson_manifest_format(use_hash_ids: bool = True) -> str:
    """Build chairperson manifest format section.

    Args:
        use_hash_ids: If True, use new hash-based ID format (v1.19.0+).
    """
    delimiter = "=" * 70

    if use_hash_ids:
        # New hash-based format (v1.19.0+)
        id_examples = """| P0-a7f3 | P0 | [CAT:compliance] | OPEN | auditor | BRD-01.6.md | [description] |
| P0-b2c1 | P0 | [CAT:integration] | OPEN | integration_lead | BRD-01.6.md | [description] |
| P1-8d4e | P1 | [CAT:functional] | OPEN | tech_lead | BRD-01.6.md | [description] |"""
        id_note = """### Finding ID Format (v1.19.0+)

Use hash-based IDs: P{0-2}-{4-char-hex}
- P0-xxxx for Critical findings
- P1-xxxx for High priority findings
- P2-xxxx for Medium priority findings

NOTE: Use P{N}-AUTO placeholder. System auto-generates hash IDs during assembly.
"""
    else:
        # Legacy sequential format
        id_examples = """| REM-P0-001 | P0 | [CAT:compliance] | OPEN | auditor | BRD-01.6.md | [description] |
| REM-P0-002 | P0 | [CAT:integration] | OPEN | integration_lead | BRD-01.6.md | [description] |
| REM-P1-001 | P1 | [CAT:functional] | OPEN | tech_lead | BRD-01.6.md | [description] |"""
        id_note = ""

    return f"""

{delimiter}
======================================================================
==  CRITICAL: CHAIRPERSON MANIFEST FORMAT - REQUIRED                ==
======================================================================
{delimiter}

You MUST include these EXACT markers for automated processing:

{id_note}

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
{id_examples}

<!-- UCX-MANIFEST-END -->

{delimiter}

WARNING: MANIFEST MARKERS ARE REQUIRED - DO NOT OMIT

{delimiter}
"""
