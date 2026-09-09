# Prediction model results (database)

Auto-generated when you run **Prediction (database)** in the web UI or CLI. Rows within each model are ordered by predicted value (highest first).

- **Generated at:** 2026-09-09T15:33:04
- **Run id:** 34
- **Status:** completed — All selected model/target fits succeeded.
- **Training data source:** Real database aggregates (PostgreSQL `job_postings` / skills)
- **Training window (months):** 12
- **Horizons:** 3
- **Models:** baseline
- **Elapsed (seconds):** 0.31

## How to read these results

**Baseline only:** these rows are a **historical snapshot**, not a prediction of future months. `horizon` is `0` and `period` is empty. **Value** = latest monthly posting count in the training window. Metrics (when present in the DB) include moving averages, growth %, and trend direction (up / down / flat).

## Training data

Models were trained on series built from saved job postings in the database. Fake-data runs write to `model_results_fake.md`.

## Time per model

| Model | Seconds |
|-------|---------|
| `baseline` | 0.145 |

## Top roles & top skills (historical shortlist)

These lists are **not** the models' forecast of future popularity. Before forecasting, roles and skills are ranked by **historical posting volume** inside the training window (highest count first); the top K (default 15) become the forecast targets. Every selected model then runs on that same shortlist. Order below = historical volume, not predicted rank.

- **Top roles (historical):** Analyst, Senior Analyst, Data Analyst, Senior Data Analyst, Data Engineer, Database Administrator, Senior Business Analyst, Business Analyst, Lead Data Analyst, Data Entry Clerk, AI Engineer, Data Processor, Credit Risk Manager, AI Security Engineer, Data Quality & BI QA Engineer
- **Top skills (historical):** SQL, Python, R, Excel, Tableau, Power BI, Looker, DBT, AWS, Google Sheets, Airflow, Snowflake, Azure, Oracle, Jira

## Model: `baseline`

Historical snapshot only (not a future forecast): latest count, moving averages, growth %, and linear trend direction.

| Type | Target | Horizon | Period | Value |
|------|--------|---------|--------|-------|
| baseline_skill | SQL | 0 | — | 15 |
| baseline_skill | AWS | 0 | — | 11 |
| baseline_skill | Python | 0 | — | 10 |
| baseline_role | Analyst | 0 | — | 7 |
| baseline_skill | Excel | 0 | — | 6 |
| baseline_skill | R | 0 | — | 6 |
| baseline_skill | Power BI | 0 | — | 5 |
| baseline_skill | DBT | 0 | — | 4 |
| baseline_role | AI Engineer | 0 | — | 3 |
| baseline_role | Business Analyst | 0 | — | 3 |
| baseline_role | Data Analyst | 0 | — | 3 |
| baseline_role | Data Entry Clerk | 0 | — | 3 |
| baseline_role | Senior Analyst | 0 | — | 3 |
| baseline_role | Senior Business Analyst | 0 | — | 3 |
| baseline_role | Senior Data Analyst | 0 | — | 3 |
| baseline_skill | Airflow | 0 | — | 3 |
| baseline_skill | Looker | 0 | — | 3 |
| baseline_skill | Snowflake | 0 | — | 3 |
| baseline_skill | Tableau | 0 | — | 3 |
| baseline_role | AI Security Engineer | 0 | — | 2 |
| baseline_role | Data Processor | 0 | — | 2 |
| baseline_skill | Google Sheets | 0 | — | 2 |
| baseline_role | Credit Risk Manager | 0 | — | 1 |
| baseline_role | Data Engineer | 0 | — | 1 |
| baseline_role | Data Quality & BI QA Engineer | 0 | — | 1 |
| baseline_role | Database Administrator | 0 | — | 1 |
| baseline_role | Lead Data Analyst | 0 | — | 1 |
| baseline_skill | Azure | 0 | — | 1 |
| baseline_skill | Jira | 0 | — | 1 |
| baseline_skill | Oracle | 0 | — | 1 |
