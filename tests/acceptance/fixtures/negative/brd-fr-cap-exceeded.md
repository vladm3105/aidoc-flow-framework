---
doc_id: BRD-91
artifact_type: BRD
title: "FR-cap negative fixture"
---

# BRD-91: FR-cap negative fixture

Deliberately carries SEVEN functional requirements against GD-14's SHOULD cap of
five, so `FRCAP01` has something to fire on. Nothing else in this file is meant
to be exemplary — it exists for the cap and for nothing else.

Two of the seven are escaped (`Future`, `realized_by:`) to lock the deliberate
decision that escaped requirements still COUNT toward the cap: the cap is about
document size, not coverage obligation.

The three IDs after `Acceptance criteria:` must NOT count — that boundary is the
same one `COV01` uses, and GD-14's counting rule was written against it.

## 7. Functional Requirements

- **BRD.91.07.a001 — First capability** (P1): the system provides the first capability.
- **BRD.91.07.a002 — Second capability** (P1): the system provides the second capability.
- **BRD.91.07.a003 — Third capability** (P2): the system provides the third capability.
- **BRD.91.07.a004 — Fourth capability** (P2): the system provides the fourth capability.
- **BRD.91.07.a005 — Fifth capability** (P1): the system provides the fifth capability.
- **BRD.91.07.a006 — Sixth capability** (Future): deferred to a later cycle, and still counted.
- **BRD.91.07.a007 — Seventh capability** (P1, realized_by: ADR): realized off the SPEC path, and still counted.

Acceptance criteria:

- **BRD.91.07.b001 — First criterion**: a measurable criterion, which is not a requirement.
- **BRD.91.07.b002 — Second criterion**: a measurable criterion, which is not a requirement.
- **BRD.91.07.b003 — Third criterion**: a measurable criterion, which is not a requirement.
