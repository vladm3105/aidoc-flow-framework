# Workflow Integration Guide

## Overview

Maps governance workflows to SDD v3 artifact lifecycle.

Canonical chain:
`BRD->PRD->EARS->BDD->ADR->SPEC->TDD->IPLAN->Code`

## Layer-to-Workflow Mapping

| SDD v3 Artifact | Governance Activity | Workflow Surface |
|---|---|---|
| BRD/PRD | Scope and intent alignment | artifact validation |
| EARS/BDD/ADR | requirement and architecture checks | artifact validation + review |
| SPEC/TDD | implementation and test readiness | CI + QA preparation |
| IPLAN | issue execution plan | agent dispatch + issue workflow |

## Deprecated

Legacy TASKS-sync workflow references are deprecated and removed from active runbooks.
