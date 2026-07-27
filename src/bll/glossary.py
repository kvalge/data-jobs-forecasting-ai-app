# glossary.py
"""Persistent original -> English glossary (TSV file).

Only non-identity pairs are stored (skip English→English / same-text rows).
Entries are meant for user-corrected translations from the review UI, so the
LLM can reuse them next time instead of repeating a bad translation.
"""

from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
GLOSSARY_PATH = _PROJECT_ROOT / "glossary" / "original_en.tsv"

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


def load_glossary(path: Path | None = None) -> dict[str, str]:
    """Load glossary as lowercase-original -> english (preserves english casing)."""
    glossary_file = path or GLOSSARY_PATH
    mapping: dict[str, str] = {}
    if not glossary_file.is_file():
        return mapping

    for line in glossary_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "\t" not in stripped:
            continue
        original, english = stripped.split("\t", 1)
        original = original.strip()
        english = english.strip()
        if original and english and not is_identity_pair(original, english):
            mapping[_normalize_key(original)] = english
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
        original = original.strip()
        english = english.strip()
        if not original or not english:
            continue
        if is_identity_pair(original, english):
            had_identity = True
            continue
        key = _normalize_key(original)
        if key in key_to_index:
            rows[key_to_index[key]] = (original, english)
        else:
            key_to_index[key] = len(rows)
            rows.append((original, english))

    return header_lines, rows, had_identity


def add_entries(pairs: list[tuple[str, str]], path: Path | None = None) -> int:
    """Add or update original->english pairs. Skips identity (en→en) pairs.

    Returns number of newly written or updated rows.
    """
    glossary_file = path or GLOSSARY_PATH
    glossary_file.parent.mkdir(parents=True, exist_ok=True)

    header_lines, rows, had_identity = _read_file_state(glossary_file)
    key_to_index = {_normalize_key(o): i for i, (o, _) in enumerate(rows)}

    changed = 0
    for original, english in pairs:
        orig = (original or "").strip()
        eng = (english or "").strip()
        if not orig or not eng or is_identity_pair(orig, eng):
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
    glossary_file.write_text(
        header + ("\n" + body if body else "") + "\n",
        encoding="utf-8",
    )
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
