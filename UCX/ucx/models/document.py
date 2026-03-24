"""Document type and layer data models for UCX v2."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class DocumentLayer(str, Enum):
    """SDD document layer identifiers."""

    BRD = "brd"
    PRD = "prd"
    EARS = "ears"
    BDD = "bdd"
    ADR = "adr"
    SYS = "sys"
    REQ = "req"
    CTR = "ctr"


class ArtifactClass(str, Enum):
    """Classification of a PRD or processed document artifact."""

    SOURCE = "source"
    VALIDATION = "validation"
    VALIDATION_FIXED = "validation_fixed"
    REVIEW_REPORT = "review_report"
    REMEDIATION_REPORT = "remediation_report"
    UNKNOWN = "unknown"


class LayerInfo(BaseModel):
    """Metadata about a document layer."""

    layer: DocumentLayer
    number: int
    display_name: str
    tool_prefix: str

    model_config = {"frozen": True}


LAYER_REGISTRY: dict[DocumentLayer, LayerInfo] = {
    DocumentLayer.BRD: LayerInfo(layer=DocumentLayer.BRD, number=1, display_name="Business Requirements Document", tool_prefix="brd"),
    DocumentLayer.PRD: LayerInfo(layer=DocumentLayer.PRD, number=2, display_name="Product Requirements Document", tool_prefix="prd"),
    DocumentLayer.EARS: LayerInfo(layer=DocumentLayer.EARS, number=3, display_name="EARS Requirements", tool_prefix="ears"),
    DocumentLayer.BDD: LayerInfo(layer=DocumentLayer.BDD, number=4, display_name="BDD Scenarios", tool_prefix="bdd"),
    DocumentLayer.ADR: LayerInfo(layer=DocumentLayer.ADR, number=5, display_name="Architecture Decision Records", tool_prefix="adr"),
    DocumentLayer.SYS: LayerInfo(layer=DocumentLayer.SYS, number=6, display_name="System Requirements", tool_prefix="sys"),
    DocumentLayer.REQ: LayerInfo(layer=DocumentLayer.REQ, number=7, display_name="Atomic Requirements", tool_prefix="req"),
    DocumentLayer.CTR: LayerInfo(layer=DocumentLayer.CTR, number=8, display_name="Data Contracts", tool_prefix="ctr"),
}
