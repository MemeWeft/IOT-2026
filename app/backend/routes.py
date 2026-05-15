from flask import Blueprint, jsonify, render_template, request, abort, session, redirect, url_for
from .model import MeasurementRepository, ReportRepository
from .users import UserRepository
from .auth import login_required, admin_required

main_bp = Blueprint("main", __name__)

# ── Pages ──────────────────────────────────────────────────────────────────

# Nieuwe route voor de pagina van de kaart:
@main_bp.get("/kaart")
@login_required
def kaart_weergave():
    kaart      = MeasurementRepository.get_map_data()
    return render_template("kaart.html", kaart=kaart)

@main_bp.get("/")
@login_required
def index():
    return redirect(url_for("main.dashboard"))

@main_bp.get("/dashboard")
@login_required
def dashboard():
    stats      = MeasurementRepository.get_stats()
    summary    = MeasurementRepository.get_location_summary()
    compliance = MeasurementRepository.get_compliance_pct()
    loc_count  = MeasurementRepository.get_unique_location_count()
    return render_template("dashboard.html", stats=stats, summary=summary,
                           compliance_pct=compliance, loc_count=loc_count)

@main_bp.get("/reports")
@login_required
def reports():
    ReportRepository.purge_expired()
    rpts = ReportRepository.get_all()
    return render_template("reports.html", reports=rpts)

@main_bp.get("/measurement")
@login_required
def measurement():
    stats = MeasurementRepository.get_stats()
    rows  = MeasurementRepository.get_all(50)
    return render_template("measurement.html", stats=stats, rows=rows)

@main_bp.get("/users")
@admin_required
def users_page():
    all_users = UserRepository.get_all()
    return render_template("users.html", users=all_users)

# User management API
@main_bp.post("/api/users")
@admin_required
def api_create_user():
    body = request.get_json(force=True, silent=True) or {}
    username = body.get("username", "").strip()
    password = body.get("password", "")
    is_admin = bool(body.get("is_admin", False))
    if not username or not password:
        abort(400, "username and password required")
    user_id = UserRepository.create(username, password, is_admin)
    if user_id is None:
        abort(409, "Username already exists")
    return jsonify({"id": user_id, "username": username}), 201

@main_bp.post("/api/users/<int:user_id>/password")
@admin_required
def api_update_password(user_id):
    body = request.get_json(force=True, silent=True) or {}
    password = body.get("password", "")
    if not password:
        abort(400, "password required")
    UserRepository.update_password(user_id, password)
    return jsonify({"updated": user_id})

@main_bp.delete("/api/users/<int:user_id>")
@admin_required
def api_delete_user(user_id):
    if user_id == session.get("user_id"):
        abort(400, "Cannot delete your own account")
    success = UserRepository.delete(user_id)
    if not success:
        abort(400, "Cannot delete admin account")
    return jsonify({"deleted": user_id})

# Measurement API (open for Pico):

# Deze functie haalt JSON data op die de Pico instuurt en haalt daar hoogte, latitude en longitude uit.
# Als er geen hoogte is, geeft hij foutmelding terug.
# Hij slaat de meting op in de database via model.py en stuurt dan bevestiging naar Pico.
@main_bp.post("/api/measurement")
def add_measurement():
    body = request.get_json(force=True, silent=True) or {}
    height = body.get("height_mm")
    lat = body.get("latitude")
    long = body.get("longitude")
    if height is None:
        abort(400, "height_mm required")
    row_id = MeasurementRepository.insert(float(height), body.get("location", "Onbekend"), lat, long)
    return jsonify({"id": row_id, "height_mm": height, "latitude": lat, "longitude": long}), 201

@main_bp.get("/api/measurements")
@login_required
def api_measurements():
    return jsonify(MeasurementRepository.get_all(50))

@main_bp.get("/api/chart-data")
@login_required
def api_chart_data():
    return jsonify(MeasurementRepository.get_chart_data())

@main_bp.get("/api/quality-summary")
@login_required
def api_quality_summary():
    return jsonify(MeasurementRepository.get_quality_summary())

@main_bp.get("/api/location-summary")
@login_required
def api_location_summary():
    return jsonify(MeasurementRepository.get_location_summary())

@main_bp.post("/api/reports/generate")
@login_required
def api_generate_report():
    report_id = ReportRepository.generate_weekly()
    return jsonify({"id": report_id}), 201

@main_bp.delete("/api/reports/<int:report_id>")
@login_required
def api_delete_report(report_id):
    ReportRepository.delete(report_id)
    return jsonify({"deleted": report_id})