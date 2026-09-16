"""Datetime and timezone utilities for the application."""

from datetime import datetime, timedelta, timezone

# Vietnam uses ICT (UTC+7)
VIETNAM_TZ = timezone(timedelta(hours=7))


def now_utc() -> datetime:
    """Returns the current datetime in UTC."""
    return datetime.now(timezone.utc)


def now_ict() -> datetime:
    """Returns the current datetime in Vietnam time (ICT) as a naive datetime."""
    return datetime.now(VIETNAM_TZ).replace(tzinfo=None)


def now_utc() -> datetime:
    """Returns current UTC datetime."""
    return datetime.now(timezone.utc)


def utc_to_ict(dt: datetime) -> datetime:
    """Converts a UTC datetime to ICT. If naive, assumes it's already ICT."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=VIETNAM_TZ)
    return dt.astimezone(VIETNAM_TZ)

