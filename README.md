# Data Jobs Forecasting AI App

An LLM-powered application that extracts structured data from data/AI job postings and forecasts emerging role and skill trends.

## What it does

Paste a job posting's text into the app (CLI or web UI). An LLM (via OpenRouter) extracts structured fields — company, role title, responsibilities, requirements, application deadline, salary, location, work type (onsite/hybrid/remote), nondiscrimination disclaimer (y/n), and required skills — and saves them to a PostgreSQL database.

Once enough postings are collected, the app analyzes the data (most common roles, companies, skills, locations, salary ranges etc) to surface trends in the data/AI job market — and can point to forecasted momentum for specific skills or roles over the next 3, 6, or 12 months.

## Tech stack

- Python
- PostgreSQL
- SQLAlchemy + Alembic (schema migrations)
- Flask + Jinja2 (web UI for inserting postings)
- OpenRouter API (free-tier LLM) for structured extraction
- Pydantic for schema validation

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
- Success, duplicate, and error messages appear as flash banners.
- The CLI remains fully functional alongside the web UI.

## Run tests

From the project root (venv activated):

```bash
pytest
```

Tests cover config validation, domain rules, content-hash dedup (LLM mocked), skill get-or-create, and Flask insert routes (ingest mocked). They do not call OpenRouter or require PostgreSQL.

## Database migrations (Alembic)

Schema changes live under `alembic/versions/`. Prefer new Alembic revisions over editing the DB by hand.

| Situation | Command |
|-----------|---------|
| Fresh or outdated DB | `alembic upgrade head` (or start the CLI/web app) |
| DB already matches current models, but Alembic history is missing | `alembic stamp head` |
| Create a new revision after model changes | `alembic revision --autogenerate -m "describe change"` then review the file |

## Database schema notes

- Skills store a normalized unique `name` (lowercase) plus a `display_name` (first-seen casing) for reports/UI.
- Job postings store a unique `content_hash` (SHA-256 of stripped raw text). Re-submitting the same text returns the existing row and skips LLM extraction.
- Baseline migration: `alembic/versions/20260726_0001_baseline_schema.py`.
- `job_postings` also has optional `country` and `city` (migration `20260726_0002`).

## Security notes

- API keys and database credentials are kept in `.env`, excluded from version control via `.gitignore`.
- LLM extraction output is validated against a strict schema (Pydantic) before being written to the database, to guard against malformed or injected input from posting text.
