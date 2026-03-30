# UCX Context Engineering Guide

**Version**: 1.2
**Created**: 2026-03-13
**Updated**: 2026-03-18
**Reference**: PLAN-003_persona_prompt_restructuring.md, PLAN-004_advanced_context_engineering.md
**Status**: Complete (v1.13.1)

## Implementation Status

| Feature | Status | Version | Notes |
|---------|--------|---------|-------|
| Finding ID Format (`PREFIX-P0-NNN`) | ✅ Implemented | v1.13.0 | `PERSONA_PREFIX_MAP` in context_engine.py |
| Hierarchical Context (Level 1/2) | ✅ Implemented | v1.13.0 | `HierarchicalContext`, `ContextEngine` |
| Prior Findings Summarization | ✅ Implemented | v1.13.0 | `PriorFindingsSummarizer` |
| Attention Steering | ✅ Implemented | v1.13.0 | `build_attention_steering_format()` |
| Chairperson Manifest Format | ✅ Implemented | v1.13.0 | `build_chairperson_manifest_format()` |
| Persona Section Mapping | ✅ Implemented | v1.13.0 | `PERSONA_SECTION_MAP` (static) |
| Hybrid Keyword Scan (Level 4) | ✅ Implemented | v1.13.1 | `RelevantSnippet`, `_scan_other_sections_for_keywords()` |
| Appendix-on-Demand | ✅ Implemented | v1.13.1 | `AppendixInfo`, `_build_appendix_index()` |
| Dynamic Section Mapping | ✅ Implemented | v1.13.1 | `SECTION_CATEGORIES`, `DynamicSectionMapper` |
| Verification Phase | ✅ Implemented | v1.13.1 | `AppendixVerifier`, `[VERIFY:]` tags |

---

## Table of Contents

1. [Overview](#overview)
2. [Problem Statement](#problem-statement)
3. [Architecture](#architecture)
4. [Skills vs System Instructions](#skills-vs-system-instructions)
5. [Prompt Flow](#prompt-flow)
6. [Hierarchical Document Context](#hierarchical-document-context)
7. [Dynamic Section Mapping](#dynamic-section-mapping)
8. [Prior Findings Summarization](#prior-findings-summarization)
9. [Attention Steering](#attention-steering)
10. [Appendix-on-Demand](#appendix-on-demand)
11. [Verification Phase](#verification-phase)
12. [Configuration](#configuration)
13. [API Reference](#api-reference)

---

## Overview

UCX Context Engineering is a set of techniques to optimize persona prompts for document review. It addresses the challenge of reviewing large documents (100K+ tokens) with multiple personas while staying within LLM context limits and ensuring consistent, structured output.

### Key Principles

| Principle | Description |
|-----------|-------------|
| **Token Efficiency** | Reduce prompt size from 170KB to 40-65KB |
| **Semantic Filtering** | Include only sections relevant to each persona |
| **Attention Steering** | Place critical instructions at prompt END |
| **Progressive Summarization** | Summarize prior findings instead of raw text |
| **On-Demand Loading** | Load appendices only when needed |
| **Dynamic Mapping** | Match sections by content, not hardcoded IDs |

### Token Budget

| Component | Tokens | Purpose |
|-----------|--------|---------|
| Level 1: Overview | ~2K | Document structure, always included |
| Level 2: Relevant | ~30-50K | Persona-filtered sections |
| Level 4: Discovered | ~5-10K | Keyword-discovered snippets |
| Appendix Index | ~1-2K | Lightweight metadata with summaries |
| Prior Findings | ~2-5K | Summarized (vs 50K raw) |
| Format Instructions | ~1K | Attention steering at END |
| **Total** | **~40-65K** | Down from 170KB+ |

---

## Problem Statement

### Original Issues

| Issue | Symptom | Root Cause |
|-------|---------|------------|
| Finding extraction fails | Frontmatter shows P0=0 despite 30+ findings | Regex mismatch |
| Summaries instead of tables | 600-1200 char responses | Format instructions lost in middle |
| Prompt size explosion | 170-187KB prompts | No content filtering |
| Missing manifest markers | No `<!-- UCX-MANIFEST-START -->` | Instructions buried in prompt |
| Inconsistent Finding IDs | `P0-OP-001` vs `OP-P0-001` | No standard format |

### Solution Summary

```
BEFORE: 170KB prompt → LLM ignores format → summary output → extraction fails
AFTER:  60KB prompt → format at END → structured tables → accurate extraction
```

---

## Architecture

### Three-Level Prompt Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LEVEL 1: FRAMEWORK (UCX)                         │
│  Location: /opt/data/docs_flow_framework/UCX/                       │
│                                                                     │
│  Components:                                                        │
│  ├── ucx/core/persona_prompts.py   # PERSONA_TEMPLATES              │
│  ├── ucx/core/context_engine.py    # Context engineering            │
│  │   ├── SECTION_CATEGORIES        # Semantic categories            │
│  │   ├── PERSONA_CATEGORY_MAP      # Persona-to-category mapping    │
│  │   ├── DynamicSectionMapper      # Section discovery              │
│  │   ├── ContextEngine             # Hierarchical context           │
│  │   └── PriorFindingsSummarizer   # Prior context compression      │
│  └── skills/                       # Default persona skills         │
│      ├── architect.md                                               │
│      ├── auditor.md                                                 │
│      └── ...                                                        │
│                                                                     │
│  Provides: Base templates, context algorithms, default skills       │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LEVEL 2: PROJECT                                 │
│  Location: {project_root}/docs/UCX/                                 │
│                                                                     │
│  Components:                                                        │
│  ├── review/                                                        │
│  │   ├── UCR_PROMPT_BRD_PROJECT.md  # Project BRD review prompt     │
│  │   └── UCR_PROMPT_PRD_PROJECT.md  # Project PRD review prompt     │
│  ├── skills/                        # Project-specific overrides    │
│  │   ├── chairperson.md             # Override framework skill      │
│  │   └── ...                                                        │
│  └── config/                        # Optional configuration        │
│      └── section_categories.yaml    # Project-specific categories   │
│                                                                     │
│  Provides: Domain knowledge, project context, custom categories     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LEVEL 3: DOCUMENT                                │
│  Loaded at runtime from document being reviewed                     │
│                                                                     │
│  Input:                                                             │
│  ├── doc_sections: dict[str, str]   # Actual section content        │
│  ├── doc_type: str                  # "brd", "prd", "ears"          │
│  ├── doc_path: Path                 # Document location             │
│  └── previous_responses: dict       # Prior persona outputs         │
│                                                                     │
│  Processing:                                                        │
│  ├── DynamicSectionMapper           # Discover & categorize         │
│  ├── ContextEngine                  # Build hierarchical context    │
│  └── PriorFindingsSummarizer        # Compress prior findings       │
│                                                                     │
│  Output: Optimized prompt for each persona                          │
└─────────────────────────────────────────────────────────────────────┘
```

### Skill Loading Priority

```python
def load_skill(persona: str, project_dir: Path) -> str:
    """Load skill with project override priority."""

    # Priority 1: Project-specific skill
    project_skill = project_dir / "docs/UCX/skills" / f"{persona}.md"
    if project_skill.exists():
        return project_skill.read_text()

    # Priority 2: Framework skill (fallback)
    framework_skill = FRAMEWORK_ROOT / "UCX/skills" / f"{persona}.md"
    if framework_skill.exists():
        return framework_skill.read_text()

    return ""
```

---

## Skills vs System Instructions

### Standard LLM API Structure

Most LLM APIs support two message roles:

```
┌─────────────────────────────────────────────────────────────┐
│                      LLM API Request                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  SYSTEM PROMPT (system role)                        │   │
│  │                                                     │   │
│  │  "You are a helpful assistant that..."              │   │
│  │  - Sets persistent persona/behavior                 │   │
│  │  - Defines rules and constraints                    │   │
│  │  - Establishes output format                        │   │
│  │  - Higher priority in model attention               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  USER PROMPT (user role)                            │   │
│  │                                                     │   │
│  │  "Review this document and find issues..."          │   │
│  │  - The actual task                                  │   │
│  │  - Context/content to analyze                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Where Can Skills Go?

Skills (domain knowledge) can be injected into **either** location:

```
Option A: Skills in SYSTEM prompt
─────────────────────────────────
┌─────────────────────────────────┐
│ SYSTEM:                         │
│                                 │
│ You are an Architect.           │  ← Base persona
│                                 │
│ ## Domain Knowledge             │  ← SKILL HERE
│ - CAP theorem principles        │
│ - Anti-patterns to detect       │
│ - Review questions              │
│                                 │
│ ## Output Format                │
│ Use [P0-001] format...          │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│ USER:                           │
│                                 │
│ Review this BRD document:       │
│ [document content]              │
└─────────────────────────────────┘


Option B: Skills in USER prompt (UCX approach)
──────────────────────────────────────────────
┌─────────────────────────────────┐
│ SYSTEM:                         │
│                                 │
│ (minimal or none)               │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│ USER:                           │
│                                 │
│ ## Your Role: Architect         │  ← SKILL HERE
│ - CAP theorem principles        │
│ - Anti-patterns to detect       │
│                                 │
│ ## Document to Review           │
│ [document content]              │
│                                 │
│ ## Instructions                 │
│ Find issues, use [P0-001]...    │
└─────────────────────────────────┘
```

### Why UCX Uses User Prompt (Option B)

| Factor | System Prompt | User Prompt (UCX) |
|--------|---------------|-------------------|
| **CLI Compatibility** | Claude CLI doesn't support separate system prompt | Works with all backends |
| **API Compatibility** | Some APIs have system prompt limits | No limits |
| **Flexibility** | Fixed per conversation | Can vary per call |
| **Backend Portability** | Requires API-specific handling | Single prompt works everywhere |

**UCX Design Decision**: Since UCX supports multiple backends (Claude CLI, Gemini CLI, Ollama, LiteLLM APIs), using user prompt ensures consistency.

### CLI Mode Reality

When using Claude Code CLI, there's no "system" vs "user" - it's all one prompt:

```bash
# UCX runs this:
echo "$FULL_PROMPT" | claude -p --model opus

# Where $FULL_PROMPT contains:
# 1. Skill content (domain knowledge)
# 2. Document content
# 3. Task instructions
```

### API Mode (Could Use System, But Doesn't)

```python
# What UCX actually does (consistency with CLI mode):
response = litellm.completion(
    model="anthropic/claude-opus-4-5-20251101",
    messages=[
        {"role": "user", "content": full_prompt_with_skills}
    ]
)

# What it COULD do (but doesn't for portability):
response = litellm.completion(
    model="anthropic/claude-opus-4-5-20251101",
    messages=[
        {"role": "system", "content": skill_content},
        {"role": "user", "content": document_and_instructions}
    ]
)
```

### Terminology Clarification

| Term | Definition | Where It Lives |
|------|------------|----------------|
| **System Instruction** | Persistent behavior rules for the LLM | `system` role in API |
| **Skill** | Domain knowledge that shapes reasoning | Injected into prompt text |
| **Tool** | External capability LLM can invoke | Tool definitions in API |
| **User Instruction** | Task-specific directions | `user` role in API |

### Skills Are Just Text

Skills are **NOT** a special LLM feature. They are text that becomes part of the prompt:

```
┌─────────────────────────────────────────────────────────────┐
│                     PROMPT STRUCTURE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ SKILL: "Who you are and what you know"                │ │
│  │                                                       │ │
│  │ # Platform Architect Domain Knowledge                 │ │
│  │                                                       │ │
│  │ ## Role                                               │ │
│  │ You evaluate systems for scalability and design.      │ │
│  │                                                       │ │
│  │ ## Core Principles                                    │ │
│  │ 1. Separation of Concerns                             │ │
│  │ 2. Single Point of Failure elimination                │ │
│  └───────────────────────────────────────────────────────┘ │
│                           ↓                                 │
│                    SHAPES HOW LLM                           │
│                    APPROACHES THE TASK                      │
│                           ↓                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ CONTENT: "What to analyze"                            │ │
│  │                                                       │ │
│  │ [50-150KB of BRD document]                            │ │
│  └───────────────────────────────────────────────────────┘ │
│                           ↓                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ INSTRUCTIONS: "What to do" (at END for attention)     │ │
│  │                                                       │ │
│  │ Output findings using format: [ARCH-P0-001]           │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Comparison: Different Agent Frameworks

| Framework | Where Skills/Instructions Go | Notes |
|-----------|------------------------------|-------|
| **UCX** | User prompt | Single prompt for CLI/API portability |
| **Claude Code** | System prompt | Uses `CLAUDE.md` as persistent context |
| **LangChain** | System prompt | Tools in system, task in user |
| **OpenAI Assistants** | Instructions field | Separate from conversation |
| **AutoGPT** | System prompt | Goals and constraints in system |

### Key Takeaway

> **Skills are domain knowledge injected as text into prompts.** They shape how the LLM reasons about the task, but they are not a special API feature. UCX places them in the user prompt for maximum backend compatibility.

---

## Prompt Flow

### Complete Prompt Construction

```
┌────────────────────────────────────────────────────────────────────┐
│                         PERSONA PROMPT                              │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  1. DOMAIN KNOWLEDGE (~5-10K tokens)                               │
│     ├── Source: Skill file (project > framework)                   │
│     └── Contains: Persona-specific expertise, guidelines           │
│                                                                    │
│  2. EXPERT INSTRUCTIONS (~1K tokens)                               │
│     ├── Source: PERSONA_TEMPLATES[persona]                         │
│     └── Contains: Role description, focus areas                    │
│     NOTE: Output format STRIPPED here (added at END)               │
│                                                                    │
│  3. VERIFICATION PROTOCOL (~200 tokens)                            │
│     └── "Before claiming ANY requirement is missing..."            │
│                                                                    │
│  4. LAYER CLASSIFICATION (~300 tokens)                             │
│     └── BRD/PRD-specific finding classification guidance           │
│                                                                    │
│  5. PRIOR FINDINGS SUMMARY (~2-5K tokens)                          │
│     ├── Source: PriorFindingsSummarizer                            │
│     └── Contains: P0/P1/P2 counts, top issues, focus guidance      │
│     NOTE: 90% smaller than raw prior responses                     │
│                                                                    │
│  6. HIERARCHICAL DOCUMENT CONTEXT                                  │
│     ├── Level 1: Overview (~2K tokens)                             │
│     │   └── Section index, key entities, document header           │
│     ├── Level 2: Relevant Sections (~30-50K tokens)                │
│     │   └── Persona-filtered via DynamicSectionMapper              │
│     ├── Appendix Index (~1-2K tokens)                              │
│     │   └── Metadata + summaries for on-demand access              │
│     └── Level 4: Discovered Snippets (~5-10K tokens)               │
│         └── Keyword-matched content from other sections            │
│                                                                    │
│  7. OUTPUT FORMAT (AT END - ATTENTION STEERING)                    │
│     ├── Source: build_attention_steering_format()                  │
│     ├── Contains: Finding ID format, required table structure      │
│     └── Visual emphasis: ═══════ borders, ⚠️ warnings              │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Code Flow

```python
def build_persona_prompt(
    persona: str,
    doc_sections: dict[str, str],
    previous_responses: dict[str, str] = None,
    doc_type: str = "brd",
    project_dir: Path = None,
) -> str:
    """Build optimized prompt using context engineering."""

    parts = []

    # 1. Domain Knowledge (skill file)
    skill_content = load_skill(persona, project_dir)
    if skill_content:
        parts.append("=== YOUR DOMAIN KNOWLEDGE ===")
        parts.append(skill_content)
        parts.append("=== END DOMAIN KNOWLEDGE ===\n")

    # 2. Expert Instructions (WITHOUT output format)
    template = PERSONA_TEMPLATES[persona]
    parts.append("=" * 60)
    parts.append("EXPERT INSTRUCTIONS")
    parts.append("=" * 60)
    parts.append(f"You are {template['title']}.")

    # Strip output format - it comes at END
    instructions = template["instructions"]
    if "## Output Format" in instructions:
        instructions = instructions.split("## Output Format")[0]
    parts.append(instructions)

    # 3. Verification Protocol
    parts.append("\n## CRITICAL Verification Protocol")
    parts.append("Before claiming ANY requirement is missing, you MUST:")
    parts.append("1. Search the ENTIRE document including ALL appendices")
    parts.append("2. Check all related sections")
    parts.append("3. Only flag as missing if truly absent\n")

    # 4. Layer Classification
    if doc_type.lower() == "brd":
        parts.append("## LAYER-APPROPRIATE FINDING CLASSIFICATION (BRD)")
        parts.append("BRD defines WHAT is required, not HOW to implement.")
        parts.append("- P0: Regulatory mandates, security requirements")
        parts.append("- P1 (defer to SPEC): Algorithms, config values\n")

    # 5. Prior Findings Summary (COMPRESSED)
    if previous_responses:
        summarizer = PriorFindingsSummarizer()
        summary = summarizer.summarize_all(previous_responses, persona)
        parts.append(summary)

    # 6. Hierarchical Document Context
    engine = ContextEngine(doc_sections, doc_type)
    context = engine.build_hierarchical_context(persona)

    parts.append(context.level1_overview)
    parts.append(context.level2_relevant)

    if context.appendix_index:
        parts.append(format_appendix_index(context.appendix_index))

    if context.level4_discovered:
        parts.append(context.level4_discovered)

    # 7. OUTPUT FORMAT AT END (Attention Steering)
    prefix = PERSONA_PREFIX_MAP.get(persona, persona[:2].upper())

    if persona == "chairperson":
        parts.append(build_chairperson_manifest_format())
    else:
        parts.append(build_attention_steering_format(persona, prefix))

    return "\n".join(parts)
```

---

## Hierarchical Document Context

### Four-Level Structure

```
┌─────────────────────────────────────────────────────────────────┐
│ LEVEL 1: DOCUMENT OVERVIEW (~2K tokens)                         │
│ Always included for all personas                                │
├─────────────────────────────────────────────────────────────────┤
│ Contents:                                                       │
│ - Document title, version, scope                                │
│ - Section index with 1-line summaries                           │
│ - Key entities (partners, systems, regulations)                 │
│                                                                 │
│ Example:                                                        │
│ ════════════════════════════════════════════════════════════    │
│ LEVEL 1: DOCUMENT OVERVIEW                                      │
│ ════════════════════════════════════════════════════════════    │
│                                                                 │
│ ### Section Index                                               │
│ | Section | Title | Summary |                                   │
│ |---------|-------|---------|                                   │
│ | BRD-01.2 | Business Context | Market analysis and... |        │
│ | BRD-01.6 | Functional Requirements | Transaction flows... |   │
│                                                                 │
│ ### Key Entities                                                │
│ - Partners: Bridge/Noah, Asterium, Paynet                       │
│ - Systems: Cloud Run, Cloud SQL, Pub/Sub                        │
│ - Regulations: FinCEN, OFAC, PCI-DSS                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ LEVEL 2: RELEVANT SECTIONS (~30-50K tokens)                     │
│ Persona-filtered via DynamicSectionMapper                       │
├─────────────────────────────────────────────────────────────────┤
│ Source: PERSONA_CATEGORY_MAP determines which categories        │
│                                                                 │
│ Example for Architect:                                          │
│ - functional: BRD-01.6 (Functional Requirements)                │
│ - quality: BRD-01.7 (Quality Attributes)                        │
│ - technical: BRD-01.18 (Technical Appendix)                     │
│ - integration: BRD-01.8 (Integration Requirements)              │
│                                                                 │
│ Skipped for Architect:                                          │
│ - business: BRD-01.2 (Business Context)                         │
│ - metadata: BRD-01.14 (Glossary)                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ APPENDIX INDEX (~1-2K tokens)                                   │
│ Lightweight metadata with content summaries                     │
├─────────────────────────────────────────────────────────────────┤
│ NOT full content - just enough for personas to decide           │
│                                                                 │
│ Example:                                                        │
│ ════════════════════════════════════════════════════════════    │
│ AVAILABLE APPENDICES (On-Demand Verification)                   │
│ ════════════════════════════════════════════════════════════    │
│                                                                 │
│ ### BRD-01.18: Technical Appendix                               │
│ - Size: ~15,000 tokens                                          │
│ - Topics: failover, API, rate limits, architecture              │
│ - Summary: Sections: Failover Spec, API Rate Limits, DR...      │
│                                                                 │
│ **Usage**: Add [VERIFY: BRD-01.18] to flag for verification     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ LEVEL 4: DISCOVERED SNIPPETS (~5-10K tokens)                    │
│ Keyword-matched content from non-required sections              │
├─────────────────────────────────────────────────────────────────┤
│ Source: Hybrid keyword scan of "other" sections                 │
│                                                                 │
│ Example for Architect:                                          │
│ Found "failover" keyword in BRD-01.11 (Success Metrics):        │
│                                                                 │
│ ### Snippet 1 (from BRD-01.11)                                  │
│ **Keyword**: failover                                           │
│ **Relevance**: 80%                                              │
│ ```                                                             │
│ ...The system must handle failover within 30 seconds.           │
│ API response time under 200ms during failover events...         │
│ ```                                                             │
└─────────────────────────────────────────────────────────────────┘
```

### HierarchicalContext Dataclass

```python
@dataclass
class HierarchicalContext:
    """Hierarchical document context with appendix-on-demand support."""

    level1_overview: str        # ~2K tokens - always included
    level2_relevant: str        # ~30-50K tokens - persona-filtered
    level4_discovered: str      # ~5-10K tokens - keyword-discovered

    appendix_index: list[AppendixInfo]  # Lightweight metadata

    total_tokens: int
    sections_included: list[str]
    sections_skipped: list[str]
    discovered_snippets: list[RelevantSnippet]
```

---

## Dynamic Section Mapping

### The Problem with Hardcoded Section IDs

```python
# OLD: Hardcoded - only works for BRD-01
PERSONA_SECTION_MAP = {
    "architect": {
        "required": ["BRD-01.3", "BRD-01.6", "BRD-01.7"],  # ← Breaks for BRD-02
    }
}
```

### Semantic Category-Based Mapping

```python
# NEW: Works for any document
SECTION_CATEGORIES = {
    "functional": ["functional requirements", "features", "capabilities"],
    "quality": ["quality attributes", "nfr", "performance", "sla"],
    "compliance": ["compliance", "regulatory", "kyc", "aml"],
    "technical": ["technical", "architecture", "implementation"],
    # ... etc
}

PERSONA_CATEGORY_MAP = {
    "architect": {
        "required": ["functional", "quality", "technical", "integration"],
        "optional": ["appendix"],
        "skip": ["metadata", "business"],
    },
    # ... etc
}
```

### How Dynamic Mapping Works

```
Document: BRD-02 (different section numbers than BRD-01)

Step 1: Discover Sections
┌──────────────┬────────────────────────────┐
│ Section ID   │ Title                      │
├──────────────┼────────────────────────────┤
│ BRD-02.3     │ Functional Requirements    │
│ BRD-02.4     │ Quality Attributes         │
│ BRD-02.7     │ Compliance Requirements    │
│ BRD-02.12    │ Glossary                   │
└──────────────┴────────────────────────────┘

Step 2: Categorize by Title/Content
┌──────────────┬────────────────────────────┬────────────┐
│ Section ID   │ Title                      │ Category   │
├──────────────┼────────────────────────────┼────────────┤
│ BRD-02.3     │ Functional Requirements    │ functional │
│ BRD-02.4     │ Quality Attributes         │ quality    │
│ BRD-02.7     │ Compliance Requirements    │ compliance │
│ BRD-02.12    │ Glossary                   │ metadata   │
└──────────────┴────────────────────────────┴────────────┘

Step 3: Map to Persona (Architect)
┌────────────┬─────────────────────────────────────────┐
│ Category   │ Persona Mapping                         │
├────────────┼─────────────────────────────────────────┤
│ functional │ required → BRD-02.3 included            │
│ quality    │ required → BRD-02.4 included            │
│ compliance │ not in architect's required → skipped   │
│ metadata   │ skip → BRD-02.12 excluded               │
└────────────┴─────────────────────────────────────────┘

Result: Architect gets BRD-02.3 and BRD-02.4
        (Same outcome as BRD-01.6 and BRD-01.7)
```

### DynamicSectionMapper API

```python
class DynamicSectionMapper:
    """Map sections to personas based on semantic categories."""

    def __init__(self, doc_sections: dict[str, str], doc_type: str = "brd"):
        self._sections = doc_sections
        self._doc_type = doc_type
        self._discover_and_categorize_sections()

    def get_sections_for_persona(self, persona: str) -> dict[str, list[str]]:
        """
        Get sections for persona based on category mapping.

        Returns:
            {
                "required": ["BRD-01.6", "BRD-01.7"],
                "optional": ["BRD-01.18"],
                "skip": ["BRD-01.14"]
            }
        """
        ...

    def get_section_summary(self) -> str:
        """Get summary of discovered sections for logging."""
        ...
```

---

## Prior Findings Summarization

### The Problem

```
Architect response: 10K tokens
Auditor response: 8K tokens
Tech Lead response: 12K tokens
...
Total prior context: 50K+ tokens → Prompt explosion!
```

### The Solution: 90% Compression

```python
class PriorFindingsSummarizer:
    """Summarize prior findings to reduce context size."""

    def summarize_all(
        self,
        previous_responses: dict[str, str],
        current_persona: str,
    ) -> str:
        """
        Compress 50K tokens → 5K tokens (90% reduction).

        Output format:
        ════════════════════════════════════════════════════════════
        PRIOR FINDINGS SUMMARY (Context Optimized)
        ════════════════════════════════════════════════════════════

        ### Persona Summary
        | Persona | P0 | P1 | P2 | Key Issues |
        |---------|----|----|----|-----------|
        | architect | 5 | 8 | 3 | ARCH-P0-001: Missing failover; ARCH-P0-002: ... |
        | auditor | 3 | 2 | 1 | AUD-P0-001: OFAC screening... |
        | **TOTAL** | **8** | **10** | **4** | |

        ### Critical P0 Findings (Top 10)
        - **ARCH-P0-001** (architect): Missing failover specification
        - **AUD-P0-001** (auditor): OFAC screening frequency undefined
        ...

        ### Focus Areas for TECH_LEAD
        Review areas NOT yet covered by previous 5 personas.
        Avoid duplicating findings already identified above.
        """
```

### Compression Statistics

| Metric | Before | After | Reduction |
|--------|--------|-------|-----------|
| Architect raw | 10K tokens | ~500 tokens | 95% |
| Auditor raw | 8K tokens | ~400 tokens | 95% |
| Total prior | 50K tokens | ~5K tokens | 90% |

---

## Attention Steering

### The Problem: Lost in the Middle

```
┌─────────────────────────────────────────────────────────────┐
│ Standard prompt structure:                                   │
│                                                             │
│ [Instructions with output format]  ← Position 1 (ignored)   │
│ [40K tokens of document content]                            │
│ [10K tokens of prior findings]                              │
│                                                             │
│ LLM attention focuses on:                                   │
│ - Beginning (instructions seen but forgotten)               │
│ - End (where to start generating)                           │
│ - NOT the middle where format was defined                   │
└─────────────────────────────────────────────────────────────┘
```

### The Solution: Format at END

```
┌─────────────────────────────────────────────────────────────┐
│ Context-engineered prompt structure:                         │
│                                                             │
│ [Instructions WITHOUT format]                                │
│ [Hierarchical document context]                              │
│ [Prior findings summary]                                     │
│                                                             │
│ ═══════════════════════════════════════════════════════════ │
│ ██  CRITICAL: REQUIRED OUTPUT FORMAT - READ THIS LAST    ██ │
│ ═══════════════════════════════════════════════════════════ │
│                                                             │
│ ### Finding ID Format: ARCH-P{0-2}-NNN                      │
│                                                             │
│ | ID (ARCH-P0-NNN) | Finding | Section | Gap | Remediation | │
│ |------------------|---------|---------|-----|-------------| │
│ | ARCH-P0-001 | [finding] | [X.X] | [gap] | [fix] |         │
│                                                             │
│ ⚠️⚠️⚠️ FAILURE TO USE THIS FORMAT WILL CAUSE FAILURE ⚠️⚠️⚠️     │
│ ═══════════════════════════════════════════════════════════ │
└─────────────────────────────────────────────────────────────┘
```

### Attention Steering API

```python
def build_attention_steering_format(persona: str, prefix: str) -> str:
    """
    Build format instructions with visual emphasis for prompt END.

    Features:
    - Box drawing characters for visual separation
    - Warning emojis for emphasis
    - Explicit examples with correct format
    - Rules numbered for clarity
    """
    return f"""
═══════════════════════════════════════════════════════════════════
██████████████████████████████████████████████████████████████████████
██  CRITICAL: REQUIRED OUTPUT FORMAT - READ THIS SECTION LAST       ██
██████████████████████████████████████████████████████████████████████
═══════════════════════════════════════════════════════════════════

⚠️⚠️⚠️ FAILURE TO USE THIS EXACT FORMAT WILL CAUSE PROCESSING FAILURE ⚠️⚠️⚠️

### Finding ID Format: {prefix}-P{{0-2}}-NNN

Examples:
- {prefix}-P0-001 (Critical finding #1)
- {prefix}-P1-002 (High priority finding #2)

### Required Output Table

| ID ({prefix}-P0-NNN) | Finding | Section | Gap | Remediation |
|{'-' * 20}|---------|---------|-----|-------------|
| {prefix}-P0-001 | [Specific finding] | [X.X] | [What's missing] | [Exact fix] |

### Rules

1. Each finding MUST have unique ID: {prefix}-P{{N}}-{{NNN}}
2. Section MUST reference exact section number
3. Remediation MUST include specific text to add
4. Do NOT produce summaries - produce COMPLETE TABLES
5. Minimum 5 findings expected

═══════════════════════════════════════════════════════════════════
"""
```

---

## Appendix-on-Demand

### The Problem

```
Appendix size: 20-50K tokens
If included for all personas: 20K × 11 personas = 220K extra tokens
```

### The Solution: Index + Verification Tags

```
┌─────────────────────────────────────────────────────────────┐
│ 1. BUILD LIGHTWEIGHT INDEX (~1-2K tokens)                    │
│                                                             │
│    ### BRD-01.18: Technical Appendix                        │
│    - Size: ~15,000 tokens                                   │
│    - Topics: failover, API, rate limits                     │
│    - Summary: Failover within 30s, 1000 req/min limit...    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. PERSONA REVIEWS WITH INDEX (not full content)            │
│                                                             │
│    Persona sees summary and decides:                        │
│    - Content exists in appendix? → Don't flag as missing    │
│    - Need verification? → Add [VERIFY: BRD-01.18] tag       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. POST-PROCESSING VERIFICATION                              │
│                                                             │
│    For findings with [VERIFY: appendix-id]:                 │
│    1. Load actual appendix content                          │
│    2. Search for relevant keywords                          │
│    3. Update finding status:                                │
│       - VERIFIED: Content exists → finding may be false +   │
│       - NOT_FOUND: Content missing → finding is valid       │
└─────────────────────────────────────────────────────────────┘
```

### AppendixInfo Dataclass

```python
@dataclass
class AppendixInfo:
    """Metadata about an appendix for on-demand access."""
    section_id: str           # e.g., "BRD-01.18"
    title: str               # e.g., "Technical Appendix"
    estimated_tokens: int    # e.g., 15000
    keywords: list[str]      # e.g., ["failover", "API", "rate limits"]
    content_summary: str     # ~200 chars summary
```

### VERIFY Tag Pattern

```python
# In persona output:
"| ARCH-P0-001 | Missing failover spec [VERIFY: BRD-01.18] | 6.1.2 | ... |"

# Extraction pattern:
VERIFY_TAG_PATTERN = re.compile(r'\[VERIFY:\s*([A-Za-z0-9\-_.]+)\]')
```

---

## Verification Phase

### Workflow Integration

```
┌─────────────────────────────────────────────────────────────┐
│                    REVIEW ORCHESTRATOR                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Run all personas (architect → ... → chairperson)        │
│                                                             │
│  2. Extract all findings                                    │
│     findings = memory._extract_findings(responses)          │
│                                                             │
│  3. RUN VERIFICATION PHASE (NEW)                            │
│     verified, stats = run_verification_phase(               │
│         findings=findings,                                  │
│         doc_sections=doc_sections,                          │
│     )                                                       │
│                                                             │
│  4. Generate report with verification summary               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Verification Results in Report

```markdown
## Appendix Verification Summary

| Metric | Count |
|--------|-------|
| Findings Needing Verification | 12 |
| ✅ Verified (content exists) | 4 |
| ⚠️ Partially Verified | 3 |
| ❌ Not Found in Appendix | 5 |

### Verification Details

| Finding ID | Status | Note |
|------------|--------|------|
| ARCH-P0-001 | ✅ VERIFIED | Found in BRD-01.18 (match: 80%) |
| ARCH-P0-002 | ❌ NOT_FOUND | Not found in BRD-01.18 |
```

---

## Configuration

### Project-Level Configuration

```yaml
# docs/UCX/config/section_categories.yaml

# Add project-specific categories
additional_categories:
  remittance:
    - "remittance"
    - "transfer"
    - "cross-border"
    - "fx"

# Override persona mappings
persona_overrides:
  architect:
    required:
      - functional
      - quality
      - technical
      - remittance  # Project-specific
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `UCX_CONTEXT_ENGINEERING` | Enable context engineering | `true` |
| `UCX_ENABLE_KEYWORD_SCAN` | Enable hybrid keyword scan | `true` |
| `UCX_MAX_DISCOVERED_SNIPPETS` | Max snippets from keyword scan | `10` |
| `UCX_ENABLE_VERIFICATION` | Enable post-processing verification | `true` |

---

## API Reference

### Core Classes

```python
# Context Engine
class ContextEngine:
    def __init__(self, doc_sections: dict[str, str], doc_type: str = "brd")
    def build_hierarchical_context(self, persona: str, ...) -> HierarchicalContext

# Dynamic Section Mapper
class DynamicSectionMapper:
    def __init__(self, doc_sections: dict[str, str], doc_type: str = "brd")
    def get_sections_for_persona(self, persona: str) -> dict[str, list[str]]
    def get_section_summary(self) -> str

# Prior Findings Summarizer
class PriorFindingsSummarizer:
    def summarize_all(self, responses: dict[str, str], persona: str) -> str

# Appendix Verifier
class AppendixVerifier:
    def __init__(self, doc_sections: dict[str, str])
    def verify_findings(self, findings: list[dict]) -> list[dict]
```

### Key Functions

```python
# Prompt building
def build_persona_prompt(
    persona: str,
    doc_sections: dict[str, str],
    previous_responses: dict[str, str] = None,
    doc_type: str = "brd",
    project_dir: Path = None,
    use_context_engineering: bool = True,
) -> str

# Attention steering
def build_attention_steering_format(persona: str, prefix: str) -> str
def build_chairperson_manifest_format() -> str

# Verification
def run_verification_phase(
    findings: list[dict],
    doc_sections: dict[str, str],
) -> tuple[list[dict], dict]
```

### Constants

```python
# Finding ID pattern
FINDING_ID_PATTERN = re.compile(
    r'(?:'
    r'\|\s*\*?\*?([A-Z]{2,4}-P[012]-\d{1,3})\*?\*?\s*\|'
    r'|'
    r'\*\*([A-Z]{2,4}-P[012]-\d{1,3})\*\*'
    r'|'
    r'(?:^|\n)\s*([A-Z]{2,4}-P[012]-\d{1,3})[:\s]'
    r')',
    re.MULTILINE
)

# Persona prefixes
PERSONA_PREFIX_MAP = {
    "architect": "ARCH",
    "auditor": "AUD",
    "tech_lead": "TL",
    "strategist": "STR",
    "chaos_engineer": "DA",
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

---

## Related Documentation

- [PLAN-003: Persona Prompt Restructuring](plans/PLAN-003_persona_prompt_restructuring.md)
- [PLAN-004: Advanced Context Engineering](plans/PLAN-004_advanced_context_engineering.md)
- [CHANGELOG_v1.13.0](CHANGELOG_v1.13.0.md)
- [CHANGELOG_v1.13.1](CHANGELOG_v1.13.1.md)
- [UCX README](../README.md)

---

*Last Updated: 2026-03-18*
