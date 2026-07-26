# Plan: Time series prediction on (fake → DB) job market data

**Created:** 2026-07-26  
**Status:** Complete (all planned steps done)  
**Scope:** Synthetic historical data, baseline trend analysis, role/skill/salary forecasting (3/6/12 months), multi-model runs with user-selected training window and models, persist results + metainfo in PostgreSQL, Flask UI + CLI entry that call the same pipeline.  
**Out of scope:** Auth, README chart embeds for forecasts, live OpenRouter usage in forecasting, replacing the existing descriptive `/analysis` page.

**Defaults:**
- Fake data: `data/fake/`; prediction code: `src/prediction/`
- Models: baseline, prophet, sarima, arima, rf, hgb
- Training windows: 12 / 24 / 36; horizons: 3 / 6 / 12
- Data switch: `PREDICTION_DATA_SOURCE=fake|database` (default fake)

---

## Progress

| Step | Title | Status |
|------|--------|--------|
| 0 | Write durable plan file under `.cursor/` | Done (2026-07-26) |
| 1 | Fake data generator + `data/fake/` | Done (2026-07-26) |
| 2 | `src/prediction` + FakeFileSource / DatabaseSource | Done (2026-07-26) |
| 3 | Baseline analysis module | Done (2026-07-26) |
| 4 | Prophet / SARIMA / ARIMA / RF / HGB adapters | Done (2026-07-26) |
| 5 | `prediction_service` orchestration | Done (2026-07-26) |
| 6 | Alembic forecast tables + DAL | Done (2026-07-26) |
| 7 | Flask `/prediction` + CLI wire-up | Done (2026-07-26) |
| 8 | requirements, README, tests | Done (2026-07-26) |

---

## Notes log

- **2026-07-26:** Plan file created (Step 0).
- **2026-07-26:** Implemented Steps 1–8: fake generator (10k/36mo), `src/prediction` package, baseline + classical/ML models, BLL orchestration, `forecast_*` tables, Flask `/prediction` + CLI menu, docs/tests (55 passed).
