# Prediction model results (database)

Auto-generated when you run **Prediction (database)** in the web UI or CLI. Rows within each model are ordered by predicted value (highest first).

- **Generated at:** 2026-09-04T16:13:12
- **Run id:** 33
- **Status:** completed_with_errors — Some model/target fits failed (often not enough monthly history), but other result rows were still saved. See warnings below.
- **Training data source:** Real database aggregates (PostgreSQL `job_postings` / skills)
- **Training window (months):** 12
- **Horizons:** 3
- **Models:** baseline, prophet
- **Elapsed (seconds):** 0.248

## How to read these results

- **Forecast models** (`prophet`, `arima`, `sarima`, `rf`, `hgb`): **Value** is the predicted posting count (or average salary for `salary_role`) for that future month. **Horizon** = months ahead (3 / 6 / 12). **Period** = calendar month-start of that forecast step.
- **Baseline** rows (if included): historical latest counts only (`horizon` 0) — not future forecasts.
- Tree models (`rf`, `hgb`) often stay flat on strong trends; prefer `arima` / `prophet` when history is long enough.

### Minimum history (months of data per series)

- `prophet`: ≥ 6
- `arima`: ≥ 8
- `sarima`: ≥ 8
- `rf`: ≥ 10
- `hgb`: ≥ 10

## Training data

Models were trained on series built from saved job postings in the database. Fake-data runs write to `model_results_fake.md`.

## Time per model

| Model | Seconds |
|-------|---------|
| `baseline` | 0.064 |
| `prophet` | 0.135 |

## Top roles & top skills (historical shortlist)

These lists are **not** the models' forecast of future popularity. Before forecasting, roles and skills are ranked by **historical posting volume** inside the training window (highest count first); the top K (default 15) become the forecast targets. Every selected model then runs on that same shortlist. Order below = historical volume, not predicted rank.

- **Top roles (historical):** Analyst, Senior Analyst, Data Analyst, Senior Data Analyst, Data Engineer, Senior Business Analyst, Lead Data Analyst, Data Entry Clerk, Database Administrator, AI Engineer, Business Analyst, Junior Analyst, Credit Risk Manager, Bioanalyst, AI Security Engineer
- **Top skills (historical):** Python, SQL, Tableau, R, Excel, Power BI, DBT, Looker, AWS, Google Sheets, Airflow, Snowflake, Jira, bash, Azure

## Warnings (soft-fail errors)

Individual model/target fits failed; other rows may still be present. The most common cause is **not enough monthly history** for that series.

| Target | Error | Why it matters |
|--------|-------|----------------|
| `prophet:role:AI Engineer` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:role:AI Security Engineer` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:role:Analyst` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:role:Bioanalyst` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:role:Business Analyst` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:role:Credit Risk Manager` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:role:Data Analyst` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:role:Data Engineer` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:role:Data Entry Clerk` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:role:Database Administrator` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:role:Junior Analyst` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:role:Lead Data Analyst` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:role:Senior Analyst` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:role:Senior Business Analyst` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:role:Senior Data Analyst` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:salary:AI Engineer` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:salary:AI Security Engineer` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:salary:Analyst` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:salary:Bioanalyst` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:salary:Business Analyst` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:salary:Credit Risk Manager` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:salary:Data Analyst` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:salary:Data Engineer` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:salary:Data Entry Clerk` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:salary:Database Administrator` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:salary:Junior Analyst` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:salary:Lead Data Analyst` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:salary:Senior Analyst` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:salary:Senior Business Analyst` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:salary:Senior Data Analyst` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:skill:AWS` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:skill:Airflow` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:skill:Azure` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:skill:DBT` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:skill:Excel` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:skill:Google Sheets` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:skill:Jira` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:skill:Looker` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:skill:Power BI` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:skill:Python` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:skill:R` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:skill:SQL` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:skill:Snowflake` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:skill:Tableau` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |
| `prophet:skill:bash` | Need at least 6 months of history for Prophet. | Need at least 6 months of history for Prophet. That role/skill/salary series does not span enough months in the training window (common on the database tab when few postings exist yet). Add more postings over time, widen the window if history exists, or choose baseline / models with lower minimums. |

## Model: `baseline`

Historical snapshot only (not a future forecast): latest count, moving averages, growth %, and linear trend direction.

| Type | Target | Horizon | Period | Value |
|------|--------|---------|--------|-------|
| baseline_skill | AWS | 0 | — | 11 |
| baseline_skill | Azure | 0 | — | 6 |
| baseline_skill | Python | 0 | — | 6 |
| baseline_skill | SQL | 0 | — | 6 |
| baseline_role | Analyst | 0 | — | 5 |
| baseline_role | Data Engineer | 0 | — | 5 |
| baseline_skill | bash | 0 | — | 4 |
| baseline_role | AI Engineer | 0 | — | 3 |
| baseline_role | Business Analyst | 0 | — | 3 |
| baseline_role | Data Entry Clerk | 0 | — | 3 |
| baseline_role | Senior Business Analyst | 0 | — | 3 |
| baseline_skill | DBT | 0 | — | 3 |
| baseline_skill | R | 0 | — | 3 |
| baseline_role | AI Security Engineer | 0 | — | 2 |
| baseline_role | Bioanalyst | 0 | — | 2 |
| baseline_role | Database Administrator | 0 | — | 2 |
| baseline_role | Junior Analyst | 0 | — | 2 |
| baseline_role | Senior Analyst | 0 | — | 2 |
| baseline_role | Senior Data Analyst | 0 | — | 2 |
| baseline_skill | Airflow | 0 | — | 2 |
| baseline_skill | Excel | 0 | — | 2 |
| baseline_skill | Snowflake | 0 | — | 2 |
| baseline_role | Credit Risk Manager | 0 | — | 1 |
| baseline_role | Data Analyst | 0 | — | 1 |
| baseline_role | Lead Data Analyst | 0 | — | 1 |
| baseline_skill | Google Sheets | 0 | — | 1 |
| baseline_skill | Jira | 0 | — | 1 |
| baseline_skill | Looker | 0 | — | 1 |
| baseline_skill | Power BI | 0 | — | 1 |
| baseline_skill | Tableau | 0 | — | 1 |
