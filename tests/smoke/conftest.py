"""
Smoke test fixtures and configuration.

These fixtures are specific to smoke tests (STEST) which:
- Verify deployment health
- Check critical system paths
- Run quickly after deployment
- Validate system is operational

Reference: ai_dev_flow/10_TSPEC/STEST/
"""

import pytest
from typing import Any, Dict, List


# Apply stest marker to all tests in this directory
def pytest_collection_modifyitems(items):
    """Add stest marker to all tests in this directory."""
    for item in items:
        if "smoke" in str(item.fspath):
            item.add_marker(pytest.mark.stest)


@pytest.fixture
def critical_paths() -> List[str]:
    """List of critical paths that must be operational."""
    return [
        "/health",
        "/api/v1/status",
        "/api/v1/artifacts",
    ]


@pytest.fixture
def expected_services() -> List[str]:
    """List of services that should be running."""
    return [
        "api",
        "database",
        "cache",
    ]


@pytest.fixture
def health_thresholds() -> Dict[str, Any]:
    """Health check thresholds."""
    return {
        "response_time_ms": 1000,
        "memory_percent": 90,
        "disk_percent": 85,
        "cpu_percent": 80,
    }


@pytest.fixture
def smoke_test_config() -> Dict[str, Any]:
    """Configuration for smoke tests."""
    return {
        "timeout_seconds": 30,
        "retry_count": 3,
        "retry_delay_seconds": 5,
    }
