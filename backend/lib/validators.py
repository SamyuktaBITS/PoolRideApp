import re
from typing import Optional
from .settings import settings


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[0-9]{10,15}$")

def normalize_email(email: str) -> str:
    return email.strip().lower()


def email_domain(email: str) -> str:
    return normalize_email(email).split("@")[-1]


def validate_email_format(email: str) -> None:
    if not EMAIL_RE.match(email.strip()):
        raise ValueError("Invalid email format")


def validate_campus_email(email: str) -> None:
    validate_email_format(email)
    domain = email_domain(email)
    if settings.ENABLE_CAMPUS_VERIFICATION and domain not in set(d.lower() for d in settings.ALLOWED_CAMPUS_DOMAINS):
        raise ValueError("Email domain not allowed for campus verification")


def validate_phone(phone: str) -> None:
    # MVP: allow digits + optional + and spaces; keep simple
    clean = phone.strip().replace(" ", "")
    if not re.match(r"^\+?[0-9]{8,15}$", clean):
        raise ValueError("Invalid phone number")





def validate_user_type(user_type: str) -> None:
    if not user_type:
        raise ValueError("user_type is required")
    user_type = user_type.strip().lower()
    if user_type not in {"campus", "guest"}:
        raise ValueError("user_type must be 'campus' or 'guest'")


def validate_contact(contact: str, user_type: str) -> None:
    if not contact:
        raise ValueError("contact is required")

    contact = contact.strip()
    user_type = (user_type or "").strip().lower()

    # Campus => email only
    if user_type == "campus":
        if not EMAIL_RE.match(contact):
            raise ValueError("campus users must provide email")
        return

    # Guest => email OR phone
    if user_type == "guest":
        if EMAIL_RE.match(contact):
            return
        if PHONE_RE.match(contact):
            return
        raise ValueError("guest users must provide a valid email or phone number")

    # If user_type unknown, still validate something
    if not (EMAIL_RE.match(contact) or PHONE_RE.match(contact)):
        raise ValueError("contact must be a valid email or phone number")
