"""Tests for fail-fast environment configuration."""

import os

import pytest

import src.config as config


def _set_all_required(**overrides: str) -> None:
    values = {
        "OPENROUTER_API_KEY": "test-key",
        "DATABASE_URL": "postgresql+psycopg2://u:p@localhost/db",
        "MODEL": "primary-model",
        "FALLBACK_MODEL": "fallback-model",
    }
    values.update(overrides)
    for name, value in values.items():
        os.environ[name] = value


@pytest.mark.usefixtures("restore_env")
def test_validate_config_raises_when_vars_missing():
    for name in config.REQUIRED_ENV_VARS:
        os.environ.pop(name, None)

    with pytest.raises(EnvironmentError, match="Missing or empty"):
        config.validate_config()


@pytest.mark.usefixtures("restore_env")
def test_validate_config_raises_when_var_blank():
    _set_all_required(MODEL="   ")

    with pytest.raises(EnvironmentError, match="MODEL"):
        config.validate_config()


@pytest.mark.usefixtures("restore_env")
def test_validate_config_strips_and_sets_globals():
    _set_all_required(
        OPENROUTER_API_KEY="  key  ",
        DATABASE_URL="  postgresql+psycopg2://u:p@localhost/db  ",
        MODEL="  model-a  ",
        FALLBACK_MODEL="  model-b  ",
    )

    config.validate_config()

    assert config.OPENROUTER_API_KEY == "key"
    assert config.DATABASE_URL == "postgresql+psycopg2://u:p@localhost/db"
    assert config.MODEL == "model-a"
    assert config.FALLBACK_MODEL == "model-b"
    assert config.PREDICTION_DATA_SOURCE == "fake"


@pytest.mark.usefixtures("restore_env")
def test_validate_config_rejects_bad_prediction_source():
    _set_all_required()
    os.environ["PREDICTION_DATA_SOURCE"] = "mongo"
    with pytest.raises(EnvironmentError, match="PREDICTION_DATA_SOURCE"):
        config.validate_config()
