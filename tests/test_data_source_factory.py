"""Tests for prediction data-source factory."""

from src.prediction.data_source import get_data_source
from src.prediction.database_source import DatabaseSource
from src.prediction.fake_file_source import FakeFileSource


def test_get_data_source_fake_default():
    src = get_data_source("fake")
    assert isinstance(src, FakeFileSource)
    assert src.name == "fake"


def test_get_data_source_database():
    src = get_data_source("database")
    assert isinstance(src, DatabaseSource)
    assert src.name == "database"
