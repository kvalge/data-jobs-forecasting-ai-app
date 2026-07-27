"""Tests for prediction data-source factory fail-closed behavior."""

import pytest

from src.prediction.data_source import get_data_source
from src.prediction.fake_file_source import FakeFileSource


def test_get_data_source_fake_default():
    src = get_data_source("fake")
    assert isinstance(src, FakeFileSource)
    assert src.name == "fake"


def test_get_data_source_rejects_database():
    with pytest.raises(ValueError, match="not implemented"):
        get_data_source("database")
