"""Export prediction run results to a markdown file for the repo / README."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any

from src.bll.prediction_types import TargetType

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESULTS_PATH = _PROJECT_ROOT / "docs" / "prediction" / "model_results.md"


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
) -> Path:
    """Write model results (sorted by value within each model) to markdown."""
    out = Path(path or DEFAULT_RESULTS_PATH)
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

    data_source = (summary.get("data_source") or "unknown").strip().lower()
    if data_source == "fake":
        data_source_label = "Fake / synthetic series (`data/fake/` CSVs)"
        data_source_note = (
            "Models were trained on generated job-market aggregates "
            "(not live PostgreSQL postings). Regenerate with "
            "`python scripts/generate_fake_job_market.py`. "
            "Use the **Prediction (database)** UI tab or "
            "`PREDICTION_DATA_SOURCE=database` for live posting aggregates."
        )
    elif data_source == "database":
        data_source_label = "Real database aggregates (PostgreSQL `job_postings` / skills)"
        data_source_note = (
            "Models were trained on series built from saved job postings in the database."
        )
    else:
        data_source_label = summary.get("data_source") or "—"
        data_source_note = "See `PREDICTION_DATA_SOURCE` in `.env`."

    lines: list[str] = [
        "# Prediction model results",
        "",
        "Auto-generated when you run **Prediction** in the web UI or CLI. "
        "Rows within each model are ordered by predicted value (highest first).",
        "",
        f"- **Generated at:** {datetime.now().isoformat(timespec='seconds')}",
        f"- **Run id:** {run_id if run_id is not None else '—'}",
        f"- **Status:** {status}",
        f"- **Training data source:** {data_source_label}",
        f"- **Training window (months):** {summary.get('training_window_months', '—')}",
        f"- **Horizons:** {', '.join(str(h) for h in summary.get('horizons') or []) or '—'}",
        f"- **Models:** {', '.join(summary.get('models') or []) or '—'}",
        f"- **Elapsed (seconds):** {summary.get('elapsed_seconds', '—')}",
        "",
        "## Training data",
        "",
        data_source_note,
        "",
    ]

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
