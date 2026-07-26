# Data Jobs Forecasting AI App

An LLM-powered application that extracts structured data from data/AI job postings and forecasts emerging role and skill trends.

## What it does

Paste a job posting's text into the app (CLI or web UI). An LLM (via OpenRouter) extracts structured fields — company, role title, responsibilities, requirements, application deadline, salary, location, work type (onsite/hybrid/remote), nondiscrimination disclaimer (y/n), and required skills — and saves them to a PostgreSQL database.

Once enough postings are collected, the app analyzes the data (most common roles, companies, skills, locations, salary ranges etc) to surface trends in the data/AI job market — and can point to forecasted momentum for specific skills or roles over the next 3, 6, or 12 months.

## Sample analyses

Charts below are generated from the database when you run **Analysis** in the web UI (`/analysis`). PNGs are written to `docs/analysis/` and overwritten on each run.

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
- Flask + Jinja2 (web UI for inserting postings and running analyses)
- OpenRouter API (free-tier LLM) for structured extraction
- Pydantic for schema validation
- matplotlib (analysis chart PNGs for the UI export / README)

## Scope

Job postings are entered manually (copy-paste or `.txt` upload), covering a broad range of search terms: engineer, analyst, insener, analüütik, plus AI/data-related roles.

## Project status

🚧 Work in progress — built step by step as a portfolio project.

## Prerequisites

- Python 3.10+ recommended
- A running PostgreSQL database you can connect to
- An OpenRouter API key and model IDs for primary + fallback extraction

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
   OPENROUTER_API_KEY=
   DATABASE_URL=
   MODEL=
   FALLBACK_MODEL=
   SECRET_KEY=
   ```

   - `OPENROUTER_API_KEY`, `DATABASE_URL`, `MODEL`, and `FALLBACK_MODEL` are required (non-empty).
   - `SECRET_KEY` is used by the Flask UI for sessions/flash messages. Set a long random value for real use (a dev default is used only if unset).

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
2. Run analysis
0. Exit
```

- **Add job posting:** enter a path to a UTF-8 `.txt` file. Re-submitting the same text skips extraction (content hash).
- **Run analysis:** not implemented yet (stub).

## Run — Web UI

```bash
python -m src.web
```

Then open the URL shown in the terminal (typically `http://127.0.0.1:5000/`).

- Paste posting text and/or upload a `.txt` file, then **Extract and save**.
- If a file is uploaded, it is used instead of the pasted text.
- After save you are taken to a **review/edit** page for company, titles, salary, work type, disclaimer, location/country/city, and English skills.
- Saving edits updates the database and appends original→English pairs to `glossary/original_en.tsv` (also used before LLM translation).
- Open **Analysis** (`/analysis`) to query top companies, top English roles, salary min/avg/max (nulls excluded), and top English skills. Results show on the page and refresh PNG charts under `docs/analysis/` (linked in [Sample analyses](#sample-analyses) above).
- Success, duplicate, and error messages appear as flash banners.
- The CLI remains fully functional alongside the web UI.

## Run tests

From the project root (venv activated):

```bash
pytest
```

Tests cover config validation, domain rules, content-hash dedup (LLM mocked), skill get-or-create, analysis aggregations (in-memory SQLite), and Flask insert/analysis routes (ingest/DB mocked). They do not call OpenRouter or require PostgreSQL.

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
- Later revisions: `20260726_0002` (country/city), `20260726_0003` (role_title_en, display_name_en).

## Security notes

- API keys and database credentials are kept in `.env`, excluded from version control via `.gitignore`.
- LLM extraction output is validated against a strict schema (Pydantic) before being written to the database, to guard against malformed or injected input from posting text.
