"""Layer-to-skills mapping for UCX phases."""

from ucx.models.enums import DocType

# Skills to load for each document type during CREATION (UCC)
UCC_LAYER_SKILLS: dict[DocType, list[str]] = {
    DocType.BRD: ["architect", "product_owner", "business_analyst", "strategist", "tech_lead"],
    DocType.PRD: ["product_owner", "ux_strategist", "tech_lead", "qa_lead", "architect"],
    DocType.EARS: ["requirements_specialist", "tech_lead", "qa_lead", "chaos_engineer"],
    DocType.BDD: ["qa_lead", "tech_lead", "chaos_engineer", "operator"],
    DocType.ADR: ["architect", "tech_lead", "strategist", "chaos_engineer", "operator"],
    DocType.SYS: ["architect", "tech_lead", "operator", "integration_lead"],
    DocType.REQ: ["requirements_specialist", "tech_lead", "integration_lead"],
    DocType.CTR: ["architect", "tech_lead", "integration_lead"],
    DocType.SPEC: ["tech_lead", "architect", "operator", "integration_lead"],
    DocType.TSPEC: ["qa_lead", "tech_lead", "operator"],
}

# Skills to load for each document type during REVIEW (UCR)
UCR_LAYER_SKILLS: dict[DocType, list[str]] = {
    DocType.BRD: [
        "architect", "auditor", "tech_lead", "strategist",
        "chaos_engineer", "operator", "integration_lead",
        "product_owner", "business_analyst",
    ],
    DocType.PRD: [
        "architect", "auditor", "tech_lead", "strategist",
        "chaos_engineer", "operator", "integration_lead",
        "product_owner", "qa_lead", "ux_strategist",
    ],
    DocType.EARS: [
        "tech_lead", "chaos_engineer", "integration_lead",
        "qa_lead", "requirements_specialist",
    ],
    DocType.BDD: [
        "auditor", "tech_lead", "chaos_engineer",
        "operator", "integration_lead", "qa_lead",
    ],
    DocType.ADR: [
        "architect", "auditor", "tech_lead", "strategist",
        "chaos_engineer", "operator", "integration_lead",
    ],
    DocType.SYS: [
        "architect", "tech_lead", "chaos_engineer",
        "operator", "integration_lead", "qa_lead",
    ],
    DocType.REQ: [
        "tech_lead", "chaos_engineer", "integration_lead",
        "qa_lead", "requirements_specialist",
    ],
    DocType.CTR: [
        "architect", "auditor", "tech_lead",
        "chaos_engineer", "integration_lead",
    ],
    DocType.SPEC: [
        "architect", "tech_lead", "chaos_engineer",
        "operator", "integration_lead",
    ],
    DocType.TSPEC: [
        "tech_lead", "chaos_engineer", "operator",
        "integration_lead", "qa_lead",
    ],
}

# Domain-specific fixer skills (adaptive loading based on pre-screening)
DOMAIN_FIXER_SKILLS: list[str] = [
    "architect",
    "auditor",
    "qa_lead",
    "integration_lead",
]

# Mandatory fixer skills (always loaded regardless of findings)
MANDATORY_FIXER_SKILLS: list[str] = [
    "chaos_engineer",  # Safety: root cause vs symptom validation
    "chairperson",      # Synthesis: de-dupe, conflict resolution, final conclusion
]

# Full fixer skills list (for backward compatibility)
FIXER_SKILLS: list[str] = DOMAIN_FIXER_SKILLS + MANDATORY_FIXER_SKILLS

# Alias for backward compatibility
LAYER_SKILLS = UCR_LAYER_SKILLS


def get_skills_for_phase(
    doc_type: DocType,
    phase: str,
    adaptive_fixers: list[str] | None = None,
) -> list[str]:
    """
    Get skill list for a document type and phase.

    Args:
        doc_type: Document type
        phase: Phase name (ucc, ucr, ucrem)
        adaptive_fixers: For ucrem phase, optional list of fixers from pre-screening.
                        If provided, only these domain fixers are loaded plus mandatory.

    Returns:
        List of skill names to load
    """
    if phase == "ucc":
        return UCC_LAYER_SKILLS.get(doc_type, [])
    elif phase == "ucr":
        return UCR_LAYER_SKILLS.get(doc_type, [])
    elif phase == "ucrem":
        if adaptive_fixers is not None:
            # Use pre-screened fixers, ensure mandatory are included
            result = list(adaptive_fixers)
            for mandatory in MANDATORY_FIXER_SKILLS:
                if mandatory not in result:
                    result.append(mandatory)
            return result
        return FIXER_SKILLS
    else:
        return []


def get_adaptive_fixers(required_domain_fixers: list[str]) -> list[str]:
    """
    Build adaptive fixer list from required domain fixers.

    Args:
        required_domain_fixers: Domain fixers identified by pre-screening

    Returns:
        Complete fixer list with mandatory fixers appended
    """
    # Filter to valid domain fixers only
    valid_domain = [f for f in required_domain_fixers if f in DOMAIN_FIXER_SKILLS]

    # Always include mandatory fixers
    result = valid_domain + MANDATORY_FIXER_SKILLS

    # Sort in execution order
    order = {
        "architect": 1,
        "auditor": 2,
        "integration_lead": 3,
        "qa_lead": 4,
        "chaos_engineer": 10,
        "chairperson": 20,
    }
    return sorted(result, key=lambda x: order.get(x, 99))
