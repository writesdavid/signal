from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from typing import Optional

MAX_AGE_DAYS = 7


def cutoff() -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)


def is_recent(date_str: str) -> bool:
    """Return True if date_str is within MAX_AGE_DAYS. Unknown dates pass through."""
    if not date_str:
        return True
    try:
        # ISO 8601 (arXiv, HN)
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except ValueError:
        try:
            # RFC 2822 (HuggingFace RSS)
            dt = parsedate_to_datetime(date_str)
        except Exception:
            return True  # unparseable — let it through
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt >= cutoff()


def unix_cutoff() -> int:
    return int(cutoff().timestamp())
