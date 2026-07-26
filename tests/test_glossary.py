"""Tests for original -> English glossary helpers."""

from src.bll.glossary import add_entries, load_glossary, lookup_english, pairs_from_posting


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


def test_pairs_from_posting():
    pairs = pairs_from_posting(
        "Analüütik",
        "Analyst",
        ["Python", "Andmebaasid"],
        ["Python", "Databases"],
    )
    assert ("Analüütik", "Analyst") in pairs
    assert ("Andmebaasid", "Databases") in pairs
