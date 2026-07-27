"""Flask UI tests — ingest/LLM mocked; no OpenRouter or PostgreSQL required."""

from io import BytesIO
from unittest.mock import MagicMock

import pytest

from src.bll.extraction_service import ExtractAndSaveResult
from src.bll.posting_review_service import ReviewUpdateResult
from src.domain.job_posting_entity import JobPostingEntity
from src.domain.work_type import WorkType
from src.web import create_app
import src.web.routes.postings as postings_routes


@pytest.fixture
def app():
    application = create_app(run_startup=False)
    application.config.update(TESTING=True, SECRET_KEY="test-secret", WTF_CSRF_ENABLED=False)
    return application


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_new_posting_form(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Add job posting" in response.data
    assert b'name="posting_text"' in response.data
    assert b'name="posting_file"' in response.data


def test_post_empty_shows_error_flash(client):
    response = client.post("/", data={"posting_text": ""}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Extraction failed" in response.data
    assert b"Provide posting text" in response.data


def test_post_llm_429_shows_clear_flash(client, monkeypatch):
    monkeypatch.setattr(
        postings_routes,
        "ingest_posting_text",
        MagicMock(
            side_effect=RuntimeError(
                "Both primary and fallback AI models failed. "
                "Primary (a): AI rate limit or free-tier quota reached for model 'a' (HTTP 429). "
                "Fallback (b): AI rate limit or free-tier quota reached for model 'b' (HTTP 429)."
            )
        ),
    )
    response = client.post("/", data={"posting_text": "some posting"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"rate limit" in response.data.lower() or b"free-tier" in response.data.lower()
    assert b"OpenRouter HTTP 429 for model" not in response.data


def test_post_paste_success_redirects_to_edit(client, monkeypatch):
    entity = JobPostingEntity(
        id=1,
        role_title="Engineer",
        role_title_en="Engineer",
        company_name="Acme",
        work_type=WorkType.remote,
        skills_en=["Python"],
    )
    monkeypatch.setattr(
        postings_routes,
        "ingest_posting_text",
        lambda text: ExtractAndSaveResult(entity=entity, created=True),
    )
    monkeypatch.setattr(
        "src.bll.posting_review_service.get_posting_for_review",
        lambda posting_id: entity,
    )

    response = client.post(
        "/",
        data={"posting_text": "Full job posting body"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Saved posting" in response.data
    assert b"Review saved posting" in response.data
    assert b'name="role_title_en"' in response.data
    assert b"Python" in response.data


def test_post_duplicate_info_flash(client, monkeypatch):
    entity = JobPostingEntity(
        id=9,
        role_title="Analyst",
        role_title_en="Analyst",
        company_name="Co",
        work_type=WorkType.unknown,
        skills_en=[],
    )
    monkeypatch.setattr(
        postings_routes,
        "ingest_posting_text",
        lambda text: ExtractAndSaveResult(entity=entity, created=False),
    )
    monkeypatch.setattr(
        "src.bll.posting_review_service.get_posting_for_review",
        lambda posting_id: entity,
    )

    response = client.post(
        "/",
        data={"posting_text": "Same posting again"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Posting already saved" in response.data
    assert b"Review saved posting" in response.data


def test_post_file_upload_used_over_paste(client, monkeypatch):
    captured: dict[str, str] = {}
    entity = JobPostingEntity(
        id=2,
        role_title="Dev",
        role_title_en="Dev",
        company_name="X",
        work_type=WorkType.hybrid,
        skills_en=["SQL"],
    )

    def fake_ingest(text: str):
        captured["text"] = text
        return ExtractAndSaveResult(entity=entity, created=True)

    monkeypatch.setattr(postings_routes, "ingest_posting_text", fake_ingest)
    monkeypatch.setattr(
        "src.bll.posting_review_service.get_posting_for_review",
        lambda posting_id: entity,
    )

    data = {
        "posting_text": "this paste should be ignored",
        "posting_file": (BytesIO(b"File contents win"), "posting.txt"),
    }
    response = client.post("/", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert captured["text"] == "File contents win"
    assert b"Saved posting" in response.data


def test_update_posting_saves_via_review_service(client, monkeypatch):
    updated = JobPostingEntity(
        id=5,
        role_title="Vanemanalüütik",
        role_title_en="Senior Analyst",
        company_name="Acme",
        work_type=WorkType.hybrid,
        skills=["Python"],
        skills_en=["Senior analysis"],
        has_nondiscrimination_disclaimer=True,
        location="Tallinn",
        country="Estonia",
        city="Tallinn",
    )
    captured: dict = {}

    def fake_update(posting_id, **kwargs):
        captured["posting_id"] = posting_id
        captured["kwargs"] = kwargs
        return ReviewUpdateResult(posting=updated, glossary_pairs_added=1)

    monkeypatch.setattr(
        "src.bll.posting_review_service.update_posting_review",
        fake_update,
    )
    monkeypatch.setattr(
        "src.bll.posting_review_service.get_posting_for_review",
        lambda posting_id: updated,
    )

    response = client.post(
        "/postings/5/edit",
        data={
            "company_name": "Acme",
            "role_title": "Vanemanalüütik",
            "role_title_en": "Senior Analyst",
            "salary_min": "3000",
            "salary_max": "4000",
            "work_type": "hybrid",
            "has_nondiscrimination_disclaimer": "on",
            "location": "Tallinn",
            "country": "Estonia",
            "city": "Tallinn",
            "skills_en": "Senior analysis",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Posting updated" in response.data
    assert b"Glossary saved" in response.data
    assert captured["posting_id"] == 5
    assert captured["kwargs"]["role_title"] == "Vanemanalüütik"
    assert captured["kwargs"]["skills_en"] == ["Senior analysis"]
