# Prediction model results

Auto-generated when you run **Prediction** in the web UI or CLI. Rows within each model are ordered by predicted value (highest first).

- **Generated at:** 2026-07-27T23:01:51
- **Run id:** 99
- **Status:** completed
- **Training data source:** Fake / synthetic series (`data/fake/` CSVs)
- **Training window (months):** 12
- **Horizons:** 3
- **Models:** baseline, rf
- **Elapsed (seconds):** 1.744

## Training data

Models were trained on generated job-market aggregates (not live PostgreSQL postings). Regenerate with `python scripts/generate_fake_job_market.py`. Switch later with `PREDICTION_DATA_SOURCE=database` when `DatabaseSource` is implemented.

## Time per model

| Model | Seconds |
|-------|---------|
| `baseline` | 0.03 |
| `rf` | 1.642 |

## Top roles & top skills (historical shortlist)

These lists are **not** the models' forecast of future popularity. Before forecasting, roles and skills are ranked by **historical posting volume** inside the training window (highest count first); the top K (default 15) become the forecast targets. Every selected model then runs on that same shortlist. Order below = historical volume, not predicted rank.

- **Top roles (historical):** Data Analyst, Data Engineer, ML Engineer
- **Top skills (historical):** SQL, Python, AWS

## Model: `baseline`

| Type | Target | Horizon | Period | Value |
|------|--------|---------|--------|-------|
| baseline_skill | Python | 0 | — | 5 |
| baseline_skill | SQL | 0 | — | 4 |
| baseline_skill | AWS | 0 | — | 2 |
| baseline_role | Data Analyst | 0 | — | 1 |
| baseline_role | Data Engineer | 0 | — | 1 |
| baseline_role | ML Engineer | 0 | — | 1 |

## Model: `rf`

| Type | Target | Horizon | Period | Value |
|------|--------|---------|--------|-------|
| salary_role | ML Engineer | 3 | 2026-10-01 | 5309 |
| salary_role | Data Engineer | 3 | 2026-10-01 | 4463 |
| salary_role | Data Analyst | 3 | 2026-09-01 | 3667 |
| skill | SQL | 3 | 2026-10-01 | 5.92 |
| skill | AWS | 3 | 2026-10-01 | 5.26 |
| skill | Python | 3 | 2026-10-01 | 5.21 |
| role | ML Engineer | 3 | 2026-10-01 | 2.25 |
| role | Data Analyst | 3 | 2026-09-01 | 1.24 |
| role | Data Engineer | 3 | 2026-10-01 | 0.80 |
