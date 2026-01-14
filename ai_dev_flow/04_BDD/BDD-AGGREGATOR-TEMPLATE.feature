# =============================================================================
# BDD Aggregator Template (Redirect Stub)
# =============================================================================
#
# File: BDD-NN.SS.00_{slug}.feature
# Pattern: ^BDD-\d{2,}\.\d+\.00_[a-z0-9_]+\.feature$
# Use when: Organizing multiple subsections under one section
#
# =============================================================================

# Traceability Tags
@redirect
@section: N.S.00
@parent_doc: BDD-NN
@index: BDD-NN.0_index.md

Feature: BDD-NN.SS: [Section Name] (Aggregator)

  This is a redirect stub. Test scenarios are in subsections:
  - BDD-NN.SS.01_{slug}.feature - [Brief description of subsection 1]
  - BDD-NN.SS.02_{slug}.feature - [Brief description of subsection 2]
  - BDD-NN.SS.03_{slug}.feature - [Brief description of subsection 3]
  - BDD-NN.SS.04_{slug}.feature - [Brief description of subsection 4]

  # Section Context
  #
  # This section was split into multiple subsections due to:
  # - Size: Section exceeded 500-line limit
  # - Scenario count: Section exceeded 12-scenario limit
  # - Logical grouping: Different aspects of functionality
  #
  # All executable scenarios are in numbered subsections (.01, .02, .03, etc.)
  # This aggregator file serves as navigation hub and provides section overview

Background:
  Given the system timezone is "America/New_York"
  # No scenarios in aggregator - redirect only

# =============================================================================
# AGGREGATOR GUIDELINES
# =============================================================================
#
# **Purpose**:
# - Navigation hub for multiple subsections
# - Provides section overview and context
# - NO executable scenarios (0 scenarios)
# - @redirect tag REQUIRED
#
# **When to Create**:
# - Parent section split into 5+ subsections
# - Need clear navigation structure
# - Subsections represent different aspects of same feature area
#
# **Requirements**:
# - @redirect tag MUST be present
# - Fixed subsection: .00 (always)
# - 0 scenarios (no executable tests)
# - List all subsections with brief descriptions in Feature description
# - Background section allowed but no scenario blocks
#
# **File Organization**:
# - Aggregator: BDD-NN.SS.00_{slug}.feature (this file)
# - Subsections: BDD-NN.SS.01_{slug}.feature, BDD-NN.SS.02_{slug}.feature, etc.
# - Index: BDD-NN.0_index.md (references aggregator and subsections)
#
# **Metadata**:
# - @redirect tag is MANDATORY
# - @section: Parent section + .00 (e.g., 2.12.00)
# - @parent_doc: Parent BDD suite (e.g., BDD-02)
# - @index: Index file reference (e.g., BDD-02.0_index.md)
#
# **Validation**:
# - Validator checks for @redirect tag
# - Validator ensures 0 scenarios
# - Validator verifies .00 subsection number
#
# =============================================================================

# Document Path: BDD/BDD-NN.SS.00_{slug}.feature
# Framework: AI Dev Flow SDD
# Layer: 4 (BDD - Behavior-Driven Development)
# Template Version: 1.0
# Last Updated: 2025-12-27
