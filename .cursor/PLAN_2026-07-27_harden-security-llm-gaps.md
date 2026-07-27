# Plan: Harden security, LLM usage, and remaining product gaps

**Created:** 2026-07-27  
**Status:** In progress (Step 1 done)  
**Scope:** Fix high/medium shortcomings found in a full-project review after OpenRouter → Ollama fallback landed. Prioritize security when calling LLMs via OpenRouter API or local Ollama, user-selectable LLM provider mode (OpenRouter+Ollama vs Ollama-only), privacy-safe LLM request metadata logging, stricter validation of model output before persistence, web hardening for a portfolio/local app, and a few integrity/ops gaps.  
**Out of scope:** Full multi-user auth product, production Kubernetes/Docker packaging, implementing live `DatabaseSource` aggregates end-to-end (only guard/reject until ready), redesigning the analysis/prediction UIs, swapping the primary LLM provider stack beyond the configured modes below.

**Context:** Prior plans under `.cursor/` covered config/sessions/dedup (complete), Flask insert UI (complete), analysis UI (complete), and prediction/forecasting (complete). This plan is the next backlog.

---

## Progress

| Step | Title | Status |
|------|--------|--------|
| 0 | Create this plan file | Done (2026-07-27) |
| 1 | Web runtime hardening (debug, bind, SECRET_KEY) | Done (2026-07-27) |
| 2 | Cap posting size before any LLM call | Done (2026-07-27) |
| 3 | Allowlist `OLLAMA_BASE_URL` (SSRF guard) | Done (2026-07-27) |
| 4 | Stricter post-LLM / review-path validation | Done (2026-07-27) |
| 5 | Sanitize glossary TSV writes + safer errors to UI | Done (2026-07-27) |
| 6 | CSRF + upload type checks + safer flash messages | Done (2026-07-27) |
| 7 | Transaction ownership (flush-only repos) | Done (2026-07-27) |
| 8 | Prediction `database` source fail-closed + UI catch | Done (2026-07-27) |
| 9 | User-selectable LLM mode (OpenRouter+Ollama vs Ollama-only) | Done (2026-07-27) |
| 10 | LLM request metadata logging (privacy-safe) | Pending |
| 11 | LLM client cleanup (narrow recoverable errors, orchestrator) | Pending |
| 12 | Dead code / docs / pinned deps / tests | Pending |

After each completed step: update this table + notes below, propose a git commit message in chat, then ask permission before the next step.

---

## Findings summary (why these steps)

### Security — LLM via API and local Ollama

| Severity | Issue | Evidence |
|----------|--------|----------|
| High | Soft prompt-injection defense only; posting text is the user message and biased fields can pass weak validation into Postgres / charts / glossary | `EXTRACTION_SYSTEM_PROMPT` + user message in `openrouter_client.py` / `ollama_client.py`; thin `validate_extraction_dto` |
| High | `OLLAMA_BASE_URL` is used as `requests.post` target with no host allowlist → SSRF if `.env` is wrong or compromised | `ollama_client.py`, `config.py` |
| High | No char/token budget before LLM call; 1 MB upload still allows huge prompts (cost, timeout, local DoS) | `posting_ingest.py`, `web/__init__.py` `MAX_CONTENT_LENGTH` |
| High | Flask `debug=True`; default `SECRET_KEY`; no auth — reachable port can burn OpenRouter quota and write DB | `web/__main__.py`, `web/__init__.py`, all routes |
| Medium | Provider error snippets and raw `ValidationError` / SQLAlchemy text can leak to flash/CLI | `error_messages.py`, `postings.py` |
| Medium | Glossary TSV accepts tabs/newlines; LLM-influenced then user-edited pairs become trusted overrides | `glossary.py`, review save in `postings.py` |
| Medium | No CSRF on mutating POSTs; upload accepts any UTF-8 body (browser `accept=` is not enforcement) | templates + `_resolve_posting_text` |
| Medium | No structured LLM request metadata log — hard to monitor reliability without dumping sensitive prompts | LLM clients / extraction path |
| Low | Jinja autoescape on (good); ORM parameterized (good); keep that way | templates, repositories |

### Other high/medium product gaps

| Severity | Issue |
|----------|--------|
| High | Review update skips salary/domain re-validation; skills rebuilt from English-only labels |
| High | `PREDICTION_DATA_SOURCE=database` raises uncaught `NotImplementedError` |
| Medium | Repositories `commit()` inside `session_scope` → unclear transaction boundaries |
| Medium | Leftover `translation.py` unused on ingest; OpenRouter always required even when user wants local-only |
| Medium | Unpinned `requirements.txt`; auto-migrate on every app start |

---

## Steps (detail)

### Step 0 — Create this plan file
- Add dated plan under `.cursor/`.
- No application code changes.

### Step 1 — Web runtime hardening (debug, bind, SECRET_KEY)
**Addresses:** High — exposed debugger / weak session secret  
- Run Flask with `debug` from env (default **False**); bind `127.0.0.1` by default.
- Require a non-default `SECRET_KEY` for the web entrypoint (fail closed outside an explicit `FLASK_ENV=development` / similar).
- Document in README: local-only bind; do not expose without auth.
- Do **not** implement full auth in this plan (out of scope); document the risk if the port is LAN-exposed.

### Step 2 — Cap posting size before any LLM call
**Addresses:** High — OpenRouter cost / Ollama DoS / timeouts  
- Enforce a shared max character limit in BLL ingest (stricter than or equal to upload limit), for CLI and web.
- Reject early with a clear message **before** OpenRouter or Ollama is called.
- Optionally lower effective prompt size further for Ollama if needed (same cap is enough for v1).

### Step 3 — Allowlist `OLLAMA_BASE_URL` (SSRF guard)
**Addresses:** High — SSRF via local LLM fallback  
- In `validate_config()` (or dedicated helper): allow only loopback hosts by default (`127.0.0.1`, `localhost`, `::1`) and `http` (or documented https).
- Reject cloud metadata / arbitrary private IPs unless an explicit opt-in env (e.g. `OLLAMA_ALLOW_REMOTE=true`) is set for advanced users.
- Disable redirects on the Ollama `requests.post` call.
- Add unit tests for rejected URLs.

### Step 4 — Stricter post-LLM / review-path validation
**Addresses:** High — malicious or hallucinated LLM JSON persisting; review bypass  
- Tighten Pydantic / domain rules: max string lengths, skill count cap, `salary_min/max >= 0` and soft upper bound, currency format/allowlist, reject mismatched `skills` vs `skills_en` lengths (stop silent padding-as-truth).
- Re-run the same validation on web review save before `update_review_fields`.
- Preserve original skill `display_name` when only English labels are edited on review (do not wipe originals).
- Keep treating model output as **untrusted data** only (never execute it); system prompt anti-instruction rule stays as defense-in-depth, not the sole control.
- Optional small note in UI: extracted values are model suggestions pending review.
- Emit validation accepted/rejected into the metadata logger added in Step 10 (wire when both exist).

### Step 5 — Sanitize glossary TSV writes + safer errors to UI
**Addresses:** Medium — glossary poisoning / row smuggling; info disclosure  
- Forbid `\t`, `\n`, `\r` in glossary keys/values; length limits; atomic write.
- Keep glossary updates only from explicit user review corrections (already the case).
- Log full LLM/DB errors server-side; show short stable user messages (extend `format_llm_failure_for_user` / posting routes). Do not append raw provider JSON bodies to flash text.

### Step 6 — CSRF + upload type checks + safer flash messages
**Addresses:** Medium — CSRF / odd uploads  
- Add Flask CSRF protection on mutating forms (Flask-WTF or equivalent minimal approach).
- Require `.txt` (or sniffed text) on upload; reject empty/binary; keep UTF-8 decode errors user-friendly.
- Whitelist flash categories used in CSS class names.

### Step 7 — Transaction ownership (flush-only repos)
**Addresses:** Medium — partial commits / rollback surprises  
- Repositories flush (and use savepoints where needed) but do not `commit()`.
- Single commit at end of `session_scope` / service unit of work (ingest, review update, prediction persist).
- Add/adjust tests so failure mid-save does not leave partial committed rows.

### Step 8 — Prediction `database` source fail-closed + UI catch
**Addresses:** High/Medium — hard crash when `PREDICTION_DATA_SOURCE=database`  
- Reject `database` at `validate_config()` until `DatabaseSource` is implemented **or** catch `NotImplementedError` in CLI + Flask and show a clear message.
- Prefer fail-closed config so the UI option cannot be selected into a 500.
- Do not implement full DB aggregates in this plan (out of scope).

### Step 9 — User-selectable LLM mode (OpenRouter+Ollama vs Ollama-only)
**Addresses:** Medium — force OpenRouter even when user wants local-only; unclear ops choice  
- Add an explicit config switch (e.g. `LLM_PROVIDER_MODE`) so the user can choose:
  - **`openrouter_ollama`** (default): try OpenRouter model chain (`MODEL` → `FALLBACK_MODEL` → optional `FALLBACK_MODEL2`/`3`), then local Ollama if enabled / needed.
  - **`ollama_only`**: call local Ollama only; do **not** require `OPENROUTER_API_KEY` / OpenRouter models.
- Validate env accordingly:
  - `openrouter_ollama`: keep requiring OpenRouter key + at least primary/fallback models; Ollama settings as today.
  - `ollama_only`: require `OLLAMA_BASE_URL` / `OLLAMA_MODEL` (and allowlist from Step 3); skip OpenRouter required vars.
- Wire factory/orchestrator so mode selection is obvious (not buried only inside OpenRouter client).
- Update `.env.example`, `README.md`, and `PROJECT_SUMMARY.md` with the two choices and when to use each.
- Tests: config accept/reject per mode; extract path uses only Ollama when `ollama_only` (HTTP mocked).

### Step 10 — LLM request metadata logging (privacy-safe)
**Addresses:** Medium — no monitoring of reliability/performance without leaking content  
**Purpose:** Monitor LLM reliability and performance; detect frequent fallback usage or model failures; understand validation issues; support debugging **without** exposing sensitive data.

**Implementation:**
- Add structured logging for each LLM request attempt / outcome (NDJSON or similar), written to a dedicated log file under the project (e.g. `logs/llm_requests.ndjson` or `var/log/llm_requests.ndjson`), gitignored.
- Each record should include at least:
  - `timestamp`
  - `provider` (`openrouter` / `ollama`)
  - `model` (model name)
  - `status` (`success` / `failure`)
  - `response_time_ms` (or equivalent)
  - `token_usage` (prompt/completion/total if the provider returns it; otherwise omit or null — never invent)
  - `fallback_used` (whether a fallback model/provider was triggered for this extract attempt)
  - `validation_result` (`accepted` / `rejected` / `n/a` when validation not reached)
  - `error_category` when failed (`timeout`, `api_error`, `rate_limit`, `validation_failure`, `connection`, `parse_error`, `other`, …)
- **Do not log:** full prompts, job posting text, personal data, raw LLM response bodies, API keys.
- Optional safe fields only if useful and non-sensitive: posting length in chars (not content), content-hash prefix, request id / run id.
- Config: path and enable flag (default on for local dev is fine); document in `.env.example` / README.
- Hook points: OpenRouter/Ollama HTTP call boundaries + extraction validation outcome in BLL (so validation failures are visible even when HTTP succeeded).

**Tests (mocked providers; no live OpenRouter/Ollama):**
- Successful LLM call logs success metadata (provider, model, status, timing).
- Fallback activation logs that a fallback was used (and which provider/model succeeded).
- Validation failure logs `validation_result=rejected` / appropriate `error_category` without content.
- Provider errors (timeout / HTTP failure) log `status=failure` + category.

### Step 11 — LLM client cleanup (narrow recoverable errors, orchestrator)
**Addresses:** Medium — architecture / reliability  
- Narrow `_RECOVERABLE_ERRORS` so programming bugs are not silently rotated across models.
- Keep Ollama `think: false` for qwen3.x (already done); document timeout guidance.
- Prefer composing fallback in factory/orchestrator over nesting Ollama inside OpenRouter (align with Step 9 mode switch; keep behavior identical for default mode).
- Remove or clearly quarantine unused `translation.py` (and its tests) **or** wire it to the same provider mode — prefer delete if unused on ingest.

### Step 12 — Dead code / docs / pinned deps / tests
**Addresses:** Medium/Low — reproducibility and alignment  
- Pin critical versions in `requirements.txt` (or add a lock/constraints file); note Windows/Prophet fragility in README.
- Align README “locations etc.” wording with actual analysis metrics.
- Mark older `.cursor` plans that still say forecasting is a stub as archived/complete (metadata only).
- Add focused tests: posting size reject, Ollama URL allowlist, stricter DTO validation, glossary sanitization, SECRET_KEY/debug defaults, CSRF smoke if added, LLM mode switch, metadata logger cases from Step 10.
- Ensure LLM metadata log path is in `.gitignore`.
- Tests must not call OpenRouter or Ollama.

---

## Suggested implementation order (security first)

1. Steps **1–3** (runtime + size cap + SSRF) — reduce blast radius of LLM calls  
2. Steps **4–6** (validate output, glossary, CSRF/uploads) — reduce poisoned DB / UI abuse  
3. Steps **7–8** (transactions + prediction fail-closed) — integrity  
4. Steps **9–11** (provider mode choice, metadata logging, LLM cleanup) — operable local/cloud LLM usage  
5. Step **12** (deps, docs, remaining tests) — maintainability  

---

## Explicitly not in this plan

- Full login/roles/SSO
- Implementing live PostgreSQL prediction aggregates (`DatabaseSource`)
- Background job queue for long Prophet runs (note as future work if needed)
- Content-security-policy / HTTPS termination / reverse proxy setup
- Changing default Ollama model or OpenRouter model IDs in user `.env` (user chooses via config)
- Logging prompt/response content for “better debugging” (explicitly forbidden)

---

## Notes log

- **2026-07-27:** Plan created from full-project review (architecture, LLM chain, security, data integrity, web/CLI, prediction, tests/docs, ops). No application code changes. Awaiting permission to begin Step 1.
- **2026-07-27:** Plan revised (still not implementing): Step 9 is a **user-selectable** LLM mode (`openrouter_ollama` vs `ollama_only`); added Step 10 for privacy-safe LLM request metadata logging to a dedicated log file + tests; renumbered cleanup/docs to Steps 11–12.
- **2026-07-27 (Step 1):** Added `src/web/runtime.py` — `FLASK_DEBUG` default false, `FLASK_HOST` default `127.0.0.1`, strong `SECRET_KEY` required unless `FLASK_ENV=development` (placeholders rejected). `__main__.py` uses those helpers; `create_app(run_startup=True)` enforces the secret policy. Updated `.env.example`, README, PROJECT_SUMMARY; tests in `tests/test_web_runtime.py`.
- **2026-07-27 (Step 2):** Added `MAX_POSTING_CHARS` (default 100000) in config; `ingest_posting_text` rejects oversized text before DB/LLM. Docs + `tests/test_posting_ingest.py`.
- **2026-07-27 (Step 3):** Added `validate_ollama_base_url` (loopback-only by default; `OLLAMA_ALLOW_REMOTE` opt-in). Enforced in `validate_config` and Ollama client; `allow_redirects=False` on Ollama POST. Tests in `tests/test_ollama_url.py`.
- **2026-07-27 (Step 4):** Tightened DTO bounds (lengths, salary ge/le, skill caps); reject mismatched `skills`/`skills_en`; currency normalize; `validate_review_fields` on review save; preserve original skill labels in `update_review_fields`; UI note that LLM values are untrusted.
- **2026-07-27 (Step 5):** Glossary field sanitization (no tab/newline, length cap) + atomic TSV write; stop appending provider bodies to user errors; generic DB/validation flash helpers with server-side logging.
- **2026-07-27 (Step 6):** Flask-WTF CSRF on all mutating forms; require UTF-8 `.txt` uploads (reject binary/null); whitelist flash CSS categories; tests in `tests/test_web_csrf.py`.
- **2026-07-27 (Step 7):** `session_scope` commits on success; `JobPostingRepository` flush-only (savepoint on IntegrityError); removed extra commit from prediction persist; `tests/test_session_scope.py`.
- **2026-07-27 (Step 8):** Fail-closed `PREDICTION_DATA_SOURCE=database` in `validate_config` + factory; catch `NotImplementedError` in CLI/Flask; docs updated.
- **2026-07-27 (Step 9):** Added `LLM_PROVIDER_MODE` (`openrouter_ollama` / `ollama_only`); mode-aware config validation; factory returns OllamaClient for local-only; docs + tests.
