import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+?[0-9]{8,15}$")


def is_valid_email(email: str) -> bool:
    return bool(email and EMAIL_RE.match(email.strip()))


def is_valid_phone(phone: str) -> bool:
    if not phone:
        return False
    return bool(PHONE_RE.match(phone.strip().replace(" ", "")))


def safe_strip(s: str) -> str:
    return (s or "").strip()
