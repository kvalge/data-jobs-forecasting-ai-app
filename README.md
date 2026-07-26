# Data Jobs Forecasting AI App

An LLM-powered application that extracts structured data from data/AI job postings and forecasts emerging role and skill trends.

## What it does

Paste a job posting's text into the app. An LLM (via OpenRouter) extracts structured fields — company, role title, responsibilities, requirements, application deadline, salary, location, work type (onsite/hybrid/remote), nondiscrimination disclaimer (y/n), and required skills — and saves them to a PostgreSQL database.

Once enough postings are collected, the app analyzes the data (most common roles, companies, skills, locations, salary ranges etc) to surface trends in the data/AI job market — and can point to forecasted momentum for specific skills or roles over the next 3, 6, or 12 months.

## Tech stack

- Python
- PostgreSQL
- SQLAlchemy + Alembic (schema migrations)
- OpenRouter API (free-tier LLM) for structured extraction
- Pydantic for schema validation

## Scope

Job postings are entered manually (copy-paste), covering a broad range of search terms: engineer, analyst, insener, analüütik, plus AI/data-related roles.

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

3. Copy `.env.example` to `.env` and fill in your own values (all are required):

   ```
   OPENROUTER_API_KEY=
   DATABASE_URL=
   MODEL=
   FALLBACK_MODEL=
   ```

   Example `DATABASE_URL` shape:

   ```
   postgresql+psycopg2://USER:PASSWORD@HOST:5432/DATABASE_NAME
   ```

   The app validates these at startup and exits with a clear error if any are missing or empty.

4. Apply database migrations (also runs automatically when you start the app):

   ```bash
   alembic upgrade head
   ```

## Run

From the **project root** (with the venv activated and `.env` configured):

```bash
python -m src.main
```

Startup applies Alembic migrations to `head`, then shows the CLI menu:

```
=== Job Market Analyzer ===
1. Add job posting
2. Run analysis
0. Exit
```

- **Add job posting:** enter a path to a UTF-8 `.txt` file containing the posting text (e.g. `data/sample_posting.txt`). The app extracts fields via the LLM and saves them to PostgreSQL. Re-submitting the same text skips extraction (deduplicated by content hash).
- **Run analysis:** not implemented yet (stub).

## Database migrations (Alembic)

Schema changes live under `alembic/versions/`. Prefer new Alembic revisions over editing the DB by hand.

| Situation | Command |
|-----------|---------|
| Fresh or outdated DB | `alembic upgrade head` (or just run `python -m src.main`) |
| DB already matches current models, but Alembic history is missing | `alembic stamp head` |
| Create a new revision after model changes | `alembic revision --autogenerate -m "describe change"` then review the file |

## Database schema notes

- Skills store a normalized unique `name` (lowercase) plus a `display_name` (first-seen casing) for reports/UI.
- Job postings store a unique `content_hash` (SHA-256 of stripped raw text). Re-submitting the same text returns the existing row and skips LLM extraction.
- Baseline migration: `alembic/versions/20260726_0001_baseline_schema.py`.

## Security notes

- API keys and database credentials are kept in `.env`, excluded from version control via `.gitignore`.
- LLM extraction output is validated against a strict schema (Pydantic) before being written to the database, to guard against malformed or injected input from posting text.
