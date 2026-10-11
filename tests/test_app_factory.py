"""Tests for the Flask app factory's configuration."""

import pytest

from app import create_app

PLACEHOLDER = "your-secret-key-change-in-production"


def test_secret_key_read_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """A set FLASK_SECRET_KEY becomes the app's SECRET_KEY."""
    monkeypatch.setenv("FLASK_SECRET_KEY", "from-env")
    assert create_app().config["SECRET_KEY"] == "from-env"


def test_secret_key_falls_back_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unset FLASK_SECRET_KEY falls back to the placeholder."""
    monkeypatch.delenv("FLASK_SECRET_KEY", raising=False)
    assert create_app().config["SECRET_KEY"] == PLACEHOLDER


def test_secret_key_falls_back_when_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    """An empty FLASK_SECRET_KEY falls back too, so flash() keeps working."""
    monkeypatch.setenv("FLASK_SECRET_KEY", "")
    assert create_app().config["SECRET_KEY"] == PLACEHOLDER
