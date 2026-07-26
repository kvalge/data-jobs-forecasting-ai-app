# main.py
from sqlalchemy.exc import SQLAlchemyError

from src.bll.posting_ingest import ingest_posting_text
from src.config import validate_config
from src.dal.session import init_db
from src.llm.error_messages import format_llm_failure_for_user


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
        print(f"\nExtraction failed: {e}")
    except RuntimeError as e:
        print(f"\n{format_llm_failure_for_user(e)}")
    except SQLAlchemyError as e:
        print(f"\nDatabase error: {e}")


def analysis_flow() -> None:
    print("\nAnalysis is not implemented yet — coming in a future step.")


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
        print("2. Run analysis")
        print("0. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_posting_flow()
        elif choice == "2":
            analysis_flow()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    main()
