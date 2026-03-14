# DEPRECATED

This directory is deprecated as of UCX v1.7.2.

Skill files have been consolidated into `/UCX/skills/` (project root).

The consolidated skills contain both:
- **Domain knowledge** (CAP theorem, OWASP, failure modes, etc.)
- **Review metadata** (scoring weights, tags, checklists)

## Migration

All persona skills are now in:
```
/opt/data/docs_flow_framework/UCX/skills/
├── architect.md
├── auditor.md
├── business_analyst.md
├── chairperson.md
├── chaos_engineer.md
├── fact_checker.md
├── integration_lead.md
├── operator.md
├── product_owner.md
├── qa_lead.md
├── requirements_specialist.md
├── strategist.md
├── tech_lead.md
└── ux_strategist.md
```

## Code References

- `SkillLoader` defaults to `/UCX/skills/`
- `build_persona_prompt()` uses `/UCX/skills/`

This directory will be removed in a future version.
