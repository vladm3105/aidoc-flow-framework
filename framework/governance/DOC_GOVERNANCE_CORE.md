# Document Governance — SDD

## Principles

1. **Single source of truth** — Each layer has one template. No duplicate representations.
2. **YAML-first** — All templates are `.yaml`. MD is for indexes and reference docs only.
3. **Necessary-upstream traceability** — Each layer cites only its `required_tags` (`LAYER_REGISTRY.yaml`), not the cumulative closure of every upstream layer; deeper lineage is transitive.
4. **Readiness gates** — Each layer must score >=90/100 before downstream generation.
5. **No circular dependencies** — Downstream artifacts reference upstream, never the reverse.
6. **Separation of development and deployment** — Development plans produce source code, Terraform modules, Helm charts, CI/CD workflow files, schema DDL, scripts — anything authored, committed, and shipped through version control. Deployment plans handle operator-only execution of those artifacts. A development plan is complete when its artifacts are authored, committed, and green — it does NOT wait for deployment.
7. **Token-efficient authoring** — Documents must be **precise and complete**, not **detailed and exhaustive**. Completeness comes from covering every required template section, not from prose volume. Authoring voice, form preferences, and size targets are defined in [`AUTHORING_STYLE.md`](AUTHORING_STYLE.md); every creation and audit engine loads it alongside the layer template.
8. **Change-of-record discipline** — Every change must keep its documents-of-record in sync within the same PR. A doc-of-record is any document whose content is the durable answer to "what state is the project in" — `CHANGELOG`, `ROADMAP`, `README`, `PARITY`, `TAGGING`, `DECISIONS`, the handoff log, and the project memory (`CLAUDE.md`). No catch-up "doc-refresh" PR may follow a change; the doc updates ship in the change's own PR. Enforcement is two-tier: (a) **mechanical** — version-reference propagation runs automatically on commit (`scripts/sync-version-refs.sh` re-syncs every doc that quotes a `VERSION` file when that file changes); (b) **semantic** — a warning hook (`scripts/check-docs-updated.sh`) flags likely-stale docs when a commit touches code/spec/skills without touching a doc-of-record. The contributor authors the semantic content (changelog entry text, roadmap bullet, decision rationale, handoff narrative); the hook decides whether to remind. See [`../../CONTRIBUTING.md`](../../CONTRIBUTING.md#documentation-discipline--update-docs-of-record-per-pr) §Documentation discipline for the per-change-category matrix.
9. **Example-driven / project-driven framework improvement** — Examples are the system-under-test, and every consumer project applying the framework is an additional empirical test. Friction discovered during use (lint-rule misfires, harness flag absences, engine prose contradicting the spec, sync-script gotchas, missing convenience features) is **NEW knowledge about the framework itself** and is captured immediately, not held in personal memory. The capture mechanism is a two-tier feedback pipeline defined in [`FRAMEWORK_FEEDBACK_LOG.md`](FRAMEWORK_FEEDBACK_LOG.md): (a) **Tier 1 — consumer project** keeps a `framework-feedback-log.md` at project root recording every framework friction it hits; (b) **Tier 2 — framework repo** aggregates into `plans/FRAMEWORK-TODO.md`. Without the pipeline, learning evaporates between sessions and the next project rediscovers the same pain. **A backlog file is a capture queue, not a publication channel:** a Tier-2 entry that is actionable by someone other than its finder, reproducible at `file:line` with a fix shape, or user-visible ALSO gets an issue on the framework's tracker, linked both ways and closed on the same merge SHA (`FRAMEWORK_FEEDBACK_LOG.md` §"Tier 2 → the tracker"). A file inside the framework repo is read only by a session already inside that repo — never by the consumers a gap affects.

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

## Security

- Artifacts are agent-authored from inputs the agent does not control. Every
  agent-authored artifact passes the `SECURITY_REVIEW.md` checks — no embedded
  secrets, no instruction obeyed from external/untrusted content, traceable
  provenance for promotions, and sanitized active content. A failed check is a
  blocking finding, not a score deduction.

## Governance Baseline

| Governance Area | Standard |
|----|------|
| Layer registry | 8-layer registry |
| Lifecycle status field | `status` |
| Template format | YAML-only templates |
| Traceability depth | 8-depth chain |
| Specification and testing | Unified SPEC (L6) + TDD with embedded test cases (L7) |
| Change governance | CHG project-level overlay |
