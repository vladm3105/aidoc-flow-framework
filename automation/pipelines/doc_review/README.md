# Automation Pipeline: Doc Review (`run_review.sh`)

The **Doc Review Pipeline** is the core testing logic for the 15-layer `docs_flow_framework`. Rather than relying on human eyesight to catch missing cross-references, architectural single-points-of-failure, or poor REST boundaries, this pipeline summons an adversarial board of 7 specialized AI personas.

It is located at: `/opt/data/docs_flow_framework/automation/pipelines/doc_review/run_review.sh`

## 1. Review (`run_review.sh`)

Summons the complete 7-persona AI Expert Board to blindly audit a system design document, score it, and synthesize a formal Audit Report.

### Usage
```bash
# General usage
bash automation/pipelines/doc_review/run_review.sh <path/to/document.md>

# Example
bash automation/pipelines/doc_review/run_review.sh docs/01_BRD/BRD-01_platform_architecture/BRD-01.0_index.md
```

### What it does:
1. Loads the expert definitions from `project_experts.yaml`.
2. Asks each of the 7 personas (Architect, QA Lead, Strategist, etc.) to review the document in isolation.
3. Passes all 7 conflicting reports to the AI Chairperson.
4. The Chairperson synthesizes a final `*_PERSONA_REVIEW_REPORT.md` saved in the same directory as the target document.

---

## 2. Remediation (`run_remediate.sh`)

Processes a generated Persona Review Report, executing automated structural fixes and converting architectural flaws into tracked GitHub Issues inside the project's governance board.

### Usage
```bash
# General usage (requires the source document for auto-apply to work)
bash automation/pipelines/doc_review/run_remediate.sh <path/to/AUDIT_REPORT> --target-doc <path/to/source_document.md>

# Example
bash automation/pipelines/doc_review/run_remediate.sh \
  docs/01_BRD/BRD-01_platform_architecture/BRD-01_PERSONA_REVIEW_REPORT_7MEMBERS.md \
  --target-doc docs/01_BRD/BRD-01_platform_architecture/BRD-01.0_index.md
```

### Options
- `--target-doc <path>`: Required if you want Step 3 (Auto-Apply) to modify the source document.
- `--dry-run`: Previews actions without hitting the AI agent, committing code, or creating GitHub issues.
- `--no-index`: Skips indexing the report into the Knowledge Base (Neo4j/RAG).
- `--no-apply`: Skips Step 3 entirely.
- `--no-issues`: Skips Step 4 (GitHub issue creation).
- `--doc-id <ID>`: Manually specify the document ID (e.g. `BRD-01`) for GitHub tags.

### Pipeline Steps:

1. **Parse (`01_parse.sh`)**: Converts the markdown audit report into a structured JSON array of remediation actions with Priorities (P0, P1, P2) and Types (`frontmatter_tag`, `content_write`, etc.).
2. **Index (`02_index.sh`)**: Embeds the report into the project Knowledge Base (skips gracefully if `KB_ENABLED=false`).
3. **Auto-Apply (`03_auto_apply.sh`)**: P0 structural quick-fixes (e.g., missing tags, missing sections) are sent to the AI agent to be patched directly into the `--target-doc`, automatically generating git commits.
4. **Create Issues (`04_create_issues.py`)**: For architectural flaws requiring human/AI extended work (`content_write`), generates GitHub Issues mapped to the Project Board with governance lifecycle labels (`experts:remediation`, `ai:ready`).
