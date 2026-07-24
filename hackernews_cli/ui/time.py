"""Time formatting helpers shared by terminal screens."""

from datetime import datetime, timezone


def full_relative_time(value, now=None, display_timezone=None):
    """Format an ISO timestamp as a full local date followed by its age."""
    timestamp = _parse_timestamp(value)
    if timestamp is None:
        return "-"

    displayed = (
        timestamp.astimezone(display_timezone)
        if display_timezone is not None
        else timestamp.astimezone()
    )
    full_date = displayed.strftime("%Y-%m-%d %H:%M:%S")
    return f"{full_date} ({relative_time(value, now)})"


def relative_time(value, now=None):
    """Format an ISO timestamp as a compact relative age."""
    timestamp = _parse_timestamp(value)
    if timestamp is None:
        return "-"

    current = now or datetime.now(timezone.utc)
    seconds = max(0, int((current - timestamp).total_seconds()))

    if seconds < 60:
        return "just now"
    if seconds < 3600:
        return f"{seconds // 60}m ago"
    if seconds < 86400:
        return f"{seconds // 3600}h ago"

    days = seconds // 86400
    if days < 7:
        return f"{days}d ago"
    if days < 35:
        return f"{days // 7}w ago"
    if days < 365:
        return f"{days // 30}mo ago"
    return f"{days // 365}y ago"


def _parse_timestamp(value):
    if not value:
        return None

    try:
        timestamp = datetime.fromisoformat(value)
    except ValueError:
        return None

    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=timezone.utc)
    return timestamp
