"""Shared pytest fixtures for the test suite."""

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Allow tests to load the custom integration."""
    yield
