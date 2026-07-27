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
# Optional extra fallbacks when primary + FALLBACK_MODEL hit limits / fail.
FALLBACK_MODEL2: str | None = os.getenv("FALLBACK_MODEL2")
FALLBACK_MODEL3: str | None = os.getenv("FALLBACK_MODEL3")
# Local Ollama fallback after all OpenRouter models fail (e.g. free-tier limits).
OLLAMA_FALLBACK_ENABLED: bool = (
    (os.getenv("OLLAMA_FALLBACK_ENABLED") or "true").strip().lower()
    in ("1", "true", "yes", "on")
)
OLLAMA_BASE_URL: str = (os.getenv("OLLAMA_BASE_URL") or "http://127.0.0.1:11434").strip()
OLLAMA_MODEL: str = (os.getenv("OLLAMA_MODEL") or "qwen3.5:latest").strip()
OLLAMA_TIMEOUT_SECONDS: int = int((os.getenv("OLLAMA_TIMEOUT_SECONDS") or "180").strip() or "180")
# Prediction series source: "fake" (data/fake CSVs) or "database" (future).
PREDICTION_DATA_SOURCE: str = (os.getenv("PREDICTION_DATA_SOURCE") or "fake").strip() or "fake"


def llm_model_chain() -> list[str]:
    """Ordered models for extraction/translation: primary then fallbacks.

    Tries MODEL, FALLBACK_MODEL, then optional FALLBACK_MODEL2 / FALLBACK_MODEL3
    when set. Skips blanks and consecutive duplicates.
    """
    candidates = (MODEL, FALLBACK_MODEL, FALLBACK_MODEL2, FALLBACK_MODEL3)
    chain: list[str] = []
    for name in candidates:
        cleaned = (name or "").strip()
        if not cleaned:
            continue
        if chain and chain[-1] == cleaned:
            continue
        chain.append(cleaned)
    return chain


def validate_config() -> None:
    """Fail fast if any required environment variable is missing or blank.

    Call this at application startup before using the DB or LLM clients.
    """
    global OPENROUTER_API_KEY, DATABASE_URL, MODEL, FALLBACK_MODEL
    global FALLBACK_MODEL2, FALLBACK_MODEL3, PREDICTION_DATA_SOURCE
    global OLLAMA_FALLBACK_ENABLED, OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT_SECONDS

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
    FALLBACK_MODEL2 = (os.getenv("FALLBACK_MODEL2") or "").strip() or None
    FALLBACK_MODEL3 = (os.getenv("FALLBACK_MODEL3") or "").strip() or None
    OLLAMA_FALLBACK_ENABLED = (
        (os.getenv("OLLAMA_FALLBACK_ENABLED") or "true").strip().lower()
        in ("1", "true", "yes", "on")
    )
    OLLAMA_BASE_URL = (os.getenv("OLLAMA_BASE_URL") or "http://127.0.0.1:11434").strip()
    OLLAMA_MODEL = (os.getenv("OLLAMA_MODEL") or "qwen3.5:latest").strip()
    try:
        OLLAMA_TIMEOUT_SECONDS = int(
            (os.getenv("OLLAMA_TIMEOUT_SECONDS") or "180").strip() or "180"
        )
    except ValueError as e:
        raise EnvironmentError("OLLAMA_TIMEOUT_SECONDS must be an integer.") from e
    if OLLAMA_TIMEOUT_SECONDS < 1:
        raise EnvironmentError("OLLAMA_TIMEOUT_SECONDS must be >= 1.")
    PREDICTION_DATA_SOURCE = (os.getenv("PREDICTION_DATA_SOURCE") or "fake").strip() or "fake"
    if PREDICTION_DATA_SOURCE not in ("fake", "database"):
        raise EnvironmentError(
            "PREDICTION_DATA_SOURCE must be 'fake' or 'database' "
            f"(got {PREDICTION_DATA_SOURCE!r})."
        )
    if len(llm_model_chain()) < 2:
        raise EnvironmentError(
            "At least MODEL and FALLBACK_MODEL must be set to distinct non-empty values."
        )
