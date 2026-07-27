# Plan: Architecture and maintainability refactors

**Created:** 2026-07-27  
**Status:** Complete (all steps 0–12 done, 2026-07-27)  
**Scope:** Improve layer honesty, session/LLM boundaries, prediction orchestration size/cost, and a few maintainability hotspots found in a full-project architecture review after the security/LLM hardening plan completed. Prefer small, testable steps that keep CLI/web behavior the same unless a step explicitly changes defaults.  
**Out of scope:** Full multi-user auth, implementing live `DatabaseSource` end-to-end (quarantine/clarify only), prediction/analysis UI redesign, changing OpenRouter/Ollama provider stack, micro-optimizations unrelated to structure, Docker/K8s packaging.

**Context:** Prior `.cursor` plans covered config/sessions/dedup, Flask insert UI, analysis UI, prediction/forecasting, and harden-security-llm-gaps (complete). This plan is the next maintainability backlog.

---

## Progress

| Step | Title | Status |
|------|--------|--------|
| 0 | Create this plan file | Done (2026-07-27) |
| 1 | Close DB session before LLM; reopen for save | Done (2026-07-27) |
| 2 | Move analysis SQL into DAL (query repo) | Done (2026-07-27) |
| 3 | Split `prediction_service` orchestration | Done (2026-07-27) |
| 4 | Safer prediction defaults / cost staging | Done (2026-07-27) |
| 5 | Shared LLM prompt + response parsing | Done (2026-07-27) |
| 6 | Glossary cache + skill resolution batching | Done (2026-07-27) |
| 7 | Thin BLL facades for edit / analysis / forecast history | Done (2026-07-27) |
| 8 | Forecast `target_type` / status constants or enums | Done (2026-07-27) |
| 9 | Quarantine unfinished `DatabaseSource` surface | Done (2026-07-27) |
| 10 | Align repo transaction rules + slim `BaseRepository` | Done (2026-07-27) |
| 11 | Config load/validate cleanup (parse-once) | Done (2026-07-27) |
| 12 | Docs/tests layout polish (optional mirrors, DTOs) | Done (2026-07-27) |

After each completed step: update this table + notes below, propose a git commit message in chat, then ask permission before the next step.

---

## Findings summary (why these steps)

### Architecture / layering

| Severity | Issue | Evidence |
|----------|--------|----------|
| High | DB `session_scope` wraps hash check **and** LLM **and** save — connection held for OpenRouter/Ollama latency | `src/bll/posting_ingest.py` → `ExtractionService.extract_and_save` |
| High | Analysis “BLL” runs SQLAlchemy ORM queries directly (skips repositories) | `src/bll/analysis_service.py` imports `JobPostingORM` / `SkillORM` |
| High | `prediction_service.py` is a god orchestrator (~400 LOC): ranking, baseline, all models, persist, export | `src/bll/prediction_service.py` |
| Medium | Web routes open sessions and call repos for edit / analysis / recent runs (uneven vs ingest BLL) | `src/web/routes/postings.py`, `analysis.py`, `prediction.py` |
| Medium | Ollama constructs `OpenRouterClient` only to call private `_parse_message_content` | `src/llm/ollama_client.py` |
| Medium | Unfinished `DatabaseSource` vs fail-closed config / docs drift | `src/prediction/database_source.py`, `data_source.py`, `config.validate_config` |
| Medium | `JobPostingRepository.save` calls `session.rollback()` despite flush-only / `session_scope` ownership | `src/dal/job_posting_repository.py` |
| Low | `BaseRepository` forces unused `get_all` / `delete`; `ForecastRepository` skips the ABC and returns ORM to templates | `src/dal/base_repository.py`, `forecast_repository.py` |

### Maintainability / cost

| Severity | Issue |
|----------|--------|
| High | Default “all models” prediction is multiplicative (models × series × double-fit in classical) — slow demos |
| Medium | Glossary reloads full TSV per `lookup_english`; skill `get_or_create` is N queries per posting |
| Medium | Magic strings for forecast `target_type` / run `status` |
| Medium | `config.py` import-time `int()` / dual global rewrite vs `validate_config` |
| Low | Flat `tests/` vs layered `src/`; dual docs (`README` + `PROJECT_SUMMARY`) drift risk |

### What is already in good shape (do not “fix”)

- Clear CLI/Web → BLL → domain/dto + dal + llm + prediction intent
- Shared ingest path; LLM factory + `OpenRouterWithOllamaFallback` composition
- Content-hash dedup before LLM; single extract JSON (no per-skill translate API)
- Domain entities framework-free; Alembic migrations; privacy-safe LLM metadata; live-LLM HTTP guard in tests

---

## Steps (detail)

### Step 0 — Create this plan file
- Add dated plan under `.cursor/`.
- No application code changes.

### Step 1 — Close DB session before LLM; reopen for save
**Addresses:** High — pool / idle-in-transaction under web uploads  
- Pattern: short session for content-hash lookup → LLM outside any session → short session for validate + save.
- Keep existing IntegrityError / dedup handling for rare races.
- Tests: ingest still dedups; oversized reject still happens before session/LLM; mocked LLM path does not leave a session open across the mock call (assert via structure/unit test).

### Step 2 — Move analysis SQL into DAL
**Addresses:** High — BLL/DAL layer honesty  
- Introduce e.g. `AnalysisRepository` (or query module under `dal/`) owning company/role/salary/skill aggregates.
- `analysis_service` becomes a thin façade (clamp top-N, call repo, optional chart orchestration stays BLL or route).
- Keep result dict shapes stable for web + chart export.

### Step 3 — Split `prediction_service` orchestration
**Addresses:** High — god module / testability  
- Extract helpers or modules: shortlist/ranking, baseline runner, forecast model loop, persist+export glue.
- Public `run_prediction` (or equivalent) keeps the same inputs/outputs for CLI/web.
- Prefer unit tests on ranking/horizon filtering without fitting Prophet.

### Step 4 — Safer prediction defaults / cost staging
**Addresses:** High — demo cost  
- Do not run every classical/ML model by default in UI/CLI unless user explicitly selects “all”.
- Document recommended default shortlist in README; keep “all models” as an opt-in.
- No change to model implementations themselves beyond how they are selected by default.

### Step 5 — Shared LLM prompt + response parsing
**Addresses:** Medium — Ollama↔OpenRouter coupling  
- Move `EXTRACTION_SYSTEM_PROMPT` and JSON/fence parsing to a shared module (e.g. `llm/prompts.py`, `llm/response_parse.py`).
- Both OpenRouter and Ollama clients use it; drop constructing `OpenRouterClient` as a parser.

### Step 6 — Glossary cache + skill resolution batching
**Addresses:** Medium — hot-path I/O and N+1  
- In-process glossary cache invalidated on `add_entries` (path-aware for tests).
- Prefetch existing skill names / batch get-or-create where safe under current uniqueness rules.

### Step 7 — Thin BLL facades for web flows
**Addresses:** Medium — routes owning transactions  
- Facades for review update, analysis run (+ export), recent forecast history so routes stay HTTP/form focused.
- Align session_scope boundaries with Step 1/10 rules.

### Step 8 — Forecast type/status constants or enums
**Addresses:** Medium — late typos  
- Centralize `target_type` and run `status` strings used by service, repository, export, templates.
- Update tests to import the same constants.

### Step 9 — Quarantine unfinished `DatabaseSource`
**Addresses:** Medium — docs/API drift  
- Keep fail-closed `PREDICTION_DATA_SOURCE=database`.
- Clearly mark stub (module docstring / `NotImplementedError` / move under `prediction/_future/` or similar) and align README/`PROJECT_SUMMARY` / any stale plan notes that imply it is live.
- Do **not** implement live DB aggregates in this plan.

### Step 10 — Repo transaction rules + slim `BaseRepository`
**Addresses:** Medium/Low — transaction ownership honesty  
- Replace `rollback()` in `JobPostingRepository.save` with savepoint/`begin_nested` pattern (like skills) or re-raise for `session_scope`.
- Relax ABC so unused `get_all`/`delete` are not mandatory, or drop dead methods if unused.

### Step 11 — Config load/validate cleanup
**Addresses:** Medium — import-time failures / dual state  
- Prefer parse-and-assign inside `validate_config()` (or explicit `load_config()`) rather than fragile import-time `int()` side effects where practical.
- Keep env var names and defaults behaviorally compatible; update `restore_env` tests as needed.

### Step 12 — Docs/tests layout polish
**Addresses:** Low — navigation and drift  
- Optional: group tests under `tests/bll`, `tests/dal`, `tests/llm`, `tests/web`, `tests/prediction` (pytest discovery must keep working).
- Optional: map forecast ORM → simple dicts/DTOs for templates.
- Sync README / PROJECT_SUMMARY with structural changes from earlier steps.
- Single salary aggregate query if touching analysis DAL anyway (Step 2).

---

## Suggested implementation order

1. Steps **1–2** (session/LLM boundary + analysis DAL) — reliability and layer clarity  
2. Steps **3–4** (prediction structure + defaults) — maintainability and demo cost  
3. Steps **5–7** (LLM parse, caches, web façades) — coupling and hot paths  
4. Steps **8–11** (constants, stub quarantine, transactions, config) — consistency  
5. Step **12** (docs/tests polish) — last  

---

## Explicitly not in this plan

- Implementing PostgreSQL prediction aggregates (`DatabaseSource`) for real
- Auth / CSRF redesign (already done in hardening plan)
- Changing default Ollama/OpenRouter model IDs
- Background job queue for long Prophet runs (note as future work if needed after Step 4)
- Merging README and PROJECT_SUMMARY into one doc

---

## Notes log

- **2026-07-27:** Plan created from architecture/code-organization review (layering, session/LLM span, analysis ORM in BLL, prediction god module, LLM parse coupling, glossary/skills hot paths, unfinished DatabaseSource, config/repo ABC smells). No application code changes. Awaiting permission to begin Step 1.
- **2026-07-27 (Step 1):** Ingest uses short lookup session → LLM with no open session → short save session; `ExtractionService` split into `find_by_content_hash` / `extract_entity` / `save_extracted`; tests assert session exit before LLM.
- **2026-07-27 (Step 2):** Moved analysis SQL into `AnalysisRepository`; `analysis_service` clamps top-N and delegates (stable result shapes for web/charts).
- **2026-07-27 (Steps 3–12):** Split prediction orchestration; default models `baseline/prophet/arima`; shared LLM prompts/parse; glossary cache + skill prefetch; web BLL façades; `TargetType`/`RunStatus`; quarantined `DatabaseSource`; savepoint on posting IntegrityError + slim `BaseRepository`; soft int env parse; salary one-query + docs/tests updates.
