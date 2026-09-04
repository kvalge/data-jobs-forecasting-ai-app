"""User-facing explanations for prediction results and soft-fail errors."""

from __future__ import annotations

from typing import Any

# Minimum monthly points required by each forecaster (see models/classical.py, ml.py).
MODEL_MIN_MONTHS: dict[str, int] = {
    "prophet": 6,
    "arima": 8,
    "sarima": 8,
    "rf": 10,
    "hgb": 10,
}

MODEL_BLURBS: dict[str, str] = {
    "baseline": (
        "Historical snapshot only (not a future forecast): latest count, "
        "moving averages, growth %, and linear trend direction."
    ),
    "prophet": "Trend + yearly seasonality forecast (needs ≥6 months of history).",
    "arima": "Classical ARIMA(1,1,1) forecast (needs ≥8 months).",
    "sarima": (
        "Seasonal ARIMA with yearly seasonality term (needs ≥8 months; "
        "works best with ~24+ months)."
    ),
    "rf": "Random-forest lag model (needs ≥10 months; weak at extrapolating strong trends).",
    "hgb": (
        "Histogram gradient-boosting lag model (needs ≥10 months; "
        "weak at extrapolating strong trends)."
    ),
}


def explain_prediction_error(key: str, message: str) -> str:
    """Turn a soft-fail key/message into a short user-facing reason."""
    text = (message or "").strip()
    lower = text.lower()

    if "need at least" in lower and "history" in lower:
        return (
            f"{text} That role/skill/salary series does not span enough months "
            "in the training window (common on the database tab when few postings "
            "exist yet). Add more postings over time, widen the window if history "
            "exists, or choose baseline / models with lower minimums."
        )
    if "prophet not installed" in lower:
        return (
            "Prophet is not installed or failed to import (often a Windows "
            "toolchain/CmdStan issue). Uncheck prophet or install it; other "
            "models can still run."
        )
    if "statsmodels not installed" in lower:
        return "statsmodels is missing; install requirements to run ARIMA/SARIMA."
    if "singular" in lower or "linalg" in lower or "convergence" in lower:
        return (
            f"Model fit failed numerically ({text}). Often caused by a nearly "
            "constant or very sparse series — try another model or more history."
        )
    if key == "baseline":
        return f"Baseline analysis failed: {text}"
    return text or "Unknown model/target failure."


def format_error_details(errors: dict[str, str] | None) -> list[dict[str, str]]:
    """List of {target, message, explanation} for the UI, stable order."""
    if not errors:
        return []
    rows: list[dict[str, str]] = []
    for key in sorted(errors.keys()):
        message = str(errors[key])
        rows.append(
            {
                "target": key,
                "message": message,
                "explanation": explain_prediction_error(key, message),
            }
        )
    return rows


def status_explanation(status: str | None) -> str:
    s = (status or "").strip().lower()
    if s == "completed":
        return "All selected model/target fits succeeded."
    if s == "completed_with_errors":
        return (
            "Some model/target fits failed (often not enough monthly history), "
            "but other result rows were still saved. See warnings below."
        )
    if s == "failed":
        return "No result rows were produced; every selected fit failed."
    return "Run finished."


def is_baseline_only(models: list[str] | None) -> bool:
    cleaned = [str(m).strip().lower() for m in (models or []) if str(m).strip()]
    return cleaned == ["baseline"]


def result_type_label(target_type: str | None) -> str:
    mapping = {
        "role": "Role demand (postings/month)",
        "skill": "Skill demand (postings/month)",
        "salary_role": "Avg salary for role",
        "baseline_role": "Baseline: role latest count",
        "baseline_skill": "Baseline: skill latest count",
    }
    return mapping.get((target_type or "").strip(), target_type or "—")


def summarize_for_template(outcome: Any) -> dict[str, Any]:
    """Extra template fields derived from a PredictionRunOutcome."""
    if outcome is None:
        return {
            "error_details": [],
            "status_explanation": "",
            "baseline_only": False,
            "model_blurbs": MODEL_BLURBS,
            "model_min_months": MODEL_MIN_MONTHS,
        }
    models = list(outcome.summary.get("models") or [])
    return {
        "error_details": format_error_details(outcome.errors),
        "status_explanation": status_explanation(outcome.status),
        "baseline_only": is_baseline_only(models),
        "model_blurbs": MODEL_BLURBS,
        "model_min_months": MODEL_MIN_MONTHS,
    }
