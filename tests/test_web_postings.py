"""Flask UI tests — ingest/LLM mocked; no OpenRouter or PostgreSQL required."""

from io import BytesIO

import pytest

from src.bll.extraction_service import ExtractAndSaveResult
from src.domain.job_posting_entity import JobPostingEntity
from src.web import create_app


@pytest.fixture
def app():
    application = create_app(run_startup=False)
    application.config.update(TESTING=True, SECRET_KEY="test-secret")
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


def test_post_paste_success(client, monkeypatch):
    entity = JobPostingEntity(id=1, role_title="Engineer", company_name="Acme")
    monkeypatch.setattr(
        "src.web.routes.postings.ingest_posting_text",
        lambda text: ExtractAndSaveResult(entity=entity, created=True),
    )

    response = client.post(
        "/",
        data={"posting_text": "Full job posting body"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Saved posting" in response.data
    assert b"Engineer" in response.data


def test_post_duplicate_info_flash(client, monkeypatch):
    entity = JobPostingEntity(id=9, role_title="Analyst", company_name="Co")
    monkeypatch.setattr(
        "src.web.routes.postings.ingest_posting_text",
        lambda text: ExtractAndSaveResult(entity=entity, created=False),
    )

    response = client.post(
        "/",
        data={"posting_text": "Same posting again"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Posting already saved" in response.data


def test_post_file_upload_used_over_paste(client, monkeypatch):
    captured: dict[str, str] = {}

    def fake_ingest(text: str):
        captured["text"] = text
        entity = JobPostingEntity(id=2, role_title="Dev", company_name="X")
        return ExtractAndSaveResult(entity=entity, created=True)

    monkeypatch.setattr("src.web.routes.postings.ingest_posting_text", fake_ingest)

    data = {
        "posting_text": "this paste should be ignored",
        "posting_file": (BytesIO(b"File contents win"), "posting.txt"),
    }
    response = client.post("/", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert captured["text"] == "File contents win"
    assert b"Saved posting" in response.data
