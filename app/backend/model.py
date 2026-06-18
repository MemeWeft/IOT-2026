from datetime import datetime, timedelta
from .database import get_db


def _client_filter(client_name):
    """Geeft (WHERE-clause, params) terug gefilterd op client_name als opgegeven."""
    if client_name:
        return "AND client_name = ?", (client_name,)
    return "", ()


class MeasurementRepository:

    @staticmethod
    def get_map_data(client_name=None) -> list[dict]:
        cf, params = _client_filter(client_name)
        rows = get_db().execute(
            f"SELECT location, latitude, longitude, height_mm "
            f"FROM measurements "
            f"WHERE latitude IS NOT NULL AND longitude IS NOT NULL {cf} "
            f"ORDER BY location, height_mm DESC",
            params
        ).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def get_all(limit: int = 50, client_name=None) -> list[dict]:
        cf, params = _client_filter(client_name)
        rows = get_db().execute(
            f"SELECT * FROM measurements WHERE 1=1 {cf} ORDER BY measured_at DESC LIMIT ?",
            params + (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def insert(height_mm: float, location: str = "Onbekend", latitude: float = None, longitude: float = None, client_name: str = None) -> int:
        db = get_db()
        cur = db.execute(
            "INSERT INTO measurements (height_mm, location, latitude, longitude, client_name) VALUES (?, ?, ?, ?, ?)",
            (height_mm, location, latitude, longitude, client_name or None)
        )
        db.commit()
        return cur.lastrowid

    @staticmethod
    def get_stats(client_name=None) -> dict:
        cf, params = _client_filter(client_name)
        row = get_db().execute(f"""
            SELECT
                COUNT(*)                 AS total,
                ROUND(AVG(height_mm), 1) AS avg_height,
                ROUND(MAX(height_mm), 1) AS max_height,
                ROUND(MIN(height_mm), 1) AS min_height
            FROM measurements WHERE 1=1 {cf}
        """, params).fetchone()
        return dict(row) if row else {}

    @staticmethod
    def get_location_summary(client_name=None) -> list[dict]:
        cf, params = _client_filter(client_name)
        rows = get_db().execute(f"""
            SELECT
                location,
                ROUND(AVG(height_mm), 1) AS avg_height,
                ROUND(MAX(height_mm), 1) AS max_height,
                COUNT(*)                 AS total,
                MAX(measured_at)         AS last_measured
            FROM measurements WHERE 1=1 {cf}
            GROUP BY location
            ORDER BY avg_height DESC
        """, params).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            h = d["avg_height"] or 0
            d["quality"] = "A" if h <= 50 else ("B" if h <= 80 else "C")
            result.append(d)
        return result

    @staticmethod
    def get_quality_summary(client_name=None) -> list[dict]:
        cf, params = _client_filter(client_name)
        rows = get_db().execute(f"""
            SELECT
                CASE
                    WHEN height_mm <= 50 THEN 'A'
                    WHEN height_mm <= 80 THEN 'B'
                    ELSE 'C'
                END AS quality,
                COUNT(*) AS count
            FROM measurements WHERE 1=1 {cf}
            GROUP BY quality
            ORDER BY quality
        """, params).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def get_compliance_pct(client_name=None) -> float:
        cf, params = _client_filter(client_name)
        row = get_db().execute(f"""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN height_mm <= 80 THEN 1 ELSE 0 END) AS compliant
            FROM measurements WHERE 1=1 {cf}
        """, params).fetchone()
        if not row or not row["total"]:
            return 0.0
        return round(row["compliant"] / row["total"] * 100, 1)

    @staticmethod
    def get_chart_data(client_name=None) -> list[dict]:
        cf, params = _client_filter(client_name)
        rows = get_db().execute(f"""
            SELECT
                DATE(measured_at)        AS day,
                location,
                ROUND(AVG(height_mm), 1) AS avg_height
            FROM measurements
            WHERE measured_at >= datetime('now', '-28 days') {cf}
            GROUP BY day, location
            ORDER BY day ASC
        """, params).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def get_unique_location_count(client_name=None) -> int:
        cf, params = _client_filter(client_name)
        row = get_db().execute(
            f"SELECT COUNT(DISTINCT location) AS cnt FROM measurements WHERE 1=1 {cf}",
            params
        ).fetchone()
        return row["cnt"] if row else 0


class ReportRepository:

    @staticmethod
    def get_all() -> list[dict]:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rows = get_db().execute("""
            SELECT *,
                CAST(ROUND(JULIANDAY(expires_at) - JULIANDAY(?)) AS INTEGER) AS days_left
            FROM reports
            WHERE expires_at > ?
            ORDER BY created_at DESC
        """, (now, now)).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def delete(report_id: int):
        db = get_db()
        db.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        db.commit()

    @staticmethod
    def generate_weekly() -> int:
        """Create a weekly report based on current measurement data."""
        db = get_db()
        now = datetime.now()
        week_nr = now.isocalendar()[1]
        year = now.year

        # Check if this week already exists
        existing = db.execute(
            "SELECT id FROM reports WHERE week_nr = ? AND year = ?", (week_nr, year)
        ).fetchone()
        if existing:
            return existing["id"]

        # Gather stats from the past 7 days
        stats = db.execute("""
            SELECT
                ROUND(AVG(height_mm), 1) AS avg_height,
                SUM(CASE WHEN height_mm <= 80 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS compliance
            FROM measurements
            WHERE measured_at >= datetime('now', '-7 days')
        """).fetchone()

        avg_h = stats["avg_height"] or 0
        comp = round(stats["compliance"] or 0, 1)
        expires = (now + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")

        cur = db.execute("""
            INSERT INTO reports (title, week_nr, year, avg_height, compliance, notes, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            f"Weekrapportage W{week_nr}-{year}",
            week_nr, year, avg_h, comp,
            "Automatisch gegenereerd rapport.",
            expires
        ))
        db.commit()
        return cur.lastrowid

    @staticmethod
    def purge_expired():
        db = get_db()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute("DELETE FROM reports WHERE expires_at <= ?", (now,))
        db.commit()