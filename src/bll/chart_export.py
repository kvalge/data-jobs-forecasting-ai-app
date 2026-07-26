"""Write analysis charts as PNG files under docs/analysis/."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_DIR = _PROJECT_ROOT / "docs" / "analysis"

TOP_COMPANIES_PNG = ANALYSIS_DIR / "top_companies.png"
TOP_ROLES_PNG = ANALYSIS_DIR / "top_roles.png"
SALARY_SUMMARY_PNG = ANALYSIS_DIR / "salary_summary.png"
TOP_SKILLS_PNG = ANALYSIS_DIR / "top_skills.png"

# Match web UI palette
_NAVY = "#0b1f3a"
_DARK_RED = "#7a1f1f"
_DARK_GRAY = "#2e2e2e"
_LIGHT_GRAY = "#e6e6e6"


def ensure_analysis_dir() -> Path:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    return ANALYSIS_DIR


def _finish(fig: plt.Figure, path: Path) -> Path:
    ensure_analysis_dir()
    fig.tight_layout()
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def _empty_chart(title: str, path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.text(0.5, 0.5, "No data", ha="center", va="center", color=_DARK_GRAY, fontsize=14)
    ax.set_axis_off()
    ax.set_title(title, color=_NAVY, fontsize=13, fontweight="bold")
    return _finish(fig, path)


def export_top_n_bar(
    rows: list[dict[str, Any]],
    *,
    title: str,
    path: Path,
    xlabel: str = "Count",
) -> Path:
    """Horizontal bar chart for top-N label/count rows."""
    if not rows:
        return _empty_chart(title, path)

    labels = [str(r["label"]) for r in reversed(rows)]
    counts = [int(r["count"]) for r in reversed(rows)]

    fig, ax = plt.subplots(figsize=(8, max(3.5, 0.45 * len(labels) + 1.5)))
    bars = ax.barh(labels, counts, color=_NAVY)
    ax.set_xlabel(xlabel, color=_DARK_GRAY)
    ax.set_title(title, color=_NAVY, fontsize=13, fontweight="bold")
    ax.tick_params(colors=_DARK_GRAY)
    for spine in ax.spines.values():
        spine.set_color(_LIGHT_GRAY)
    # Leave room so labels past the bar end stay visible
    max_count = max(counts) if counts else 0
    ax.set_xlim(0, max_count * 1.12 if max_count else 1)
    for bar, count in zip(bars, counts):
        ax.text(
            bar.get_width() + max(max_count * 0.015, 0.05),
            bar.get_y() + bar.get_height() / 2,
            str(count),
            ha="left",
            va="center",
            color=_DARK_GRAY,
            fontsize=9,
            fontweight="600",
        )
    return _finish(fig, path)


def export_salary_summary(summary: dict[str, Any], *, path: Path = SALARY_SUMMARY_PNG) -> Path:
    """Bar chart for salary min / averages / max."""
    metrics = [
        ("Min of salary_min", summary.get("min_salary_min")),
        ("Avg salary_min", summary.get("avg_salary_min")),
        ("Avg salary_max", summary.get("avg_salary_max")),
        ("Max of salary_max", summary.get("max_salary_max")),
    ]
    labels = [m[0] for m in metrics]
    values = [m[1] for m in metrics]
    if all(v is None for v in values):
        return _empty_chart("Salary summary", path)

    plot_values = [0.0 if v is None else float(v) for v in values]
    colors = [_DARK_RED, _NAVY, _NAVY, _DARK_RED]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(labels, plot_values, color=colors)
    ax.set_ylabel("Salary", color=_DARK_GRAY)
    ax.set_title("Salary summary", color=_NAVY, fontsize=13, fontweight="bold")
    ax.tick_params(axis="x", labelrotation=15, colors=_DARK_GRAY)
    ax.tick_params(axis="y", colors=_DARK_GRAY)
    for spine in ax.spines.values():
        spine.set_color(_LIGHT_GRAY)
    max_plot = max(plot_values) if plot_values else 0
    ax.set_ylim(0, max_plot * 1.15 if max_plot else 1)
    for bar, raw in zip(bars, values):
        if raw is None:
            label = "n/a"
            y = 0
        else:
            label = f"{round(float(raw)):.0f}"
            y = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            y,
            label,
            ha="center",
            va="bottom",
            color=_DARK_GRAY,
            fontsize=9,
            fontweight="600",
        )
    return _finish(fig, path)


def export_top_companies(rows: list[dict[str, Any]]) -> Path:
    return export_top_n_bar(rows, title="Top companies", path=TOP_COMPANIES_PNG)


def export_top_roles(rows: list[dict[str, Any]]) -> Path:
    return export_top_n_bar(rows, title="Top roles (English)", path=TOP_ROLES_PNG)


def export_top_skills(rows: list[dict[str, Any]]) -> Path:
    return export_top_n_bar(rows, title="Top skills (English)", path=TOP_SKILLS_PNG)


def export_selected(
    *,
    companies: list[dict[str, Any]] | None = None,
    roles: list[dict[str, Any]] | None = None,
    salary: dict[str, Any] | None = None,
    skills: list[dict[str, Any]] | None = None,
) -> list[Path]:
    """Export PNGs for whichever result sets are provided."""
    written: list[Path] = []
    if companies is not None:
        written.append(export_top_companies(companies))
    if roles is not None:
        written.append(export_top_roles(roles))
    if salary is not None:
        written.append(export_salary_summary(salary))
    if skills is not None:
        written.append(export_top_skills(skills))
    return written
