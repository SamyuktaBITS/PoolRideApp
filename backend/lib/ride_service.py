from __future__ import annotations

from .db import connect
from .settings import settings
from .notification_service import create_notification
from .utils import utc_iso


def create_ride(payload):
    """
    payload: RideCreateRequest
    Rule: Only campus users (and verified) can post rides.
    """
    con = connect()
    cur = con.cursor()

    # driver exists?
    cur.execute("SELECT id, user_type, is_verified FROM users WHERE id=?", (payload.driver_id,))
    driver = cur.fetchone()
    if not driver:
        con.close()
        raise ValueError("Driver not found")

    if driver["user_type"] != "campus":
        con.close()
        raise ValueError("Only campus users can post rides")

    if int(driver["is_verified"]) != 1:
        con.close()
        raise ValueError("Driver must be verified before posting rides")

    allow_guests = int(bool(payload.allow_guests))
    # if not explicitly set, fallback to config default
    if payload.allow_guests is None:
        allow_guests = int(settings.ALLOW_GUESTS_BY_DEFAULT)

    cur.execute(
        """
        INSERT INTO rides (driver_id, from_text, to_text, depart_time, seats_total, seats_left,
                           vehicle_type, allow_guests, distance_km, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload.driver_id,
            payload.from_text.strip(),
            payload.to_text.strip(),
            payload.depart_time.isoformat(),
            payload.seats_total,
            payload.seats_total,
            payload.vehicle_type.strip().lower(),
            allow_guests,
            float(payload.distance_km),
            utc_iso(),
        ),
    )
    con.commit()
    ride_id = cur.lastrowid
    con.close()

    if settings.ENABLE_IN_APP_NOTIFICATIONS:
        create_notification(payload.driver_id, "Ride Posted", "Your ride is now visible for bookings.")

    return {
        "id": ride_id,
        "driver_id": payload.driver_id,
        "from_text": payload.from_text.strip(),
        "to_text": payload.to_text.strip(),
        "depart_time": payload.depart_time,
        "seats_total": payload.seats_total,
        "seats_left": payload.seats_total,
        "vehicle_type": payload.vehicle_type.strip().lower(),
        "allow_guests": bool(allow_guests),
        "distance_km": float(payload.distance_km),
    }


def search_rides(from_q: str, to_q: str):
    con = connect()
    cur = con.cursor()
    cur.execute(
        """
        SELECT id, driver_id, from_text, to_text, depart_time, seats_total, seats_left,
               vehicle_type, allow_guests, distance_km
        FROM rides
        WHERE seats_left > 0
          AND LOWER(from_text) LIKE ?
          AND LOWER(to_text) LIKE ?
        ORDER BY depart_time ASC
        """,
        (f"%{from_q.lower()}%", f"%{to_q.lower()}%"),
    )
    rows = cur.fetchall()
    con.close()

    from .utils import parse_iso_datetime
    out = []
    for r in rows:
        out.append(
            {
                "id": r["id"],
                "driver_id": r["driver_id"],
                "from_text": r["from_text"],
                "to_text": r["to_text"],
                "depart_time": parse_iso_datetime(r["depart_time"]),
                "seats_total": r["seats_total"],
                "seats_left": r["seats_left"],
                "vehicle_type": r["vehicle_type"],
                "allow_guests": bool(r["allow_guests"]),
                "distance_km": float(r["distance_km"]),
            }
        )
    return out


def get_ride_by_id(ride_id: int):
    con = connect()
    cur = con.cursor()
    cur.execute(
        """
        SELECT id, driver_id, from_text, to_text, depart_time, seats_total, seats_left,
               vehicle_type, allow_guests, distance_km
        FROM rides
        WHERE id=?
        """,
        (ride_id,),
    )
    r = cur.fetchone()
    con.close()

    if not r:
        raise ValueError("Ride not found")

    from .utils import parse_iso_datetime
    return {
        "id": r["id"],
        "driver_id": r["driver_id"],
        "from_text": r["from_text"],
        "to_text": r["to_text"],
        "depart_time": parse_iso_datetime(r["depart_time"]),
        "seats_total": r["seats_total"],
        "seats_left": r["seats_left"],
        "vehicle_type": r["vehicle_type"],
        "allow_guests": bool(r["allow_guests"]),
        "distance_km": float(r["distance_km"]),
    }
