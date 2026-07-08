"""Shared pytest fixtures for the xctsk-viewer test-suite."""

from pathlib import Path

import pytest

import app.services.airspace_service as airspace_module
from app import create_app

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_airspace_path() -> str:
    """Return the path to the bundled sample OpenAir file."""
    return str(FIXTURES / "sample_airspace.txt")


@pytest.fixture
def sample_airspace_bytes() -> bytes:
    """Return the raw bytes of the bundled sample OpenAir file."""
    return (FIXTURES / "sample_airspace.txt").read_bytes()


@pytest.fixture(autouse=True)
def reset_airspace_singleton():
    """Reset the global AirspaceService singleton around every test.

    The service caches loaded data in a module-level global, so tests that
    upload or reset datasets would otherwise leak state into one another.
    """
    airspace_module.airspace_service = None
    yield
    airspace_module.airspace_service = None


@pytest.fixture
def app():
    """Create a Flask application instance for testing."""
    application = create_app()
    application.config.update(TESTING=True)
    return application


@pytest.fixture
def client(app):
    """Return a Flask test client."""
    return app.test_client()
