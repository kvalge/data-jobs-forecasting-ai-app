# posting_hash.py
"""Stable fingerprint for job posting raw text (deduplication)."""

import hashlib


def hash_posting_text(raw_text: str) -> str:
    """SHA-256 hex digest of stripped UTF-8 posting text."""
    normalized = raw_text.strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
