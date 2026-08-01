"""Time series prediction package (fake-file and database data sources)."""

from src.prediction.data_source import DataSource, get_data_source

__all__ = ["DataSource", "get_data_source"]
