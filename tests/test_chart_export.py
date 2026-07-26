"""Chart export writes PNGs under docs/analysis/."""

from pathlib import Path

from src.bll import chart_export


def test_export_selected_writes_pngs(tmp_path, monkeypatch):
    monkeypatch.setattr(chart_export, "ANALYSIS_DIR", tmp_path)
    monkeypatch.setattr(chart_export, "TOP_COMPANIES_PNG", tmp_path / "top_companies.png")
    monkeypatch.setattr(chart_export, "TOP_ROLES_PNG", tmp_path / "top_roles.png")
    monkeypatch.setattr(chart_export, "SALARY_SUMMARY_PNG", tmp_path / "salary_summary.png")
    monkeypatch.setattr(chart_export, "TOP_SKILLS_PNG", tmp_path / "top_skills.png")

    written = chart_export.export_selected(
        companies=[{"label": "Acme", "count": 3}],
        roles=[],
        salary={
            "min_salary_min": 1000,
            "avg_salary_min": 1500,
            "avg_salary_max": 2500,
            "max_salary_max": 3000,
        },
        skills=[{"label": "Python", "count": 2}],
    )
    assert len(written) == 4
    for path in written:
        assert Path(path).is_file()
        assert Path(path).stat().st_size > 0
