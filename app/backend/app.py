from pathlib import Path
from flask import Flask
from .database import init_app
from .routes import main_bp


def create_app() -> Flask:
    root = Path(__file__).resolve().parents[1]  # een map omhoog → app/
    (root / "data").mkdir(exist_ok=True)

    app = Flask(
        __name__,
        template_folder=str(root / "templates"),
        static_folder=str(root / "static"),
    )
    app.config["DATABASE_PATH"] = str(root / "data" / "measurements.db")

    init_app(app)
    app.register_blueprint(main_bp)
    return app