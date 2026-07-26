"""Time series prediction package (fake-file data now; DB source later)."""

from src.prediction.data_source import DataSource, get_data_source

__all__ = ["DataSource", "get_data_source"]
