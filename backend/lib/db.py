from __future__ import annotations

import sqlite3
from pathlib import Path
from .settings import settings


def connect() -> sqlite3.Connection:
    db_path = settings.db_path_abs
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    return con


def init_db() -> None:
    con = connect()
    cur = con.cursor()

    # USERS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        user_type TEXT NOT NULL,                 -- "campus" | "guest"
        email TEXT UNIQUE,                       -- nullable for guest (phone-only)
        phone TEXT UNIQUE,                       -- nullable for campus (email-only)
        is_verified INTEGER NOT NULL DEFAULT 0,  -- OTP verified
        created_at TEXT NOT NULL
    )
    """)

    # OTPs
    cur.execute("""
    CREATE TABLE IF NOT EXISTS otps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        code TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        used INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # RIDES
    cur.execute("""
    CREATE TABLE IF NOT EXISTS rides (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        driver_id INTEGER NOT NULL,
        from_text TEXT NOT NULL,
        to_text TEXT NOT NULL,
        depart_time TEXT NOT NULL,
        seats_total INTEGER NOT NULL,
        seats_left INTEGER NOT NULL,
        vehicle_type TEXT NOT NULL,
        allow_guests INTEGER NOT NULL DEFAULT 0,
        distance_km REAL NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(driver_id) REFERENCES users(id)
    )
    """)

    # BOOKINGS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ride_id INTEGER NOT NULL,
        rider_id INTEGER NOT NULL,
        seats INTEGER NOT NULL,
        status TEXT NOT NULL,                    -- "CONFIRMED" | "CANCELLED"
        created_at TEXT NOT NULL,
        cancelled_at TEXT,
        FOREIGN KEY(ride_id) REFERENCES rides(id),
        FOREIGN KEY(rider_id) REFERENCES users(id)
    )
    """)

    # NOTIFICATIONS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        created_at TEXT NOT NULL,
        is_read INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # RATINGS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ride_id INTEGER NOT NULL,
        rater_id INTEGER NOT NULL,
        driver_id INTEGER NOT NULL,
        stars INTEGER NOT NULL,
        comment TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(ride_id) REFERENCES rides(id),
        FOREIGN KEY(rater_id) REFERENCES users(id),
        FOREIGN KEY(driver_id) REFERENCES users(id)
    )
    """)

    con.commit()
    con.close()
