# `chain-trace-broken/` — mid-cascade reference to deleted upstream

This fixture is a partial chain (`01_BRD/` + `02_PRD/`) where the PRD
references an upstream BRD element-ID that exists nowhere in the chain.

| File | What's broken |
|---|---|
| `01_BRD/BRD-01.md` | Well-formed BRD with element-ID `BRD.01.01.aaaa` |
| `02_PRD/PRD-01.md` | References `@brd: BRD.01.99.f7f7` — well-formed 4-segment ID, but no BRD section publishes that hash |

`sdd_doc_lint` won't flag this (the ID is structurally valid).
`doc-validator` (live LLM) must report the broken trace.
