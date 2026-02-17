from datetime import datetime


def format_datetime(dt_str_or_obj) -> str:
    """
    Accepts ISO datetime string or datetime object and returns readable format.
    """
    if isinstance(dt_str_or_obj, datetime):
        dt = dt_str_or_obj
    else:
        dt = datetime.fromisoformat(str(dt_str_or_obj))
    return dt.strftime("%d %b %Y, %I:%M %p")


def iso_now_local_example() -> str:
    """
    Helpful placeholder for depart_time entry (MVP).
    """
    return "2026-02-06T18:30:00"
