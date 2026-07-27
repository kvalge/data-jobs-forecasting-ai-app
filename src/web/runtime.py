"""Web runtime helpers: bind address, debug flag, SECRET_KEY policy."""

from __future__ import annotations

import os

# Known placeholder / default secrets — reject outside development.
_WEAK_SECRET_KEYS = frozenset(
    {
        "",
        "dev-only-change-me",
        "change-me-to-a-long-random-string",
        "replace-with-a-long-random-string",
    }
)


def flask_env_name() -> str:
    return (os.getenv("FLASK_ENV") or "").strip().lower()


def is_flask_development() -> bool:
    return flask_env_name() in ("development", "dev")


def env_flag(name: str, *, default: bool = False) -> bool:
    raw = (os.getenv(name) or "").strip().lower()
    if not raw:
        return default
    if raw in ("1", "true", "yes", "on"):
        return True
    if raw in ("0", "false", "no", "off"):
        return False
    return default


def flask_debug_enabled() -> bool:
    """FLASK_DEBUG; default False (never default to the interactive debugger)."""
    return env_flag("FLASK_DEBUG", default=False)


def flask_bind_host() -> str:
    """Bind host; default loopback so the UI is not LAN-exposed by accident."""
    return (os.getenv("FLASK_HOST") or "127.0.0.1").strip() or "127.0.0.1"


def is_weak_secret_key(secret: str | None) -> bool:
    return (secret or "").strip() in _WEAK_SECRET_KEYS


def resolve_secret_key(*, allow_dev_default: bool) -> str:
    """Return SECRET_KEY or raise if missing/weak outside development.

    Args:
        allow_dev_default: When True (tests / explicit skip), use a weak
            placeholder if unset. When False, development env may use the
            built-in default; otherwise a strong SECRET_KEY is required.
    """
    secret = (os.getenv("SECRET_KEY") or "").strip()
    if secret and not is_weak_secret_key(secret):
        return secret

    if allow_dev_default:
        return secret or "dev-only-change-me"

    if is_flask_development():
        return secret or "dev-only-change-me"

    raise EnvironmentError(
        "SECRET_KEY is missing or uses a known placeholder. "
        "Set a long random SECRET_KEY in .env for the web UI, "
        "or set FLASK_ENV=development only for local trusted use "
        "(still bind to 127.0.0.1; the app has no authentication)."
    )
