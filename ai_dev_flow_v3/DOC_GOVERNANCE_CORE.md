# Document Governance — SDD v3.2

## Principles

1. **Single source of truth** — Each layer has one template. No duplicate representations.
2. **YAML-first** — All templates are `.yaml`. MD is for indexes and reference docs only.
3. **Cumulative traceability** — Each layer inherits all upstream tags; adds one.
4. **Readiness gates** — Each layer must score >=90/100 before downstream generation.
5. **No circular dependencies** — Downstream artifacts reference upstream, never the reverse.
6. **Separation of development and deployment** — Development plans produce source code, Terraform modules, Helm charts, CI/CD workflow files, schema DDL, scripts — anything authored, committed, and shipped through version control. Deployment plans handle operator-only execution of those artifacts. A development plan is complete when its artifacts are authored, committed, and green — it does NOT wait for deployment.

### Development vs Deployment Plans

Adopted 2026-04-29. Permanent plans split into two roles:

| Role | Owns | Done when |
| ---- | ---- | --------- |
| **Development plan (IPLAN)** | Source code, Terraform modules, Helm charts, CI/CD workflow files, schema DDL, scripts — anything that gets authored, committed, and shipped through `git push`. | Source code + Terraform modules + CI/CD scripts authored, committed, and green under `pre-commit run --all-files`; tests pass. |
| **Deployment plan** | Operator-only execution of those artifacts: `terraform apply`, `atlas migrate apply`, Auth0 tenant config push, Secret Manager seeding, project provisioning, image build + deploy, environment activation, acceptance/soak runs. | Artifacts applied to the target environment; acceptance/soak gates green. |

**Rule.** A development IPLAN flips to `Completed` once its source code + Terraform modules + CI/CD scripts are authored, committed, and green. **It does NOT wait for the artifacts to be deployed.** The deploy execution belongs to a separate deployment plan.

Practical effect:
- An IPLAN's validation_results entry like "ready for deployment provisioning before IMPLEMENTED flip" or "`terraform apply` pending" is **NOT** a gate on the IPLAN's status. Those gates belong on the deployment plan's phase markers.
- An IPLAN that has shipped source code + Terraform module declarations + integration tests **IS** complete from the development side, even if no `terraform apply` has run.
- Conversely, the deployment plan stays `In Progress` until the apply + acceptance steps actually execute against the target environment.

**Cross-plan obligation handoff.** When closing a development IPLAN whose artifacts depend on a deployment-plan apply step, register the obligation in `IPLAN-00_index.yaml` §deferred_items before flipping `Completed`. The IPLAN's status reflects authoring-completion; the registry entry tracks the deploy-side handoff.

## Immutability

- Published artifacts (status: Approved) must not be modified.
- Changes require a new document version or a new document ID.
- Superseded documents are marked as Deprecated/Superseded in document_control.status.

## Template Policy

- **Unified YAML only** — No `.md` templates, no `.feature` templates.
- Each layer has exactly one `{TYPE}-TEMPLATE.yaml`.
- Template fields use `_guidance` prefix for authoring instructions (not validated).
- Metadata block (`metadata:`) defines layer, schema version, and document type.

## Validation

- Layer entries must validate against `LAYER_REGISTRY.yaml`.
- Required upstream tags must be present in traceability sections.
- Element IDs must match the 4-segment hash format: `TYPE.NN.SS.xxxx`.
- Document IDs must match the format: `TYPE-NN`.

## What's Different from SDD v2

| v2 | v3.2 |
|----|------|
| 14-layer registry | 8-layer registry |
| `development_status` frontmatter | `status` field (simplified) |
| MD + YAML dual templates | YAML-only templates |
| 14-depth traceability chain | 8-depth chain |
| 5 SPEC subtypes + 6 TSPEC subtypes | Unified SPEC (L6) + TDD with test cases (L7) |
| CHG gate system | Project-level concern |
| SYS/REQ/CTR/TASKS | Cut — replaced by ADR/BDD-spec_trace/SPEC inline/IPLAN |
