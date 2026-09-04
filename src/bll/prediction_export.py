"""Export prediction run results to a markdown file for the repo / README."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any

from src.bll.prediction_types import TargetType
from src.bll.prediction_explanations import (
    MODEL_BLURBS,
    MODEL_MIN_MONTHS,
    explain_prediction_error,
    is_baseline_only,
    status_explanation,
)

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_RESULTS_DIR = _PROJECT_ROOT / "docs" / "prediction"
RESULTS_PATH_FAKE = _RESULTS_DIR / "model_results_fake.md"
RESULTS_PATH_DATABASE = _RESULTS_DIR / "model_results_database.md"
# Legacy single-file path (kept only for docs that still mention it).
DEFAULT_RESULTS_PATH = RESULTS_PATH_FAKE


def results_path_for_source(data_source: str | None) -> Path:
    """Return the markdown export path for a prediction data source."""
    kind = (data_source or "fake").strip().lower()
    if kind in ("database", "db"):
        return RESULTS_PATH_DATABASE
    return RESULTS_PATH_FAKE


def _format_value(target_type: str, value: float | None) -> str:
    if value is None:
        return "—"
    if target_type == TargetType.SALARY_ROLE or "salary" in (target_type or ""):
        return str(int(round(float(value))))
    # Counts / baseline latest: whole numbers when close to int
    number = float(value)
    if abs(number - round(number)) < 1e-6:
        return str(int(round(number)))
    return f"{number:.2f}"


def _period_str(period: date | str | None) -> str:
    if period is None:
        return "—"
    if isinstance(period, date):
        return period.isoformat()
    return str(period)[:10]


def export_model_results_markdown(
    *,
    run_id: int | None,
    status: str,
    summary: dict[str, Any],
    results: list[dict[str, Any]],
    path: Path | None = None,
    errors: dict[str, str] | None = None,
) -> Path:
    """Write model results (sorted by value within each model) to markdown.

    Fake and database runs write to separate files under ``docs/prediction/``
    unless an explicit ``path`` is provided.
    """
    data_source = (summary.get("data_source") or "unknown").strip().lower()
    out = Path(path) if path is not None else results_path_for_source(data_source)
    out.parent.mkdir(parents=True, exist_ok=True)

    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in results:
        by_model[str(row.get("model_name") or "unknown")].append(row)

    for model_name in by_model:
        by_model[model_name].sort(
            key=lambda r: (
                -(float(r["predicted_value"]) if r.get("predicted_value") is not None else float("-inf")),
                int(r.get("horizon_months") or 0),
                str(r.get("target_type") or ""),
                str(r.get("target_key") or ""),
            )
        )

    if data_source == "fake":
        title = "Prediction model results (fake data)"
        data_source_label = "Fake / synthetic series (`data/fake/` CSVs)"
        data_source_note = (
            "Models were trained on generated job-market aggregates "
            "(not live PostgreSQL postings). Regenerate with "
            "`python scripts/generate_fake_job_market.py`. "
            "Database-backed runs write to `model_results_database.md`."
        )
        ui_hint = "**Prediction (fake)**"
    elif data_source == "database":
        title = "Prediction model results (database)"
        data_source_label = "Real database aggregates (PostgreSQL `job_postings` / skills)"
        data_source_note = (
            "Models were trained on series built from saved job postings in the database. "
            "Fake-data runs write to `model_results_fake.md`."
        )
        ui_hint = "**Prediction (database)**"
    else:
        title = "Prediction model results"
        data_source_label = summary.get("data_source") or "—"
        data_source_note = "See `PREDICTION_DATA_SOURCE` in `.env`."
        ui_hint = "**Prediction**"

    models = list(summary.get("models") or [])
    lines: list[str] = [
        f"# {title}",
        "",
        f"Auto-generated when you run {ui_hint} in the web UI or CLI. "
        "Rows within each model are ordered by predicted value (highest first).",
        "",
        f"- **Generated at:** {datetime.now().isoformat(timespec='seconds')}",
        f"- **Run id:** {run_id if run_id is not None else '—'}",
        f"- **Status:** {status} — {status_explanation(status)}",
        f"- **Training data source:** {data_source_label}",
        f"- **Training window (months):** {summary.get('training_window_months', '—')}",
        f"- **Horizons:** {', '.join(str(h) for h in summary.get('horizons') or []) or '—'}",
        f"- **Models:** {', '.join(models) or '—'}",
        f"- **Elapsed (seconds):** {summary.get('elapsed_seconds', '—')}",
        "",
        "## How to read these results",
        "",
    ]

    if is_baseline_only(models):
        lines.extend(
            [
                "**Baseline only:** these rows are a **historical snapshot**, not a prediction "
                "of future months. `horizon` is `0` and `period` is empty. "
                "**Value** = latest monthly posting count in the training window. "
                "Metrics (when present in the DB) include moving averages, growth %, and "
                "trend direction (up / down / flat).",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "- **Forecast models** (`prophet`, `arima`, `sarima`, `rf`, `hgb`): "
                "**Value** is the predicted posting count (or average salary for "
                "`salary_role`) for that future month. **Horizon** = months ahead "
                "(3 / 6 / 12). **Period** = calendar month-start of that forecast step.",
                "- **Baseline** rows (if included): historical latest counts only "
                "(`horizon` 0) — not future forecasts.",
                "- Tree models (`rf`, `hgb`) often stay flat on strong trends; "
                "prefer `arima` / `prophet` when history is long enough.",
                "",
                "### Minimum history (months of data per series)",
                "",
            ]
        )
        for key, months in MODEL_MIN_MONTHS.items():
            lines.append(f"- `{key}`: ≥ {months}")
        lines.append("")

    lines.extend(
        [
            "## Training data",
            "",
            data_source_note,
            "",
        ]
    )

    timings = summary.get("model_timings_seconds") or {}
    if timings:
        lines.append("## Time per model")
        lines.append("")
        lines.append("| Model | Seconds |")
        lines.append("|-------|---------|")
        for name, secs in timings.items():
            lines.append(f"| `{name}` | {secs} |")
        lines.append("")

    roles = summary.get("roles") or []
    skills = summary.get("skills") or []
    if roles or skills:
        lines.append("## Top roles & top skills (historical shortlist)")
        lines.append("")
        lines.append(
            "These lists are **not** the models' forecast of future popularity. "
            "Before forecasting, roles and skills are ranked by **historical posting "
            "volume** inside the training window (highest count first); the top K "
            "(default 15) become the forecast targets. Every selected model then "
            "runs on that same shortlist. Order below = historical volume, not "
            "predicted rank."
        )
        lines.append("")
        if roles:
            lines.append(f"- **Top roles (historical):** {', '.join(roles)}")
        if skills:
            lines.append(f"- **Top skills (historical):** {', '.join(skills)}")
        lines.append("")

    err_map = errors if errors is not None else (summary.get("errors") or {})
    if err_map:
        lines.append("## Warnings (soft-fail errors)")
        lines.append("")
        lines.append(
            "Individual model/target fits failed; other rows may still be present. "
            "The most common cause is **not enough monthly history** for that series."
        )
        lines.append("")
        lines.append("| Target | Error | Why it matters |")
        lines.append("|--------|-------|----------------|")
        for key in sorted(err_map.keys()):
            msg = str(err_map[key])
            lines.append(
                f"| `{key}` | {msg} | {explain_prediction_error(key, msg)} |"
            )
        lines.append("")

    if not by_model:
        lines.extend(
            [
                "## Results",
                "",
                "_No result rows. Run Prediction to populate this file._",
                "",
            ]
        )
    else:
        for model_name in sorted(by_model.keys()):
            lines.append(f"## Model: `{model_name}`")
            lines.append("")
            blurb = MODEL_BLURBS.get(model_name)
            if blurb:
                lines.append(blurb)
                lines.append("")
            lines.append("| Type | Target | Horizon | Period | Value |")
            lines.append("|------|--------|---------|--------|-------|")
            for row in by_model[model_name]:
                lines.append(
                    "| {type} | {target} | {horizon} | {period} | {value} |".format(
                        type=row.get("target_type") or "—",
                        target=row.get("target_key") or "—",
                        horizon=row.get("horizon_months") if row.get("horizon_months") is not None else "—",
                        period=_period_str(row.get("period_start")),
                        value=_format_value(
                            str(row.get("target_type") or ""),
                            row.get("predicted_value"),
                        ),
                    )
                )
            lines.append("")

    out.write_text("\n".join(lines), encoding="utf-8")
    return out
