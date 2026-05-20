# SDD Depth Guide (v3.2)

This guide maps governance depth to the active SDD v3.2 artifact chain.

## Canonical Chain

`BRD->PRD->EARS->BDD->ADR->SPEC->TDD->IPLAN->Code`

## Depth Comparison

| Aspect | Lite | Standard | Full |
|---|---|---|---|
| Artifact count | Minimal | Moderate | Full |
| Chain usage | BRD->PRD->IPLAN | BRD->PRD->EARS->ADR->SPEC->TDD->IPLAN | BRD->PRD->EARS->BDD->ADR->SPEC->TDD->IPLAN |
| CHG gates | Optional | Optional | Required |
| Traceability | Basic | Strong | Full governance + CHG |

## CHG Gate Overlay (v3)

- `GATE-01` business/product
- `GATE-03` requirements/architecture
- `GATE-06` design/test
- `GATE-08` execution plan
- `GATE-CODE` implementation/release

## Scaling Guidance

- Start Lite for constrained scope.
- Add EARS/ADR/SPEC/TDD for stronger validation.
- Add BDD + CHG gates for regulated or high-risk programs.

## UCX Hermes Runtime Controls

Use these controls when review/remediation gates run under UCX Hermes:

- `review_mode`: `prompt_only` (default) or `saga_parallel`.
- `saga_branch_llm_enabled`: enables branch-level LLM fan-out in saga mode.
- `UCX_REVIEW_SAGA_BRANCH_LLM_PHASE`: rollout phase default (`A/B` off, `C` on without explicit flag).
- `UCX_REVIEW_SAGA_BRANCH_LLM_ENABLED`: explicit env override.
- `UCX_REVIEW_DEBUG_RAW_OUTPUTS=true`: persists redacted raw branch outputs for debugging only.

Default executor/runtime parameters:

- Review saga branch executor default: `api/openrouter`.
- Remediation executor default when omitted: `api/claude-sonnet`.
- Generation defaults: `temperature=0.2`, `top_p=0.9`, `top_k` unset, `max_output_tokens=4000`.

## References

- `ucx_flow_v3/README.md`
- `ucx_flow_v3/LAYER_REGISTRY.yaml`
- `ucx_flow_v3/CHG/`
