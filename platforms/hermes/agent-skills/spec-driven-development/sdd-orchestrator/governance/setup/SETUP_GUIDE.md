# SDD Framework Setup Guide

## Baseline

Use SDD v3 templates and governance defaults from `framework/`.

Canonical chain:
`BRD->PRD->EARS->BDD->ADR->SPEC->TDD->IPLAN->Code`

## Quick Setup

1. Copy framework files
2. Replace placeholders in governance docs/configs
3. Configure GitHub labels/project board
4. Configure CI/CD secrets and environments
5. Validate governance configuration

## Required Checks

- No active references to legacy framework roots
- IPLAN template available in `governance/plans/IPLAN-TEMPLATE.md`
- QA strategy references TDD/BDD model
