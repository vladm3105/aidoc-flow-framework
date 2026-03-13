# PLAN-004: UCX v1.13.1 - Advanced Context Engineering Features

**Status**: ✅ COMPLETE
**Created**: 2026-03-13
**Completed**: 2026-03-13
**Version**: v1.13.1

## Overview

Implement three deferred features from PLAN-003 to complete the context engineering system:

| Phase | Feature | Purpose | Token Impact |
|-------|---------|---------|--------------|
| **6.7** | Hybrid Keyword Scan | Discover relevant content in non-mapped sections | Completeness |
| **6.9** | Appendix-on-Demand | Lightweight appendix index with verification tags | -20-50K/call |
| **6.10** | Dynamic Section Mapping | Semantic category-based section filtering | Multi-doc support |

---

## Phase 6.7: Hybrid Keyword Scan

### Goal
Discover relevant content scattered in sections NOT in `PERSONA_SECTION_MAP` using persona-specific keyword matching.

### Changes

**File: `/opt/data/docs_flow_framework/UCX/ucx/core/context_engine.py`**

1. Add `RelevantSnippet` dataclass (~line 134):
```python
@dataclass
class RelevantSnippet:
    """Snippet discovered via keyword scan."""
    section_id: str
    content: str
    keywords_matched: list[str]
    relevance_score: float
```

2. Update `HierarchicalContext` dataclass (~line 136):
```python
@dataclass
class HierarchicalContext:
    level1_overview: str
    level2_relevant: str
    level3_reference: str
    level4_discovered: str = ""  # NEW: keyword-discovered snippets
    appendix_index: list = None  # NEW: for Phase 6.9
    total_tokens: int = 0
    sections_included: list[str] = None
    sections_skipped: list[str] = None
    discovered_snippets: list = None  # NEW: RelevantSnippet list
```

3. Add `_scan_other_sections_for_keywords()` method (~line 340):
```python
def _scan_other_sections_for_keywords(
    self,
    persona: str,
    excluded_sections: set[str],
    max_snippets: int = 10,
) -> list[RelevantSnippet]:
    """Scan non-mapped sections for persona-relevant keywords."""
```

4. Add `_format_discovered_snippets()` method.

5. Update `build_hierarchical_context()` to accept `enable_keyword_scan: bool = True`.

---

## Phase 6.9: Appendix-on-Demand

### Goal
Build lightweight appendix index (~500 tokens) instead of including full appendices (20-50K tokens). Use `[VERIFY: appendix-id]` tags for post-processing verification.

### Changes

**File: `/opt/data/docs_flow_framework/UCX/ucx/core/context_engine.py`**

1. Add `AppendixInfo` dataclass (~line 150):
```python
@dataclass
class AppendixInfo:
    section_id: str
    title: str
    estimated_tokens: int
    keywords: list[str]
    content_summary: str  # ~200 chars
```

2. Add `APPENDIX_TITLE_PATTERNS` constant.

3. Add methods:
   - `_build_appendix_index(persona: str) -> list[AppendixInfo]`
   - `_generate_appendix_summary(content: str, max_chars: int = 200) -> str`
   - `_extract_appendix_keywords(content: str, max_keywords: int = 20) -> list[str]`
   - `_format_appendix_index(appendix_index: list[AppendixInfo]) -> str`

**File: `/opt/data/docs_flow_framework/UCX/ucx/core/review_memory.py`**

1. Add `VERIFY_TAG_PATTERN` regex:
```python
VERIFY_TAG_PATTERN = re.compile(r'\[VERIFY:\s*([A-Za-z0-9\-_.]+)\]')
```

2. Add `AppendixVerifier` class for post-processing verification.

3. Update `_extract_findings()` to parse `[VERIFY:]` tags.

**Files: Skill files** (optional guideline updates)

- `/opt/data/docs_flow_framework/UCX/skills/architect.md` - Add appendix consultation guidelines
- Similar updates for other personas

---

## Phase 6.10: Dynamic Section Mapping

### Goal
Replace hardcoded `PERSONA_SECTION_MAP` with semantic category-based mapping that works across document types (BRD-01, BRD-02, PRD, EARS).

### Changes

**File: `/opt/data/docs_flow_framework/UCX/ucx/core/context_engine.py`**

1. Add `SECTION_CATEGORIES` constant (~line 120):
```python
SECTION_CATEGORIES = {
    "functional": ["functional requirements", "features", "capabilities", "use cases"],
    "quality": ["quality attributes", "nfr", "non-functional", "performance", "sla"],
    "compliance": ["compliance", "regulatory", "legal", "security requirements", "kyc", "aml"],
    "integration": ["integration", "interfaces", "api", "external systems", "partners"],
    "risk": ["risk", "mitigation", "assumptions", "constraints", "dependencies"],
    "business": ["business context", "market", "stakeholders", "objectives", "cost-benefit"],
    "technical": ["technical", "architecture", "design", "implementation", "deployment"],
    "scope": ["scope", "boundaries", "in-scope", "out-of-scope", "exclusions"],
    "appendix": ["appendix", "annex", "reference", "supplementary", "attachment"],
    "metadata": ["glossary", "index", "traceability", "revision history", "table of contents"],
}
```

2. Add `PERSONA_CATEGORY_MAP` constant:
```python
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

3. Add `SectionInfo` dataclass:
```python
@dataclass
class SectionInfo:
    section_id: str
    title: str
    category: str
    doc_type: str
    estimated_tokens: int
    keywords: list[str]
    confidence: float  # Category match confidence 0.0-1.0
```

4. Add `DynamicSectionMapper` class:
```python
class DynamicSectionMapper:
    def __init__(self, doc_sections: dict[str, str], doc_type: str = "brd")
    def _discover_and_categorize_sections(self)
    def _categorize_section(self, title: str, content: str) -> tuple[str, float]
    def get_sections_for_persona(self, persona: str) -> dict[str, list[str]]
    def get_section_summary(self) -> str
```

5. Update `ContextEngine.__init__()` to use `DynamicSectionMapper`.

6. Update `build_hierarchical_context()` to use dynamic mapping.

---

## Implementation Order

| Step | Phase | Task | File | Status |
|------|-------|------|------|--------|
| 1 | 6.10 | Add `SECTION_CATEGORIES`, `PERSONA_CATEGORY_MAP` | context_engine.py | ✅ |
| 2 | 6.10 | Add `SectionInfo` dataclass | context_engine.py | ✅ |
| 3 | 6.10 | Add `DynamicSectionMapper` class | context_engine.py | ✅ |
| 4 | 6.7 | Add `RelevantSnippet` dataclass | context_engine.py | ✅ |
| 5 | 6.7 | Update `HierarchicalContext` with level4/discovered_snippets | context_engine.py | ✅ |
| 6 | 6.7 | Add `_scan_other_sections_for_keywords()` | context_engine.py | ✅ |
| 7 | 6.9 | Add `AppendixInfo` dataclass | context_engine.py | ✅ |
| 8 | 6.9 | Add appendix index methods | context_engine.py | ✅ |
| 9 | 6.9 | Add `VERIFY_TAG_PATTERN`, `AppendixVerifier` | review_memory.py | ✅ |
| 10 | All | Update `ContextEngine` to use all new components | context_engine.py | ✅ |
| 11 | All | Add unit tests | test_context_engine.py | ✅ |
| 12 | Docs | Update CHANGELOG, ROADMAP, README | docs/ | ✅ |

---

## Files to Modify

| File | Changes |
|------|---------|
| `/opt/data/docs_flow_framework/UCX/ucx/core/context_engine.py` | Major: Add 3 new classes, 5+ methods, update ContextEngine |
| `/opt/data/docs_flow_framework/UCX/ucx/core/review_memory.py` | Add VERIFY_TAG_PATTERN, AppendixVerifier |
| `/opt/data/docs_flow_framework/UCX/tests/test_context_engine.py` | Add tests for new components |
| `/opt/data/docs_flow_framework/UCX/docs/CHANGELOG_v1.13.0.md` | Update status to show features implemented |
| `/opt/data/docs_flow_framework/UCX/docs/ROADMAP.md` | Mark features complete |
| `/opt/data/docs_flow_framework/UCX/README.md` | Document new features |

---

## Verification

1. **Test Dynamic Section Mapping**:
```bash
cd /opt/data/docs_flow_framework/UCX
PYTHONPATH=. python -c "
from ucx.core.context_engine import DynamicSectionMapper

sections = {
    'BRD-02.3': '# Functional Requirements\nFeatures...',
    'BRD-02.5': '# Compliance Requirements\nKYC/AML...',
}
mapper = DynamicSectionMapper(sections, 'brd')
print(mapper.get_section_summary())
print(mapper.get_sections_for_persona('auditor'))
"
```

2. **Test Hybrid Keyword Scan**:
```bash
PYTHONPATH=. python -c "
from ucx.core.context_engine import ContextEngine

sections = {'BRD-01.6': '...circuit breaker...', 'BRD-01.12': '...webhook retry...'}
engine = ContextEngine(sections)
ctx = engine.build_hierarchical_context('integration_lead', enable_keyword_scan=True)
print(f'Discovered: {len(ctx.discovered_snippets)} snippets')
"
```

3. **Test Appendix Index**:
```bash
PYTHONPATH=. python -c "
from ucx.core.context_engine import ContextEngine

sections = {'BRD-01.18': '# Technical Appendix\nArchitecture diagrams...'}
engine = ContextEngine(sections)
index = engine._build_appendix_index('architect')
print(f'Appendix index: {len(index)} entries')
"
```

4. **Run unit tests**:
```bash
cd /opt/data/docs_flow_framework/UCX
pytest tests/test_context_engine.py -v
```

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Category misclassification | Fallback to "other" category; fact_checker/chairperson get all |
| Keyword scan slow | Limit to 10 snippets; only scan non-mapped sections |
| Appendix verification false negatives | Keep VERIFY as optional hint, not blocker |
| Backwards compatibility | Keep PERSONA_SECTION_MAP as fallback |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-13 | Claude | Initial plan for v1.13.1 deferred features |
