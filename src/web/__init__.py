"""Flask web application factory."""

from pathlib import Path

from flask import Flask
from flask_wtf import CSRFProtect

from src.config import validate_config
from src.dal.session import init_db
from src.web.routes.analysis import analysis_bp
from src.web.routes.postings import postings_bp
from src.web.routes.prediction import prediction_bp
from src.web.runtime import resolve_secret_key

_WEB_DIR = Path(__file__).resolve().parent
csrf = CSRFProtect()


def create_app(*, run_startup: bool = True) -> Flask:
    """Create and configure the Flask app.

    Args:
        run_startup: When True, validate config and apply DB migrations.
            Set False in unit tests that mock ingest and skip the real DB.
            Also skips strict SECRET_KEY enforcement (tests set their own key).
    """
    app = Flask(
        __name__,
        template_folder=str(_WEB_DIR / "templates"),
        static_folder=str(_WEB_DIR / "static"),
    )
    # Real web entry requires a strong SECRET_KEY unless FLASK_ENV=development.
    app.config["SECRET_KEY"] = resolve_secret_key(allow_dev_default=not run_startup)
    app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1 MB uploads
    app.config.setdefault("WTF_CSRF_ENABLED", True)

    csrf.init_app(app)

    if run_startup:
        validate_config()
        init_db()

    app.register_blueprint(postings_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(prediction_bp)
    return app
