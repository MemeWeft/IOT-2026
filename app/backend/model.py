from .database import get_db


class MeasurementRepository:

    @staticmethod
    def get_all(limit: int = 50) -> list[dict]:
        rows = get_db().execute(
            "SELECT * FROM measurements ORDER BY measured_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def insert(height_mm: float, location: str = "Onbekend") -> int:
        db = get_db()
        cur = db.execute(
            "INSERT INTO measurements (height_mm, location) VALUES (?, ?)",
            (height_mm, location)
        )
        db.commit()
        return cur.lastrowid

    @staticmethod
    def get_stats() -> dict:
        row = get_db().execute("""
            SELECT
                COUNT(*)           AS total,
                ROUND(AVG(height_mm), 1) AS avg_height,
                ROUND(MAX(height_mm), 1) AS max_height,
                ROUND(MIN(height_mm), 1) AS min_height
            FROM measurements
        """).fetchone()
        return dict(row) if row else {}