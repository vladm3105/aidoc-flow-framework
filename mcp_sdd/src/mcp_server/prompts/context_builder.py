from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from mcp_server.models.context_engineering_contracts import serialize_prompt_metadata_sidecar
from mcp_server.skills.project_ucx_loader import (
    load_project_document_template,
    load_project_layer_assets,
    load_project_persona_file,
    load_project_prompt_template,
)
from mcp_server.utils.template_naming import load_tuned_template

from mcp_server.models.context_engineering_contracts import (
    AppendixIndexEntry,
    ContextContract,
    PromptBundle,
    PromptMetadataSidecar,
    RelevantSnippet,
    validate_context_contract,
    validate_prompt_metadata_sidecar,
)


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
    persona_text: str


@dataclass(frozen=True)
class CreationAssembly:
    prompt_text: str
    bundle: PromptBundle
    prompt_template_text: str
    persona_text: str
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
    "chairperson": ("functional", "quality", "technical", "integration", "compliance", "risk", "operations"),
}


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


def map_sections_for_persona(persona: str, sections: list[SourceSection]) -> SectionMappingResult:
    required_categories = PERSONA_CATEGORY_MAP.get(persona, ("functional", "technical"))
    included_sections: list[SourceSection] = []
    skipped_sections: list[SourceSection] = []
    category_confidence: dict[str, float] = {}

    for section in sections:
        category, confidence = categorize_section(section)
        category_confidence[section.section_id] = confidence
        if category in required_categories:
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
    persona: str,
    skipped_sections: list[SourceSection],
    max_snippets: int = 5,
) -> list[RelevantSnippet]:
    keywords = PERSONA_CATEGORY_MAP.get(persona, ("functional", "technical"))
    snippets: list[RelevantSnippet] = []

    for section in skipped_sections:
        lowered = _normalize_text(section.content)
        matched_keyword = next((keyword for keyword in keywords if keyword in lowered), None)
        if not matched_keyword:
            matched_keyword = next(
                (keyword for category in keywords for keyword in SECTION_CATEGORIES.get(category, ()) if keyword in lowered),
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
    persona: str,
    doc_type: str,
    structure_blocks: list[str],
    included_sections: list[SourceSection],
    skipped_sections: list[SourceSection],
    discovered_snippets: list[RelevantSnippet],
    appendix_index: list[AppendixIndexEntry],
) -> PromptBundle:
    context = build_runtime_context(
        included_sections=included_sections,
        skipped_sections=skipped_sections,
        discovered_snippets=discovered_snippets,
        appendix_index=appendix_index,
    )
    metadata = PromptMetadataSidecar(
        persona=persona,
        doc_type=doc_type,
        structure_blocks=structure_blocks,
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


def inspect_prompt_bundle(bundle: PromptBundle, *, token_warning_threshold: int = 12000) -> dict[str, object]:
    warnings: list[str] = []
    if "format_rules" not in bundle.metadata.structure_blocks:
        warnings.append("format degradation risk: missing format_rules block")
    if bundle.metadata.tokens_total > token_warning_threshold:
        warnings.append("token budget warning: bundle exceeds warning threshold")

    return {
        "persona": bundle.metadata.persona,
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


def assemble_project_review_prompt(
    *,
    project_root: Path,
    persona: str,
    doc_type: str,
    template_name: str,
    sections: list[SourceSection],
    layer: str | None = None,
) -> PromptAssembly:
    mapping = map_sections_for_persona(persona, sections)
    discovered_snippets = discover_relevant_snippets(
        persona=persona,
        skipped_sections=mapping.skipped_sections,
    )
    appendix_index = build_appendix_index(sections)
    structure_blocks = ["level1_overview", "level2_relevant", "appendix_index", "format_rules"]
    if layer:
        structure_blocks.append("layer_assets")

    bundle = build_prompt_bundle(
        persona=persona,
        doc_type=doc_type,
        structure_blocks=structure_blocks,
        included_sections=mapping.included_sections,
        skipped_sections=mapping.skipped_sections,
        discovered_snippets=discovered_snippets,
        appendix_index=appendix_index,
    )
    persona_text = load_project_persona_file(project_root=project_root, persona=persona)
    prompt_template_text = load_project_prompt_template(
        project_root=project_root,
        phase="review",
        template_name=template_name,
    )
    parts = [
        persona_text.strip(),
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
        persona_text=persona_text,
    )


def assemble_project_creation_prompt(
    *,
    project_root: Path,
    persona: str,
    doc_type: str,
    layer: str,
    template_name: str,
    sections: list[SourceSection] | None = None,
) -> CreationAssembly:
    """Assemble a creation prompt that fuses MCP runtime assets with authoritative SSD layer inputs.

    Layer assets (*-TEMPLATE.* and *_MVP_SCHEMA.yaml files) from docs/UCX/templates/layers/<layer>/
    and the project-specific tuned template from docs/UCX/templates/<template_name> are both
    included in the assembled prompt text so the AI has full authoritative context for creation.
    """
    if not sections:
        # Creation builds don't have an existing document to section; synthesize a task anchor
        # so the PromptBundle contract (sections_included must be non-empty) is satisfied.
        # The content uses category keywords (functional, workflow, architecture, technical)
        # so it survives persona-based section mapping for all standard personas.
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

    mapping = map_sections_for_persona(persona, sections)
    discovered_snippets = discover_relevant_snippets(
        persona=persona,
        skipped_sections=mapping.skipped_sections,
    )
    appendix_index = build_appendix_index(sections)
    bundle = build_prompt_bundle(
        persona=persona,
        doc_type=doc_type,
        structure_blocks=["level1_overview", "level2_relevant", "layer_assets", "format_rules"],
        included_sections=mapping.included_sections,
        skipped_sections=mapping.skipped_sections,
        discovered_snippets=discovered_snippets,
        appendix_index=appendix_index,
    )

    persona_text = load_project_persona_file(project_root=project_root, persona=persona)
    prompt_template_text = load_project_prompt_template(
        project_root=project_root,
        phase="creation",
        template_name=template_name,
    )

    # Authoritative SSD layer assets (template + schema) copied during scaffold
    layer_assets = load_project_layer_assets(project_root=project_root, layer=layer)

    # Project-tuned document template (may not exist for all layers; tolerated)
    document_template_text = load_tuned_template(
        doc_type=doc_type,
        loader_fn=load_project_document_template,
        project_root=project_root,
    )

    # Assemble prompt: persona | creation template | layer authoritative assets | tuned template
    layer_section = "\n\n".join(
        f"### Layer asset: {name}\n{content.strip()}"
        for name, content in sorted(layer_assets.items())
    )
    parts = [
        persona_text.strip(),
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
        persona_text=persona_text,
        layer_assets=layer_assets,
        document_template_text=document_template_text,
    )
