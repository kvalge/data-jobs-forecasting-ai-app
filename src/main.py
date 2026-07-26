# main.py
from src.bll.extraction_service import ExtractionService
from src.config import validate_config
from src.dal.job_posting_repository import JobPostingRepository
from src.dal.session import init_db, session_scope


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

    with session_scope() as session:
        repository = JobPostingRepository(session)
        service = ExtractionService(repository)
        try:
            saved = service.extract_and_save(posting_text)
            print(f"\nSaved posting: '{saved.role_title}' at '{saved.company_name}' (id={saved.id})")
        except ValueError as e:
            print(f"\nExtraction failed: {e}")


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
