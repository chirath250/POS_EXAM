import re
from datetime import timedelta, timezone, tzinfo

try:
    from zoneinfo import ZoneInfo
    COLOMBO: tzinfo = ZoneInfo("Asia/Colombo")
except Exception:
    COLOMBO = timezone(timedelta(hours=5, minutes=30), "Asia/Colombo")

_LOCAL = re.compile(r"^07\d{8}$")
_INTL = re.compile(r"^\+947\d{8}$")
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_mobile(value: str) -> str:
    cleaned = re.sub(r"[ \-]", "", (value or "").strip())
    if _LOCAL.match(cleaned):
        return "+94" + cleaned[1:]
    if _INTL.match(cleaned):
        return cleaned
    raise ValueError("Mobile number must be 07XXXXXXXX or +947XXXXXXXX")


def validate_email(value: str) -> str:
    value = value.strip()
    if not _EMAIL.match(value):
        raise ValueError("Invalid email address")
    return value
