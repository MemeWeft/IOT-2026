from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    return render_template("index.html")
