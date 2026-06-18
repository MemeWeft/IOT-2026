from werkzeug.security import generate_password_hash, check_password_hash
from .users_db import get_users_db


class UserRepository:

    @staticmethod
    def get_all() -> list[dict]:
        rows = get_users_db().execute(
<<<<<<< HEAD
            "SELECT id, username, is_admin, client_name, created_at FROM users ORDER BY is_admin DESC, username ASC"
=======
            "SELECT id, username, is_admin, created_at FROM users ORDER BY is_admin DESC, username ASC"
>>>>>>> d7c69c298701bbb996e43421c0ddf7ff3df61f79
        ).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_username(username: str) -> dict | None:
        row = get_users_db().execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def get_by_id(user_id: int) -> dict | None:
        row = get_users_db().execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def verify(username: str, password: str) -> dict | None:
        user = UserRepository.get_by_username(username)
        if user and check_password_hash(user["password_hash"], password):
            return user
        return None

    @staticmethod
<<<<<<< HEAD
    def create(username: str, password: str, is_admin: bool = False, client_name: str = None) -> int | None:
        db = get_users_db()
        try:
            cur = db.execute(
                "INSERT INTO users (username, password_hash, is_admin, client_name) VALUES (?, ?, ?, ?)",
                (username.strip(), generate_password_hash(password), int(is_admin), client_name or None)
=======
    def create(username: str, password: str, is_admin: bool = False) -> int | None:
        db = get_users_db()
        try:
            cur = db.execute(
                "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                (username.strip(), generate_password_hash(password), int(is_admin))
>>>>>>> d7c69c298701bbb996e43421c0ddf7ff3df61f79
            )
            db.commit()
            return cur.lastrowid
        except Exception:
            return None  # username already exists

    @staticmethod
    def update_password(user_id: int, new_password: str) -> bool:
        db = get_users_db()
        db.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (generate_password_hash(new_password), user_id)
        )
        db.commit()
        return True

    @staticmethod
    def delete(user_id: int) -> bool:
        db = get_users_db()
        # Never delete the hardcoded admin
        user = UserRepository.get_by_id(user_id)
        if user and user["username"] == "admin":
            return False
        db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.commit()
        return True