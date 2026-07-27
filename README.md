# Data Jobs Forecasting AI App

An LLM-powered application that extracts structured data from data/AI job postings and forecasts emerging role and skill trends.

## What it does

Paste a job posting's text into the app (CLI or web UI). An LLM (via OpenRouter, with local Ollama as last resort) extracts structured fields — company, role title (plus English), responsibilities, requirements, application deadline, salary, location, work type (onsite/hybrid/remote), nondiscrimination disclaimer (y/n), and required skills (plus English) — in **one successful API call** (extra OpenRouter models, then Ollama, only if earlier calls fail), then saves them to a PostgreSQL database.

Once enough postings are collected, the app analyzes the data (most common roles, companies, skills, locations, salary ranges etc) to surface trends in the data/AI job market — and can point to forecasted momentum for specific skills or roles over the next 3, 6, or 12 months.

## Sample analyses

[Latest prediction model results](docs/prediction/model_results.md)

Charts below are generated from the database when you run **Analysis** in the web UI (`/analysis`). PNGs are written to `docs/analysis/` and overwritten on each run. Prediction runs also refresh `docs/prediction/model_results.md` (includes whether models trained on **fake** `data/fake/` series or **database** aggregates, plus what “top roles / top skills” means).

### Top companies

![Top companies](docs/analysis/top_companies.png)

### Top roles (English)

![Top roles](docs/analysis/top_roles.png)

### Salary summary

![Salary summary](docs/analysis/salary_summary.png)

### Top skills (English)

![Top skills](docs/analysis/top_skills.png)

## Tech stack

- Python
- PostgreSQL
- SQLAlchemy + Alembic (schema migrations)
- Flask + Jinja2 (web UI for inserting postings, descriptive analysis, and prediction)
- OpenRouter API (free-tier LLM) for structured extraction, with local Ollama (`qwen3.5:latest`) when OpenRouter is exhausted
- Pydantic for schema validation
- matplotlib (analysis chart PNGs for the UI export / README)
- pandas / numpy / scikit-learn / statsmodels / Prophet (time series prediction)

## Scope

Job postings are entered manually (copy-paste or `.txt` upload), covering a broad range of search terms: engineer, analyst, insener, analüütik, plus AI/data-related roles.

## Project status

The planned functionalities have been implemented. Due to the small amount of real data, currently synthetically generated data is used for forecasting.

## Prerequisites

- Python 3.10+ recommended
- A running PostgreSQL database you can connect to
- An OpenRouter API key and model IDs for primary + fallback extraction
- Optional: [Ollama](https://ollama.com/) with `OLLAMA_MODEL` pulled (default `qwen3.5:latest`) for local fallback when OpenRouter is exhausted

## Setup

1. Clone the repo and create a virtual environment from the **project root**:

   ```bash
   python -m venv venv
   ```

   Activate it:

   - Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
   - Windows (cmd) / Git Bash: `source venv/Scripts/activate`
   - macOS / Linux: `source venv/bin/activate`

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in your own values:

   ```
   LLM_PROVIDER_MODE=openrouter_ollama
   OPENROUTER_API_KEY=
   DATABASE_URL=
   MODEL=
   FALLBACK_MODEL=
   FALLBACK_MODEL2=
   FALLBACK_MODEL3=
   SECRET_KEY=
   FLASK_ENV=development
   FLASK_HOST=127.0.0.1
   FLASK_DEBUG=false
   MAX_POSTING_CHARS=100000
   PREDICTION_DATA_SOURCE=fake
   OLLAMA_FALLBACK_ENABLED=true
   OLLAMA_BASE_URL=http://127.0.0.1:11434
   OLLAMA_MODEL=qwen3.5:latest
   OLLAMA_TIMEOUT_SECONDS=180
   ```

   - `LLM_PROVIDER_MODE`: `openrouter_ollama` (default) tries OpenRouter models then optional Ollama; `ollama_only` uses local Ollama only (no OpenRouter API key required).
   - `DATABASE_URL` is always required.
   - For `openrouter_ollama`: `OPENROUTER_API_KEY`, `MODEL`, and `FALLBACK_MODEL` are required (non-empty).
   - `FALLBACK_MODEL2` and `FALLBACK_MODEL3` are optional; when set, they are tried if earlier OpenRouter models fail or hit rate limits.
   - After **all** OpenRouter models fail (e.g. free-tier limits), the app tries local **Ollama** when `OLLAMA_FALLBACK_ENABLED=true` (default). In `ollama_only` mode, Ollama is the only provider. Requires Ollama running (`ollama serve`). `OLLAMA_TIMEOUT_SECONDS` defaults to 180.
   - `OLLAMA_BASE_URL` must be loopback by default (`127.0.0.1`, `localhost`, or `::1`) to avoid SSRF. Set `OLLAMA_ALLOW_REMOTE=true` only for a trusted remote Ollama.
   - `SECRET_KEY` is required for the Flask UI unless `FLASK_ENV=development` (known placeholders are rejected). Use a long random value for anything beyond trusted local use.
   - `FLASK_HOST` defaults to `127.0.0.1` (loopback). The app has **no authentication** — do not bind to `0.0.0.0` on an untrusted network.
   - `FLASK_DEBUG` defaults to `false`. Only enable for local debugging; never expose the debugger remotely.
   - `MAX_POSTING_CHARS` caps posting text before any LLM call (default `100000`). Oversized paste/upload is rejected early (stricter than the 1 MB upload byte limit).
   - `LLM_METADATA_LOG_ENABLED` / `LLM_METADATA_LOG_PATH` write privacy-safe NDJSON metadata per LLM attempt (provider, model, status, timing, tokens if available, fallback flag, validation result). Prompts and responses are never logged. Default path: `logs/llm_requests.ndjson`.
   - `PREDICTION_DATA_SOURCE` is optional (`fake` default). `database` is reserved but **rejected at startup** until `DatabaseSource` is implemented.
   Example `DATABASE_URL` shape:

   ```
   postgresql+psycopg2://USER:PASSWORD@HOST:5432/DATABASE_NAME
   ```

4. Apply database migrations (also runs automatically when you start the CLI or web app):

   ```bash
   alembic upgrade head
   ```

## Run — CLI

From the **project root** (venv activated, `.env` configured):

```bash
python -m src.main
```

```
=== Job Market Analyzer ===
1. Add job posting
2. Run prediction
0. Exit
```

- **Add job posting:** enter a path to a UTF-8 `.txt` file. Re-submitting the same text skips extraction (content hash).
- **Run prediction:** choose training window (12/24/36 months), horizons (3/6/12), and models (baseline, prophet, sarima, arima, rf, hgb). Results are saved to `forecast_runs` / `forecast_results`.

## Fake data for prediction

Prediction currently trains on synthetic market series under `data/fake/` (gitignored with the rest of `data/`). Generate or refresh with:

```bash
python scripts/generate_fake_job_market.py
```

This creates ~10 000 postings over 36 months (8–12 skills each), plus day / week / month aggregates for roles, skills, and totals. Live DB aggregates (`PREDICTION_DATA_SOURCE=database`) are not available yet — keep `fake` until `DatabaseSource` is implemented.

## Run — Web UI

```bash
python -m src.web
```

Then open the URL shown in the terminal (typically `http://127.0.0.1:5000/`). The server binds to **127.0.0.1** by default (`FLASK_HOST`) with the interactive debugger **off** (`FLASK_DEBUG=false`). There is no login — treat this as a local tool; do not expose it on a public interface without adding authentication.

- Paste posting text and/or upload a `.txt` file, then **Extract and save**.
- Uploads must be UTF-8 `.txt` (other extensions and binary content are rejected). Mutating forms are CSRF-protected.
- If a file is uploaded, it is used instead of the pasted text.
- After save you are taken to a **review/edit** page for company, titles, salary, work type, disclaimer, location/country/city, and English skills.
- Saving edits updates the database. If you correct a non-English → English translation on the review page, that pair is saved to `glossary/original_en.tsv` (English→English pairs are skipped; glossary is not filled on initial extract).
- Open **Analysis** (`/analysis`) to query top companies, top English roles, salary min/avg/max (nulls excluded), and top English skills. Results show on the page and refresh PNG charts under `docs/analysis/` (linked in [Sample analyses](#sample-analyses) above).
- Open **Prediction** (`/prediction`) to run baseline trend analysis and classical/ML forecasts for popular roles, skills, and average salary per role. Choose training window, horizons, and one/some/all models; outcomes are stored in PostgreSQL. The “Top roles / Top skills” lines on the results page are the **historical shortlist** used as forecast targets (by past posting volume), not the models’ predicted ranking.
- Success, duplicate, and error messages appear as flash banners.
- The CLI remains fully functional alongside the web UI.

## Run tests

From the project root (venv activated):

```bash
pytest
```

Tests cover config validation, domain rules, content-hash dedup (LLM mocked), OpenRouter model chain + Ollama fallback (HTTP mocked), skill get-or-create, analysis aggregations (in-memory SQLite), prediction baseline/models/orchestration (fake mini datasets; Flask prediction mocked), and Flask insert/analysis/prediction routes (ingest/DB mocked). They do not call OpenRouter, Ollama, or require PostgreSQL.

## Database migrations (Alembic)

Schema changes live under `alembic/versions/`. Prefer new Alembic revisions over editing the DB by hand.

| Situation | Command |
|-----------|---------|
| Fresh or outdated DB | `alembic upgrade head` (or start the CLI/web app) |
| DB already matches current models, but Alembic history is missing | `alembic stamp head` |
| Create a new revision after model changes | `alembic revision --autogenerate -m "describe change"` then review the file |

## Database schema notes

- Skills store a normalized unique `name` (lowercase English), `display_name` (first-seen original label), and `display_name_en` (English).
- Job postings store `role_title` plus `role_title_en` (English; same value when already English).
- Job postings store a unique `content_hash` (SHA-256 of stripped raw text). Re-submitting the same text returns the existing row and skips LLM extraction.
- Baseline migration: `alembic/versions/20260726_0001_baseline_schema.py`.
- Later revisions: `20260726_0002` (country/city), `20260726_0003` (role_title_en, display_name_en), `20260726_0004` (`forecast_runs` / `forecast_results`).

## Security notes

- API keys and database credentials are kept in `.env`, excluded from version control via `.gitignore`.
- LLM extraction output is validated against a strict schema (Pydantic) before being written to the database, to guard against malformed or injected input from posting text.
