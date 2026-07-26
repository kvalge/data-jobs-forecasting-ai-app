"""Flask routes for job posting UI."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from src.bll.posting_ingest import ingest_posting_text

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
    except ValueError as e:
        flash(f"Extraction failed: {e}", "error")
    except RuntimeError as e:
        flash(f"LLM request failed: {e}", "error")
    except SQLAlchemyError as e:
        flash(f"Database error: {e}", "error")

    return redirect(url_for("postings.new_posting"))
