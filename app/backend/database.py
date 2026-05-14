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
                measured_at TEXT    DEFAULT (datetime('now','localtime')),
                latitude    REAL    NULL,   -- horizontale meting met decimaal getal (want komma's), en NULL ('geen waarde') toegestaan
                longitude   REAL    NULL    -- verticale meting met decimaal getal (want komma's), en NULL ('geen waarde') toegestaan
            );

            CREATE TABLE IF NOT EXISTS reports (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT    NOT NULL,
                week_nr     INTEGER NOT NULL,
                year        INTEGER NOT NULL,
                avg_height  REAL,
                compliance  REAL,
                notes       TEXT,
                created_at  TEXT    DEFAULT (datetime('now','localtime')),
                expires_at  TEXT    NOT NULL
            );
        """)
        get_db().commit()