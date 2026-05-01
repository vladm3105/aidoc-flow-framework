"""Shared pytest configuration for ucx_kb tests."""


def pytest_addoption(parser):
    """Add flag to enable integration tests that require external services."""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="run integration tests requiring live databases/services",
    )
