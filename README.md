# Data Jobs Forecasting AI App

An LLM-powered application that extracts structured data from data/AI job postings and forecasts emerging role and skill trends.

## What it does

Paste a job posting's text into the app. An LLM (via OpenRouter) extracts structured fields — company, role title, responsibilities, requirements, application deadline, salary, location, work type (onsite/hybrid/remote), nondiscrimination disclaimer (y/n), and required skills — and saves them to a PostgreSQL database.

Once enough postings are collected, the app analyzes the data (most common roles, companies, skills, locations, salary ranges etc) to surface trends in the data/AI job market — and can point to forecasted momentum for specific skills or roles over the next 3, 6, or 12 months.

## Tech stack

- Python
- PostgreSQL
- OpenRouter API (free-tier LLM) for structured extraction
- Pydantic for schema validation

## Scope

Job postings are entered manually (copy-paste), covering a broad range of search terms: engineer, analyst, insener, analüütik, plus AI/data-related roles.

## Project status

🚧 Work in progress — built step by step as a portfolio project.

## Setup

1. Clone the repo and create a virtual environment:
   \`\`\`bash
   python -m venv venv
   source venv/Scripts/activate
   \`\`\`
2. Install dependencies:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`
3. Copy `.env.example` to `.env` and fill in your own values (all are required):
   \`\`\`
   OPENROUTER_API_KEY=
   DATABASE_URL=
   MODEL=
   FALLBACK_MODEL=
   \`\`\`
   The app validates these at startup and exits with a clear error if any are missing or empty.

## Database schema notes

- Skills store a normalized unique `name` (lowercase) plus a `display_name` (first-seen casing) for reports/UI.
- `create_all` only creates missing tables; it does **not** add new columns to existing tables. If you already have a `skills` table without `display_name`, run:
  ```sql
  ALTER TABLE skills ADD COLUMN display_name VARCHAR;
  ```
  Or drop/recreate the tables in a throwaway local database. Migrations (Alembic) are planned separately.

## Security notes

- API keys and database credentials are kept in `.env`, excluded from version control via `.gitignore`.
- LLM extraction output is validated against a strict schema (Pydantic) before being written to the database, to guard against malformed or injected input from posting text.

