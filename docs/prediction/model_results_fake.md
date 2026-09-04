# Prediction model results (fake data)

Auto-generated when you run **Prediction (fake)** in the web UI or CLI. Rows within each model are ordered by predicted value (highest first).

- **Generated at:** 2026-09-04T15:56:10
- **Run id:** 29
- **Status:** completed
- **Training data source:** Fake / synthetic series (`data/fake/` CSVs)
- **Training window (months):** 12
- **Horizons:** 3
- **Models:** baseline, prophet, arima
- **Elapsed (seconds):** 154.694

## Training data

Models were trained on generated job-market aggregates (not live PostgreSQL postings). Regenerate with `python scripts/generate_fake_job_market.py`. Database-backed runs write to `model_results_database.md`.

## Time per model

| Model | Seconds |
|-------|---------|
| `baseline` | 0.158 |
| `prophet` | 151.719 |
| `arima` | 2.775 |

## Top roles & top skills (historical shortlist)

These lists are **not** the models' forecast of future popularity. Before forecasting, roles and skills are ranked by **historical posting volume** inside the training window (highest count first); the top K (default 15) become the forecast targets. Every selected model then runs on that same shortlist. Order below = historical volume, not predicted rank.

- **Top roles (historical):** Data Analyst, Data Engineer, Data Scientist, Analytics Engineer, ML Engineer, AI Engineer, BI Developer, MLOps Engineer, Product Analyst, Research Scientist, Backend Engineer, Data Platform Engineer, Platform Engineer, NLP Engineer, Computer Vision Engineer
- **Top skills (historical):** SQL, Python, Spark, dbt, Airflow, Tableau, Power BI, AWS, GCP, Azure, Kubernetes, TensorFlow, Docker, PyTorch, scikit-learn

## Model: `arima`

| Type | Target | Horizon | Period | Value |
|------|--------|---------|--------|-------|
| salary_role | NLP Engineer | 3 | 2026-10-01 | 5743 |
| salary_role | AI Engineer | 3 | 2026-10-01 | 5675 |
| salary_role | Computer Vision Engineer | 3 | 2026-10-01 | 5546 |
| salary_role | ML Engineer | 3 | 2026-10-01 | 5461 |
| salary_role | MLOps Engineer | 3 | 2026-10-01 | 5355 |
| salary_role | Data Platform Engineer | 3 | 2026-10-01 | 5350 |
| salary_role | Data Scientist | 3 | 2026-10-01 | 5164 |
| salary_role | Research Scientist | 3 | 2026-10-01 | 5145 |
| salary_role | Platform Engineer | 3 | 2026-10-01 | 5065 |
| salary_role | Backend Engineer | 3 | 2026-10-01 | 4822 |
| salary_role | Data Engineer | 3 | 2026-10-01 | 4773 |
| salary_role | Analytics Engineer | 3 | 2026-10-01 | 4423 |
| salary_role | Product Analyst | 3 | 2026-10-01 | 4141 |
| salary_role | BI Developer | 3 | 2026-10-01 | 4104 |
| salary_role | Data Analyst | 3 | 2026-10-01 | 3802 |
| skill | dbt | 3 | 2026-10-01 | 124.83 |
| skill | Spark | 3 | 2026-10-01 | 124.26 |
| skill | Power BI | 3 | 2026-10-01 | 120.38 |
| skill | GCP | 3 | 2026-10-01 | 116.82 |
| skill | AWS | 3 | 2026-10-01 | 115.10 |
| skill | Tableau | 3 | 2026-10-01 | 110.92 |
| skill | SQL | 3 | 2026-10-01 | 106.12 |
| skill | Docker | 3 | 2026-10-01 | 99.72 |
| skill | Airflow | 3 | 2026-10-01 | 97.73 |
| skill | PyTorch | 3 | 2026-10-01 | 96.80 |
| skill | Azure | 3 | 2026-10-01 | 95.03 |
| skill | Python | 3 | 2026-10-01 | 90.35 |
| skill | Kubernetes | 3 | 2026-10-01 | 87.79 |
| skill | TensorFlow | 3 | 2026-10-01 | 67.83 |
| skill | scikit-learn | 3 | 2026-10-01 | 65.48 |
| role | Data Analyst | 3 | 2026-10-01 | 36.93 |
| role | Data Engineer | 3 | 2026-10-01 | 35.12 |
| role | Data Scientist | 3 | 2026-10-01 | 30.21 |
| role | ML Engineer | 3 | 2026-10-01 | 24.09 |
| role | Analytics Engineer | 3 | 2026-10-01 | 21.66 |
| role | AI Engineer | 3 | 2026-10-01 | 21.59 |
| role | BI Developer | 3 | 2026-10-01 | 15.61 |
| role | MLOps Engineer | 3 | 2026-10-01 | 13.03 |
| role | Research Scientist | 3 | 2026-10-01 | 13.00 |
| role | Product Analyst | 3 | 2026-10-01 | 12.71 |
| role | Backend Engineer | 3 | 2026-10-01 | 11.46 |
| role | Platform Engineer | 3 | 2026-10-01 | 9.67 |
| role | Data Platform Engineer | 3 | 2026-10-01 | 9.48 |
| role | NLP Engineer | 3 | 2026-10-01 | 9.31 |
| role | Computer Vision Engineer | 3 | 2026-10-01 | 7.83 |

## Model: `baseline`

| Type | Target | Horizon | Period | Value |
|------|--------|---------|--------|-------|
| baseline_skill | SQL | 0 | — | 118 |
| baseline_skill | Spark | 0 | — | 110 |
| baseline_skill | Airflow | 0 | — | 107 |
| baseline_skill | dbt | 0 | — | 106 |
| baseline_skill | Python | 0 | — | 103 |
| baseline_skill | AWS | 0 | — | 95 |
| baseline_skill | GCP | 0 | — | 95 |
| baseline_skill | Tableau | 0 | — | 90 |
| baseline_skill | Azure | 0 | — | 87 |
| baseline_skill | Power BI | 0 | — | 87 |
| baseline_skill | Docker | 0 | — | 81 |
| baseline_skill | Kubernetes | 0 | — | 80 |
| baseline_skill | TensorFlow | 0 | — | 74 |
| baseline_skill | PyTorch | 0 | — | 71 |
| baseline_skill | scikit-learn | 0 | — | 69 |
| baseline_role | Data Engineer | 0 | — | 30 |
| baseline_role | Data Scientist | 0 | — | 29 |
| baseline_role | Data Analyst | 0 | — | 26 |
| baseline_role | Backend Engineer | 0 | — | 20 |
| baseline_role | ML Engineer | 0 | — | 17 |
| baseline_role | BI Developer | 0 | — | 16 |
| baseline_role | AI Engineer | 0 | — | 14 |
| baseline_role | Analytics Engineer | 0 | — | 13 |
| baseline_role | Research Scientist | 0 | — | 12 |
| baseline_role | MLOps Engineer | 0 | — | 9 |
| baseline_role | NLP Engineer | 0 | — | 8 |
| baseline_role | Platform Engineer | 0 | — | 8 |
| baseline_role | Data Platform Engineer | 0 | — | 7 |
| baseline_role | Product Analyst | 0 | — | 7 |
| baseline_role | Computer Vision Engineer | 0 | — | 4 |

## Model: `prophet`

| Type | Target | Horizon | Period | Value |
|------|--------|---------|--------|-------|
| salary_role | AI Engineer | 3 | 2026-10-01 | 63884 |
| salary_role | Product Analyst | 3 | 2026-10-01 | 24881 |
| salary_role | NLP Engineer | 3 | 2026-10-01 | 13800 |
| salary_role | MLOps Engineer | 3 | 2026-10-01 | 13120 |
| salary_role | Data Scientist | 3 | 2026-10-01 | 12730 |
| salary_role | BI Developer | 3 | 2026-10-01 | 12510 |
| salary_role | Computer Vision Engineer | 3 | 2026-10-01 | 10116 |
| salary_role | Research Scientist | 3 | 2026-10-01 | 8078 |
| salary_role | Backend Engineer | 3 | 2026-10-01 | 5988 |
| salary_role | Data Analyst | 3 | 2026-10-01 | 3685 |
| salary_role | Analytics Engineer | 3 | 2026-10-01 | 1724 |
| skill | SQL | 3 | 2026-10-01 | 671.52 |
| salary_role | Data Engineer | 3 | 2026-10-01 | 535 |
| skill | Power BI | 3 | 2026-10-01 | 295.45 |
| skill | Kubernetes | 3 | 2026-10-01 | 273.06 |
| skill | AWS | 3 | 2026-10-01 | 266.88 |
| skill | Docker | 3 | 2026-10-01 | 258.59 |
| skill | Azure | 3 | 2026-10-01 | 249.30 |
| skill | dbt | 3 | 2026-10-01 | 229.70 |
| role | BI Developer | 3 | 2026-10-01 | 180.20 |
| role | Data Engineer | 3 | 2026-10-01 | 177.12 |
| skill | Spark | 3 | 2026-10-01 | 148.51 |
| skill | Python | 3 | 2026-10-01 | 131.90 |
| role | Analytics Engineer | 3 | 2026-10-01 | 131.19 |
| skill | Airflow | 3 | 2026-10-01 | 127.38 |
| skill | scikit-learn | 3 | 2026-10-01 | 120.96 |
| skill | GCP | 3 | 2026-10-01 | 75.21 |
| skill | Tableau | 3 | 2026-10-01 | 47.26 |
| skill | PyTorch | 3 | 2026-10-01 | 32.61 |
| role | NLP Engineer | 3 | 2026-10-01 | 24.69 |
| role | ML Engineer | 3 | 2026-10-01 | 24.55 |
| role | Platform Engineer | 3 | 2026-10-01 | 17.88 |
| role | Data Scientist | 3 | 2026-10-01 | 11.52 |
| role | Computer Vision Engineer | 3 | 2026-10-01 | 10.34 |
| role | AI Engineer | 3 | 2026-10-01 | 0 |
| role | Backend Engineer | 3 | 2026-10-01 | 0 |
| role | Data Analyst | 3 | 2026-10-01 | 0 |
| role | Data Platform Engineer | 3 | 2026-10-01 | 0 |
| role | MLOps Engineer | 3 | 2026-10-01 | 0 |
| role | Product Analyst | 3 | 2026-10-01 | 0 |
| role | Research Scientist | 3 | 2026-10-01 | 0 |
| salary_role | Data Platform Engineer | 3 | 2026-10-01 | 0 |
| salary_role | ML Engineer | 3 | 2026-10-01 | 0 |
| salary_role | Platform Engineer | 3 | 2026-10-01 | 0 |
| skill | TensorFlow | 3 | 2026-10-01 | 0 |
