# PLAN-007 Implementation Checklist

**Plan**: PLAN-007_sys_layer_unification.md
**Status**: Complete
**Date**: 2026-03-29

---

## Pre-Flight

- [ ] Baseline tests: `___` passed, `___` failed
- [ ] Read 6 source files

---

## Phase 2: Create SYS-TEMPLATE.yaml

- [ ] 12 sections + glossary, c4_level: component, diagram tags: c4-l3/dfd-l3
- [ ] req_ready_score (drop ears_ready_score)
- [ ] Old IDs: SYS.NN.01.SS→SYS.NN.04.xxxx, SYS.NN.02.SS→SYS.NN.05.xxxx
- [ ] Old upstream: @adr: ADR-NN → @adr: ADR.NN.03.xxxx
- [ ] Validate YAML

## Phase 3: Archive + Phase 4: Index + Phase 5: README + Phase 6: mcp_ucx

- [ ] Archive 17+ files + scripts/ + examples/ + 2 backups
- [ ] Update SYS-00_index.md refs
- [ ] Create new README (~90 lines)
- [ ] Copy to mcp_ucx, remove old
- [ ] Update BRD downstream SYS description (stale ref)

## Phase 8: Validation + Docs

- [ ] Tests pass, template resolves, changelog + roadmap updated
