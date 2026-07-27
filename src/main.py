# main.py
from sqlalchemy.exc import SQLAlchemyError

from src.bll.posting_ingest import ingest_posting_text
from src.bll.prediction_service import ALLOWED_HORIZONS, ALLOWED_WINDOWS, run_prediction
from src.config import validate_config
from src.dal.session import init_db
from src.llm.error_messages import (
    format_db_error_for_user,
    format_llm_failure_for_user,
    format_validation_error_for_user,
)
from src.prediction.models.registry import ALL_RUNNABLE, DEFAULT_MODELS


def add_posting_flow() -> None:
    file_path = input("\nEnter path to the job posting .txt file (e.g. data/sample_posting.txt): ").strip()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            posting_text = f.read().strip()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return

    if not posting_text:
        print("File is empty — skipping.")
        return

    try:
        result = ingest_posting_text(posting_text)
        saved = result.entity
        if result.created:
            print(f"\nSaved posting: '{saved.role_title}' at '{saved.company_name}' (id={saved.id})")
        else:
            print(
                f"\nPosting already saved: '{saved.role_title}' at '{saved.company_name}' "
                f"(id={saved.id}) — skipped LLM extraction."
            )
    except ValueError as e:
        print(f"\n{format_validation_error_for_user(e, context='Extraction')}")
    except RuntimeError as e:
        print(f"\n{format_llm_failure_for_user(e)}")
    except SQLAlchemyError as e:
        print(f"\n{format_db_error_for_user(e)}")


def prediction_flow() -> None:
    print("\n=== Prediction / forecasting ===")
    print("Uses PREDICTION_DATA_SOURCE (default: fake files under data/fake/).")
    window_raw = input(f"Training window months {ALLOWED_WINDOWS} (default 24): ").strip()
    try:
        window = int(window_raw) if window_raw else 24
    except ValueError:
        window = 24

    horizons_raw = input("Horizons comma-separated from 3,6,12 (default 3,6,12): ").strip()
    if horizons_raw:
        horizons = []
        for part in horizons_raw.split(","):
            try:
                h = int(part.strip())
            except ValueError:
                continue
            if h in ALLOWED_HORIZONS:
                horizons.append(h)
    else:
        horizons = list(ALLOWED_HORIZONS)

    print(f"Default models: {', '.join(DEFAULT_MODELS)}")
    print(f"All models: {', '.join(ALL_RUNNABLE)}")
    models_raw = input(
        "Models comma-separated, 'all', or Enter for default: "
    ).strip().lower()
    if not models_raw:
        models = list(DEFAULT_MODELS)
    elif models_raw == "all":
        models = list(ALL_RUNNABLE)
    else:
        models = [m.strip() for m in models_raw.split(",") if m.strip()]

    try:
        outcome = run_prediction(
            training_window_months=window,
            horizons=horizons,
            models=models,
            persist=True,
        )
    except (ValueError, NotImplementedError, FileNotFoundError, EnvironmentError, SQLAlchemyError) as e:
        print(f"\nPrediction failed: {e}")
        return

    print(f"\nRun id: {outcome.run_id}")
    print(f"Status: {outcome.status}")
    print(f"Results: {outcome.summary.get('n_results')}")
    print(f"Elapsed total: {outcome.summary.get('elapsed_seconds')} s")
    timings = outcome.summary.get("model_timings_seconds") or {}
    if timings:
        print("Time per model:")
        for name, secs in timings.items():
            print(f"  {name}: {secs} s")
    if outcome.errors:
        print(f"Warnings: {len(outcome.errors)}")
        for key, msg in list(outcome.errors.items())[:8]:
            print(f"  - {key}: {msg}")


def main() -> None:
    try:
        validate_config()
    except EnvironmentError as e:
        print(f"Configuration error: {e}")
        return

    init_db()

    while True:
        print("\n=== Job Market Analyzer ===")
        print("1. Add job posting")
        print("2. Run prediction")
        print("0. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_posting_flow()
        elif choice == "2":
            prediction_flow()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    main()
