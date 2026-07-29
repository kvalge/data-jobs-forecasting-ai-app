"""Unit tests for mid-chain extraction schema validation."""

import pytest

from src.llm.extract_validate import assert_extraction_usable


def test_assert_extraction_usable_accepts_minimal_valid():
    parsed = {"role_title": "Engineer", "skills": [], "skills_en": []}
    assert assert_extraction_usable(parsed)["role_title"] == "Engineer"


def test_assert_extraction_usable_rejects_empty_object_key():
    with pytest.raises(ValueError, match="schema validation"):
        assert_extraction_usable({"": {}})


def test_assert_extraction_usable_rejects_missing_role_title():
    with pytest.raises(ValueError, match="schema validation"):
        assert_extraction_usable({"skills": []})
