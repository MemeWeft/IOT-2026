from pathlib import Path
from flask import Flask
from .database import init_app
from .users_db import init_users_app
from .routes import main_bp
from .auth import auth_bp


def create_app() -> Flask:
    root = Path(__file__).resolve().parents[1]
    (root / "data").mkdir(exist_ok=True)

    app = Flask(
        __name__,
        template_folder=str(root / "templates"),
        static_folder=str(root / "static"),
    )
    app.config.update(
        DATABASE_PATH = str(root / "data" / "measurements.db"),
        USERS_DB_PATH = str(root / "data" / "users.db"),
        SECRET_KEY    = "groenwerf-secret-key-2026",
    )

    init_app(app)
    init_users_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    return app