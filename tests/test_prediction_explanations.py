"""User-facing prediction error / result explanations."""

from src.bll.prediction_explanations import (
    explain_prediction_error,
    format_error_details,
    is_baseline_only,
    status_explanation,
)
from src.bll.prediction_service import PredictionRunOutcome
from src.bll.prediction_explanations import summarize_for_template


def test_explain_not_enough_history():
    text = explain_prediction_error(
        "arima:role:Data Engineer",
        "Need at least 8 months of history for ARIMA/SARIMA.",
    )
    assert "enough months" in text.lower() or "8 months" in text
    assert "database" in text.lower() or "postings" in text.lower()


def test_format_error_details_sorted():
    rows = format_error_details(
        {
            "prophet:skill:Python": "Need at least 6 months of history for Prophet.",
            "arima:role:X": "Need at least 8 months of history for ARIMA/SARIMA.",
        }
    )
    assert [r["target"] for r in rows] == [
        "arima:role:X",
        "prophet:skill:Python",
    ]
    assert all(r["explanation"] for r in rows)


def test_baseline_only_and_status():
    assert is_baseline_only(["baseline"]) is True
    assert is_baseline_only(["baseline", "arima"]) is False
    assert "soft-fail" in status_explanation("completed_with_errors").lower() or "failed" in status_explanation(
        "completed_with_errors"
    ).lower()


def test_summarize_for_template_with_outcome():
    outcome = PredictionRunOutcome(
        run_id=1,
        status="completed_with_errors",
        summary={"models": ["baseline", "arima"], "error_count": 1},
        errors={"arima:role:X": "Need at least 8 months of history for ARIMA/SARIMA."},
    )
    extras = summarize_for_template(outcome)
    assert extras["baseline_only"] is False
    assert len(extras["error_details"]) == 1
    assert extras["status_explanation"]
