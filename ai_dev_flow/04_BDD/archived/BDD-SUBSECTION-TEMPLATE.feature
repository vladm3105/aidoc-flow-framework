# =============================================================================
# BDD Subsection Template
# =============================================================================
#
# File: BDD-NN.SS.mm_{slug}.feature
# Pattern: ^BDD-\d{2,}\.\d+\.\d{2}_[a-z0-9_]+\.feature$
# Use when: Section requires splitting (each subsection ≤500 lines)
#
# =============================================================================

# Traceability Tags
@section: N.S.m
@parent_section: N.S
@parent_doc: BDD-NN
@index: BDD-NN.0_index.md
@brd:BRD.XX.YY.ZZ
@prd:PRD.AA.BB.CC
@ears:EARS.NN.SS.RR

Feature: BDD-NN.SS.mm: [Subsection Feature Name]
  As a [user role/persona]
  I want [specific capability within parent section scope]
  So that [focused business value for this subsection]

  # Subsection Context
  #
  # This subsection is part of BDD-NN.SS: [Parent Section Name]
  # Focus: [1-2 sentences on what this subsection covers]
  #
  # Parent section was split due to size (>500 lines) or scenario count (>12 scenarios)

Background:
  # Inherits preconditions from parent section
  Given the system timezone is "America/New_York"
  And the current time is "09:30:00" in "America/New_York"
  And the system is in "active" state
  And [parent section preconditions if needed]

# =============================================================================
# SUBSECTION SCENARIOS
# =============================================================================

@subsection
@scenario_id:BDD.NN.S.mm.01
Scenario: [Subsection scenario 1 name]
  # Purpose: [Brief description]
  # Upstream: @ears:EARS.NN.SS.RR
  
  Given [precondition specific to this subsection]
  When [action within subsection scope]
  Then [expected outcome]
  And it SHALL complete WITHIN @threshold:PRD.NN.category.timeout_key

@subsection
@scenario_id:BDD.NN.S.mm.02
Scenario: [Subsection scenario 2 name]
  Given [precondition]
  When [action]
  Then [outcome]

# Additional scenarios (up to 12 total per subsection)

# =============================================================================
# SUBSECTION GUIDELINES
# =============================================================================
#
# **Subsection Purpose**:
# - Split from parent section (BDD-NN.SS) when it exceeded 500 lines or 12 scenarios
# - Each subsection focuses on a logical subset of parent functionality
# - Maintains same hard limits: ≤500 lines, ≤12 scenarios
#
# **Numbering**:
# - Subsection number: .SS.mm format (e.g., .24.01, .24.02)
# - Scenario IDs: BDD.NN.S.mm.SEQ (e.g., BDD.02.24.01.01, BDD.02.24.01.02)
# - Sequential from 01 within parent section
#
# **Metadata Requirements**:
# - @section: Parent section + subsection (e.g., 2.24.01)
# - @parent_section: Parent section number (e.g., 2.24)
# - @parent_doc: Parent BDD suite (e.g., BDD-02)
# - @index: Index file reference (e.g., BDD-02.0_index.md)
#
# **When to Create Subsections**:
# - Parent section exceeds 500 lines
# - Parent section exceeds 12 scenarios
# - Logical grouping within parent section (e.g., different quality attributes)
#
# **Aggregator Coordination**:
# - If parent has many subsections (5+), consider aggregator: BDD-NN.SS.00_{slug}.feature
# - Aggregator provides redirect stub with @redirect tag and 0 scenarios
#
# =============================================================================

# Document Path: 04_BDD/BDD-NN.SS.mm_{slug}.feature
# Framework: AI Dev Flow SDD
# Layer: 4 (BDD - Behavior-Driven Development)
# Template Version: 1.0
# Last Updated: 2025-12-27
