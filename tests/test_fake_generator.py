"""Smoke tests for fake job-market generator."""

import importlib.util
from datetime import date
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT = _ROOT / "scripts" / "generate_fake_job_market.py"


def _load_generator():
    spec = importlib.util.spec_from_file_location("generate_fake_job_market", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_generate_small_fake_dataset(tmp_path):
    mod = _load_generator()
    manifest = mod.generate_fake_job_market(
        out_dir=tmp_path,
        n_postings=120,
        months=6,
        seed=7,
        end_date=date(2026, 7, 26),
    )
    assert manifest["n_postings"] == 120
    assert (tmp_path / "postings.csv").is_file()
    assert (tmp_path / "posting_skills.csv").is_file()
    assert (tmp_path / "agg_monthly_roles.csv").is_file()
    assert (tmp_path / "agg_monthly_skills.csv").is_file()
    assert (tmp_path / "manifest.json").is_file()
    assert 8 * 120 <= manifest["n_skill_links"] <= 12 * 120
