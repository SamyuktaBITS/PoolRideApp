from __future__ import annotations
from typing import List
from datetime import datetime

from .db import connect
from .utils import utc_iso, parse_iso_datetime


def create_notification(user_id: int, title: str, body: str) -> None:
    con = connect()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO notifications (user_id, title, body, created_at, is_read) VALUES (?, ?, ?, ?, 0)",
        (user_id, title, body, utc_iso()),
    )
    con.commit()
    con.close()


def get_user_notifications(user_id: int) -> List[dict]:
    con = connect()
    cur = con.cursor()
    cur.execute(
        "SELECT id, user_id, title, body, created_at, is_read FROM notifications WHERE user_id=? ORDER BY id DESC",
        (user_id,),
    )
    rows = cur.fetchall()
    con.close()

    out = []
    for r in rows:
        out.append(
            {
                "id": r["id"],
                "user_id": r["user_id"],
                "title": r["title"],
                "body": r["body"],
                "created_at": parse_iso_datetime(r["created_at"]),
                "is_read": bool(r["is_read"]),
            }
        )
    return out


def mark_notification_read(notification_id: int) -> None:
    con = connect()
    cur = con.cursor()
    cur.execute("UPDATE notifications SET is_read=1 WHERE id=?", (notification_id,))
    if cur.rowcount == 0:
        con.close()
        raise ValueError("Notification not found")
    con.commit()
    con.close()
