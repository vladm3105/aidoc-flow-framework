# Batch PRD Generation from Validated BRDs

Reference for generating 7-9 PRDs efficiently after BRD layer is complete and validated.

## Trigger

User says: "start PRD generation" or "generate PRDs" after 01_BRD layer is complete.

## Workflow

### Step 1: Pre-flight Checks
```
sdd_preflight(context="create")
sdd_create_build(doc_type="prd", layer="02_PRD", template="02_PRD-TEMPLATE.yaml")
```
If templates missing: `sdd_init(project_path)` then retry.

### Step 2: Planning Gate
Create `plans/PLAN-NNN_prd-generation.md` covering:
- Which BRDs → which PRDs (1:1 mapping)
- Priority order (umbrella first, highest-value feature second)
- Batch size (umbrella separate, features batched)
- Validation gate (all PRDs validated before proceeding)
Get human approval. Do NOT start generation without explicit approval.

### Step 3: Umbrella PRD (detailed)
Map BRD-01 → PRD-01 with full 15-section content:
- Business objectives → product KPIs and success metrics
- 12 FRs → 7 core capabilities with acceptance criteria
- Constraints → assumptions and dependencies
- Build user stories, customer-facing content, launch gates
Target: 500+ lines

### Step 4: Feature PRDs (full decomposition — NOT lightweight)
For BRD-02 through BRD-09:

**CRITICAL RULE**: Each feature PRD MUST decompose ALL BRD functional requirements
into individual core capabilities. A PRD with one generic capability per BRD is a
placeholder stub — UNBUILDABLE, REJECTED BY ALL REVIEWERS. See tradegent-cc
session 2026-05-07: all 5 persona reviewers (system-architect, security-auditor,
technical-lead, product-owner, chaos-engineer) independently flagged 7 stub PRDs
as blocking defects. Fact-checker confirmed 10/10 P0 claims with zero false positives.

Correct pattern (what passed):
- Read each BRD's functional_requirements.requirements[] array
- For EACH requirement, create a PRD core_capability with proper hash ID
- Build user stories by decomposing the first 4-5 FRs into "As a [role], I want [capability] so that [benefit]"
- Each PRD must have 3-7 core capabilities (not 1), 3-5 user stories (not 1)
- Populate ALL 15 sections with domain-specific content from the BRD
- diagram_contract must be populated (not empty {}) with containers and data_flows
- User journey diagrams MUST include alt/else branches for error/edge paths
- Error messages must be feature-specific with actionable guidance (not generic "Action failed, retrying")
- adr_topic_elaboration must be present in traceability section
- Target: 370-450 lines per feature PRD (not 233)

```python
import yaml, hashlib, re, subprocess

def make_id(doc_type, doc_num, section_num, desc):
    inp = f"{doc_type}:{doc_num}:{section_num}:{desc}"[:200]
    h = hashlib.sha256(inp.encode()).hexdigest()[:4]
    return f"{doc_type}.{doc_num:02d}.{section_num:02d}.{h}"

# Decompose ALL BRD FRs into PRD capabilities
caps = []
frs = brd['functional_requirements']['requirements']
for i, fr in enumerate(frs):
    caps.append({
        'id': make_id('PRD', num, 9, fr['title']),
        'name': fr['title'],
        'description': fr['description'][:200],
        'priority': 'P1' if i < max(1, len(frs)//2) else 'P2',
        'acceptance_criteria': [{
            'id': make_id('PRD', num, 9, fr['description'][:80]),
            'criterion': fr['description'][:200],
            'target': '>=95%'
        }],
        'brd_reference': f"@brd: BRD.{num:02d}.07.{make_id('BRD', num, 7, fr['title'])[-4:]}"
    })

# Build user stories from first 5 FRs
stories = []
for i, fr in enumerate(frs[:5]):
    stories.append({
        'id': make_id('PRD', num, 8, fr['title']),
        'role': 'Portfolio Supervisor',
        'want': fr['title'],
        'so_that': re.sub(r'^(The system shall|Ensure|Must|Will)\s+', '', fr['description'])[:120],
        'priority': 'P1' if i < 3 else 'P2',
        'acceptance_criteria': [f'System automatically {feature_name.lower()} without operator intervention'[:150]]
    })

# diagram_contract must be populated inline (not empty {})
# Build with containers list + data_flows list
diagram_contract = {
    'containers': [
        {'name': 'User Interface', 'type': 'Web Dashboard', 'interactions': ['View', 'Configure', 'Override']},
        {'name': f'{feature_name} Engine', 'type': 'Service', 'interactions': ['Fetch data', 'Process rules', 'Generate output']},
        {'name': 'Broker API', 'type': 'External', 'interactions': ['Market data', 'Order execution']}
    ],
    'data_flows': [
        {'from': 'User Interface', 'to': f'{feature_name} Engine', 'data': 'Configuration'},
        {'from': f'{feature_name} Engine', 'to': 'Broker API', 'data': 'Data requests, orders'},
        {'from': 'Broker API', 'to': f'{feature_name} Engine', 'data': 'Options chains, quotes, fills'},
        {'from': f'{feature_name} Engine', 'to': 'User Interface', 'data': 'Results, alerts'}
    ]
}
```

### Section Checklist Per Feature PRD

Every feature PRD must have:

| Section | Minimum | Correct (not this) |
|---------|---------|---------------------|
| core_capabilities | 3-7 entries (one per BRD FR) | NOT 1 generic entry with "All BRD acceptance criteria met" |
| user_stories.stories | 3-5 stories with genuine benefit | NOT 1 story: "I want automated feature to save time" |
| diagram_contract | Populated containers[] + data_flows[] | NOT empty {} |
| user_journey.diagram | alt/else branches for error paths | NOT linear 4-step without error handling |
| error_messages | 2-4 feature-specific with guidance | NOT generic "Action failed, retrying — monitor dashboard" |
| adr_topic_elaboration | At least 1 topic with options | NOT absent |
| glossary.terms | 3-6 domain terms beyond PRD/MVP/KPI | NOT 1 term: "TradeGent: autonomous trading agent" |
| mvp_hypothesis | Feature-specific belief + validation | NOT "We believe users will benefit from automated [feature]" |
| out_of_scope | 2-3 specific exclusions with rationale | NOT "Advanced features deferred to next cycle" |
| diagrams.items | At least 1 with specific source description | NOT generic "C4-L2 description" |

### Step 5: Validation
```
for prd in PRD-01 through PRD-09:
    sdd_validate(doc_type="prd", document=prd, layer="02_PRD")
```
All must pass 0 errors, 0 warnings.

### Step 6: Next Action Gate
```
sdd_next_action(document="02_PRD")
```
Confirm current_stage="created", next_action="validate" or "review".

## Key Mapping Rules

| BRD Section | PRD Section | Mapping |
|-------------|-------------|---------|
| executive_summary.overview | executive_summary.overview | Direct copy |
| business_objectives.goals[] | goals_and_objectives.primary[] | Goal → goal, metric → metric, target → target |
| functional_requirements.requirements[] | functional_requirements.core_capabilities[] | FR title → capability name, FR description → capability description, AC from FR → AC in capability |
| constraints_and_assumptions.constraints[] | constraints_and_assumptions.constraints[] | Direct copy with id re-prefixing |
| constraints_and_assumptions.assumptions[] | constraints_and_assumptions.assumptions[] | Direct copy |
| risk_management.risks[] | risk_assessment.risks[] | Direct copy with id re-prefixing |
| traceability | traceability | BRD reference updated to @brd: BRD-NN, discoverability updated to PRDs |

## Common PRD Validation Issues

1. **Diagrams.items missing** — always add top-level `diagrams` with at least one `items[]`
2. **Metadata tags count** — max 1 tag (same as BRD). Drop `layer-2-artifact`; keep only `prd-document`.
3. **Comparison operator YAML errors** — post-process to quote `>=`, `<=`, `>`, `<` values
4. **Placeholder-stub PRDs (BLOCKING)** — a feature PRD with 1 generic capability is rejected by all reviewers. Must decompose every BRD FR into a PRD capability. See checklist above for the minimum per PRD.
5. **Empty diagram_contract** — `diagram_contract: {}` is insufficient. Must contain `containers[]` + `data_flows[]`.
6. **Missing adr_topic_elaboration** — traceability section must elaborate BRD Section 8 ADR topics with options for evaluation.

## Files

- Output: `02_PRD/PRD-01.yaml` through `PRD-09.yaml`
- Plan: `plans/PLAN-NNN_prd-generation.md`
