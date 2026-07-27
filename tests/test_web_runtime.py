"""Tests for Flask runtime hardening (SECRET_KEY, debug/host helpers)."""

import pytest

from src.web.runtime import (
    flask_bind_host,
    flask_debug_enabled,
    is_weak_secret_key,
    resolve_secret_key,
)


def test_flask_debug_defaults_false(monkeypatch):
    monkeypatch.delenv("FLASK_DEBUG", raising=False)
    assert flask_debug_enabled() is False


def test_flask_debug_true_from_env(monkeypatch):
    monkeypatch.setenv("FLASK_DEBUG", "true")
    assert flask_debug_enabled() is True


def test_flask_host_defaults_to_loopback(monkeypatch):
    monkeypatch.delenv("FLASK_HOST", raising=False)
    assert flask_bind_host() == "127.0.0.1"


def test_weak_secret_placeholders():
    assert is_weak_secret_key("")
    assert is_weak_secret_key("dev-only-change-me")
    assert is_weak_secret_key("change-me-to-a-long-random-string")
    assert is_weak_secret_key("replace-with-a-long-random-string")
    assert not is_weak_secret_key("a-long-random-production-secret")


def test_resolve_secret_key_rejects_weak_outside_development(monkeypatch):
    monkeypatch.delenv("FLASK_ENV", raising=False)
    monkeypatch.setenv("SECRET_KEY", "dev-only-change-me")
    with pytest.raises(EnvironmentError, match="SECRET_KEY"):
        resolve_secret_key(allow_dev_default=False)


def test_resolve_secret_key_allows_dev_env_default(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    assert resolve_secret_key(allow_dev_default=False) == "dev-only-change-me"


def test_resolve_secret_key_accepts_strong_key(monkeypatch):
    monkeypatch.delenv("FLASK_ENV", raising=False)
    monkeypatch.setenv("SECRET_KEY", "unit-test-strong-secret-key-value")
    assert resolve_secret_key(allow_dev_default=False) == "unit-test-strong-secret-key-value"


def test_create_app_run_startup_false_allows_placeholder(monkeypatch):
    monkeypatch.delenv("FLASK_ENV", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    from src.web import create_app

    application = create_app(run_startup=False)
    assert application.config["SECRET_KEY"]
