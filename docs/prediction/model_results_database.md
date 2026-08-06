# Prediction model results (database)

Auto-generated when you run **Prediction (database)** in the web UI or CLI. Rows within each model are ordered by predicted value (highest first).

- **Generated at:** 2026-08-06T18:48:10
- **Run id:** 21
- **Status:** completed_with_errors
- **Training data source:** Real database aggregates (PostgreSQL `job_postings` / skills)
- **Training window (months):** 12
- **Horizons:** 3
- **Models:** baseline, arima
- **Elapsed (seconds):** 0.374

## Training data

Models were trained on series built from saved job postings in the database. Fake-data runs write to `model_results_fake.md`.

## Time per model

| Model | Seconds |
|-------|---------|
| `baseline` | 0.092 |
| `arima` | 0.22 |

## Top roles & top skills (historical shortlist)

These lists are **not** the models' forecast of future popularity. Before forecasting, roles and skills are ranked by **historical posting volume** inside the training window (highest count first); the top K (default 15) become the forecast targets. Every selected model then runs on that same shortlist. Order below = historical volume, not predicted rank.

- **Top roles (historical):** Data Analyst, Data Engineer, Data Quality & BI QA Engineer, Analyst, AI Security Engineer, Database Administrator, Operations Specialist, Senior Data Analyst, AI Platform Engineer, AI Engineer, Credit Risk Manager, Compliance Analyst, Climate Analyst, Credit Risk Underwriting Modeler, Data Administrator
- **Top skills (historical):** Python, SQL, Tableau, R, DBT, Power BI, Looker, Excel, AWS, bash, Snowflake, Java, Docker, Airflow, BigQuery

## Model: `baseline`

| Type | Target | Horizon | Period | Value |
|------|--------|---------|--------|-------|
| baseline_skill | Python | 0 | — | 17 |
| baseline_skill | SQL | 0 | — | 17 |
| baseline_skill | R | 0 | — | 7 |
| baseline_skill | Tableau | 0 | — | 7 |
| baseline_skill | AWS | 0 | — | 5 |
| baseline_skill | DBT | 0 | — | 5 |
| baseline_skill | Power BI | 0 | — | 4 |
| baseline_skill | Airflow | 0 | — | 3 |
| baseline_skill | Docker | 0 | — | 3 |
| baseline_skill | Excel | 0 | — | 3 |
| baseline_skill | Snowflake | 0 | — | 3 |
| baseline_role | AI Security Engineer | 0 | — | 2 |
| baseline_role | Data Analyst | 0 | — | 2 |
| baseline_role | Data Engineer | 0 | — | 2 |
| baseline_skill | BigQuery | 0 | — | 2 |
| baseline_skill | Java | 0 | — | 2 |
| baseline_skill | Looker | 0 | — | 2 |
| baseline_skill | bash | 0 | — | 2 |
| baseline_role | AI Engineer | 0 | — | 1 |
| baseline_role | AI Platform Engineer | 0 | — | 1 |
| baseline_role | Analyst | 0 | — | 1 |
| baseline_role | Climate Analyst | 0 | — | 1 |
| baseline_role | Compliance Analyst | 0 | — | 1 |
| baseline_role | Credit Risk Manager | 0 | — | 1 |
| baseline_role | Credit Risk Underwriting Modeler | 0 | — | 1 |
| baseline_role | Data Administrator | 0 | — | 1 |
| baseline_role | Data Quality & BI QA Engineer | 0 | — | 1 |
| baseline_role | Database Administrator | 0 | — | 1 |
| baseline_role | Operations Specialist | 0 | — | 1 |
| baseline_role | Senior Data Analyst | 0 | — | 1 |
