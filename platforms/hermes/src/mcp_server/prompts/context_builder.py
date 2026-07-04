from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from mcp_server.models.context_engineering_contracts import (
    AppendixIndexEntry,
    ContextContract,
    PromptBundle,
    PromptMetadataSidecar,
    RelevantSnippet,
    serialize_prompt_metadata_sidecar,
    validate_context_contract,
    validate_prompt_metadata_sidecar,
)
from mcp_server.skills.project_ucx_loader import (
    PersonaMappingError,
    load_multi_persona_files,
    load_persona_mapping,
    load_project_document_template,
    load_project_layer_assets,
    load_project_prompt_template,
)
from mcp_server.utils.template_naming import load_tuned_template


class ContractValidationError(ValueError):
    """Raised when a prompt bundle fails MCP context contract validation."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


@dataclass(frozen=True)
class SourceSection:
    section_id: str
    title: str
    content: str
    included: bool = True


@dataclass(frozen=True)
class SectionMappingResult:
    included_sections: list[SourceSection]
    skipped_sections: list[SourceSection]
    category_confidence: dict[str, float]


@dataclass(frozen=True)
class PromptAssembly:
    prompt_text: str
    bundle: PromptBundle
    prompt_template_text: str
    persona_texts: list[str]
    persona_names: list[str]


@dataclass(frozen=True)
class CreationAssembly:
    prompt_text: str
    bundle: PromptBundle
    prompt_template_text: str
    persona_texts: list[str]
    persona_names: list[str]
    layer_assets: dict[str, str]
    document_template_text: str | None


SECTION_CATEGORIES: dict[str, tuple[str, ...]] = {
    "functional": ("functional", "feature", "capability", "workflow", "behavior"),
    "quality": ("quality", "latency", "availability", "performance", "reliability"),
    "technical": ("technical", "architecture", "system", "implementation", "component"),
    "integration": ("integration", "api", "contract", "dependency", "interface"),
    "compliance": ("compliance", "regulation", "audit", "policy", "security"),
    "risk": ("risk", "failure", "rollback", "incident", "hazard"),
    "operations": ("operations", "monitoring", "logging", "alert", "runbook"),
    "metadata": ("glossary", "metadata", "appendix", "reference", "index"),
}


PERSONA_CATEGORY_MAP: dict[str, tuple[str, ...]] = {
    "architect": ("functional", "quality", "technical", "integration"),
    "auditor": ("compliance", "risk", "quality", "integration"),
    "tech_lead": ("functional", "technical", "integration", "quality"),
    "chaos_engineer": ("risk", "quality", "operations", "integration"),
    "operator": ("operations", "quality", "technical", "risk"),
    "integration_lead": ("integration", "technical", "functional"),
    "chairperson": (
        "functional",
        "quality",
        "technical",
        "integration",
        "compliance",
        "risk",
        "operations",
    ),
    "product_owner": ("functional", "quality", "compliance"),
    "business_analyst": ("functional", "compliance", "quality"),
    "strategist": ("functional", "quality", "risk"),
    "requirements_specialist": ("functional", "technical", "compliance"),
    "ux_strategist": ("functional", "quality"),
    "qa_lead": ("functional", "technical", "quality", "risk"),
    "fact_checker": ("compliance", "quality", "functional"),
    "content_strategist": ("functional", "quality", "compliance"),
}

TOKEN_WARNING_THRESHOLD = 15_000  # ~60KB text; default BRD review (11 personas) is ~12K tokens


MCP_CREATION_ACTIONABLE_RULES = """## MCP Actionable Creation Rules
- Use the layer template file (`*-TEMPLATE.*`) as the primary structural source.
- Use the layer schema file (`*_MVP_SCHEMA.yaml`) for required fields, section ordering, and validation constraints.
- Resolve conflicts using this precedence: project-tuned template > layer template > layer schema.
- Do not rely on deprecated `*_MVP_CREATION_RULES.md` or `*_MVP_VALIDATION_RULES.md` files.
- Keep output deterministic: preserve section order from template/schema and include required metadata fields.
"""


MCP_REVIEW_ACTIONABLE_RULES = """## MCP Actionable Review Rules
- Use the layer template file (`*-TEMPLATE.*`) as the structural authority for section and formatting checks.
- Use the layer schema file (`*_MVP_SCHEMA.yaml`) as the machine-readable authority for required fields and validation constraints.
- Use this precedence for review findings: project-tuned template > layer template > layer schema.
- Do not rely on deprecated `*_MVP_CREATION_RULES.md` or `*_MVP_VALIDATION_RULES.md` files.
- Report deterministic findings tied to concrete template/schema constraints.
"""


def estimate_tokens(*parts: str) -> int:
    """Cheap deterministic token estimate for contract validation and diagnostics."""

    total_chars = sum(len(part) for part in parts)
    return max(1, total_chars // 4)


def _normalize_text(value: str) -> str:
    return value.casefold()


def categorize_section(section: SourceSection) -> tuple[str, float]:
    haystack = _normalize_text(f"{section.title}\n{section.content}")
    best_category = "metadata"
    best_score = 0.0

    for category, keywords in SECTION_CATEGORIES.items():
        matches = sum(1 for keyword in keywords if keyword in haystack)
        if matches > best_score:
            best_category = category
            best_score = float(matches)

    normalized_score = min(1.0, best_score / 3.0) if best_score else 0.2
    return best_category, normalized_score


def map_sections_for_personas(
    personas: list[str], sections: list[SourceSection]
) -> SectionMappingResult:
    """Union of all persona categories — include section if ANY persona needs it."""
    all_categories: set[str] = set()
    for p in personas:
        all_categories.update(PERSONA_CATEGORY_MAP.get(p, ("functional", "technical")))

    included_sections: list[SourceSection] = []
    skipped_sections: list[SourceSection] = []
    category_confidence: dict[str, float] = {}

    for section in sections:
        category, confidence = categorize_section(section)
        category_confidence[section.section_id] = confidence
        if category in all_categories:
            included_sections.append(section)
        else:
            skipped_sections.append(section)

    return SectionMappingResult(
        included_sections=included_sections,
        skipped_sections=skipped_sections,
        category_confidence=category_confidence,
    )


def discover_relevant_snippets(
    *,
    personas: list[str],
    skipped_sections: list[SourceSection],
    max_snippets: int = 5,
) -> list[RelevantSnippet]:
    """Find relevant snippets using union of all persona keywords."""
    all_keywords: set[str] = set()
    for p in personas:
        all_keywords.update(PERSONA_CATEGORY_MAP.get(p, ("functional", "technical")))
    keywords = tuple(all_keywords)
    snippets: list[RelevantSnippet] = []

    for section in skipped_sections:
        lowered = _normalize_text(section.content)
        matched_keyword = next((keyword for keyword in keywords if keyword in lowered), None)
        if not matched_keyword:
            matched_keyword = next(
                (
                    keyword
                    for category in keywords
                    for keyword in SECTION_CATEGORIES.get(category, ())
                    if keyword in lowered
                ),
                None,
            )
        if not matched_keyword:
            continue

        snippet_text = section.content[:280].strip()
        snippets.append(
            RelevantSnippet(
                section_id=section.section_id,
                keyword=matched_keyword,
                text=snippet_text,
                confidence=0.7,
            )
        )
        if len(snippets) >= max_snippets:
            break

    return snippets


def build_appendix_index(sections: list[SourceSection]) -> list[AppendixIndexEntry]:
    appendix_entries: list[AppendixIndexEntry] = []
    for section in sections:
        category, _ = categorize_section(section)
        if category != "metadata":
            continue
        appendix_entries.append(
            AppendixIndexEntry(
                appendix_id=section.section_id,
                title=section.title,
                token_estimate=estimate_tokens(section.content),
                summary=section.content[:200].strip(),
            )
        )
    return appendix_entries


def build_runtime_context(
    *,
    included_sections: list[SourceSection],
    skipped_sections: list[SourceSection],
    discovered_snippets: list[RelevantSnippet],
    appendix_index: list[AppendixIndexEntry],
) -> ContextContract:
    sections_included = [section.section_id for section in included_sections]
    sections_skipped = [section.section_id for section in skipped_sections]

    token_estimate = estimate_tokens(
        *(section.content for section in included_sections),
        *(snippet.text for snippet in discovered_snippets),
        *(appendix.summary for appendix in appendix_index),
    )

    return ContextContract(
        sections_included=sections_included,
        sections_skipped=sections_skipped,
        discovered_snippets=discovered_snippets,
        appendix_index=appendix_index,
        token_estimate=token_estimate,
    )


def build_prompt_bundle(
    *,
    personas: list[str],
    doc_type: str,
    structure_blocks: list[str],
    included_sections: list[SourceSection],
    skipped_sections: list[SourceSection],
    discovered_snippets: list[RelevantSnippet],
    appendix_index: list[AppendixIndexEntry],
    persona_token_estimate: int = 0,
    persona_token_warning: str | None = None,
) -> PromptBundle:
    context = build_runtime_context(
        included_sections=included_sections,
        skipped_sections=skipped_sections,
        discovered_snippets=discovered_snippets,
        appendix_index=appendix_index,
    )
    metadata = PromptMetadataSidecar(
        personas=personas,
        doc_type=doc_type,
        structure_blocks=structure_blocks,
        persona_count=len(personas),
        persona_token_estimate=persona_token_estimate,
        persona_token_warning=persona_token_warning,
        sections_included=context.sections_included,
        sections_skipped=context.sections_skipped,
        tokens_total=context.token_estimate,
    )
    bundle = PromptBundle(context=context, metadata=metadata)
    validate_prompt_bundle_or_raise(bundle)
    return bundle


def validate_prompt_bundle_or_raise(bundle: PromptBundle) -> None:
    errors = [
        *validate_context_contract(bundle.context),
        *validate_prompt_metadata_sidecar(bundle.metadata),
    ]
    if errors:
        raise ContractValidationError(errors)


def inspect_prompt_bundle(
    bundle: PromptBundle, *, token_warning_threshold: int = 12000
) -> dict[str, object]:
    warnings: list[str] = []
    if "format_rules" not in bundle.metadata.structure_blocks:
        warnings.append("format degradation risk: missing format_rules block")
    if bundle.metadata.tokens_total > token_warning_threshold:
        warnings.append("token budget warning: bundle exceeds warning threshold")

    return {
        "personas": bundle.metadata.personas,
        "persona_count": bundle.metadata.persona_count,
        "doc_type": bundle.metadata.doc_type,
        "structure_blocks": bundle.metadata.structure_blocks,
        "sections": {
            "included": bundle.metadata.sections_included,
            "skipped": bundle.metadata.sections_skipped,
        },
        "tokens": {
            "total": bundle.metadata.tokens_total,
        },
        "warnings": warnings,
    }


def _resolve_personas(
    project_root: Path,
    personas: list[str] | None,
    doc_type: str,
    phase: str,
) -> list[tuple[str, str]]:
    """Resolve persona list from explicit param or mapping config."""
    if personas is None:
        mapping = load_persona_mapping(project_root=project_root)
        phase_map = mapping.get(phase)
        if not phase_map:
            raise PersonaMappingError(
                f"No persona mapping for phase '{phase}' in persona_mappings.yaml"
            )
        doc_map = phase_map.get(doc_type) or phase_map.get("_default")
        if not doc_map or "personas" not in doc_map:
            raise PersonaMappingError(
                f"No persona mapping for phase '{phase}', doctype '{doc_type}' "
                f"and no _default fallback in persona_mappings.yaml"
            )
        personas = doc_map["personas"]
    return load_multi_persona_files(project_root=project_root, personas=personas)


def _format_persona_block(persona_pairs: list[tuple[str, str]]) -> str:
    """Format multiple personas into a single prompt block."""
    if len(persona_pairs) == 1:
        return persona_pairs[0][1]
    parts = []
    for i, (name, content) in enumerate(persona_pairs, 1):
        parts.append(f"### Persona {i}: {name.upper()}\n\n{content.strip()}")
    return "\n\n---\n\n".join(parts)


def _compute_token_warning(combined_text: str) -> tuple[int, str | None]:
    """Compute persona token estimate and optional warning."""
    token_est = estimate_tokens(combined_text)
    warning = None
    if token_est > TOKEN_WARNING_THRESHOLD:
        warning = (
            f"Combined persona text ({token_est} tokens) exceeds "
            f"threshold ({TOKEN_WARNING_THRESHOLD}). Consider reducing persona count."
        )
    return token_est, warning


#: Binding citation instruction inlined with a per-lens playbook (HERMES-PARITY-PHASE-2).
#: Only emitted when a playbook is present, so non-crew personas (fact_checker) are
#: never told to cite checks that do not apply to them.
_PLAYBOOK_CITATION_RULE = (
    "**Finding citation (binding contract):** every finding you produce MUST cite "
    'which playbook check fired — `check: "C1"` (a checklist id from the playbook '
    'above) or `check: "beyond-checklist:<principle-tag>"`. Findings without a valid '
    "`check` citation are discarded by the synthesizer."
)


def assemble_project_review_prompt(
    *,
    project_root: Path,
    personas: list[str] | None = None,
    doc_type: str,
    template_name: str,
    sections: list[SourceSection],
    layer: str | None = None,
    playbook_text: str | None = None,
) -> PromptAssembly:
    persona_pairs = _resolve_personas(project_root, personas, doc_type, "review")
    persona_names = [name for name, _ in persona_pairs]
    persona_texts = [text for _, text in persona_pairs]

    mapping = map_sections_for_personas(persona_names, sections)
    discovered_snippets = discover_relevant_snippets(
        personas=persona_names,
        skipped_sections=mapping.skipped_sections,
    )
    appendix_index = build_appendix_index(sections)
    structure_blocks = ["level1_overview", "level2_relevant", "appendix_index", "format_rules"]
    if layer:
        structure_blocks.append("layer_assets")

    combined_persona_text = _format_persona_block(persona_pairs)
    persona_token_est, persona_token_warn = _compute_token_warning(combined_persona_text)

    bundle = build_prompt_bundle(
        personas=persona_names,
        doc_type=doc_type,
        structure_blocks=structure_blocks,
        included_sections=mapping.included_sections,
        skipped_sections=mapping.skipped_sections,
        discovered_snippets=discovered_snippets,
        appendix_index=appendix_index,
        persona_token_estimate=persona_token_est,
        persona_token_warning=persona_token_warn,
    )
    prompt_template_text = load_project_prompt_template(
        project_root=project_root,
        phase="review",
        template_name=template_name,
    )
    parts = [combined_persona_text.strip()]
    if playbook_text:
        parts.append(
            "## Layer-specific playbook\n\n"
            + playbook_text.strip()
            + "\n\n"
            + _PLAYBOOK_CITATION_RULE
        )
    parts += [
        prompt_template_text.strip(),
        MCP_REVIEW_ACTIONABLE_RULES.strip(),
    ]
    if layer:
        layer_assets = load_project_layer_assets(project_root=project_root, layer=layer)
        layer_section = "\n\n".join(
            f"### Layer asset: {name}\n{content.strip()}"
            for name, content in sorted(layer_assets.items())
        )
        parts.append("## Authoritative Layer Assets\n" + layer_section)
    parts.append(json.dumps(inspect_prompt_bundle(bundle), sort_keys=True))
    parts.append(serialize_prompt_metadata_sidecar(bundle.metadata))

    prompt_text = "\n\n".join(parts)
    return PromptAssembly(
        prompt_text=prompt_text,
        bundle=bundle,
        prompt_template_text=prompt_template_text,
        persona_texts=persona_texts,
        persona_names=persona_names,
    )


def assemble_project_creation_prompt(
    *,
    project_root: Path,
    personas: list[str] | None = None,
    doc_type: str,
    layer: str,
    template_name: str,
    sections: list[SourceSection] | None = None,
) -> CreationAssembly:
    """Assemble a creation prompt that fuses MCP runtime assets with authoritative SSD layer inputs.

    Layer assets (*-TEMPLATE.* and *_MVP_SCHEMA.yaml files) from UCX/templates/layers/<layer>/
    and the project-specific tuned template from UCX/templates/<template_name> are both
    included in the assembled prompt text so the AI has full authoritative context for creation.
    """
    if not sections:
        sections = [
            SourceSection(
                section_id="creation_task",
                title=f"Create {doc_type.upper()} document: functional and technical scope",
                content=(
                    f"Define functional requirements, system architecture, and workflow behavior "
                    f"for a new {doc_type.upper()} document. "
                    f"Use the authoritative {layer} SSD layer assets and the project template."
                ),
                included=True,
            )
        ]

    persona_pairs = _resolve_personas(project_root, personas, doc_type, "creation")
    persona_names = [name for name, _ in persona_pairs]
    persona_texts = [text for _, text in persona_pairs]

    mapping = map_sections_for_personas(persona_names, sections)
    discovered_snippets = discover_relevant_snippets(
        personas=persona_names,
        skipped_sections=mapping.skipped_sections,
    )
    appendix_index = build_appendix_index(sections)

    combined_persona_text = _format_persona_block(persona_pairs)
    persona_token_est, persona_token_warn = _compute_token_warning(combined_persona_text)

    bundle = build_prompt_bundle(
        personas=persona_names,
        doc_type=doc_type,
        structure_blocks=["level1_overview", "level2_relevant", "layer_assets", "format_rules"],
        included_sections=mapping.included_sections,
        skipped_sections=mapping.skipped_sections,
        discovered_snippets=discovered_snippets,
        appendix_index=appendix_index,
        persona_token_estimate=persona_token_est,
        persona_token_warning=persona_token_warn,
    )

    prompt_template_text = load_project_prompt_template(
        project_root=project_root,
        phase="creation",
        template_name=template_name,
    )

    layer_assets = load_project_layer_assets(project_root=project_root, layer=layer)

    document_template_text = load_tuned_template(
        doc_type=doc_type,
        loader_fn=load_project_document_template,
        project_root=project_root,
    )

    layer_section = "\n\n".join(
        f"### Layer asset: {name}\n{content.strip()}"
        for name, content in sorted(layer_assets.items())
    )
    parts = [
        combined_persona_text.strip(),
        prompt_template_text.strip(),
        MCP_CREATION_ACTIONABLE_RULES.strip(),
        "## Authoritative Layer Assets\n" + layer_section,
    ]
    if document_template_text:
        parts.append("## Project-Tuned Template\n" + document_template_text.strip())
    parts.append(json.dumps(inspect_prompt_bundle(bundle), sort_keys=True))
    parts.append(serialize_prompt_metadata_sidecar(bundle.metadata))

    prompt_text = "\n\n".join(parts)
    return CreationAssembly(
        prompt_text=prompt_text,
        bundle=bundle,
        prompt_template_text=prompt_template_text,
        persona_texts=persona_texts,
        persona_names=persona_names,
        layer_assets=layer_assets,
        document_template_text=document_template_text,
    )
