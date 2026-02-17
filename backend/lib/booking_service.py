from __future__ import annotations

from typing import List
from .db import connect
from .settings import settings
from .utils import utc_iso, parse_iso_datetime
from .co2_service import estimate_co2_saved
from .notification_service import create_notification


def _ensure_user_verified(user_id: int):
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT id, is_verified, user_type FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    con.close()
    if not row:
        raise ValueError("User not found")
    if int(row["is_verified"]) != 1:
        raise ValueError("User must be verified to perform this action")
    return row


def create_booking(payload):
    """
    payload: BookingCreateRequest
    """
    rider = _ensure_user_verified(payload.rider_id)

    con = connect()
    cur = con.cursor()

    # ride exists?
    cur.execute("SELECT * FROM rides WHERE id=?", (payload.ride_id,))
    ride = cur.fetchone()
    if not ride:
        con.close()
        raise ValueError("Ride not found")

    # seats
    if int(ride["seats_left"]) < int(payload.seats):
        con.close()
        raise ValueError("Not enough seats available")

    # guest policy
    rider_is_guest = (rider["user_type"] == "guest")
    allow_guests = bool(int(ride["allow_guests"]))
    if rider_is_guest and not allow_guests:
        con.close()
        raise ValueError("This ride does not allow guest bookings")

    # booking limits (MVP simple check: bookings today)
    # optional: kept simple here; you can enforce later with date filtering

    # update seats and create booking
    cur.execute(
        "UPDATE rides SET seats_left = seats_left - ? WHERE id=?",
        (int(payload.seats), int(payload.ride_id)),
    )

    created_at = utc_iso()
    cur.execute(
        """
        INSERT INTO bookings (ride_id, rider_id, seats, status, created_at)
        VALUES (?, ?, ?, 'CONFIRMED', ?)
        """,
        (int(payload.ride_id), int(payload.rider_id), int(payload.seats), created_at),
    )
    booking_id = cur.lastrowid

    # compute passengers total (driver + current riders)
    cur.execute("SELECT seats_total, seats_left FROM rides WHERE id=?", (int(payload.ride_id),))
    seat_row = cur.fetchone()
    seats_total = int(seat_row["seats_total"])
    seats_left = int(seat_row["seats_left"])
    riders_now = seats_total - seats_left
    passengers_total = 1 + max(riders_now, 0)

    con.commit()
    con.close()

    # notifications
    if settings.ENABLE_IN_APP_NOTIFICATIONS:
        create_notification(int(ride["driver_id"]), "New Booking", "Someone booked a seat on your ride.")
        create_notification(int(payload.rider_id), "Booking Confirmed", "Your booking is confirmed. 🌱")

    co2_saved = estimate_co2_saved(float(ride["distance_km"]), ride["vehicle_type"], passengers_total)

    drop_note = None
    if rider_is_guest and settings.GUEST_DROP_POLICY == "GATE_ONLY":
        drop_note = f"Guest drop-off at {settings.DEFAULT_GATE_NAME}. Entry inside campus is handled by gate security."

    return {
        "id": booking_id,
        "ride_id": int(payload.ride_id),
        "rider_id": int(payload.rider_id),
        "seats": int(payload.seats),
        "status": "CONFIRMED",
        "created_at": parse_iso_datetime(created_at),
        "co2_saved_kg_est": float(co2_saved),
        "drop_note": drop_note,
        "driver_id": int(ride["driver_id"]),
        "from_text": ride["from_text"],
        "to_text": ride["to_text"],
        "depart_time": parse_iso_datetime(ride["depart_time"]),
        
    }


def cancel_booking(booking_id: int) -> None:
    con = connect()
    cur = con.cursor()

    # only cancel if exists and confirmed
    cur.execute("SELECT id, status, ride_id, seats, rider_id FROM bookings WHERE id=?", (booking_id,))
    b = cur.fetchone()
    if not b:
        con.close()
        raise ValueError("Booking not found")

    if b["status"] != "CONFIRMED":
        con.close()
        raise ValueError("Booking already cancelled")

    # mark cancelled + restore seats
    cur.execute(
        "UPDATE bookings SET status='CANCELLED', cancelled_at=? WHERE id=?",
        (utc_iso(), booking_id),
    )
    cur.execute(
        "UPDATE rides SET seats_left = seats_left + ? WHERE id=?",
        (int(b["seats"]), int(b["ride_id"])),
    )

    con.commit()
    con.close()

    if settings.ENABLE_IN_APP_NOTIFICATIONS:
        create_notification(int(b["rider_id"]), "Booking Cancelled", "Your booking was cancelled.")
        # driver notification optional; can add later


def get_user_bookings(user_id: int) -> List[dict]:
    con = connect()
    cur = con.cursor()
    cur.execute(
       """
        SELECT b.id, b.ride_id, b.rider_id, b.seats, b.status, b.created_at,
               r.driver_id, r.from_text, r.to_text, r.depart_time,
               r.distance_km, r.vehicle_type, r.seats_total, r.seats_left
        FROM bookings b
        JOIN rides r ON r.id = b.ride_id
        WHERE b.rider_id=?
        ORDER BY b.id DESC
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    con.close()

    out = []
    for row in rows:
        seats_total = int(row["seats_total"])
        seats_left = int(row["seats_left"])
        riders_now = seats_total - seats_left
        passengers_total = 1 + max(riders_now, 0)
        co2_saved = estimate_co2_saved(float(row["distance_km"]), row["vehicle_type"], passengers_total)

        out.append(
            {
                "id": row["id"],
                "ride_id": row["ride_id"],
                "rider_id": row["rider_id"],
                "seats": row["seats"],
                "status": row["status"],
                "created_at": parse_iso_datetime(row["created_at"]),
                "co2_saved_kg_est": float(co2_saved),
                "drop_note": None,
                "driver_id": int(row["driver_id"]),
                "from_text": row["from_text"],
                "to_text": row["to_text"],
                "depart_time": parse_iso_datetime(row["depart_time"]),
            }
        )
    return out
