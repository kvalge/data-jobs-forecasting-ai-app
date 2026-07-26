# Plan: Add job posting UI (Flask)

**Created:** 2026-07-26  
**Status:** Complete (all planned steps done)  
**Scope:** Web UI to insert job postings (paste + `.txt` upload), reuse existing BLL/DAL/LLM pipeline.  
**Out of scope:** Analysis/forecasting UI, auth, listing/editing postings, React/SPA.

**Stack choice:** Flask + Jinja2 + static CSS.  
**Input:** Both paste textarea and file upload.  
**CLI:** `python -m src.main` remains unchanged in behavior.

---

## Progress

| Step | Title | Status |
|------|--------|--------|
| 0 | Write durable plan file under `.cursor/` | Done (2026-07-26) |
| 1 | Shared posting ingest helper (CLI + web) | Done (2026-07-26) |
| 2 | Refactor CLI to use shared helper | Done (2026-07-26) |
| 3 | Flask app factory + package skeleton | Done (2026-07-26) |
| 4 | Design tokens + base CSS | Done (2026-07-26) |
| 5 | Base Jinja layout | Done (2026-07-26) |
| 6 | Insert form page (paste + file upload) | Done (2026-07-26) |
| 7 | POST handler wired to ingest + flash results | Done (2026-07-26) |
| 8 | Web entrypoint + requirements + README | Done (2026-07-26) |
| 9 | Focused Flask route tests | Done (2026-07-26) |

---

## Notes log

- **2026-07-26:** Plan file created (Step 0).
- **2026-07-26:** Implemented Steps 1–9: `posting_ingest`, CLI refactor, Flask UI (paste + file), CSS palette, README/`SECRET_KEY`, web tests with mocked ingest.
