"""Unit tests for ucx.models.document."""

from __future__ import annotations

import pytest

from ucx.models.document import (
    ArtifactClass,
    DocumentLayer,
    LAYER_REGISTRY,
    LayerInfo,
)


class TestDocumentLayer:
    def test_values_are_lowercase(self) -> None:
        for layer in DocumentLayer:
            assert layer == layer.lower()

    def test_eight_layers_defined(self) -> None:
        assert len(DocumentLayer) == 8

    def test_expected_layer_ids(self) -> None:
        ids = {layer.value for layer in DocumentLayer}
        assert ids == {"brd", "prd", "ears", "bdd", "adr", "sys", "req", "ctr"}


class TestArtifactClass:
    def test_expected_classes(self) -> None:
        classes = {ac.value for ac in ArtifactClass}
        assert "source" in classes
        assert "validation" in classes
        assert "validation_fixed" in classes
        assert "review_report" in classes
        assert "remediation_report" in classes
        assert "unknown" in classes


class TestLayerInfo:
    def test_layer_info_is_immutable(self) -> None:
        info = LAYER_REGISTRY[DocumentLayer.BRD]
        with pytest.raises(Exception):
            info.number = 99  # frozen model should raise

    def test_layer_info_fields(self) -> None:
        info = LAYER_REGISTRY[DocumentLayer.BRD]
        assert info.layer == DocumentLayer.BRD
        assert info.number == 1
        assert info.tool_prefix == "brd"
        assert len(info.display_name) > 0


class TestLayerRegistry:
    def test_registry_covers_all_layers(self) -> None:
        for layer in DocumentLayer:
            assert layer in LAYER_REGISTRY, f"{layer} not in LAYER_REGISTRY"

    def test_layer_numbers_are_unique(self) -> None:
        numbers = [info.number for info in LAYER_REGISTRY.values()]
        assert len(numbers) == len(set(numbers))

    def test_tool_prefixes_match_layer_values(self) -> None:
        for layer, info in LAYER_REGISTRY.items():
            assert info.tool_prefix == layer.value

    def test_prd_is_layer_2(self) -> None:
        assert LAYER_REGISTRY[DocumentLayer.PRD].number == 2

    def test_ctr_is_layer_8(self) -> None:
        assert LAYER_REGISTRY[DocumentLayer.CTR].number == 8
