"""Run the Flask UI: python -m src.web"""

from src.web import create_app
from src.web.runtime import flask_bind_host, flask_debug_enabled

app = create_app()


def main() -> None:
    # Default: loopback + debug off. Override with FLASK_HOST / FLASK_DEBUG.
    # There is no authentication — do not bind to 0.0.0.0 on an untrusted network.
    app.run(host=flask_bind_host(), debug=flask_debug_enabled())


if __name__ == "__main__":
    main()
