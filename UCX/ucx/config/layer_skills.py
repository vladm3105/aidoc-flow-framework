"""Layer-to-skills mapping for UCX phases."""

from ucx.models.enums import DocType

# Skills to load for each document type during CREATION (UCC)
UCC_LAYER_SKILLS: dict[DocType, list[str]] = {
    DocType.BRD: ["architect", "product_owner", "business_analyst", "strategist", "tech_lead"],
    DocType.PRD: ["product_owner", "ux_strategist", "tech_lead", "qa_lead", "architect"],
    DocType.EARS: ["requirements_specialist", "tech_lead", "qa_lead", "devils_advocate"],
    DocType.BDD: ["qa_lead", "tech_lead", "devils_advocate", "operator"],
    DocType.ADR: ["architect", "tech_lead", "strategist", "devils_advocate", "operator"],
    DocType.SYS: ["architect", "tech_lead", "operator", "integration_expert"],
    DocType.REQ: ["requirements_specialist", "tech_lead", "integration_expert"],
    DocType.CTR: ["architect", "tech_lead", "integration_expert"],
    DocType.SPEC: ["tech_lead", "architect", "operator", "integration_expert"],
    DocType.TSPEC: ["qa_lead", "tech_lead", "operator"],
}

# Skills to load for each document type during REVIEW (UCR)
UCR_LAYER_SKILLS: dict[DocType, list[str]] = {
    DocType.BRD: [
        "architect", "auditor", "tech_lead", "strategist",
        "devils_advocate", "operator", "integration_expert",
        "product_owner", "business_analyst",
    ],
    DocType.PRD: [
        "architect", "auditor", "tech_lead", "strategist",
        "devils_advocate", "operator", "integration_expert",
        "product_owner", "qa_lead", "ux_strategist",
    ],
    DocType.EARS: [
        "tech_lead", "devils_advocate", "integration_expert",
        "qa_lead", "requirements_specialist",
    ],
    DocType.BDD: [
        "auditor", "tech_lead", "devils_advocate",
        "operator", "integration_expert", "qa_lead",
    ],
    DocType.ADR: [
        "architect", "auditor", "tech_lead", "strategist",
        "devils_advocate", "operator", "integration_expert",
    ],
    DocType.SYS: [
        "architect", "tech_lead", "devils_advocate",
        "operator", "integration_expert", "qa_lead",
    ],
    DocType.REQ: [
        "tech_lead", "devils_advocate", "integration_expert",
        "qa_lead", "requirements_specialist",
    ],
    DocType.CTR: [
        "architect", "auditor", "tech_lead",
        "devils_advocate", "integration_expert",
    ],
    DocType.SPEC: [
        "architect", "tech_lead", "devils_advocate",
        "operator", "integration_expert",
    ],
    DocType.TSPEC: [
        "tech_lead", "devils_advocate", "operator",
        "integration_expert", "qa_lead",
    ],
}

# Skills to load for REMEDIATION (UCRem) - same for all layers
FIXER_SKILLS: list[str] = [
    "architect",
    "auditor",
    "qa_lead",
    "integration_expert",
    "devils_advocate",
]

# Alias for backward compatibility
LAYER_SKILLS = UCR_LAYER_SKILLS


def get_skills_for_phase(doc_type: DocType, phase: str) -> list[str]:
    """
    Get skill list for a document type and phase.

    Args:
        doc_type: Document type
        phase: Phase name (ucc, ucr, ucrem)

    Returns:
        List of skill names to load
    """
    if phase == "ucc":
        return UCC_LAYER_SKILLS.get(doc_type, [])
    elif phase == "ucr":
        return UCR_LAYER_SKILLS.get(doc_type, [])
    elif phase == "ucrem":
        return FIXER_SKILLS
    else:
        return []
