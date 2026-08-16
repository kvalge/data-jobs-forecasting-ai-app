# Prediction model results (database)

Auto-generated when you run **Prediction (database)** in the web UI or CLI. Rows within each model are ordered by predicted value (highest first).

- **Generated at:** 2026-08-16T09:30:46
- **Run id:** 23
- **Status:** completed
- **Training data source:** Real database aggregates (PostgreSQL `job_postings` / skills)
- **Training window (months):** 12
- **Horizons:** 3
- **Models:** baseline
- **Elapsed (seconds):** 0.167

## Training data

Models were trained on series built from saved job postings in the database. Fake-data runs write to `model_results_fake.md`.

## Time per model

| Model | Seconds |
|-------|---------|
| `baseline` | 0.095 |

## Top roles & top skills (historical shortlist)

These lists are **not** the models' forecast of future popularity. Before forecasting, roles and skills are ranked by **historical posting volume** inside the training window (highest count first); the top K (default 15) become the forecast targets. Every selected model then runs on that same shortlist. Order below = historical volume, not predicted rank.

- **Top roles (historical):** Analyst, Data Analyst, Senior Analyst, Data Engineer, Senior Data Analyst, AI Engineer, Bioanalyst, Data Quality & BI QA Engineer, Database Administrator, Credit Risk Manager, Senior Credit Risk Modeller, Senior Business Analyst, Operations Specialist, Business Analyst, AI Security Engineer
- **Top skills (historical):** Python, SQL, Tableau, Excel, R, Power BI, AWS, DBT, Looker, Azure, GCP, Snowflake, BigQuery, Google Sheets, bash

## Model: `baseline`

| Type | Target | Horizon | Period | Value |
|------|--------|---------|--------|-------|
| baseline_skill | SQL | 0 | — | 34 |
| baseline_skill | Python | 0 | — | 33 |
| baseline_skill | Excel | 0 | — | 14 |
| baseline_skill | R | 0 | — | 14 |
| baseline_skill | Tableau | 0 | — | 14 |
| baseline_skill | Power BI | 0 | — | 9 |
| baseline_role | Analyst | 0 | — | 8 |
| baseline_skill | AWS | 0 | — | 8 |
| baseline_role | Senior Analyst | 0 | — | 7 |
| baseline_role | Data Analyst | 0 | — | 6 |
| baseline_skill | DBT | 0 | — | 6 |
| baseline_skill | GCP | 0 | — | 6 |
| baseline_skill | Azure | 0 | — | 5 |
| baseline_role | Data Engineer | 0 | — | 4 |
| baseline_skill | Google Sheets | 0 | — | 4 |
| baseline_skill | Looker | 0 | — | 4 |
| baseline_skill | Snowflake | 0 | — | 4 |
| baseline_role | AI Engineer | 0 | — | 3 |
| baseline_role | Senior Data Analyst | 0 | — | 3 |
| baseline_skill | BigQuery | 0 | — | 3 |
| baseline_role | AI Security Engineer | 0 | — | 2 |
| baseline_role | Bioanalyst | 0 | — | 2 |
| baseline_role | Business Analyst | 0 | — | 2 |
| baseline_skill | bash | 0 | — | 2 |
| baseline_role | Credit Risk Manager | 0 | — | 1 |
| baseline_role | Data Quality & BI QA Engineer | 0 | — | 1 |
| baseline_role | Database Administrator | 0 | — | 1 |
| baseline_role | Operations Specialist | 0 | — | 1 |
| baseline_role | Senior Business Analyst | 0 | — | 1 |
| baseline_role | Senior Credit Risk Modeller | 0 | — | 1 |
