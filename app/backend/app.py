from __future__ import annotations

from pathlib import Path
from flask import Flask

from .database import init_app as init_db_app
from .route import main_bp


def create_app() -> Flask:
    root_dir = Path(__file__).resolve().parents[1]
    data_dir = root_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    app = Flask(
        __name__,
        template_folder=str(root_dir / "templates"),
        static_folder=str(root_dir / "static"),
    )

    app.config.update(
        DATABASE_PATH=str(data_dir / "grass.db"),
        JSON_SORT_KEYS=False,
    )

    init_db_app(app)

    app.register_blueprint(main_bp)
    return app