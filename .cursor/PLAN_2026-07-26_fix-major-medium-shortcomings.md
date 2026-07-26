# Plan: Fix major + medium shortcomings (excl. analysis/forecasting)

**Created:** 2026-07-26  
**Status:** In progress (Step 3 done)  
**Scope:** Address major and medium issues identified in project review.  
**Out of scope:** Analysis / forecasting feature (menu option 2 remains a stub).

---

## Progress

| Step | Title | Status |
|------|--------|--------|
| 0 | Create this plan file | Done (2026-07-26) |
| 1 | Fail-fast config validation | Done (2026-07-26) |
| 2 | Session-per-operation + rollback | Done (2026-07-26) |
| 3 | Catch LLM/DB errors in CLI | Done (2026-07-26) |
| 4 | Map `created_at` on entity read | Pending |
| 5 | Safer skill `get_or_create` | Pending |
| 6 | Preserve skill display casing | Pending |
| 7 | Domain validation after LLM | Pending |
| 8 | Deduplicate job postings | Pending |
| 9 | Harden LLM client errors | Pending |
| 10 | Document how to run the app | Pending |
| 11 | Add Alembic migrations | Pending |
| 12 | Add focused tests | Pending |

After each completed step: update this table + notes below, propose a git commit message in chat, then ask permission before the next step.

---

## Steps (detail)

### Step 0 — Create this plan file
- Add dated plan under `.cursor/`.
- No application code changes.

### Step 1 — Fail-fast config validation
**Addresses:** Major #3  
- Validate required env vars at startup (`OPENROUTER_API_KEY`, `DATABASE_URL`, `MODEL`, `FALLBACK_MODEL`).
- Fail with a clear message if any are missing/empty.
- Avoid creating the DB engine with `None`.
- Update `.env.example` / `README.md` if messaging changes.

### Step 2 — Session-per-operation + rollback
**Addresses:** Major #2, #5  
- Do not reuse one SQLAlchemy session for the whole CLI lifetime.
- Open a session per add-posting (or per menu action), commit on success, rollback on failure, always close.
- Repositories keep using the injected session; ownership of lifecycle stays in `main` (or a small helper).

### Step 3 — Catch LLM/DB errors in CLI
**Addresses:** Major #1  
- In `add_posting_flow`, catch `RuntimeError` and DB/SQLAlchemy errors (in addition to `ValueError`).
- Print a clear user-facing message; do not leave an unhandled traceback for expected failures.

### Step 4 — Map `created_at` on entity read
**Addresses:** Major #4  
- In `JobPostingRepository._to_entity` (and skill mapping if needed), copy `created_at` from ORM → domain entity.
- Ensure loaded entities reflect DB timestamps, not a fresh `datetime.now()`.

### Step 5 — Safer skill `get_or_create`
**Addresses:** Medium #7  
- Handle unique-constraint race / `IntegrityError` on insert (retry lookup after conflict).
- Keep behavior correct for single-user CLI and safer if usage grows.

### Step 6 — Preserve skill display casing
**Addresses:** Medium #8  
- Keep normalized name for uniqueness/lookup (e.g. lowercase).
- Store a display form (first-seen casing) for future UI/reports, **or** an equivalent simple approach that does not permanently destroy casing.
- Prefer the smallest schema/code change that fits current architecture; document the choice in this plan when done.

### Step 7 — Domain validation after LLM
**Addresses:** Medium #10  
- After DTO validation, enforce business rules (e.g. non-empty `role_title`, `salary_min <= salary_max` when both set, drop/reject empty skill strings).
- Keep validation in BLL (or a small validator), not in the LLM client.

### Step 8 — Deduplicate job postings
**Addresses:** Medium #9  
- Add a stable fingerprint of `raw_text` (e.g. hash).
- Skip insert or return existing row when the same posting is submitted again.
- Update ORM/entity/DTO flow as needed; keep change minimal and documented.

### Step 9 — Harden LLM client errors
**Addresses:** Medium #11  
- Broaden handled failure cases where useful (clearer errors, safer fallback path).
- Still raise a clear `RuntimeError` (or similar) when both models fail.
- Do not log or print API keys.

### Step 10 — Document how to run the app
**Addresses:** Medium #14  
- Update `README.md` with exact run command(s) from project root (e.g. `python -m src.main`).
- Note venv, `.env`, and DB prerequisites briefly.

### Step 11 — Add Alembic migrations
**Addresses:** Medium #12  
- Add Alembic; baseline migration matching current schema (including any columns added in earlier steps).
- Prefer migrations over relying only on `create_all` going forward.
- Update `requirements.txt` and README.

### Step 12 — Add focused tests
**Addresses:** Medium #13  
- Add a small test suite (e.g. `pytest`) for: config validation, domain/business rules, posting dedup hash behavior, skill get_or_create (with test DB or mocks as appropriate).
- Mock LLM HTTP calls; do not call OpenRouter in tests.
- Update `requirements.txt` and README.

---

## Explicitly not in this plan

- Analysis / forecasting implementation
- Web UI
- Changing LLM provider (factory already supports swap)

---

## Notes log

- **2026-07-26:** Plan created. Implementation not started. Awaiting permission to begin Step 1.
- **2026-07-26 (Step 1):** Added `validate_config()` in `src/config.py`; `main()` calls it before DB init and prints a clear error on failure. DB engine is created lazily in `session.py` (reads `config.DATABASE_URL` at first use). OpenRouter client reads config via `import src.config as config` so values after validation are used. Updated `.env.example` and `README.md`.
- **2026-07-26 (Step 2):** Added `session_scope()` context manager (rollback on error, always close). `add_posting_flow` opens a fresh session per save instead of one session for the whole CLI. `JobPostingRepository.save` rolls back if `commit` fails.
- **2026-07-26 (Step 3):** `add_posting_flow` now catches `ValueError` (schema), `RuntimeError` (LLM), and `SQLAlchemyError` (DB) and prints clear messages instead of unhandled tracebacks.
