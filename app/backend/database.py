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
<<<<<<< HEAD
                latitude    REAL    NULL,
                longitude   REAL    NULL,
                client_name TEXT    NULL
=======
                latitude    REAL    NULL,   -- horizontale meting met decimaal getal (want komma's), en NULL ('geen waarde') toegestaan
                longitude   REAL    NULL    -- verticale meting met decimaal getal (want komma's), en NULL ('geen waarde') toegestaan
>>>>>>> d7c69c298701bbb996e43421c0ddf7ff3df61f79
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
<<<<<<< HEAD
        # Migratie: voeg client_name toe aan bestaande measurements tabel
        try:
            get_db().execute("ALTER TABLE measurements ADD COLUMN client_name TEXT NULL")
        except Exception:
            pass  # kolom bestaat al

        # Koppel bekende Gemeente Groningen locaties aan de juiste klant
        get_db().execute("""
            UPDATE measurements
            SET client_name = 'Gemeente Groningen'
            WHERE client_name IS NULL
              AND location IN (
                'Sportveld Bedum',
                'Recreatiegebied Zuidhorn',
                'Bedumer bos - Groningen'
              )
        """)
=======
>>>>>>> d7c69c298701bbb996e43421c0ddf7ff3df61f79
        get_db().commit()