---
title: "BRD Archived Documents"
tags:
  - index-document
  - layer-1-artifact
  - shared-architecture
custom_fields:
  document_type: readme
  artifact_type: BRD
  layer: 1
  priority: shared
---

# BRD Archived Documents

## Purpose

This directory contains archived Business Requirements Documents (BRDs) that have been superseded, deprecated, or are no longer actively used but retained for historical reference.

## When to Archive BRDs

Archive a BRD when:

- **Superseded**: Replaced by a newer BRD with updated business requirements
- **Project Cancelled**: Business initiative cancelled or postponed indefinitely
- **Scope Changed**: Business requirements significantly changed, requiring new BRD
- **Historical Reference**: Completed project but requirements kept for reference

## Archive Process

When archiving a BRD:

1. **Update Status**: Mark BRD status as "Archived" in main document
2. **Add Archive Date**: Document when and why it was archived
3. **Move File**: Move from main BRD directory to this archived/ subdirectory
4. **Update Index**: Update `BRD-00_index.md` to reflect archived status
5. **Preserve Links**: Ensure downstream documents (PRD, EARS) note the archival

## Archive Format

Archived BRD filenames maintain original format with archive date:

```
BRD-NN_{original_slug}_ARCHIVED_YYYYMMDD.md
```

Example:
- Original: `BRD-03_mobile_app_features.md`
- Archived: `BRD-03_mobile_app_features_ARCHIVED_20251113.md`

## Archived Documents

Currently no archived BRDs.

When BRDs are archived, they will be listed here with:
- Original BRD ID and title
- Archive date and reason
- Superseding document (if applicable)
- Link to original file

---

**Directory Purpose**: Historical BRD archive
**Last Updated**: 2025-11-13
**Maintainer**: [Project Team]
