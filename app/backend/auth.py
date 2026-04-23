from functools import wraps
from flask import Blueprint, session, redirect, url_for, request, render_template
from .users import UserRepository

auth_bp = Blueprint("auth", __name__)


# ── Decorators ─────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        if not session.get("is_admin"):
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated


# ── Routes ─────────────────────────────────────────────────────────────────

@auth_bp.get("/login")
def login():
    if "user_id" in session:
        return redirect(url_for("main.index"))
    return render_template("login.html")


@auth_bp.post("/login")
def login_post():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    user = UserRepository.verify(username, password)
    if not user:
        return render_template("login.html", error="Onjuiste gebruikersnaam of wachtwoord.")
    session["user_id"]  = user["id"]
    session["username"] = user["username"]
    session["is_admin"] = bool(user["is_admin"])
    return redirect(url_for("main.index"))


@auth_bp.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))