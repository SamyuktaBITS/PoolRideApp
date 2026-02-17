from __future__ import annotations

import secrets
from typing import Optional,Dict,Any
from fastapi import HTTPException

from .db import connect
from .utils import utc_iso


from .validators import (
    validate_user_type,
    validate_contact,
    normalize_email,
    validate_campus_email,
    validate_email_format,
    validate_phone,
)


from .models import AuthResponse, UserPublic, UserProfileResponse

from .settings import settings
from .notification_service import create_notification

def _user_row_to_public(row) -> UserPublic:
    return UserPublic(
        id=row["id"],
        name=row["name"],
        user_type=row["user_type"],
        is_verified=bool(row["is_verified"]),
    )

def _token_from_auth_header(authorization: Optional[str]) -> str:
    if not authorization:
        raise ValueError("Missing Authorization header")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise ValueError("Invalid Authorization header format")
    return parts[1].strip()

def get_user_id_from_token(token: str) -> int | None:
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM sessions WHERE token = ?", (token,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def require_user_id(authorization: Optional[str]) -> int:
    token = _token_from_auth_header(authorization)
    uid = get_user_id_from_token(token)
    if not uid:
        raise ValueError("Invalid or expired token")
    return int(uid)

def logout_token(authorization: Optional[str]) -> None:
    token = _token_from_auth_header(authorization)
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()
    conn.close()

def login_or_create_user(name: str, contact: str, user_type: str) -> Dict[str, Any]:
    validate_user_type(user_type)
    validate_contact(contact, user_type)

    name = (name or "").strip()
    contact = (contact or "").strip()

    is_email = "@" in contact

    email = None
    phone = None

    if is_email:
        email = normalize_email(contact)
        if user_type == "campus":
            validate_campus_email(email)
        else:
            validate_email_format(email)
    else:
        phone = contact
        validate_phone(phone)

    conn = connect()
    cur = conn.cursor()

    if email:
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    else:
        cur.execute("SELECT * FROM users WHERE phone = ?", (phone,))

    row = cur.fetchone()

    if not row:
        cur.execute(
            """
            INSERT INTO users (name, user_type, email, phone, is_verified, created_at)
            VALUES (?, ?, ?, ?, 1, ?)
            """,
            (name, user_type, email, phone, utc_iso()),
        )
        conn.commit()
        user_id = cur.lastrowid

        if settings.ENABLE_IN_APP_NOTIFICATIONS:
            create_notification(int(user_id), "Welcome to PoolRide", "You’re all set. 🌱")
    else:
        user_id = row["id"]
        cur.execute(
            "UPDATE users SET name=?, user_type=? WHERE id=?",
            (name or row["name"], user_type or row["user_type"], user_id),
        )
        conn.commit()

    token = secrets.token_urlsafe(24)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
    conn.commit()
    conn.close()

    return {
        "token": token,
        "user": {"id": user_id, "name": name, "user_type": user_type},
        "message": "Login successful",
    }


def get_user_profile(user_id: int) -> UserProfileResponse:
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cur.fetchone()
    if not user:
        conn.close()
        raise ValueError("User not found")

    cur.execute("SELECT COUNT(*) AS c FROM rides WHERE driver_id=?", (user_id,))
    rides_posted = int(cur.fetchone()["c"])

    cur.execute(
        "SELECT COUNT(*) AS c FROM bookings WHERE rider_id=? AND status='CONFIRMED'",
        (user_id,),
    )
    rides_taken = int(cur.fetchone()["c"])

    cur.execute(
        """
        SELECT b.id, r.distance_km, r.vehicle_type, r.seats_total, r.seats_left
        FROM bookings b
        JOIN rides r ON r.id = b.ride_id
        WHERE b.rider_id=? AND b.status='CONFIRMED'
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()

    from .co2_service import estimate_co2_saved

    total = 0.0
    for row in rows:
        seats_total = int(row["seats_total"])
        seats_left = int(row["seats_left"])
        riders_now = seats_total - seats_left
        passengers_total = 1 + max(riders_now, 0)
        total += float(estimate_co2_saved(float(row["distance_km"]), row["vehicle_type"], passengers_total))

    return UserProfileResponse(
        user=_user_row_to_public(user),
        rides_posted=rides_posted,
        rides_taken=rides_taken,
        total_co2_saved_kg=round(total, 3),
    )
