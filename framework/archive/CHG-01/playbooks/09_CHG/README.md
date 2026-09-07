# 09_CHG — Playbooks

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-09-07 |
| Author | Framework Maintainer |
| Framework Version | 0.52.0 |


## Purpose

Layer-specific review playbooks for the SDD framework. Each playbook defines
role-based workflows and checklists for the review team.

## Roles

| Role | Purpose |
|------|---------|
| See files in this directory | Role-specific checklists and workflows |

## Usage

Each role file is a self-contained playbook that an AI agent or human reviewer
can follow to perform layer-specific validation.

## Files

**Review lenses** (persona-specific checklists for CHG artifact review):
- architect.md
- auditor.md
- chaos_engineer.md
- integration_lead.md
- operator.md
- security_engineer.md

**Process playbooks** (execution guides for specific CHG workflows):
- gate_spec_change.md — Step-by-step process for GATE-SPEC framework self-changes
- document_control.md — Document Control lifecycle management (GD-24)
