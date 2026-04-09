from flask import Blueprint, jsonify, render_template, request, abort
from .model import MeasurementRepository

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    stats = MeasurementRepository.get_stats()
    rows  = MeasurementRepository.get_all(50)
    return render_template("index.html", stats=stats, rows=rows)


# Pico POST endpoint  →  POST /api/measurement
# Body (JSON): { "height_mm": 63.4, "location": "Testlocatie" }
@main_bp.post("/api/measurement")
def add_measurement():
    body = request.get_json(force=True, silent=True) or {}
    height = body.get("height_mm")
    if height is None:
        abort(400, "height_mm required")
    row_id = MeasurementRepository.insert(
        height_mm=float(height),
        location=body.get("location", "Onbekend")
    )
    return jsonify({"id": row_id, "height_mm": height}), 201


# Handy GET for debugging / quick check
@main_bp.get("/api/measurements")
def get_measurements():
    return jsonify(MeasurementRepository.get_all(50))