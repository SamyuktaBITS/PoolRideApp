from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_iso(dt: datetime | None = None) -> str:
    """
    Returns ISO string in UTC timezone.
    """
    if dt is None:
        dt = utc_now()
    return dt.astimezone(timezone.utc).isoformat()


def parse_iso_datetime(value: str) -> datetime:
    """
    Parse ISO 8601 datetime string.
    """
    return datetime.fromisoformat(value)
