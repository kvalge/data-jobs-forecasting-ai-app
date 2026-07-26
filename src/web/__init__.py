"""Flask web application factory."""

import os
from pathlib import Path

from flask import Flask

from src.config import validate_config
from src.dal.session import init_db
from src.web.routes.analysis import analysis_bp
from src.web.routes.postings import postings_bp

_WEB_DIR = Path(__file__).resolve().parent


def create_app(*, run_startup: bool = True) -> Flask:
    """Create and configure the Flask app.

    Args:
        run_startup: When True, validate config and apply DB migrations.
            Set False in unit tests that mock ingest and skip the real DB.
    """
    app = Flask(
        __name__,
        template_folder=str(_WEB_DIR / "templates"),
        static_folder=str(_WEB_DIR / "static"),
    )
    app.config["SECRET_KEY"] = (os.getenv("SECRET_KEY") or "").strip() or "dev-only-change-me"
    app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1 MB uploads

    if run_startup:
        validate_config()
        init_db()

    app.register_blueprint(postings_bp)
    app.register_blueprint(analysis_bp)
    return app
