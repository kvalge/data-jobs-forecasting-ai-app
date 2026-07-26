# Plan: Data analysis UI + README charts

**Created:** 2026-07-26  
**Status:** Complete (all planned steps done)  
**Scope:** Query aggregations from PostgreSQL, show them on a Flask page, write PNG charts into the repo, and show those images in README.  
**Out of scope:** Forecasting, auth, date-range filters, CLI analysis commands.

**Defaults:**
- Charts via matplotlib → `docs/analysis/*.png`
- Salary stats: `MIN(salary_min)`, `AVG(salary_min)`, `AVG(salary_max)`, `MAX(salary_max)` — each ignores its own nulls
- Top-N default 10, clamp 1–50; null/blank labels excluded
- README keeps stable image links; analysis overwrites PNGs

---

## Progress

| Step | Title | Status |
|------|--------|--------|
| 0 | Write durable plan file under `.cursor/` | Done (2026-07-26) |
| 1 | Analysis queries (DAL + BLL) | Done (2026-07-26) |
| 2 | Chart export (matplotlib PNGs) | Done (2026-07-26) |
| 3 | Flask `/analysis` UI | Done (2026-07-26) |
| 4 | README embed after What it does | Done (2026-07-26) |
| 5 | Tests + docs polish | Done (2026-07-26) |

---

## Notes log

- **2026-07-26:** Plan file created (Step 0).
- **2026-07-26:** Implemented Steps 1–5: `analysis_service`, `chart_export`, Flask `/analysis`, README Sample analyses, tests; seeded placeholder PNGs under `docs/analysis/`.
