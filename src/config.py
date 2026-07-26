# config.py
import os

from dotenv import load_dotenv

load_dotenv()

REQUIRED_ENV_VARS = (
    "OPENROUTER_API_KEY",
    "DATABASE_URL",
    "MODEL",
    "FALLBACK_MODEL",
)

OPENROUTER_API_KEY: str | None = os.getenv("OPENROUTER_API_KEY")
DATABASE_URL: str | None = os.getenv("DATABASE_URL")
MODEL: str | None = os.getenv("MODEL")
FALLBACK_MODEL: str | None = os.getenv("FALLBACK_MODEL")
# Prediction series source: "fake" (data/fake CSVs) or "database" (future).
PREDICTION_DATA_SOURCE: str = (os.getenv("PREDICTION_DATA_SOURCE") or "fake").strip() or "fake"


def validate_config() -> None:
    """Fail fast if any required environment variable is missing or blank.

    Call this at application startup before using the DB or LLM clients.
    """
    global OPENROUTER_API_KEY, DATABASE_URL, MODEL, FALLBACK_MODEL, PREDICTION_DATA_SOURCE

    missing = [
        name
        for name in REQUIRED_ENV_VARS
        if not (os.getenv(name) or "").strip()
    ]
    if missing:
        names = ", ".join(missing)
        raise EnvironmentError(
            f"Missing or empty required environment variable(s): {names}. "
            "Copy .env.example to .env and fill in all values."
        )

    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
    DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
    MODEL = os.getenv("MODEL", "").strip()
    FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "").strip()
    PREDICTION_DATA_SOURCE = (os.getenv("PREDICTION_DATA_SOURCE") or "fake").strip() or "fake"
    if PREDICTION_DATA_SOURCE not in ("fake", "database"):
        raise EnvironmentError(
            "PREDICTION_DATA_SOURCE must be 'fake' or 'database' "
            f"(got {PREDICTION_DATA_SOURCE!r})."
        )
