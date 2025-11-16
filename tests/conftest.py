"""Pytest configuration and shared fixtures."""


# Mark for tests that need functional API keys
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "functional: marks tests as functional (requiring real API keys)"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (no API keys needed)"
    )
