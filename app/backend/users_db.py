import sqlite3
from flask import g, current_app
from werkzeug.security import generate_password_hash


def get_users_db() -> sqlite3.Connection:
    if "users_db" not in g:
        conn = sqlite3.connect(current_app.config["USERS_DB_PATH"])
        conn.row_factory = sqlite3.Row
        g.users_db = conn
    return g.users_db


def close_users_db(_=None):
    conn = g.pop("users_db", None)
    if conn:
        conn.close()


def init_users_app(app):
    app.teardown_appcontext(close_users_db)
    with app.app_context():
        db = get_users_db()
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT    NOT NULL UNIQUE,
                password_hash TEXT    NOT NULL,
                is_admin      INTEGER NOT NULL DEFAULT 0,
                client_name   TEXT    NULL,
                created_at    TEXT    DEFAULT (datetime('now','localtime'))
            );
        """)
        # Migratie: voeg client_name toe aan bestaande users tabel
        try:
            db.execute("ALTER TABLE users ADD COLUMN client_name TEXT NULL")
        except Exception:
            pass  # kolom bestaat al
        db.commit()

        # Seed hardcoded admin if not exists
        existing = db.execute(
            "SELECT id FROM users WHERE username = 'admin'"
        ).fetchone()
        if not existing:
            db.execute(
                "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, 1)",
                ("admin", generate_password_hash("69420"))
            )
            db.commit()

        # Seed voorbeeld-klant: Gemeente Groningen
        existing_client = db.execute(
            "SELECT id FROM users WHERE username = 'gemeente_groningen'"
        ).fetchone()
        if not existing_client:
            db.execute(
                "INSERT INTO users (username, password_hash, is_admin, client_name) VALUES (?, ?, 0, ?)",
                ("gemeente_groningen", generate_password_hash("groningen2026"), "Gemeente Groningen")
            )
            db.commit()