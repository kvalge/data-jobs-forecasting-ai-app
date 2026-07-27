# glossary.py
"""Persistent original -> English glossary (TSV file).

Only non-identity pairs are stored (skip English→English / same-text rows).
Entries are meant for user-corrected translations from the review UI, so the
LLM can reuse them next time instead of repeating a bad translation.
"""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
GLOSSARY_PATH = _PROJECT_ROOT / "glossary" / "original_en.tsv"

MAX_GLOSSARY_FIELD_LEN = 200
_FORBIDDEN_CHARS = re.compile(r"[\t\n\r]")

# path -> (mtime_ns or None if missing, mapping)
_glossary_cache: dict[str, tuple[int | None, dict[str, str]]] = {}

_DEFAULT_HEADER = [
    "# original_en.tsv — glossary of original (non-English) labels -> English",
    "# Format: original<TAB>english  (one pair per line; # starts a comment)",
    "# Only store real translations (skip English→English).",
    "# Updated when the user revises translations on the posting review page.",
]


def _normalize_key(text: str) -> str:
    return text.strip().lower()


def is_identity_pair(original: str, english: str) -> bool:
    """True when original and English are the same text (no real translation)."""
    return _normalize_key(original) == _normalize_key(english)


def sanitize_glossary_field(value: str, *, field_name: str = "value") -> str:
    """Strip and reject tabs/newlines or oversized glossary fields."""
    cleaned = (value or "").strip()
    if not cleaned:
        raise ValueError(f"Glossary {field_name} cannot be empty")
    if _FORBIDDEN_CHARS.search(cleaned):
        raise ValueError(
            f"Glossary {field_name} cannot contain tab or newline characters"
        )
    if len(cleaned) > MAX_GLOSSARY_FIELD_LEN:
        raise ValueError(
            f"Glossary {field_name} exceeds max length ({MAX_GLOSSARY_FIELD_LEN})"
        )
    return cleaned


def _safe_pair(original: str, english: str) -> tuple[str, str] | None:
    """Return a sanitized pair, or None if the row is unusable (load path)."""
    try:
        return (
            sanitize_glossary_field(original, field_name="original"),
            sanitize_glossary_field(english, field_name="english"),
        )
    except ValueError:
        return None


def clear_glossary_cache(path: Path | None = None) -> None:
    """Drop cached glossary mapping(s). Used by tests and after writes."""
    if path is None:
        _glossary_cache.clear()
        return
    _glossary_cache.pop(str((path or GLOSSARY_PATH).resolve()), None)


def load_glossary(path: Path | None = None) -> dict[str, str]:
    """Load glossary as lowercase-original -> english (preserves english casing)."""
    glossary_file = path or GLOSSARY_PATH
    cache_key = str(glossary_file.resolve())
    mtime: int | None
    try:
        mtime = glossary_file.stat().st_mtime_ns if glossary_file.is_file() else None
    except OSError:
        mtime = None

    cached = _glossary_cache.get(cache_key)
    if cached is not None and cached[0] == mtime:
        return cached[1]

    mapping: dict[str, str] = {}
    if glossary_file.is_file():
        for line in glossary_file.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "\t" not in stripped:
                continue
            original, english = stripped.split("\t", 1)
            pair = _safe_pair(original, english)
            if pair is None:
                continue
            orig, eng = pair
            if not is_identity_pair(orig, eng):
                mapping[_normalize_key(orig)] = eng

    _glossary_cache[cache_key] = (mtime, mapping)
    return mapping


def lookup_english(original: str, path: Path | None = None) -> str | None:
    """Return English for original if present in the glossary."""
    key = _normalize_key(original or "")
    if not key:
        return None
    return load_glossary(path).get(key)


def _read_file_state(glossary_file: Path) -> tuple[list[str], list[tuple[str, str]], bool]:
    """Return (header_lines, data_rows, had_identity_rows)."""
    header_lines: list[str] = []
    rows: list[tuple[str, str]] = []
    key_to_index: dict[str, int] = {}
    had_identity = False

    if not glossary_file.is_file():
        return header_lines, rows, had_identity

    for line in glossary_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            header_lines.append(stripped)
            continue
        if "\t" not in stripped:
            continue
        original, english = stripped.split("\t", 1)
        pair = _safe_pair(original, english)
        if pair is None:
            continue
        orig, eng = pair
        if is_identity_pair(orig, eng):
            had_identity = True
            continue
        key = _normalize_key(orig)
        if key in key_to_index:
            rows[key_to_index[key]] = (orig, eng)
        else:
            key_to_index[key] = len(rows)
            rows.append((orig, eng))

    return header_lines, rows, had_identity


def _atomic_write_text(path: Path, content: str) -> None:
    """Write via a temp file in the same directory, then replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def add_entries(pairs: list[tuple[str, str]], path: Path | None = None) -> int:
    """Add or update original->english pairs. Skips identity (en→en) pairs.

    Raises ValueError if a pair contains tabs/newlines or exceeds length limits.
    Returns number of newly written or updated rows.
    """
    glossary_file = path or GLOSSARY_PATH
    glossary_file.parent.mkdir(parents=True, exist_ok=True)

    header_lines, rows, had_identity = _read_file_state(glossary_file)
    key_to_index = {_normalize_key(o): i for i, (o, _) in enumerate(rows)}

    changed = 0
    for original, english in pairs:
        if not (original or "").strip() or not (english or "").strip():
            continue
        orig = sanitize_glossary_field(original, field_name="original")
        eng = sanitize_glossary_field(english, field_name="english")
        if is_identity_pair(orig, eng):
            continue
        key = _normalize_key(orig)
        if key in key_to_index:
            prev_orig, prev_eng = rows[key_to_index[key]]
            if _normalize_key(prev_eng) == _normalize_key(eng):
                continue
            rows[key_to_index[key]] = (prev_orig, eng)
            changed += 1
        else:
            key_to_index[key] = len(rows)
            rows.append((orig, eng))
            changed += 1

    if changed == 0 and not had_identity:
        return 0

    if not header_lines:
        header_lines = list(_DEFAULT_HEADER)

    body = "\n".join(f"{o}\t{e}" for o, e in rows)
    header = "\n".join(header_lines)
    _atomic_write_text(
        glossary_file,
        header + ("\n" + body if body else "") + "\n",
    )
    clear_glossary_cache(glossary_file)
    return changed


def pairs_from_posting(
    role_title: str | None,
    role_title_en: str | None,
    skills: list[str],
    skills_en: list[str],
) -> list[tuple[str, str]]:
    """Build glossary pairs from posting fields; skip identity (same-text) pairs."""
    pairs: list[tuple[str, str]] = []
    if role_title and role_title_en and not is_identity_pair(role_title, role_title_en):
        pairs.append((role_title.strip(), role_title_en.strip()))
    for index, skill in enumerate(skills):
        skill_en = skills_en[index] if index < len(skills_en) else skill
        if skill and skill_en and not is_identity_pair(skill, skill_en):
            pairs.append((skill.strip(), skill_en.strip()))
    return pairs
