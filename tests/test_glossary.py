"""Tests for original -> English glossary helpers."""

import pytest

from src.bll.glossary import (
    add_entries,
    is_identity_pair,
    load_glossary,
    lookup_english,
    pairs_from_posting,
)


def test_lookup_and_add_entries(tmp_path):
    path = tmp_path / "original_en.tsv"
    path.write_text("# comment\nanalüütik\tAnalyst\n", encoding="utf-8")

    assert lookup_english("Analüütik", path=path) == "Analyst"
    assert lookup_english("unknown", path=path) is None

    added = add_entries([("Andmeinsener", "Data Engineer"), ("analüütik", "Analyst")], path=path)
    assert added == 1
    mapping = load_glossary(path)
    assert mapping["andmeinsener"] == "Data Engineer"
    assert mapping["analüütik"] == "Analyst"


def test_skips_identity_pairs(tmp_path):
    path = tmp_path / "original_en.tsv"
    added = add_entries(
        [("Python", "Python"), ("CI/CD", "ci/cd"), ("Andmebaasid", "Databases")],
        path=path,
    )
    assert added == 1
    mapping = load_glossary(path)
    assert "python" not in mapping
    assert mapping["andmebaasid"] == "Databases"


def test_updates_existing_translation(tmp_path):
    path = tmp_path / "original_en.tsv"
    path.write_text("analüütik\tWrong\n", encoding="utf-8")
    added = add_entries([("analüütik", "Analyst")], path=path)
    assert added == 1
    assert lookup_english("analüütik", path=path) == "Analyst"


def test_rejects_tab_or_newline_in_glossary_fields(tmp_path):
    path = tmp_path / "original_en.tsv"
    with pytest.raises(ValueError, match="tab or newline"):
        add_entries([("bad\tkey", "Value")], path=path)
    with pytest.raises(ValueError, match="tab or newline"):
        add_entries([("key", "bad\nvalue")], path=path)
    assert not path.exists() or path.read_text(encoding="utf-8").strip() == ""


def test_rejects_oversized_glossary_field(tmp_path):
    path = tmp_path / "original_en.tsv"
    with pytest.raises(ValueError, match="max length"):
        add_entries([("x" * 201, "English")], path=path)


def test_skips_poisoned_rows_on_load(tmp_path):
    path = tmp_path / "original_en.tsv"
    # A well-formed row plus a comment; load path skips unusable pairs.
    path.write_text("# hdr\nok\tGood\n", encoding="utf-8")
    mapping = load_glossary(path)
    assert mapping["ok"] == "Good"


def test_pairs_from_posting_skips_en_en():
    pairs = pairs_from_posting(
        "Analüütik",
        "Analyst",
        ["Python", "Andmebaasid"],
        ["Python", "Databases"],
    )
    assert ("Analüütik", "Analyst") in pairs
    assert ("Andmebaasid", "Databases") in pairs
    assert ("Python", "Python") not in pairs
    assert is_identity_pair("Python", "python")
