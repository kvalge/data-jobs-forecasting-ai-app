# Prediction model results (database)

Auto-generated when you run **Prediction (database)** in the web UI or CLI. Rows within each model are ordered by predicted value (highest first).

- **Generated at:** 2026-08-01T15:36:42
- **Run id:** 16
- **Status:** completed
- **Training data source:** Real database aggregates (PostgreSQL `job_postings` / skills)
- **Training window (months):** 12
- **Horizons:** 3
- **Models:** baseline
- **Elapsed (seconds):** 0.183

## Training data

Models were trained on series built from saved job postings in the database. Fake-data runs write to `model_results_fake.md`.

## Time per model

| Model | Seconds |
|-------|---------|
| `baseline` | 0.092 |

## Top roles & top skills (historical shortlist)

These lists are **not** the models' forecast of future popularity. Before forecasting, roles and skills are ranked by **historical posting volume** inside the training window (highest count first); the top K (default 15) become the forecast targets. Every selected model then runs on that same shortlist. Order below = historical volume, not predicted rank.

- **Top roles (historical):** Data Analyst, Data Engineer, Central Operations Specialist, AI Security Engineer, AI Engineer, Business Information Data Architect, Compliance Data Analyst, Credit Risk Manager, Analyst, Customer Support Workforce Planning Specialist, Data Protection Manager, Data Quality & BI QA Engineer, Data Warehouse Developer, Database Administrator, DevOps Engineer
- **Top skills (historical):** Python, SQL, Tableau, Looker, R, bash, Power BI, Java, Excel, DBT, AWS, Linux, PowerShell, KNIME, English

## Model: `baseline`

| Type | Target | Horizon | Period | Value |
|------|--------|---------|--------|-------|
| baseline_skill | Python | 0 | — | 6 |
| baseline_skill | SQL | 0 | — | 6 |
| baseline_skill | Power BI | 0 | — | 4 |
| baseline_skill | DBT | 0 | — | 3 |
| baseline_skill | Linux | 0 | — | 3 |
| baseline_role | AI Security Engineer | 0 | — | 2 |
| baseline_role | Data Analyst | 0 | — | 2 |
| baseline_skill | AWS | 0 | — | 2 |
| baseline_skill | English | 0 | — | 2 |
| baseline_skill | Java | 0 | — | 2 |
| baseline_skill | KNIME | 0 | — | 2 |
| baseline_skill | R | 0 | — | 2 |
| baseline_skill | Tableau | 0 | — | 2 |
| baseline_role | AI Engineer | 0 | — | 1 |
| baseline_role | Analyst | 0 | — | 1 |
| baseline_role | Business Information Data Architect | 0 | — | 1 |
| baseline_role | Central Operations Specialist | 0 | — | 1 |
| baseline_role | Compliance Data Analyst | 0 | — | 1 |
| baseline_role | Credit Risk Manager | 0 | — | 1 |
| baseline_role | Customer Support Workforce Planning Specialist | 0 | — | 1 |
| baseline_role | Data Engineer | 0 | — | 1 |
| baseline_role | Data Protection Manager | 0 | — | 1 |
| baseline_role | Data Quality & BI QA Engineer | 0 | — | 1 |
| baseline_role | Data Warehouse Developer | 0 | — | 1 |
| baseline_role | Database Administrator | 0 | — | 1 |
| baseline_role | DevOps Engineer | 0 | — | 1 |
| baseline_skill | Excel | 0 | — | 1 |
| baseline_skill | Looker | 0 | — | 1 |
| baseline_skill | PowerShell | 0 | — | 1 |
| baseline_skill | bash | 0 | — | 1 |
