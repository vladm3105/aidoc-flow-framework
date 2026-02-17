"""Custom entity types for LightRAG knowledge graph extraction.

These 12 domain-agnostic entity types are designed to work across
multiple research domains: trading, technology, regulatory, etc.
"""

CUSTOM_ENTITY_TYPES = [
    # Universal research entities
    "organization",    # Companies, agencies, institutions, funds
    "person",          # Analysts, executives, researchers, authors
    "product",         # Software, platforms, services, instruments
    "technology",      # Frameworks, protocols, languages, algorithms
    "concept",         # Methodologies, theories, strategies, patterns
    "metric",          # KPIs, financial ratios, benchmarks, scores
    "event",           # Earnings calls, launches, regulatory actions, conferences
    "decision",        # Trade executions, architecture choices, go/no-go decisions
    "finding",         # Conclusions, insights, recommendations from analysis
    "risk",            # Identified risks, vulnerabilities, concerns
    "regulation",      # Laws, compliance requirements, standards
    "market_segment",  # Industries, sectors, geographies, demographics
]

# Entity type descriptions for better extraction
ENTITY_TYPE_DESCRIPTIONS = {
    "organization": "Companies, agencies, institutions, investment funds, or any formal organization",
    "person": "Named individuals including analysts, executives, researchers, authors, or notable figures",
    "product": "Software products, platforms, services, financial instruments, or tangible goods",
    "technology": "Technical frameworks, protocols, programming languages, algorithms, or methodologies",
    "concept": "Abstract ideas, methodologies, theories, strategies, patterns, or approaches",
    "metric": "Quantitative measures including KPIs, financial ratios, benchmarks, scores, or statistics",
    "event": "Time-bound occurrences like earnings calls, product launches, regulatory actions, or conferences",
    "decision": "Explicit choices made such as trade executions, architecture decisions, or go/no-go calls",
    "finding": "Conclusions, insights, recommendations, or key takeaways from analysis",
    "risk": "Identified risks, vulnerabilities, concerns, threats, or potential negative outcomes",
    "regulation": "Laws, compliance requirements, standards, policies, or regulatory frameworks",
    "market_segment": "Industries, market sectors, geographic regions, or demographic groups",
}

# Relationship types commonly found between entities
COMMON_RELATIONSHIP_TYPES = [
    "develops",        # organization → product
    "uses",            # organization → technology
    "competes_with",   # organization → organization
    "reports_to",      # person → person
    "founded",         # person → organization
    "announced",       # organization → event
    "measured_by",     # organization → metric
    "addresses",       # product → risk
    "requires",        # product → technology
    "contradicts",     # finding → finding
    "supports",        # finding → decision
    "governs",         # regulation → market_segment
    "affects",         # event → metric
    "mitigates",       # decision → risk
]


def get_entity_extraction_prompt() -> str:
    """Generate entity extraction prompt for LightRAG.

    Returns:
        Formatted prompt string for entity extraction.
    """
    entity_list = "\n".join(
        f"- {etype}: {ENTITY_TYPE_DESCRIPTIONS[etype]}"
        for etype in CUSTOM_ENTITY_TYPES
    )

    return f"""Extract entities from the following text. Focus on these entity types:

{entity_list}

For each entity, provide:
1. The entity name (normalized, consistent form)
2. The entity type (from the list above)
3. A brief description based on the context

Be thorough but precise. Only extract entities that are clearly mentioned or implied.
Normalize entity names for consistency (e.g., "PayPal Holdings" and "PYPL" should both be "PayPal").
"""
