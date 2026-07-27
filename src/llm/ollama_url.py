# ollama_url.py
"""Validate OLLAMA_BASE_URL to reduce SSRF risk from misconfigured .env."""

from __future__ import annotations

from urllib.parse import urlparse

_LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})


def validate_ollama_base_url(url: str, *, allow_remote: bool = False) -> str:
    """Return a cleaned base URL or raise EnvironmentError.

    By default only loopback hosts are allowed. Set allow_remote=True
    (OLLAMA_ALLOW_REMOTE) for advanced setups that point at a remote Ollama.
    """
    cleaned = (url or "").strip().rstrip("/")
    if not cleaned:
        raise EnvironmentError("OLLAMA_BASE_URL is missing or empty.")

    parsed = urlparse(cleaned)
    if parsed.scheme not in ("http", "https"):
        raise EnvironmentError(
            "OLLAMA_BASE_URL must use http or https "
            f"(got scheme {parsed.scheme!r})."
        )
    if parsed.username is not None or parsed.password is not None:
        raise EnvironmentError(
            "OLLAMA_BASE_URL must not include username/password credentials."
        )
    if parsed.query or parsed.fragment:
        raise EnvironmentError(
            "OLLAMA_BASE_URL must not include query string or fragment."
        )

    host = (parsed.hostname or "").lower()
    if not host:
        raise EnvironmentError("OLLAMA_BASE_URL must include a hostname.")

    if not allow_remote and host not in _LOOPBACK_HOSTS:
        raise EnvironmentError(
            f"OLLAMA_BASE_URL host {host!r} is not a loopback address. "
            "Use http://127.0.0.1:11434 (or localhost / ::1), "
            "or set OLLAMA_ALLOW_REMOTE=true only if you intentionally "
            "point at a trusted remote Ollama."
        )

    return cleaned
