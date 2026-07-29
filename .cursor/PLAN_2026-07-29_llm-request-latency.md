# Plan: Make LLM extraction requests faster and more effective

**Created:** 2026-07-29  
**Status:** Complete (all steps 0–7 done, 2026-07-29)  
**Scope:** Reduce wall-clock time and wasted tokens for job-posting extraction (OpenRouter model chain + optional Ollama fallback). Prefer config/order/prompt/request-shape changes that keep CLI/web behavior the same except latency and reliability. Use existing `logs/llm_requests.ndjson` as the measurement baseline.  
**Out of scope:** Changing prediction/forecast ML models, analysis charts, auth, Docker/K8s, replacing OpenRouter/Ollama with a new provider stack, multi-user rate-limit product features, redesigning the posting UI.

**Context:** Prior `.cursor` plans covered insert/analysis/prediction UIs, security/LLM hardening (provider modes, metadata logging, validation), and architecture/maintainability (DB session closed during LLM, shared prompt/parse). Extraction is still slow in practice because of **model choice/order**, **sequential free-tier failures**, **unbounded completions**, and **slow local fallback** — not because of Postgres save.

**Related runtime evidence (local metadata log, 2026-07-27 → 2026-07-28):**  
`logs/llm_requests.ndjson` shows typical patterns: primary `nvidia/nemotron-3-ultra-550b-a55b:free` often fails (`rate_limit` in ~0.3s **or** `parse_error` after ~300s); `google/gemma-4-31b-it:free` often `rate_limit`; a later model succeeds in ~16–67s with **1200–3100 completion tokens**; one `nemotron-3-super` attempt ran ~600s with **21198 completion tokens** then failed; Ollama `qwen3.5:latest` fallback succeeds in ~146–164s or times out at ~180s. Validation can still reject after a “successful” LLM call.

---

## Progress

| Step | Title | Status |
|------|--------|--------|
| 0 | Create this plan file | Done (2026-07-29) |
| 1 | Reorder / slim OpenRouter model chain (config + docs) | Done (2026-07-29) |
| 2 | Cap completion tokens + fail-fast timeouts | Done (2026-07-29) |
| 3 | Tighten extraction prompt for shorter JSON | Done (2026-07-29) |
| 4 | Treat schema/domain validation as recoverable retry | Done (2026-07-29) |
| 5 | Faster Ollama fallback (model, warm-up, keep_alive) | Done (2026-07-29) |
| 6 | Optional: skip burned free models / short-circuit rate limits | Done (2026-07-29) |
| 7 | Document latency playbook + measure with metadata log | Done (2026-07-29) |

After each completed step: update this table + notes below, propose a git commit message in chat, then ask permission before the next step.

---

## Findings summary (why these steps)

### How LLM models are used today

```
UI/CLI paste → posting_ingest
  → content-hash lookup (skip LLM if duplicate)
  → ExtractionService.extract_entity
       → get_llm_client()
            openrouter_ollama: OpenRouterWithOllamaFallback
              → OpenRouterClient: MODEL → FALLBACK_MODEL → FALLBACK_MODEL2 → FALLBACK_MODEL3 (sequential)
              → on OpenRouterChainExhausted + OLLAMA_FALLBACK_ENABLED: OllamaClient
            ollama_only: OllamaClient only
       → JobPostingExtractionDTO + validate_extraction_dto
  → save (short DB session)
```

| Piece | Current behavior | Where |
|-------|------------------|--------|
| Provider modes | `openrouter_ollama` (default) or `ollama_only` | `config.py`, `llm_client_factory.py` |
| OpenRouter chain | Up to 4 models, **sequential**, first success wins | `openrouter_client.py` `extract` / `llm_model_chain()` |
| OpenRouter request | System prompt + full posting; `response_format: json_object`; **`max_tokens`** + configurable timeout | `openrouter_client.py` |
| Ollama request | Same prompt; `format: json`; `think: false`; `keep_alive`; `num_predict`; timeout from `OLLAMA_TIMEOUT_SECONDS` | `ollama_client.py` |
| English labels | Same extract JSON (+ glossary); **no extra translate calls** | `extraction_service.py` |
| Observability | Privacy-safe NDJSON: provider, model, ms, tokens, fallback, validation | `request_metadata.py` → `logs/llm_requests.ndjson` |

### Latency / effectiveness issues

| Severity | Issue | Evidence |
|----------|--------|----------|
| High | Primary model is often the **largest/slowest free** model; when it hangs then `parse_error`, the user waits minutes **before** a working fallback starts | Metadata: ultra `parse_error` ~300s then gemma 429 then super/nano success; ultra also succeeds sometimes in 19–67s |
| High | **Sequential** free-tier chain: shared quota means early 429s are cheap, but a slow primary failure dominates wall time | Rate-limit cascade ~0.1–0.3s each; primary long-fail is the expensive part |
| High | **No completion budget** — models can emit thousands of tokens (verbose responsibilities / reasoning-like output) even for structured extract | Success rows with 1200–3100 `completion_tokens`; one failure with **21198** completion tokens / ~600s |
| High | Local Ollama fallback uses **qwen3.5:latest** (~6.6 GB); cold load + generate often **~2.5–3 min** or hits 180s timeout | Ollama success ~146–164s; timeout ~180s; `/api/ps` empty when idle |
| Medium | Prompt asks for long `responsibilities` / `requirements` text blocks → large completions and slow free inference | `prompts.py` schema |
| Medium | LLM HTTP “success” then **schema/domain validation reject** wastes the entire paid wait; no automatic retry on next model | e.g. nano success then `validation_result: rejected`; UI: `role_title` missing / `input_value={'': {}}` |
| Medium | OpenRouter client timeout in repo source is **30s**, but observed primary attempts logged ~300s — timeout policy is unclear / may have drifted locally; needs one configurable, fail-fast value | `openrouter_client.py` vs metadata `response_time_ms` ~300000 |
| Low | `MAX_POSTING_CHARS` default 100000 is safety-oriented; typical posts are ~3–6k chars — cap is fine; prompt length still dominated by system schema + long fields | ingest + metadata `posting_chars` |

### What is already in good shape (do not “fix”)

- Single extract call per successful model (no per-skill translation API)
- Content-hash dedup skips LLM for duplicates
- DB session not held during LLM wait
- Ollama `think: false` already mitigates qwen3 chain-of-thought blowups
- Metadata logging exists to measure improvements without logging prompts/PII
- Recoverable OpenRouter errors already continue the chain; Ollama composed in factory

---

## Steps (detail)

### Step 0 — Create this plan file
- Add dated plan under `.cursor/`.
- No application code changes.

### Step 1 — Reorder / slim OpenRouter model chain (config + docs)
**Addresses:** High — minutes lost on primary ultra / redundant slow models  
- Recommend a **fast-first** `.env` order for free tier, e.g. nano (or other small structured-output-friendly free model) → mid → large last; drop or demote models that repeatedly `rate_limit` or `parse_error` after long waits.
- Prefer **2–3** OpenRouter models over 4 when quota is shared (fewer sequential attempts after a slow fail).
- Update README / `.env.example` with a “latency-oriented model chain” note; do not hardcode vendor model IDs in Python if avoidable (keep IDs in `.env`).
- Success check: in `llm_requests.ndjson`, successful extracts more often have `attempt_index: 0` and `response_time_ms` in tens of seconds, not 300s+ primary failures.
- **Done:** README + `.env.example` document fast-first ordering and 2–3 model preference.

### Step 2 — Cap completion tokens + fail-fast timeouts
**Addresses:** High — 20k-token / multi-minute runaway generations  
- Add configurable OpenRouter timeout (env), default fail-fast (e.g. 45–60s) so a stuck primary does not burn ~300s before fallback.
- Pass `max_tokens` (or provider equivalent) sized for compact JSON extract (order of hundreds–low thousands, not tens of thousands).
- Optionally mirror a generation budget for Ollama (`options.num_predict` or equivalent) so local fallback cannot run forever under a high `OLLAMA_TIMEOUT_SECONDS`.
- Tests: mocked clients assert payload includes the cap; timeout comes from config.
- **Done:** `OPENROUTER_TIMEOUT_SECONDS` (default 60), `LLM_MAX_TOKENS` (default 2048) wired into OpenRouter + Ollama.

### Step 3 — Tighten extraction prompt for shorter JSON
**Addresses:** Medium — oversized completions  
- Instruct brevity: short responsibilities/requirements (e.g. capped sentences or bullet join with length guidance); skills as short tokens only; no preamble.
- Keep required schema fields and anti-injection rules.
- Optional: slightly lower effective posting truncation for LLM only (separate from storage) if posts are huge — only if Step 1–2 still leave completions large.
- Success check: median `completion_tokens` on success drops vs current 1.2k–3k baseline in metadata log.
- **Done:** `prompts.py` brevity rules (~500 char responsibilities/requirements; short skill tokens).

### Step 4 — Treat schema/domain validation as recoverable retry
**Addresses:** Medium — wasted successful HTTP calls that produce `{'': {}}` or missing `role_title`  
- After parse, if `JobPostingExtractionDTO` / `validate_extraction_dto` fails, treat as recoverable for the **model chain** (try next OpenRouter model / Ollama) instead of failing the whole ingest immediately — with a clear log `error_category` (e.g. `validation_failure`) on that attempt.
- Cap retries to remaining chain length (no infinite loops).
- Do not persist invalid JSON; UI message stays user-safe.
- Tests: first model returns bad dict → second model good dict → save succeeds; metadata shows failure then success under same `extract_id`.
- **Done:** `src/llm/extract_validate.py` + called from OpenRouter/Ollama clients after parse.

### Step 5 — Faster Ollama fallback (model, warm-up, keep_alive)
**Addresses:** High — 2.5–3 min local fallback / timeouts  
- Document / default toward a **smaller** local model for fallback when speed matters (e.g. already-pulled `llama3.2` / `mistral` vs `qwen3.5`), or keep qwen only when quality wins.
- Add Ollama `keep_alive` (and optional startup warm request) so cold load is not paid on every OpenRouter outage.
- README: `ollama run <model>` before demos; when to use `LLM_PROVIDER_MODE=ollama_only` vs OpenRouter-first.
- Success check: Ollama fallback `response_time_ms` well under 180s when model is warm; fewer `timeout` rows.
- **Done:** `OLLAMA_KEEP_ALIVE` (default `10m`) + docs for smaller models / warm-up. No separate process warm-up hook (operator runs `ollama run`).

### Step 6 — Optional: skip burned free models / short-circuit rate limits
**Addresses:** Medium — predictable 429 cascades  
- If the first OpenRouter model returns 429/free-tier, optionally **skip** remaining OpenRouter models that share the same free quota and go straight to Ollama (config flag), **or** continue but with very short timeout (already fast today for 429).
- Only implement if Step 1 ordering still leaves long multi-model waits; keep behavior configurable so paid multi-model chains still try all models.
- Tests for flag on/off.
- **Done:** `OPENROUTER_SHORTCIRCUIT_ON_RATE_LIMIT` (default `true`).

### Step 7 — Document latency playbook + measure with metadata log
**Addresses:** Low/Medium — operators need a playbook  
- README subsection: how to read `logs/llm_requests.ndjson` (provider, `attempt_index`, `response_time_ms`, `completion_tokens`, `error_category`, `validation_result`).
- Target SLOs for local demos (example): p50 success &lt; 30s when OpenRouter primary works; fallback path &lt; 90s with warm Ollama; avoid &gt; 120s primary attempts.
- No new telemetry product — reuse existing metadata logger.
- **Done:** README “LLM latency playbook” section.

---

## Suggested implementation order

1. **Step 1** (config/docs only) — fastest user win, no code required to start  
2. **Step 2** — prevents pathological multi-minute generations  
3. **Step 3** — reduces tokens on every call  
4. **Step 5** — if free OpenRouter remains unreliable  
5. **Step 4** — correctness/latency when models return junk JSON  
6. **Step 6** — only if still needed  
7. **Step 7** — docs once behavior stabilizes  

---

## Notes

- Implementation landed 2026-07-29: config knobs + client payload changes + mid-chain validation + docs/tests.
- **Operator action still required:** reorder `.env` MODEL chain to fast-first (docs cannot change your live model IDs).
- Do not log prompts, posting text, or API keys when implementing any step.
- Prediction `DEFAULT_MODELS` / Prophet / SARIMA are unrelated; leave them alone.
- If OpenRouter paid models are available later, the same chain + `max_tokens` + fail-fast timeout still apply; set `OPENROUTER_SHORTCIRCUIT_ON_RATE_LIMIT=false` so paid fallbacks still run.
