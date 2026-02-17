from __future__ import annotations

from .db import connect
from .utils import utc_iso
from .settings import settings
from .notification_service import create_notification


def submit_rating(payload) -> None:
    con = connect()
    cur = con.cursor()

    # Ensure booking exists for this rider + ride (basic trust)
    cur.execute(
        "SELECT id FROM bookings WHERE ride_id=? AND rider_id=? AND status='CONFIRMED' LIMIT 1",
        (int(payload.ride_id), int(payload.rater_id)),
    )
    if not cur.fetchone():
        con.close()
        raise ValueError("You can only rate after you have booked this ride")

    cur.execute(
        """
        INSERT INTO ratings (ride_id, rater_id, driver_id, stars, comment, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            int(payload.ride_id),
            int(payload.rater_id),
            int(payload.driver_id),
            int(payload.stars),
            payload.comment,
            utc_iso(),
        ),
    )
    con.commit()
    con.close()

    if settings.ENABLE_IN_APP_NOTIFICATIONS:
        create_notification(int(payload.driver_id), "New Rating", "You received a new rating. 🌟")


def get_driver_rating_summary(driver_id: int) -> dict:
    con = connect()
    cur = con.cursor()

    cur.execute(
        "SELECT COUNT(*) AS cnt, AVG(stars) AS avg_stars FROM ratings WHERE driver_id=?",
        (driver_id,),
    )
    row = cur.fetchone()
    con.close()

    total = int(row["cnt"] or 0)
    avg = float(row["avg_stars"] or 0.0)
    return {
        "driver_id": driver_id,
        "average_stars": round(avg, 2),
        "total_ratings": total,
    }
