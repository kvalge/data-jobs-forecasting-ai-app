# Project Summary: Data Jobs Forecasting AI App

## What this project is

A **portfolio / WIP Python app** that:

1. Accepts raw job posting text (CLI `.txt` path, or web paste / `.txt` upload)
2. Uses an **LLM via OpenRouter** to extract structured fields
3. Validates with **Pydantic** plus domain rules
4. Translates role titles and skills to English (glossary first, then LLM)
5. Saves postings and skills into **PostgreSQL** (SQLAlchemy + Alembic)
6. Offers a **Flask UI** to review/edit postings, run descriptive analysis, and run forecasts
7. Runs **descriptive analysis** (top companies/roles/skills, salary stats) and PNG chart export
8. Runs **time series prediction** (baseline + Prophet/SARIMA/ARIMA/RF/HGB) on fake series today, with a switch for future DB aggregates

**Stack:** Python, PostgreSQL, SQLAlchemy, Alembic, Flask + Jinja2, OpenRouter API, Pydantic, pandas/numpy/scikit-learn/statsmodels/Prophet, matplotlib, `python-dotenv`, `requests`, pytest

**Architecture:** layered CLI/Web → BLL → Domain/DTO → DAL / LLM / prediction

```
src/
├── main.py                 # CLI entry (python -m src.main)
├── config.py               # env + validate_config()
├── bll/                    # business logic / orchestration
├── dal/                    # SQLAlchemy models, session, repositories
├── domain/                 # pure entities + hash helper
├── dto/                    # LLM extraction schema
├── llm/                    # OpenRouter extract/translate + error messages
├── prediction/             # data sources, baseline, forecast model adapters
└── web/                    # Flask UI (python -m src.web)
alembic/                    # migrations
scripts/                    # fake job-market generator
docs/analysis/              # analysis PNG charts
docs/prediction/            # exported model_results.md
glossary/original_en.tsv    # original → English label glossary
tests/                      # pytest suite
```

---

## File-by-file

### Root

| File / folder | Role |
|---------------|------|
| `README.md` | Setup, CLI/web run, analysis charts, prediction notes, migrations |
| `requirements.txt` | Core stack + Flask, matplotlib, pandas, sklearn, statsmodels, prophet |
| `.env.example` | API/DB/models/`SECRET_KEY`/`PREDICTION_DATA_SOURCE` |
| `.gitignore` | `venv/`, `.env`, caches, `data/`, pytest artifacts |
| `PROJECT_SUMMARY.md` | This document |
| `pytest.ini` | `pythonpath = .`, `testpaths = tests` |
| `alembic.ini` | Alembic config (URL injected from `.env`) |
| `glossary/original_en.tsv` | User-corrected original → English pairs (no en→en) |
| `scripts/generate_fake_job_market.py` | Builds `data/fake/` series for forecasting |
| `docs/prediction/model_results.md` | Latest prediction export (training source + results) |
| `.cursor/` | Agent rules and implementation plans |

### Entry & config

| File | Role |
|------|------|
| `src/main.py` | CLI menu; posting ingest + prediction prompts |
| `src/config.py` | Loads `.env`; `validate_config()`; `PREDICTION_DATA_SOURCE` |
| `src/web/__main__.py` | Runs Flask app (`python -m src.web`) |
| `src/web/__init__.py` | `create_app()` — blueprints for postings, analysis, prediction |

### Business logic (`src/bll/`)

| File | Role |
|------|------|
| `posting_ingest.py` | Shared CLI/web entry: session → `ExtractionService.extract_and_save` |
| `extraction_service.py` | Dedup by hash → LLM extract → validate → translate EN → save |
| `job_posting_validator.py` | Domain rules (non-empty title, salary range, drop blank skills) |
| `glossary.py` | Lookup + save user-corrected original→English pairs (skip en→en) |
| `analysis_service.py` | Descriptive aggregates (top companies/roles/skills, salary stats) |
| `chart_export.py` | matplotlib PNGs under `docs/analysis/` |
| `prediction_service.py` | Orchestrates baseline + forecast models; timings; persist run |
| `prediction_export.py` | Writes `docs/prediction/model_results.md` |

### DTO (`src/dto/`)

| File | Role |
|------|------|
| `job_posting_extraction_dto.py` | Pydantic schema for LLM JSON (incl. country/city, skills, etc.) |

### Domain (`src/domain/`)

| File | Role |
|------|------|
| `base_entity.py` | Shared `id`, `created_at` |
| `job_posting_entity.py` | Posting model (`role_title_en`, `skills` / `skills_en`, `content_hash`, …) |
| `skill_entity.py` | `name`, `display_name`, `display_name_en` |
| `work_type.py` | `onsite` / `hybrid` / `remote` / `unknown` |
| `posting_hash.py` | SHA-256 of stripped raw text for dedup |

### Data access (`src/dal/`)

| File | Role |
|------|------|
| `models.py` | ORM: postings, skills, `forecast_runs`, `forecast_results` |
| `session.py` | Lazy engine, `session_scope()`, `init_db()` → Alembic upgrade head |
| `base_repository.py` | Abstract CRUD |
| `job_posting_repository.py` | Save/get/delete; `update_review_fields` for UI edits |
| `skill_repository.py` | `get_or_create` by lowercase English `name`; savepoint on unique race |
| `forecast_repository.py` | Persist/list prediction runs and results |

### Prediction (`src/prediction/`)

| File | Role |
|------|------|
| `data_source.py` | Protocol + `get_data_source()` factory |
| `fake_file_source.py` | Loads monthly/weekly aggregates from `data/fake/` |
| `database_source.py` | Future DB aggregates (not implemented yet) |
| `baseline/` | MA, growth, market share, linear trend |
| `models/` | Prophet, SARIMA, ARIMA, RF, HGB adapters |

### LLM (`src/llm/`)

| File | Role |
|------|------|
| `base_llm_client.py` | Abstract `extract(posting_text) -> dict` |
| `openrouter_client.py` | Extraction chat completions; primary then fallback model |
| `translation.py` | Glossary-first English translation via OpenRouter |
| `error_messages.py` | User-facing messages for 429 / API key / timeout / connection |
| `llm_client_factory.py` | Returns `OpenRouterClient` |

### Web (`src/web/`)

| File | Role |
|------|------|
| `routes/postings.py` | `GET/POST /` ingest; `GET/POST /postings/<id>/edit` review/update |
| `routes/analysis.py` | `GET/POST /analysis` descriptive queries + chart export |
| `routes/prediction.py` | `GET/POST /prediction` forecast UI |
| `templates/base.html` | Layout, nav, flash area, CSS link |
| `templates/postings/new.html` | Paste + file upload form |
| `templates/postings/edit.html` | Editable extracted fields + English skills |
| `templates/analysis.html` | Analysis form + result tables |
| `templates/prediction.html` | Prediction form + run summary (incl. shortlist meaning) |
| `static/css/main.css` | Navy / dark red / dark gray / light gray design tokens |

### Migrations & tests

| Path | Role |
|------|------|
| `alembic/versions/20260726_0001_…` | Baseline schema |
| `alembic/versions/20260726_0002_…` | `country`, `city` |
| `alembic/versions/20260726_0003_…` | `role_title_en`, `display_name_en` |
| `alembic/versions/20260726_0004_…` | `forecast_runs`, `forecast_results` |
| `tests/` | Config, ingest, analysis, prediction, Flask routes, exports |

---

## Process flow (add posting)

```mermaid
flowchart TD
    A[CLI or Flask UI] --> B[validate_config + init_db Alembic]
    B --> C[posting_ingest.ingest_posting_text]
    C --> D[content_hash lookup]
    D -->|exists| E[Return existing entity]
    D -->|new| F[OpenRouterClient.extract]
    F --> G[Pydantic DTO + domain validator]
    G --> H[Translate role_title_en + skills_en]
    H --> I[JobPostingRepository.save]
    I --> J[Skill get_or_create by English name]
    J --> K[Commit]
    K --> L{UI?}
    L -->|web| M[Redirect to edit/review page]
    L -->|CLI| N[Print saved / already-saved message]
```

### Step detail

1. **Startup** — validate env; Alembic migrates to `head`.
2. **Input** — CLI: file path. Web: paste and/or `.txt` upload (file wins if present).
3. **Dedup** — SHA-256 of stripped text; if known, skip LLM and return existing row.
4. **LLM extraction** — fixed JSON schema; primary model then fallback.
5. **Validation** — Pydantic schema, then domain rules.
6. **Translation** — glossary lookup, else LLM; on failure keep original text.
7. **Persistence** — posting + skills (unique on lowercase English name) + M2M links.
8. **Web only** — open review page; if user corrects translations, save real original→English pairs to glossary (skip English→English).

### Descriptive analysis flow

1. Web `/analysis` — choose companies / roles / salary / skills and top N.
2. `analysis_service` queries PostgreSQL; null salaries excluded per metric.
3. Results shown as tables; matching PNGs written to `docs/analysis/` (README embeds them).

### Prediction / forecasting flow

1. CLI menu 2 or web `/prediction` — choose training window (12/24/36), horizons (3/6/12), models (one/some/all).
2. Data source from `PREDICTION_DATA_SOURCE`: **`fake`** (default, `data/fake/` aggregates) or **`database`** (stub until implemented).
3. Historical top-K roles/skills by posting volume become forecast targets (UI labels these “Top roles / Top skills”; not model ranking).
4. Baseline + selected models forecast role demand, skill demand, and avg salary per role.
5. Soft-fail per series; save `forecast_runs` / `forecast_results`; export `docs/prediction/model_results.md`.

---

## Data flow (order of processing)

```
raw posting text (str)
  → content_hash (optional short-circuit)
    → dict (LLM JSON)
      → JobPostingExtractionDTO
        → domain validation
          → JobPostingEntity (+ role_title_en, skills_en)
            → JobPostingORM + SkillORM (+ glossary TSV)
              → entity with id (CLI print or web edit form)
```

| # | Where | What happens |
|---|--------|----------------|
| 1 | CLI / web route | Obtain UTF-8 posting text |
| 2 | `ingest_posting_text` | Open `session_scope`, call extraction service |
| 3 | `ExtractionService` | Hash lookup; skip LLM if duplicate |
| 4 | `OpenRouterClient.extract` | Primary then fallback model |
| 5 | DTO + `validate_extraction_dto` | Schema + business rules |
| 6 | Translator + glossary | English role title and skills (glossary first) |
| 7 | Repository `save` | Insert posting; `get_or_create` skills; commit |
| 8 | Web edit (optional) | `update_review_fields`; glossary only for corrected non-identity translations |

### Field mapping (high level)

| Field | Source | Notes |
|-------|--------|--------|
| company, role, responsibilities, requirements | LLM | `role_title` required |
| `role_title_en` | glossary / translate | Same as title if already English |
| salary, deadline, location, country, city | LLM | optional |
| `work_type`, nondiscrimination flag | LLM | enum / bool |
| `skills` / `skills_en` | LLM + translate | DB skill `name` = lowercase English |
| `display_name` / `display_name_en` | first-seen original + English | on `skills` |
| `content_hash`, `raw_text`, `date_added` | app | not from LLM inventively |

---

## Data model (simplified)

- **job_postings** — company, role_title, role_title_en, responsibilities, requirements, deadline, salary min/max/currency, location, country, city, work_type, nondiscrimination flag, date_added, raw_text, content_hash (unique), created_at
- **skills** — unique `name` (lowercase English), `display_name`, `display_name_en`
- **job_posting_skills** — many-to-many link
- **forecast_runs** — training window, horizons, models, status, meta (incl. timings, data source)
- **forecast_results** — per run/model/target/horizon predicted values

---

## How to run (quick)

```bash
# Fake series for prediction (optional refresh)
python scripts/generate_fake_job_market.py

# CLI
python -m src.main

# Web UI
python -m src.web

# Migrations (also on app startup)
alembic upgrade head

# Tests
pytest
```

---

## Current status vs goals

| Capability | Status |
|------------|--------|
| Manual `.txt` / paste + LLM extraction | Done |
| Schema + domain validation + Postgres save | Done |
| Dedup by content hash | Done |
| English titles/skills + glossary | Done |
| Flask insert + review/edit UI | Done |
| Clearer AI error messages (429, key, network) | Done |
| Alembic migrations + pytest | Done |
| Descriptive analysis UI + README charts | Done |
| Forecasting (fake data source + multi-model + persist/export) | Done |
| Forecasting on live DB aggregates | Stub (`DatabaseSource` / `PREDICTION_DATA_SOURCE=database`) |
