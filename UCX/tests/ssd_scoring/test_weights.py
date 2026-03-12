"""
Unit tests for UCX scoring weights module.

Tests weight loading, validation, and configuration merging.
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from ucx.scoring import (
    DEFAULT_WEIGHTS,
    DocumentTypeWeights,
    ScoringConfigError,
    get_all_document_types,
    load_weights,
    validate_config_file,
)


class TestDefaultWeights:
    """Tests for default weight definitions."""

    def test_all_document_types_have_defaults(self):
        """All expected document types have default weights."""
        expected = ["brd", "prd", "ears", "bdd", "adr", "sys", "req", "spec", "ctr", "tasks", "tspec"]
        for doc_type in expected:
            assert doc_type in DEFAULT_WEIGHTS, f"Missing defaults for {doc_type}"

    def test_default_weights_sum_to_100(self):
        """Each document type's weights sum to 100%."""
        for doc_type, weights in DEFAULT_WEIGHTS.items():
            total = sum(weights.values())
            assert abs(total - 1.0) < 0.001, f"{doc_type} weights sum to {total*100}%"

    def test_all_categories_present(self):
        """Each document type has all 8 categories."""
        expected_categories = [
            "functional", "quality", "compliance", "constraints",
            "integration", "acceptance", "risk", "architecture"
        ]
        for doc_type, weights in DEFAULT_WEIGHTS.items():
            for cat in expected_categories:
                assert cat in weights, f"{doc_type} missing category {cat}"


class TestLoadWeights:
    """Tests for load_weights function."""

    def test_load_brd_weights(self):
        """Load BRD weights successfully."""
        weights = load_weights("brd")
        assert weights.doc_type == "brd"
        assert "functional" in weights.categories
        assert weights.categories["functional"].weight == 0.25

    def test_load_unknown_doc_type_uses_brd(self):
        """Unknown document type falls back to BRD defaults."""
        weights = load_weights("unknown_type")
        assert weights.doc_type == "unknown_type"
        # Should use BRD defaults
        assert weights.categories["functional"].weight == 0.25

    def test_weights_include_thresholds(self):
        """Loaded weights include thresholds."""
        weights = load_weights("brd")
        assert weights.thresholds.pass_threshold == 85
        assert weights.thresholds.warn_threshold == 70
        assert weights.thresholds.fail_threshold == 0

    def test_category_weight_properties(self):
        """CategoryWeight has correct properties."""
        weights = load_weights("brd")
        func = weights.categories["functional"]
        assert func.weight == 0.25
        assert func.weight_percent == 25.0
        assert func.max_deduction == 25


class TestWeightValidation:
    """Tests for weight validation."""

    def test_validate_valid_weights(self):
        """Valid weights pass validation."""
        weights = load_weights("brd")
        # Should not raise
        weights.validate()

    def test_validate_invalid_weights_raises(self):
        """Invalid weights raise ScoringConfigError."""
        weights = load_weights("brd")
        # Corrupt the weights
        weights.categories["functional"].weight = 0.50  # type: ignore[misc]

        with pytest.raises(ScoringConfigError) as exc_info:
            weights.validate()
        assert "100%" in str(exc_info.value)


class TestConfigFileValidation:
    """Tests for validate_config_file function."""

    def test_validate_valid_config(self):
        """Valid config file passes validation."""
        config = {
            "defaults": {
                "categories": {
                    "functional": {"weight": 0.25},
                    "quality": {"weight": 0.15},
                    "compliance": {"weight": 0.20},
                    "constraints": {"weight": 0.10},
                    "integration": {"weight": 0.10},
                    "acceptance": {"weight": 0.10},
                    "risk": {"weight": 0.05},
                    "architecture": {"weight": 0.05},
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            f.flush()
            errors = validate_config_file(Path(f.name))

        assert len(errors) == 0

    def test_validate_invalid_weight_range(self):
        """Invalid weight values are caught."""
        config = {
            "document_types": {
                "brd": {
                    "categories": {
                        "functional": {"weight": 1.5}  # Invalid: > 1.0
                    }
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            f.flush()
            errors = validate_config_file(Path(f.name))

        assert len(errors) > 0
        assert "brd.functional" in errors[0]

    def test_validate_malformed_yaml(self):
        """Malformed YAML is caught."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            f.flush()
            errors = validate_config_file(Path(f.name))

        assert len(errors) > 0
        assert "YAML" in errors[0]


class TestGetAllDocumentTypes:
    """Tests for get_all_document_types function."""

    def test_returns_all_types(self):
        """Returns all supported document types."""
        types = get_all_document_types()
        assert "brd" in types
        assert "prd" in types
        assert "ears" in types
        assert len(types) == 11


class TestWeightOverrides:
    """Tests for project-specific weight overrides."""

    def test_override_merging(self):
        """Project overrides merge with defaults."""
        # Create a temporary override config
        # When increasing functional by 0.05, decrease compliance by 0.05 to maintain 100%
        override_config = {
            "document_types": {
                "brd": {
                    "categories": {
                        "functional": {"weight": 0.30},  # Override default 0.25 (+0.05)
                        "compliance": {"weight": 0.15},  # Override default 0.20 (-0.05)
                    }
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(override_config, f)
            f.flush()

            weights = load_weights("brd", project_config_path=Path(f.name))

        # Should have override values
        assert weights.categories["functional"].weight == 0.30
        assert weights.categories["compliance"].weight == 0.15
        # Other categories should have defaults
        assert weights.categories["quality"].weight == 0.15

    def test_keyword_append(self):
        """Keywords can be appended to defaults."""
        override_config = {
            "defaults": {
                "categories": {
                    "compliance": {
                        "keywords_append": ["CustomTerm1", "CustomTerm2"]
                    }
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(override_config, f)
            f.flush()

            weights = load_weights("brd", project_config_path=Path(f.name))

        # Should include both default and appended keywords
        keywords = weights.categories["compliance"].keywords
        assert "CustomTerm1" in keywords
        assert "CustomTerm2" in keywords
        # And still have defaults
        assert len(keywords) > 2  # More than just appended
