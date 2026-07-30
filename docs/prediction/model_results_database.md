# Prediction model results (database)

Auto-generated when you run **Prediction (database)** in the web UI or CLI. Rows within each model are ordered by predicted value (highest first).

- **Generated at:** 2026-07-30T05:59:27
- **Run id:** 7
- **Status:** completed
- **Training data source:** Real database aggregates (PostgreSQL `job_postings` / skills)
- **Training window (months):** 12
- **Horizons:** 3
- **Models:** baseline
- **Elapsed (seconds):** 0.14

## Training data

Models were trained on series built from saved job postings in the database. Fake-data runs write to `model_results_fake.md`.

## Time per model

| Model | Seconds |
|-------|---------|
| `baseline` | 0.076 |

## Top roles & top skills (historical shortlist)

These lists are **not** the models' forecast of future popularity. Before forecasting, roles and skills are ranked by **historical posting volume** inside the training window (highest count first); the top K (default 15) become the forecast targets. Every selected model then runs on that same shortlist. Order below = historical volume, not predicted rank.

- **Top roles (historical):** Data Engineer, AI Security Engineer, System Administrator, Business Information Data Architect, Analyst, Central Operations Specialist, Cloud Security Engineer, Credit Risk Manager, Compliance Data Analyst, Customer Support Workforce Planning Specialist, Data Protection Manager, Database Administrator, Atlassian Platform Engineer, DevOps Engineer, Developer
- **Top skills (historical):** Python, SQL, Java, Networking, Kubernetes, English, bash, Tableau, AWS, Communication, Docker, Project management, Confluence, CI/CD, cloud

## Model: `baseline`

| Type | Target | Horizon | Period | Value |
|------|--------|---------|--------|-------|
| baseline_skill | Python | 0 | — | 20 |
| baseline_skill | SQL | 0 | — | 16 |
| baseline_skill | Java | 0 | — | 7 |
| baseline_skill | Kubernetes | 0 | — | 5 |
| baseline_skill | Networking | 0 | — | 5 |
| baseline_skill | AWS | 0 | — | 4 |
| baseline_skill | Communication | 0 | — | 4 |
| baseline_skill | English | 0 | — | 4 |
| baseline_skill | Tableau | 0 | — | 4 |
| baseline_skill | bash | 0 | — | 4 |
| baseline_role | Data Engineer | 0 | — | 3 |
| baseline_skill | CI/CD | 0 | — | 3 |
| baseline_skill | Confluence | 0 | — | 3 |
| baseline_skill | Docker | 0 | — | 3 |
| baseline_skill | Project management | 0 | — | 3 |
| baseline_skill | cloud | 0 | — | 3 |
| baseline_role | AI Security Engineer | 0 | — | 2 |
| baseline_role | System Administrator | 0 | — | 2 |
| baseline_role | Analyst | 0 | — | 1 |
| baseline_role | Atlassian Platform Engineer | 0 | — | 1 |
| baseline_role | Business Information Data Architect | 0 | — | 1 |
| baseline_role | Central Operations Specialist | 0 | — | 1 |
| baseline_role | Cloud Security Engineer | 0 | — | 1 |
| baseline_role | Compliance Data Analyst | 0 | — | 1 |
| baseline_role | Credit Risk Manager | 0 | — | 1 |
| baseline_role | Customer Support Workforce Planning Specialist | 0 | — | 1 |
| baseline_role | Data Protection Manager | 0 | — | 1 |
| baseline_role | Database Administrator | 0 | — | 1 |
| baseline_role | DevOps Engineer | 0 | — | 1 |
| baseline_role | Developer | 0 | — | 1 |
