"""Flask routes for job posting UI."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from src.bll.glossary import add_entries, pairs_from_posting
from src.bll.job_posting_validator import validate_review_fields
from src.bll.posting_ingest import ingest_posting_text
from src.dal.job_posting_repository import JobPostingRepository
from src.dal.session import session_scope
from src.domain.work_type import WorkType
from src.llm.error_messages import (
    format_db_error_for_user,
    format_llm_failure_for_user,
    format_validation_error_for_user,
)

postings_bp = Blueprint("postings", __name__)


def _resolve_posting_text() -> str:
    """Prefer uploaded .txt file; otherwise use pasted text."""
    uploaded = request.files.get("posting_file")
    if uploaded and uploaded.filename:
        raw = uploaded.read()
        try:
            return raw.decode("utf-8").strip()
        except UnicodeDecodeError as e:
            raise ValueError("Uploaded file must be UTF-8 text") from e

    return (request.form.get("posting_text") or "").strip()


def _optional_str(name: str) -> str | None:
    value = (request.form.get(name) or "").strip()
    return value or None


def _optional_float(name: str) -> float | None:
    raw = (request.form.get(name) or "").strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError as e:
        raise ValueError(f"{name} must be a number") from e


def _parse_skills_en() -> list[str]:
    raw = request.form.get("skills_en") or ""
    return [line.strip() for line in raw.splitlines() if line.strip()]


@postings_bp.get("/")
def new_posting():
    return render_template("postings/new.html")


@postings_bp.post("/")
def create_posting():
    try:
        posting_text = _resolve_posting_text()
        if not posting_text:
            raise ValueError("Provide posting text (paste) or upload a .txt file")

        result = ingest_posting_text(posting_text)
        saved = result.entity
        if result.created:
            flash(
                f"Saved posting: '{saved.role_title}' at '{saved.company_name}' (id={saved.id})",
                "success",
            )
        else:
            flash(
                f"Posting already saved: '{saved.role_title}' at '{saved.company_name}' "
                f"(id={saved.id}) — skipped LLM extraction.",
                "info",
            )
        return redirect(url_for("postings.edit_posting", posting_id=saved.id))
    except ValueError as e:
        flash(format_validation_error_for_user(e, context="Extraction"), "error")
    except RuntimeError as e:
        flash(format_llm_failure_for_user(e), "error")
    except SQLAlchemyError as e:
        flash(format_db_error_for_user(e), "error")

    return redirect(url_for("postings.new_posting"))


@postings_bp.get("/postings/<int:posting_id>/edit")
def edit_posting(posting_id: int):
    with session_scope() as session:
        repository = JobPostingRepository(session)
        posting = repository.get_by_id(posting_id)

    if posting is None:
        flash(f"Job posting not found (id={posting_id})", "error")
        return redirect(url_for("postings.new_posting"))

    return render_template(
        "postings/edit.html",
        posting=posting,
        work_types=list(WorkType),
    )


@postings_bp.post("/postings/<int:posting_id>/edit")
def update_posting(posting_id: int):
    try:
        work_type_raw = (request.form.get("work_type") or "unknown").strip()
        try:
            work_type = WorkType(work_type_raw)
        except ValueError as e:
            raise ValueError("Invalid work_type") from e

        skills_en = _parse_skills_en()
        role_title = (request.form.get("role_title") or "").strip()
        role_title_en = _optional_str("role_title_en")

        with session_scope() as session:
            repository = JobPostingRepository(session)
            existing = repository.get_by_id(posting_id)
            if existing is None:
                raise ValueError(f"Job posting not found: id={posting_id}")

            original_skills = list(existing.skills or [])
            validated = validate_review_fields(
                company_name=_optional_str("company_name"),
                role_title=role_title,
                role_title_en=role_title_en,
                salary_min=_optional_float("salary_min"),
                salary_max=_optional_float("salary_max"),
                work_type=work_type,
                has_nondiscrimination_disclaimer=(
                    request.form.get("has_nondiscrimination_disclaimer") == "on"
                ),
                location=_optional_str("location"),
                country=_optional_str("country"),
                city=_optional_str("city"),
                skills=original_skills,
                skills_en=skills_en,
                salary_currency=existing.salary_currency,
            )

            updated = repository.update_review_fields(
                posting_id,
                company_name=validated.company_name,
                role_title=validated.role_title,
                role_title_en=validated.role_title_en,
                salary_min=validated.salary_min,
                salary_max=validated.salary_max,
                work_type=validated.work_type,
                has_nondiscrimination_disclaimer=validated.has_nondiscrimination_disclaimer,
                location=validated.location,
                country=validated.country,
                city=validated.city,
                skills=validated.skills,
                skills_en=validated.skills_en,
            )

        added = add_entries(
            pairs_from_posting(
                validated.role_title,
                validated.role_title_en,
                validated.skills,
                validated.skills_en,
            )
        )
        if added:
            flash(
                f"Posting updated. Glossary saved {added} corrected translation(s).",
                "success",
            )
        else:
            flash("Posting updated.", "success")
        return redirect(url_for("postings.edit_posting", posting_id=posting_id))
    except ValueError as e:
        flash(format_validation_error_for_user(e, context="Update"), "error")
    except SQLAlchemyError as e:
        flash(format_db_error_for_user(e), "error")

    return redirect(url_for("postings.edit_posting", posting_id=posting_id))
