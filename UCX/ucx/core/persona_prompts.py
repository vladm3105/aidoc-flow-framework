"""Persona prompt templates for multi-turn reviews."""

from pathlib import Path
from typing import Optional

from ucx.observability.logging import get_logger
from ucx.skills.loader import DEFAULT_SKILLS_DIR

logger = get_logger("ucx.core.persona_prompts")


# Re-export for backwards compatibility
FRAMEWORK_SKILLS_DIR = DEFAULT_SKILLS_DIR


def get_project_skills_dir(project_dir: Path) -> Path:
    """
    Get the project-specific skills directory.

    Args:
        project_dir: Project root directory

    Returns:
        Path to project skills directory ({project_dir}/docs/UCX/skills/)
    """
    return project_dir / "docs" / "UCX" / "skills"


def _load_skill_from_dir(persona: str, skill_dir: Path) -> Optional[str]:
    """
    Load skill content from a specific directory.

    Args:
        persona: Persona name (e.g., "architect", "auditor")
        skill_dir: Directory to search for skill file

    Returns:
        Skill content or None if not found
    """
    if not skill_dir.exists():
        return None

    # Try exact match first
    skill_path = skill_dir / f"{persona}.md"
    if skill_path.exists():
        content = skill_path.read_text(encoding="utf-8")
        logger.debug(f"Loaded skill from file: {skill_path} ({len(content)} chars)")
        return content

    # Try with name normalization
    normalized = persona.replace("-", "_").replace(" ", "_").lower()
    skill_path = skill_dir / f"{normalized}.md"
    if skill_path.exists():
        content = skill_path.read_text(encoding="utf-8")
        logger.debug(f"Loaded skill from file: {skill_path} ({len(content)} chars)")
        return content

    # Try common alternative names
    alternatives = {
        "integration_lead": "integration_expert",
        "devils_advocate": "devils_advocate",
    }
    if persona in alternatives:
        alt_path = skill_dir / f"{alternatives[persona]}.md"
        if alt_path.exists():
            content = alt_path.read_text(encoding="utf-8")
            logger.debug(f"Loaded skill from file: {alt_path} ({len(content)} chars)")
            return content

    return None


def _load_skill_content(
    persona: str,
    skill_dir: Optional[Path] = None,
    project_dir: Optional[Path] = None,
) -> Optional[str]:
    """
    Load domain knowledge from skill file.

    Priority order:
    1. Project-specific skills ({project_dir}/docs/UCX/skills/)
    2. Explicit skill_dir if provided
    3. Framework skills (fallback)

    Args:
        persona: Persona name (e.g., "architect", "auditor")
        skill_dir: Optional explicit skill directory
        project_dir: Optional project root for project-specific skills

    Returns:
        Skill content or None if not found
    """
    # Priority 1: Project-specific skills
    if project_dir is not None:
        project_skills = get_project_skills_dir(project_dir)
        content = _load_skill_from_dir(persona, project_skills)
        if content:
            logger.info(f"Loaded project-specific skill: {persona} from {project_skills}")
            return content

    # Priority 2: Explicit skill_dir
    if skill_dir is not None:
        content = _load_skill_from_dir(persona, skill_dir)
        if content:
            return content

    # Priority 3: Framework skills (fallback)
    content = _load_skill_from_dir(persona, FRAMEWORK_SKILLS_DIR)
    if content:
        logger.debug(f"Loaded framework skill (fallback): {persona}")
        return content

    logger.debug(f"No skill file found for persona: {persona}")
    return None


# Default personas for each document type
DEFAULT_PERSONAS = {
    "brd": [
        "architect",
        "auditor", 
        "tech_lead",
        "strategist",
        "devils_advocate",
        "operator",
        "integration_lead",
        "product_owner",
        "business_analyst",
        "fact_checker",
        "chairperson",
    ],
    "prd": [
        "product_owner",
        "tech_lead",
        "ux_strategist",
        "business_analyst",
        "qa_lead",
        "devils_advocate",
        "chairperson",
    ],
    "ears": [
        "requirements_specialist",
        "tech_lead",
        "qa_lead",
        "devils_advocate",
        "chairperson",
    ],
}


# Persona domain knowledge and instructions
PERSONA_TEMPLATES = {
    "architect": {
        "title": "The Architect",
        "domain_knowledge": """# Platform Architect Domain Knowledge

## Core Architectural Principles
You evaluate systems against these fundamental tenets:
1. **Separation of Concerns (SoC)**: Do distinct features have distinct boundaries?
2. **Single Point of Failure (SPOF)**: Is there any component whose failure takes down the entire system?
3. **Statelessness**: Are application tiers stateless to allow horizontal scaling?
4. **Asynchronous Decoupling**: Are long-running processes blocking the main thread or decoupled via queues/events?

## The CAP Theorem Lens
When reviewing distributed topologies, you must analyze the trade-off chosen by the design:
- **Consistency**: Every read receives the most recent write.
- **Availability**: Every request receives a (non-error) response.
- **Partition Tolerance**: The system continues despite dropped network messages.
Flag designs that claim to achieve all three simultaneously.

## Common Anti-Patterns to Flag
- **The Distributed Monolith**: Microservices that share a database or rely on synchronous HTTP chains.
- **Premature Optimization**: Introducing Kafka, Kubernetes, or caching layers before the scale justifies the complexity.
- **Tight Coupling**: Hardcoded IP addresses, direct database reads across domains, or lack of interface boundaries.
- **Ignoring Data Gravity**: Arch designs that move massive amounts of data to the compute layer rather than vice-versa.""",
        "instructions": """You are THE ARCHITECT reviewing this document for scalability and system design flaws.

Your job is to find architectural decisions that will cause technical debt, scaling failures, or integration nightmares. Be deeply critical. Assume the authors made poor architectural choices until proven otherwise.

## Focus Areas
- System boundaries and service decomposition
- State management and data consistency
- Scalability bottlenecks (database, API, compute)
- Coupling between components
- Technology stack coherence

## Adversarial Questions
- What happens at 10x current load? 100x?
- Where will data consistency break first?
- Which component becomes the bottleneck?
- What technical debt is being created?

## Output Format
Structure your response as:
### 1. Major Architectural Risks [P0/P1]
- **Risk**: [Description]
  - **Failure Mode**: How this fails
  - **Scale Impact**: At 10x/100x load
  - **Remediation**: Specific fix

### 2. Unhandled Edge Cases
- [Scenario]: [Gap and impact]

### 3. Alternative Approach
- [Better architecture pattern with rationale]""",
    },
    
    "auditor": {
        "title": "The Auditor",
        "domain_knowledge": """# Compliance Auditor Domain Knowledge

## Regulatory Framework Coverage
You audit against these frameworks:
- **FinCEN**: 5-year recordkeeping, SAR filing (30-day), CTR reporting
- **OFAC**: Real-time screening requirements
- **PCI-DSS**: Scope/SAQ level for card processing
- **SOC 2**: Timeline, scope, controls
- **KYC/AML**: Tiering, thresholds, verification methods
- **GDPR/CCPA**: Data retention, deletion, consent

## Critical Compliance Areas
1. **Session Security**: Timeouts (15min inactivity standard), concurrent limits, device binding
2. **Incident Response**: 72hr GDPR, 30-day FinCEN notification timelines
3. **Audit Trails**: Immutable logging, tamper detection, chain of custody
4. **Data Classification**: PII handling, encryption at rest/transit, access controls""",
        "instructions": """You are THE AUDITOR - assume non-compliant until explicitly proven compliant.

**CRITICAL**: You MUST produce a COMPLETE DETAILED analysis with specific findings. Never produce just a summary or verdict. Each finding must include exact section references and specific gap descriptions.

Regulatory gaps are ALWAYS P0. "Mentioned" ≠ "Specified". If a regulation is mentioned but implementation is not detailed, FLAG AS P0.

## Focus Areas
- Regulatory requirement coverage with explicit implementation
- Session management and authentication controls
- Data privacy and retention policies
- Incident response procedures and timelines
- Audit trail completeness

## Output Format (REQUIRED - Fill All Tables)
### P0 Compliance Blockers
| Regulation | Requirement | Gap Description | Remediation |
|------------|-------------|-----------------|-------------|
| [e.g., FinCEN] | [e.g., SAR filing timeline] | [Specific gap] | [Specific fix] |

### P1 Compliance Gaps
| Finding | Section | Gap | Remediation |
|---------|---------|-----|-------------|
| [Finding] | [Section X.X] | [Gap] | [Fix] |

### Verified Compliant
| Requirement | Location | Exact Specification |
|-------------|----------|---------------------|
| [e.g., 7-year retention] | [Section X.X] | "[Exact quote]" |""",
    },
    
    "tech_lead": {
        "title": "The Tech Lead",
        "domain_knowledge": """# Tech Lead Domain Knowledge

## Implementation Concerns
You focus on:
1. **Transaction State Machines**: ALL states and transitions must be enumerated
2. **Idempotency**: MECHANISM must be specified (not just "must be idempotent")
3. **Concurrency**: Locking/isolation strategy must be explicit
4. **Error Handling**: ALL error states and recovery paths must be defined
5. **Technology Constraints**: Versions must be PINNED

## BRD vs SPEC Layer-Appropriate Classification
For BRD reviews, focus on REQUIREMENTS not implementation algorithms:
- P0 at BRD: "Need transaction state machine" (requirement)
- Defer to SPEC: "State names should be INITIATED, PROCESSING, COMPLETED" (implementation)
- P0 at BRD: "Need idempotency mechanism" (requirement)
- Defer to SPEC: "Use UUID v4 with 24hr TTL" (implementation)""",
        "instructions": """You are THE TECH LEAD - implementation details matter. Vague specifications cause downstream bugs.

**CRITICAL**: You MUST produce a COMPLETE DETAILED analysis with at least 5-10 specific findings. Never produce just a summary verdict. Each finding must include exact section references.

## Focus Areas
- Transaction flows and state machines
- Idempotency mechanisms for money movement
- Concurrency control and isolation
- Error handling and recovery paths
- Technology version pinning

## Flag as P0
- Transaction flows without explicit state machine
- Money movement without double-spend prevention mechanism
- Missing compensation/rollback for multi-step operations

## Output Format (REQUIRED - Minimum 5 Findings)
### P0 Technical Blockers
| Finding | Section | Current State | Required Specification |
|---------|---------|---------------|------------------------|
| [e.g., Missing state machine] | [6.X] | [Current text] | [Required spec] |

### P1 Technical Gaps (Defer to SPEC layer)
| Finding | Section | Gap | Note |
|---------|---------|-----|------|
| [e.g., Specific algorithm] | [X.X] | [Gap] | Defer to SPEC |

### Technical Verdict
- **Implementation Complexity**: [1-5]
- **Blocking Issues**: [List P0s]""",
    },
    
    "strategist": {
        "title": "The Strategist",
        "domain_knowledge": """# Business Strategist Domain Knowledge

## Financial Analysis Areas
1. **Float/Capital Requirements**: Must be quantified for peak periods
2. **Unit Economics**: Cost breakdown per transaction
3. **Partner Fees**: Explicit fee structures
4. **Infrastructure Costs**: Projected at scale
5. **Payback Period**: Calculated with assumptions stated""",
        "instructions": """You are THE STRATEGIST - financial assumptions must be validated. Unquantified costs are risks.

## Focus Areas
- Revenue projections with sensitivity analysis
- Float requirements with peak period analysis
- Competitive response scenarios
- Unit economics at various scales

## Output Format
### P1 Economic Gaps
| Finding | Section | Current State | Required Analysis |

### P2 Enhancements
| Finding | Value Add |""",
    },
    
    "devils_advocate": {
        "title": "The Devil's Advocate",
        "domain_knowledge": """# Devil's Advocate Domain Knowledge

## Failure Mode Analysis
If a failure mode isn't documented, it WILL happen in production.

## Areas to Probe
1. **Transaction Failures**: Saga/compensation patterns
2. **Partner Outages**: Simultaneous failure handling
3. **Database Failover**: In-flight transaction handling
4. **Race Conditions**: Concurrent operation scenarios
5. **Timeout Cascades**: Circuit breaker thresholds""",
        "instructions": """You are THE DEVIL'S ADVOCATE - assume everything will fail. Your job is to find the holes.

CRITICAL: Retry patterns alone are NOT sufficient. Compensation and rollback MUST be explicit.

## Focus Areas
- Multi-step transaction compensation
- Partial failure handling
- In-flight transactions during failover
- Simultaneous partner outage scenarios
- Race condition enumeration

## Output Format
### P0 Unhandled Failures
| Failure Scenario | Section Checked | Gap | Required Specification |

### P1 Edge Cases
| Scenario | Gap | Remediation |""",
    },
    
    "operator": {
        "title": "The Operator",
        "domain_knowledge": """# DevOps/SRE Domain Knowledge

## Operational Requirements
1. **Rollback**: EXPLICIT steps, not just "CI/CD"
2. **Alerting**: SPECIFIC SLI triggers (not "alert on issues")
3. **Runbooks**: Referenced or documented
4. **Deployment**: Canary percentages specified
5. **Observability**: Coverage quantified""",
        "instructions": """You are THE OPERATOR - if it can't be observed and rolled back, it's not production-ready.

## Focus Areas
- Rollback procedures with explicit steps
- Alerting thresholds and SLIs
- Runbook coverage
- Deployment strategy (canary/blue-green)
- Observability instrumentation

## Output Format
### P1 Operational Gaps
| Finding | Section | Gap | Required Specification |

### P2 Operational Enhancements
| Finding | Value Add |""",
    },
    
    "integration_lead": {
        "title": "The Integration Lead",
        "domain_knowledge": """# Integration Lead Domain Knowledge

## Integration Risk Areas
Integration failures cascade. Every external dependency is a risk.

1. **API Versions**: Must be pinned to specific versions
2. **Webhook Validation**: Per-partner algorithms specified
3. **Schema Versioning**: Evolution strategy defined
4. **Data Ownership**: Entity ownership matrix explicit
5. **Circuit Breakers**: Thresholds per integration specified

## BRD vs SPEC Layer-Appropriate Classification
For BRD reviews:
- P0 at BRD: "API version pinning required" (requirement)
- Defer to SPEC: "Use v2.3.1 of Partner API" (implementation)
- P0 at BRD: "Circuit breaker pattern required" (requirement)
- Defer to SPEC: "5 failures in 60s triggers circuit" (implementation)""",
        "instructions": """You are THE INTEGRATION LEAD - external dependencies are where systems fail.

**CRITICAL**: You MUST produce a COMPLETE DETAILED analysis with specific findings for EACH integration partner. Never produce just a summary verdict. List every partner integration and assess gaps.

## Focus Areas
- API version pinning for all integrations
- Webhook signature validation per partner
- Event schema versioning strategy
- Data entity ownership matrix
- Circuit breaker configuration per partner

## Output Format (REQUIRED - Assess EACH Partner)
### P0 Integration Blockers
| Integration | Gap | Required Specification |
|-------------|-----|------------------------|
| [e.g., Partner A] | [e.g., No API version] | [e.g., Pin to v2.x] |

### P1 Integration Gaps (May Defer to SPEC)
| Finding | Section | Gap | Remediation |
|---------|---------|-----|-------------|
| [Finding] | [X.X] | [Gap] | [Fix or "Defer to SPEC"] |

### Per-Partner Assessment
For each integration partner, verify:
- [ ] API version specified
- [ ] Webhook validation defined
- [ ] Circuit breaker configured
- [ ] Fallback behavior documented

### Integration Verdict
- **Partners Assessed**: [Count]
- **Blocking Gaps**: [List]""",
    },
    
    "product_owner": {
        "title": "The Product Owner",
        "domain_knowledge": """# Product Owner Domain Knowledge

## Scope Management
Scope creep kills projects. MVP must be ruthlessly bounded.

1. **Feature-to-Goal Mapping**: Explicit traceability
2. **MVP Boundaries**: Clearly defined in/out scope
3. **User Personas**: Specific enough for trade-off decisions
4. **Acceptance Criteria**: Testable and measurable""",
        "instructions": """You are THE PRODUCT OWNER - protect the MVP scope.

## Focus Areas
- Feature alignment with business goals
- MVP boundary clarity
- User persona specificity
- Acceptance criteria testability

## Output Format
### P1 Scope Gaps
| Finding | Section | Gap | Remediation |

### Verified Complete
| Item | Location | Evidence |""",
    },
    
    "business_analyst": {
        "title": "The Business Analyst",
        "domain_knowledge": """# Business Analyst Domain Knowledge

## Requirements Quality
Ambiguous requirements cause implementation disputes.

1. **Stakeholder Coverage**: All stakeholders with roles/authority
2. **Requirements Testability**: Measurable acceptance criteria
3. **Implicit Requirements**: Must be formalized
4. **Business Rules**: Explicit and complete""",
        "instructions": """You are THE BUSINESS ANALYST - ambiguity is the enemy.

## Focus Areas
- Stakeholder identification and authority levels
- Requirements testability and measurability
- Implicit requirement formalization
- Business rule completeness

## Output Format
### P1 Requirements Gaps
| Finding | Section | Ambiguity | Required Clarification |""",
    },
    
    "fact_checker": {
        "title": "The Fact Checker",
        "domain_knowledge": """# Fact Checker Domain Knowledge

## Verification Protocol
Before claiming an item is PRESENT, verify:
1. **Explicitly stated** - Not implied or inferred
2. **Specific and actionable** - Generic mentions don't count
3. **Complete specification** - Partial coverage is a GAP""",
        "instructions": """You are THE FACT CHECKER - verify all claims against the document.

Cross-reference ALL previous persona findings against the actual document content. Flag any findings that were incorrect or where the item was actually present.

## Focus Areas
- Verify P0/P1 findings from previous personas
- Identify false positives
- Confirm true gaps with exact locations

## Output Format
### Verified Gaps (Confirmed Missing)
| Original Finding | Persona | Verification | Status |

### False Positives (Actually Present)
| Original Finding | Persona | Location Found | Exact Quote |""",
    },
    
    "chairperson": {
        "title": "The Chairperson",
        "domain_knowledge": """# Review Chairperson Domain Knowledge

## Synthesis Protocol
Consolidate all persona findings into a coherent report with:
1. **Priority Ranking**: Order by business impact
2. **Deduplication**: Merge similar findings
3. **Actionability**: Ensure each finding has clear remediation
4. **Scoring**: Compute PRD-Ready score

## Score Calculation
PRD-Ready Score = 100 - (P0 × 10) - (P1 × 3) - (P2 × 1)
- ≥85: PROCEED - Ready for next layer
- 60-84: REMEDIATION REQUIRED - Fix P0/P1 first
- <60: FUNDAMENTAL REDESIGN - Architectural issues""",
        "instructions": """You are THE CHAIRPERSON - synthesize all findings into the final report.

**CRITICAL**: You MUST produce a COMPLETE synthesis with explicit score calculation. Count ALL unique P0/P1/P2 findings from previous personas, deduplicate, and compute the exact score. Never produce just a verdict.

## Tasks
1. Review all persona findings and count unique issues
2. Deduplicate similar findings (same gap = one finding)
3. Compute final score with explicit math: 100 - (P0×10) - (P1×3) - (P2×1)
4. Generate executive summary
5. Create prioritized remediation table with complexity ratings

## Output Format (REQUIRED - Complete All Sections)
# FINAL REVIEW REPORT

## Score Calculation
- **Base Score**: 100
- **P0 Findings**: X unique × 10 = -Y points
- **P1 Findings**: X unique × 3 = -Y points
- **P2 Findings**: X unique × 1 = -Y points
- **PRD-Ready Score**: [CALCULATED]/100

## Executive Summary
* **PRD-Ready Score**: X/100
* **Recommendation**: [Proceed / Remediation Required / Fundamental Redesign]
* **P0 Count**: X | **P1 Count**: Y | **P2 Count**: Z
* **Remediation Complexity**: [1-5 scale]

## Critical Findings (P0) - Deduplicated
| ID | Finding | Source Persona | Section | Remediation |
|----|---------|----------------|---------|-------------|
| P0-1 | [Finding] | [Persona] | [X.X] | [Fix] |

## High Priority (P1) - Deduplicated
| ID | Finding | Source Persona | Section | Remediation |
|----|---------|----------------|---------|-------------|
| P1-1 | [Finding] | [Persona] | [X.X] | [Fix] |

## Remediation Priority (Top 5)
1. [Most critical with specific action and target section]

## Cross-Persona Consensus
| Persona | Verdict | Key Concerns |
|---------|---------|--------------|
| [Persona] | [PASS/FAIL] | [Summary] |""",
    },
    
    "qa_lead": {
        "title": "The QA Lead",
        "domain_knowledge": """# QA Lead Domain Knowledge

## Testing Requirements
1. **Test Coverage**: Unit, integration, E2E requirements
2. **Test Data**: Requirements for test environments
3. **Performance Testing**: Load/stress test criteria
4. **Security Testing**: Penetration test requirements""",
        "instructions": """You are THE QA LEAD - ensure testability of all requirements.

## Focus Areas
- Acceptance criteria testability
- Test environment requirements
- Performance test criteria
- Security test coverage

## Output Format
### P1 Testability Gaps
| Requirement | Gap | Required Clarification |""",
    },
    
    "ux_strategist": {
        "title": "The UX Strategist",
        "domain_knowledge": """# UX Strategist Domain Knowledge

## User Experience Areas
1. **User Flows**: Complete and logical
2. **Error States**: User-friendly handling
3. **Accessibility**: WCAG compliance
4. **Performance**: User-perceived latency""",
        "instructions": """You are THE UX STRATEGIST - advocate for user experience.

## Focus Areas
- User flow completeness
- Error message clarity
- Accessibility compliance
- Performance expectations

## Output Format
### P1 UX Gaps
| Finding | User Impact | Remediation |""",
    },
    
    "requirements_specialist": {
        "title": "The Requirements Specialist",
        "domain_knowledge": """# Requirements Specialist Domain Knowledge

## EARS Syntax Validation
1. **Ubiquitous**: "The [system] shall [action]"
2. **Event-Driven**: "When [trigger], the [system] shall [action]"
3. **Unwanted**: "If [condition], then the [system] shall [action]"
4. **State-Driven**: "While [state], the [system] shall [action]"
5. **Optional**: "Where [feature], the [system] shall [action]" """,
        "instructions": """You are THE REQUIREMENTS SPECIALIST - validate requirement structure.

## Focus Areas
- EARS syntax compliance
- Requirement atomicity
- Traceability completeness
- Ambiguity elimination

## Output Format
### P0 Syntax Violations
| Requirement ID | Issue | Corrected Form |

### P1 Clarity Issues
| Requirement ID | Ambiguity | Clarification |""",
    },
}


def get_personas_for_doc_type(doc_type: str) -> list[str]:
    """Get default personas for a document type."""
    return DEFAULT_PERSONAS.get(doc_type.lower(), DEFAULT_PERSONAS["brd"])


def build_persona_prompt(
    persona: str,
    shared_context: str,
    previous_responses: dict[str, str] = None,
    doc_type: str = "brd",
    skill_dir: Optional[Path] = None,
    project_dir: Optional[Path] = None,
) -> str:
    """
    Build a complete prompt for a persona.

    Args:
        persona: Persona name
        shared_context: Document content
        previous_responses: Dict of persona -> response from previous personas
        doc_type: Document type
        skill_dir: Optional custom skill directory for domain knowledge
        project_dir: Optional project root for project-specific skills

    Returns:
        Complete prompt string
    """
    template = PERSONA_TEMPLATES.get(persona)
    if not template:
        logger.warning(f"No template for persona: {persona}")
        return f"Review the following document:\n\n{shared_context}"

    parts = []

    # Domain knowledge - try project skills first, then skill_dir, then hardcoded
    skill_content = _load_skill_content(persona, skill_dir, project_dir)
    domain_knowledge = skill_content if skill_content else template.get("domain_knowledge", "")

    if domain_knowledge:
        parts.append("=== YOUR DOMAIN KNOWLEDGE ===")
        parts.append(domain_knowledge)
        parts.append("=== END DOMAIN KNOWLEDGE ===\n")
    
    # Expert instructions
    parts.append("==============")
    parts.append("EXPERT INSTRUCTIONS:")
    parts.append(f"You are {template['title']}.")
    parts.append(template["instructions"])
    parts.append("\n==============\n")
    
    # Verification protocol
    parts.append("## CRITICAL Verification Protocol")
    parts.append("Before claiming ANY requirement is missing, you MUST:")
    parts.append("1. Search the ENTIRE document including ALL appendices")
    parts.append("2. Check all related sections for the specification")
    parts.append("3. Only flag as missing if truly absent\n")

    # Layer-appropriate classification (v1.5.5)
    if doc_type.lower() == "brd":
        parts.append("## LAYER-APPROPRIATE FINDING CLASSIFICATION (BRD)")
        parts.append("BRD defines WHAT is required, not HOW to implement:")
        parts.append("- **P0 at BRD**: Regulatory mandates, security REQUIREMENTS, transaction safety NEEDS")
        parts.append("- **P1 (Defer to SPEC)**: Specific algorithms, config values, exact thresholds")
        parts.append("Example: 'Need idempotency mechanism' = BRD P0; 'Use UUID v4 with 24hr TTL' = SPEC detail\n")
    
    # Previous findings (for later personas)
    if previous_responses:
        parts.append("=== PREVIOUS EXPERT FINDINGS ===")
        for prev_persona, response in previous_responses.items():
            prev_title = PERSONA_TEMPLATES.get(prev_persona, {}).get("title", prev_persona)
            parts.append(f"\n### {prev_title} Findings:\n")
            # Truncate if too long
            if len(response) > 5000:
                parts.append(response[:5000] + "\n[... truncated ...]")
            else:
                parts.append(response)
        parts.append("\n=== END PREVIOUS FINDINGS ===\n")
    
    # Document content
    parts.append("=== DOCUMENT TO REVIEW ===")
    parts.append(shared_context)
    parts.append("=== END DOCUMENT ===")
    
    return "\n".join(parts)


def get_persona_title(persona: str) -> str:
    """Get display title for a persona."""
    template = PERSONA_TEMPLATES.get(persona)
    if template:
        return template["title"]
    return persona.replace("_", " ").title()


# =============================================================================
# PROJECT-SPECIFIC PERSONA LOADING
# =============================================================================
#
# CRITICAL: The PERSONA_TEMPLATES above are FRAMEWORK TEMPLATES only.
# They are used as REFERENCE for creating project-specific personas.
# For actual analysis, project-specific personas MUST be used.
#
# Project persona location:
#   {project_root}/docs/UCX/review/personas/
#   ├── architect.md
#   ├── auditor.md
#   ├── tech_lead.md
#   └── ...
# =============================================================================


class ProjectPromptNotFoundError(Exception):
    """Raised when project-specific unified prompt is not found."""

    def __init__(self, phase: str, doc_type: str, project_dir: Path):
        self.phase = phase
        self.doc_type = doc_type
        self.project_dir = project_dir
        super().__init__(
            f"Project-specific unified prompt not found for {phase}/{doc_type}. "
            f"Expected: {project_dir}/docs/UCX/{phase}/UCR_PROMPT_{doc_type.upper()}_PROJECT.md "
            f"Framework prompts cannot be used for analysis. "
            f"Create project-specific prompt using framework template as reference."
        )


# Keep for backwards compatibility
ProjectPersonaNotFoundError = ProjectPromptNotFoundError


class UnifiedPromptLoader:
    """
    Loads and parses unified project-specific prompts.

    ARCHITECTURE (Option A - Single Source of Truth):
    - ONE unified prompt file contains all persona definitions
    - Single-turn mode: Uses the full prompt as-is
    - Multi-turn mode: Extracts individual persona sections from the same file

    This ensures consistency between single-turn and multi-turn reviews.

    File location:
        {project_root}/docs/UCX/review/UCR_PROMPT_{DOC_TYPE}_PROJECT.md

    Expected format for embedded personas:
        ### N. THE PERSONA_NAME (Role Description)

        **Your stance**: ...
        **Focus**:
        - Point 1
        - Point 2

        **Output format**:
        ```
        ...
        ```

        ---
    """

    # Persona name mapping from section headers to internal names
    PERSONA_NAME_MAP = {
        "architect": ["architect", "the architect"],
        "auditor": ["auditor", "the auditor", "compliance"],
        "tech_lead": ["tech lead", "the tech lead", "technical lead"],
        "strategist": ["strategist", "the strategist"],
        "devils_advocate": ["devil's advocate", "the devil's advocate", "devils advocate"],
        "operator": ["operator", "the operator", "devops", "sre"],
        "integration_lead": ["integration lead", "the integration lead", "integration"],
        "product_owner": ["product owner", "the product owner", "po"],
        "business_analyst": ["business analyst", "the business analyst", "ba"],
        "fact_checker": ["fact checker", "the fact checker"],
        "chairperson": ["chairperson", "the chairperson", "chair"],
        "ux_strategist": ["ux strategist", "the ux strategist", "ux"],
        "qa_lead": ["qa lead", "the qa lead", "qa"],
        "requirements_specialist": ["requirements specialist", "the requirements specialist"],
    }

    def __init__(self, project_dir: Path, doc_type: str = "brd"):
        """
        Initialize with project directory and document type.

        Args:
            project_dir: Project root (containing docs/UCX/)
            doc_type: Document type (brd, prd, etc.)
        """
        self._project_dir = project_dir
        self._doc_type = doc_type.lower()
        self._review_dir = project_dir / "docs" / "UCX" / "review"
        self._skills_dir = get_project_skills_dir(project_dir)
        self._prompt_file = self._find_prompt_file()
        self._full_content: Optional[str] = None
        self._parsed_personas: dict[str, dict] = {}
        self._shared_context: Optional[str] = None

        logger.debug(
            f"UnifiedPromptLoader initialized: project={project_dir} doc_type={doc_type} "
            f"prompt_file={self._prompt_file} skills_dir={self._skills_dir}"
        )

    def _find_prompt_file(self) -> Optional[Path]:
        """Find the project-specific unified prompt file."""
        # Primary pattern: UCR_PROMPT_BRD_PROJECT.md
        primary = self._review_dir / f"UCR_PROMPT_{self._doc_type.upper()}_PROJECT.md"
        if primary.exists():
            return primary

        # Alternative patterns
        patterns = [
            f"UCR_PROMPT_{self._doc_type.upper()}_*.md",
            f"ucr_prompt_{self._doc_type}_*.md",
        ]

        for pattern in patterns:
            for f in self._review_dir.glob(pattern):
                if not f.is_symlink() and "TEMPLATE" not in f.name.upper():
                    return f

        return None

    def has_unified_prompt(self) -> bool:
        """Check if unified prompt file exists."""
        return self._prompt_file is not None and self._prompt_file.exists()

    def get_prompt_path(self) -> Optional[Path]:
        """Get path to the unified prompt file."""
        return self._prompt_file

    def load_full_prompt(self) -> str:
        """
        Load the complete unified prompt (for single-turn mode).

        Returns:
            Full prompt content

        Raises:
            ProjectPromptNotFoundError: If prompt not found
        """
        if self._full_content is not None:
            return self._full_content

        if not self.has_unified_prompt():
            raise ProjectPromptNotFoundError("review", self._doc_type, self._project_dir)

        self._full_content = self._prompt_file.read_text(encoding="utf-8")
        logger.info(f"Loaded unified prompt: {self._prompt_file} ({len(self._full_content)} chars)")
        return self._full_content

    def parse_personas(self) -> dict[str, dict]:
        """
        Parse individual persona sections from the unified prompt.

        Returns:
            Dict mapping persona name to parsed content:
            {
                "architect": {
                    "title": "THE ARCHITECT",
                    "section_number": 1,
                    "content": "...",
                    "stance": "...",
                    "focus_areas": [...],
                    "output_format": "..."
                },
                ...
            }

        Raises:
            ProjectPromptNotFoundError: If prompt not found
        """
        if self._parsed_personas:
            return self._parsed_personas

        content = self.load_full_prompt()
        self._parse_content(content)
        return self._parsed_personas

    def _parse_content(self, content: str) -> None:
        """Parse the unified prompt content into sections."""
        import re

        # Extract shared context (everything before persona sections)
        # Look for "## Persona Reviews" or first "### N. THE"
        persona_start_patterns = [
            r"##\s*Persona Reviews",
            r"###\s*1\.\s*THE\s+",
        ]

        shared_end = len(content)
        for pattern in persona_start_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                shared_end = min(shared_end, match.start())

        self._shared_context = content[:shared_end].strip()

        # Parse persona sections: ### N. THE PERSONA_NAME (Description)
        # Pattern matches: ### 1. THE ARCHITECT (Integration & Scalability)
        persona_pattern = r"###\s*(\d+)\.\s*(THE\s+)?([A-Z][A-Z\s']+?)(?:\s*\([^)]+\))?\s*\n"

        sections = list(re.finditer(persona_pattern, content, re.IGNORECASE))

        for i, match in enumerate(sections):
            section_num = int(match.group(1))
            raw_name = match.group(3).strip().lower()

            # Find the internal persona name
            internal_name = self._map_persona_name(raw_name)
            if not internal_name:
                logger.warning(f"Unknown persona in prompt: {raw_name}")
                continue

            # Extract section content (until next section or end)
            start = match.end()
            if i + 1 < len(sections):
                end = sections[i + 1].start()
            else:
                # Find "## Final Synthesis" or end
                final_match = re.search(r"\n##\s*Final Synthesis", content[start:], re.IGNORECASE)
                end = start + final_match.start() if final_match else len(content)

            section_content = content[start:end].strip()

            # Parse section components
            parsed = self._parse_persona_section(section_content, raw_name, section_num)
            self._parsed_personas[internal_name] = parsed

        logger.info(f"Parsed {len(self._parsed_personas)} personas from unified prompt")

    def _map_persona_name(self, raw_name: str) -> Optional[str]:
        """Map raw persona name from prompt to internal name."""
        raw_lower = raw_name.lower().strip()

        for internal_name, variants in self.PERSONA_NAME_MAP.items():
            if raw_lower in variants or raw_lower.replace("the ", "") in variants:
                return internal_name

        # Try direct match after cleanup
        cleaned = raw_lower.replace("the ", "").replace("'", "").replace(" ", "_")
        if cleaned in self.PERSONA_NAME_MAP:
            return cleaned

        return None

    def _parse_persona_section(self, content: str, title: str, section_num: int) -> dict:
        """Parse a single persona section."""
        import re

        result = {
            "title": f"THE {title.upper()}",
            "section_number": section_num,
            "content": content,
            "stance": "",
            "focus_areas": [],
            "output_format": "",
        }

        # Extract stance
        stance_match = re.search(r"\*\*Your stance\*\*:\s*(.+?)(?=\n\n|\n\*\*|\Z)", content, re.DOTALL)
        if stance_match:
            result["stance"] = stance_match.group(1).strip()

        # Extract focus areas (lines starting with -)
        focus_section = re.search(r"\*\*(?:Focus|BeeLocal Focus)\*\*:?\s*\n((?:\s*-[^\n]+\n?)+)", content)
        if focus_section:
            result["focus_areas"] = [
                line.strip().lstrip("-").strip()
                for line in focus_section.group(1).split("\n")
                if line.strip().startswith("-")
            ]

        # Extract output format (code block)
        output_match = re.search(r"\*\*Output format\*\*:?\s*\n```[^\n]*\n(.*?)```", content, re.DOTALL)
        if output_match:
            result["output_format"] = output_match.group(1).strip()

        return result

    def get_shared_context(self) -> str:
        """Get the shared context (non-persona parts of the prompt)."""
        if self._shared_context is None:
            self.parse_personas()
        return self._shared_context or ""

    def list_personas(self) -> list[str]:
        """List available personas in the unified prompt."""
        personas = self.parse_personas()
        # Return sorted by section number
        return sorted(personas.keys(), key=lambda p: personas[p].get("section_number", 99))

    def has_project_skills(self) -> bool:
        """Check if project-specific skills directory exists and has files."""
        if not self._skills_dir.exists():
            return False
        return any(self._skills_dir.glob("*.md"))

    def get_skill_content(self, persona: str) -> Optional[str]:
        """
        Load skill content for a persona.

        Priority: project skills > framework skills

        Args:
            persona: Persona name

        Returns:
            Skill content or None
        """
        return _load_skill_content(persona, project_dir=self._project_dir)

    def build_persona_prompt(
        self,
        persona: str,
        document_content: str,
        previous_responses: dict[str, str] = None,
    ) -> str:
        """
        Build a complete prompt for a specific persona (for multi-turn mode).

        Args:
            persona: Persona name (e.g., "architect", "auditor")
            document_content: The document to review
            previous_responses: Dict of previous persona responses

        Returns:
            Complete prompt string for this persona

        Raises:
            ProjectPromptNotFoundError: If persona not found in unified prompt
        """
        personas = self.parse_personas()

        if persona not in personas:
            raise ProjectPromptNotFoundError("review", f"{self._doc_type}/{persona}", self._project_dir)

        persona_data = personas[persona]
        shared = self.get_shared_context()

        parts = []

        # Load project-specific skill content (domain knowledge)
        skill_content = self.get_skill_content(persona)
        if skill_content:
            parts.append("=== YOUR DOMAIN KNOWLEDGE ===")
            parts.append(skill_content)
            parts.append("=== END DOMAIN KNOWLEDGE ===\n")
            logger.debug(f"Injected skill content for {persona} ({len(skill_content)} chars)")

        # Include relevant shared context (instructions, verification protocol, etc.)
        # But exclude the full document placeholder
        shared_lines = shared.split("\n")
        filtered_shared = []
        skip_until_next_section = False
        for line in shared_lines:
            if "## Document to Review" in line or "[PASTE" in line.upper():
                skip_until_next_section = True
                continue
            if skip_until_next_section and line.startswith("##"):
                skip_until_next_section = False
            if not skip_until_next_section:
                filtered_shared.append(line)

        if filtered_shared:
            parts.append("\n".join(filtered_shared))
            parts.append("\n---\n")

        # Persona-specific instructions
        parts.append(f"## YOUR ROLE: {persona_data['title']}")
        if persona_data["stance"]:
            parts.append(f"\n**Your stance**: {persona_data['stance']}\n")

        parts.append(persona_data["content"])
        parts.append("\n---\n")

        # Previous findings (for multi-turn context) with ANTI-REPETITION instructions
        if previous_responses:
            parts.append("## PREVIOUS EXPERT FINDINGS\n")
            parts.append("""**CRITICAL ANTI-REPETITION RULES:**
1. **DO NOT REPEAT** findings already identified by previous experts
2. **DO NOT SUMMARIZE** the overall document - focus ONLY on YOUR specialty area
3. **DO NOT PRODUCE** an executive summary or verdict - that's the Chairperson's job
4. **ONLY OUTPUT** findings in YOUR specific domain that are NOT already covered
5. If a finding was already identified, acknowledge it briefly: "Confirmed: [P0-X from Architect]"

**YOUR UNIQUE VALUE**: Add NEW findings in YOUR specialty area that others missed.
If there are no new findings in your domain, state: "No additional findings in [domain] beyond prior coverage."
""")

            # Create a summary of already-identified findings to prevent repetition
            parts.append("\n### Already Identified Issues (DO NOT REPEAT):\n")
            for prev_persona, response in previous_responses.items():
                prev_data = personas.get(prev_persona, {})
                prev_title = prev_data.get("title", prev_persona.replace("_", " ").title())

                # Extract just P0/P1 findings summary (not full response)
                summary = self._extract_findings_summary(response, prev_title)
                parts.append(summary)

            parts.append("\n---\n")

        # Document to review
        parts.append("## DOCUMENT TO REVIEW\n")
        parts.append(document_content)

        return "\n".join(parts)

    def _extract_findings_summary(self, response: str, persona_title: str) -> str:
        """
        Extract a brief summary of findings from a persona response.

        This creates a compact list of already-identified issues to prevent
        repetition by subsequent personas.

        Args:
            response: Full persona response text
            persona_title: Display title of the persona

        Returns:
            Compact summary of findings (P0/P1 only, ~500 chars max)
        """
        import re

        findings = []

        # Extract P0 findings (look for P0 patterns)
        p0_patterns = [
            r"\*\*P0[^*]*\*\*[:\s]*([^\n]+)",
            r"\|\s*P0[^|]*\|[^|]*\|([^|]+)",
            r"P0[:\s]+([^\n]{10,100})",
        ]

        for pattern in p0_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches[:5]:  # Limit to 5 P0s per persona
                cleaned = match.strip().strip("|").strip()
                if cleaned and len(cleaned) > 10:
                    findings.append(f"- P0: {cleaned[:100]}")

        # Extract P1 findings
        p1_patterns = [
            r"\*\*P1[^*]*\*\*[:\s]*([^\n]+)",
            r"\|\s*P1[^|]*\|[^|]*\|([^|]+)",
        ]

        for pattern in p1_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches[:3]:  # Limit to 3 P1s per persona
                cleaned = match.strip().strip("|").strip()
                if cleaned and len(cleaned) > 10:
                    findings.append(f"- P1: {cleaned[:80]}")

        if findings:
            unique_findings = list(dict.fromkeys(findings))[:8]  # Dedupe, max 8
            return f"**{persona_title}**:\n" + "\n".join(unique_findings) + "\n"
        else:
            return f"**{persona_title}**: (No P0/P1 findings extracted)\n"


# Backwards compatibility alias
ProjectPersonaLoader = UnifiedPromptLoader


def require_unified_prompt(project_dir: Path, doc_type: str) -> UnifiedPromptLoader:
    """
    Get unified prompt loader, failing if prompt not found.

    Args:
        project_dir: Project root directory
        doc_type: Document type

    Returns:
        UnifiedPromptLoader ready to use

    Raises:
        ProjectPromptNotFoundError: If unified prompt not found
    """
    loader = UnifiedPromptLoader(project_dir, doc_type)

    if not loader.has_unified_prompt():
        raise ProjectPromptNotFoundError("review", doc_type, project_dir)

    # Verify personas can be parsed
    try:
        personas = loader.parse_personas()
        required = get_personas_for_doc_type(doc_type)
        missing = [p for p in required if p not in personas]

        if missing:
            logger.warning(
                f"Some required personas not found in unified prompt: {missing}. "
                f"Available: {list(personas.keys())}"
            )

    except Exception as e:
        logger.warning(f"Could not parse personas from unified prompt: {e}")

    logger.info(
        f"Unified prompt verified: project={project_dir} doc_type={doc_type} "
        f"personas={loader.list_personas()}"
    )
    return loader


# Backwards compatibility alias
require_project_personas = require_unified_prompt


def generate_unified_prompt_template(project_dir: Path, doc_type: str = "brd") -> Path:
    """
    Generate a unified prompt template from framework templates.

    This creates a starter prompt file that should be customized for
    the specific project domain.

    Args:
        project_dir: Project root directory
        doc_type: Document type

    Returns:
        Path to generated template
    """
    review_dir = project_dir / "docs" / "UCX" / "review"
    review_dir.mkdir(parents=True, exist_ok=True)

    prompt_file = review_dir / f"UCR_PROMPT_{doc_type.upper()}_PROJECT.md"

    if prompt_file.exists():
        logger.info(f"Unified prompt already exists: {prompt_file}")
        return prompt_file

    required = get_personas_for_doc_type(doc_type)

    # Build the unified prompt template
    parts = [
        f"# UCR Prompt: Project {doc_type.upper()} Review - Layer 1",
        "",
        "## Instructions",
        "",
        f"You are an AI Expert Board conducting a Unified Context Review (UCR) of a {doc_type.upper()} document.",
        "",
        f"**Personas Applied**: {', '.join(p.replace('_', ' ').title() for p in required)}",
        "",
        "---",
        "",
        "## CRITICAL: Error Classification Philosophy",
        "",
        "**FALSE NEGATIVES ARE UNACCEPTABLE.** Missing a real issue is far worse than flagging something that turns out to be present.",
        "",
        "| Error Type | Risk Level | Consequence |",
        "|------------|------------|-------------|",
        "| **False Positive** | LOW | Extra verification during remediation - easily corrected |",
        "| **False Negative** | **CRITICAL** | Missing requirements propagate to downstream layers - expensive rework |",
        "",
        "**Rule: When in doubt, FLAG IT.**",
        "",
        "---",
        "",
        "## VERIFICATION PROTOCOL",
        "",
        "Before claiming an item is PRESENT, verify it meets ALL criteria:",
        "1. **Explicitly stated** - Not implied, inferred, or 'covered by' something else",
        "2. **Specific and actionable** - Generic mentions don't count",
        "3. **Complete specification** - Partial coverage is a GAP, not 'present'",
        "",
        "---",
        "",
        "## Persona Reviews",
        "",
    ]

    # Add persona sections
    for i, persona in enumerate(required, 1):
        template = PERSONA_TEMPLATES.get(persona, {})
        title = template.get("title", persona.replace("_", " ").title())
        instructions = template.get("instructions", "Review the document for issues.")

        parts.extend([
            f"### {i}. {title.upper()}",
            "",
            f"**Your stance**: {template.get('stance', 'Be thorough and critical.')}",
            "",
            "**Focus Areas**:",
            "- TODO: Add project-specific focus areas",
            "",
            instructions,
            "",
            "**Output format**:",
            "```",
            f"### {i}. {title.upper()}",
            "",
            "**P0 Critical**:",
            "| Finding | Section | Gap | Remediation |",
            "",
            "**P1 High**:",
            "| Finding | Section | Gap | Remediation |",
            "```",
            "",
            "---",
            "",
        ])

    # Add final synthesis section
    parts.extend([
        "## Final Synthesis",
        "",
        "After all persona reviews, produce a consolidated report.",
        "",
        "---",
        "",
        "## Document to Review",
        "",
        "[PASTE DOCUMENT CONTENT BELOW THIS LINE]",
        "",
    ])

    content = "\n".join(parts)
    prompt_file.write_text(content, encoding="utf-8")
    logger.info(f"Generated unified prompt template: {prompt_file}")

    return prompt_file


# Deprecated - use generate_unified_prompt_template instead
def generate_project_persona_templates(project_dir: Path, doc_type: str = "brd") -> None:
    """DEPRECATED: Use generate_unified_prompt_template instead."""
    logger.warning(
        "generate_project_persona_templates is deprecated. "
        "Use generate_unified_prompt_template for single-source-of-truth approach."
    )
    generate_unified_prompt_template(project_dir, doc_type)
