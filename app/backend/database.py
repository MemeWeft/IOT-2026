import sqlite3
from flask import g, current_app


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        conn = sqlite3.connect(current_app.config["DATABASE_PATH"])
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


def close_db(_=None):
    conn = g.pop("db", None)
    if conn:
        conn.close()


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        get_db().executescript("""
            CREATE TABLE IF NOT EXISTS measurements (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                height_mm   REAL    NOT NULL,
                location    TEXT    DEFAULT 'Onbekend',
                measured_at TEXT    DEFAULT (datetime('now','localtime'))
            );
        """)
        get_db().commit()