# glossary.py
"""Persistent original -> English glossary (TSV file)."""

from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
GLOSSARY_PATH = _PROJECT_ROOT / "glossary" / "original_en.tsv"


def _normalize_key(text: str) -> str:
    return text.strip().lower()


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
        if original and english:
            mapping[_normalize_key(original)] = english
    return mapping


def lookup_english(original: str, path: Path | None = None) -> str | None:
    """Return English for original if present in the glossary."""
    key = _normalize_key(original or "")
    if not key:
        return None
    return load_glossary(path).get(key)


def add_entries(pairs: list[tuple[str, str]], path: Path | None = None) -> int:
    """Append new original->english pairs. Returns number of newly written rows."""
    glossary_file = path or GLOSSARY_PATH
    glossary_file.parent.mkdir(parents=True, exist_ok=True)

    existing = load_glossary(glossary_file)
    added = 0
    lines_to_append: list[str] = []

    for original, english in pairs:
        orig = (original or "").strip()
        eng = (english or "").strip()
        if not orig or not eng:
            continue
        key = _normalize_key(orig)
        if key in existing:
            continue
        existing[key] = eng
        lines_to_append.append(f"{orig}\t{eng}")
        added += 1

    if lines_to_append:
        prefix = ""
        if glossary_file.is_file() and glossary_file.stat().st_size > 0:
            content = glossary_file.read_text(encoding="utf-8")
            if content and not content.endswith("\n"):
                prefix = "\n"
        with glossary_file.open("a", encoding="utf-8") as f:
            f.write(prefix + "\n".join(lines_to_append) + "\n")

    return added


def pairs_from_posting(
    role_title: str | None,
    role_title_en: str | None,
    skills: list[str],
    skills_en: list[str],
) -> list[tuple[str, str]]:
    """Build glossary pairs from posting fields."""
    pairs: list[tuple[str, str]] = []
    if role_title and role_title_en:
        pairs.append((role_title, role_title_en))
    for index, skill in enumerate(skills):
        skill_en = skills_en[index] if index < len(skills_en) else skill
        if skill and skill_en:
            pairs.append((skill, skill_en))
    return pairs
