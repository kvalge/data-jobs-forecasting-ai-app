"""CSRF and upload-type checks for the Flask UI."""

import re
from unittest.mock import MagicMock

import pytest

from src.bll.extraction_service import ExtractAndSaveResult
from src.domain.job_posting_entity import JobPostingEntity
from src.domain.work_type import WorkType
from src.web import create_app
import src.web.routes.postings as postings_routes


def _csrf_token_from_home(client) -> str:
    html = client.get("/").get_data(as_text=True)
    match = re.search(r'name="csrf_token"\s+value="([^"]+)"', html)
    assert match, "csrf_token missing from add-posting form"
    return match.group(1)


@pytest.fixture
def app_csrf():
    application = create_app(run_startup=False)
    application.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-csrf",
        WTF_CSRF_ENABLED=True,
    )
    return application


@pytest.fixture
def client_csrf(app_csrf):
    return app_csrf.test_client()


def test_post_without_csrf_is_rejected(client_csrf):
    response = client_csrf.post("/", data={"posting_text": "hello"}, follow_redirects=False)
    assert response.status_code == 400


def test_post_with_csrf_token_succeeds(client_csrf, monkeypatch):
    entity = JobPostingEntity(
        id=1,
        role_title="Dev",
        company_name="Acme",
        work_type=WorkType.unknown,
        skills=[],
        skills_en=[],
    )
    monkeypatch.setattr(
        postings_routes,
        "ingest_posting_text",
        MagicMock(return_value=ExtractAndSaveResult(entity=entity, created=True)),
    )

    token = _csrf_token_from_home(client_csrf)
    response = client_csrf.post(
        "/",
        data={"posting_text": "hello world", "csrf_token": token},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Saved posting" in response.data


def test_upload_rejects_non_txt(monkeypatch):
    class FakeFile:
        filename = "notes.pdf"

        def read(self):
            return b"%PDF-1.4"

    class FakeRequest:
        files = {"posting_file": FakeFile()}
        form = {}

    monkeypatch.setattr(postings_routes, "request", FakeRequest())
    with pytest.raises(ValueError, match=r"\.txt"):
        postings_routes._resolve_posting_text()


def test_upload_rejects_binary_null_bytes(monkeypatch):
    class FakeFile:
        filename = "posting.txt"

        def read(self):
            return b"hello\x00world"

    class FakeRequest:
        files = {"posting_file": FakeFile()}
        form = {}

    monkeypatch.setattr(postings_routes, "request", FakeRequest())
    with pytest.raises(ValueError, match="plain UTF-8"):
        postings_routes._resolve_posting_text()


def test_upload_accepts_txt(monkeypatch):
    class FakeFile:
        filename = "posting.txt"

        def read(self):
            return b"Role: Engineer\n"

    class FakeRequest:
        files = {"posting_file": FakeFile()}
        form = {}

    monkeypatch.setattr(postings_routes, "request", FakeRequest())
    assert postings_routes._resolve_posting_text() == "Role: Engineer"
