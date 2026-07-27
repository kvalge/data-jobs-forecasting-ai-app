"""Flask routes for database analysis and chart export."""

from __future__ import annotations

from flask import Blueprint, flash, render_template, request
from sqlalchemy.exc import SQLAlchemyError

from src.bll import analysis_service
from src.bll.analysis_facade import run_analysis

analysis_bp = Blueprint("analysis", __name__)

_ANALYSIS_KEYS = ("companies", "roles", "salary", "skills")


def _parse_selected() -> set[str]:
    selected = {key for key in _ANALYSIS_KEYS if request.form.get(key) == "on"}
    return selected


def _parse_n() -> int:
    raw = request.form.get("n")
    if raw is None or str(raw).strip() == "":
        return analysis_service.DEFAULT_TOP_N
    try:
        return analysis_service.clamp_top_n(int(raw))
    except (TypeError, ValueError):
        return analysis_service.DEFAULT_TOP_N


@analysis_bp.route("/analysis", methods=["GET", "POST"])
def analysis_page():
    results: dict = {}
    selected: set[str] = set()
    n = analysis_service.DEFAULT_TOP_N

    if request.method == "POST":
        selected = _parse_selected()
        n = _parse_n()
        if not selected:
            flash("Select at least one analysis option.", "error")
        else:
            try:
                results, written = run_analysis(selected, n)
                flash(
                    f"Analysis complete. Updated {len(written)} chart file(s) under docs/analysis/.",
                    "success",
                )
            except (SQLAlchemyError, EnvironmentError, OSError) as e:
                flash(f"Analysis failed: {e}", "error")

    return render_template(
        "analysis.html",
        results=results,
        selected=selected,
        n=n,
        default_n=analysis_service.DEFAULT_TOP_N,
        min_n=analysis_service.MIN_TOP_N,
        max_n=analysis_service.MAX_TOP_N,
    )
