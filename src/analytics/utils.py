"""Utility functions for analytics platform"""

from datetime import datetime
from typing import Optional


def generate_timestamped_filename(prefix: str = "analytics", extension: str = "json") -> str:
    """Generate a timestamped filename with the current datetime.

    Args:
        prefix: Filename prefix (default: "analytics")
        extension: File extension without dot (default: "json")

    Returns:
        Filename in format: prefix_YYYYMMDD_HHMMSS.extension
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{timestamp}.{extension}"


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string like "1.5m", "2.3s", or "150ms"
    """
    if seconds >= 60:
        return f"{seconds/60:.1f}m"
    elif seconds >= 1:
        return f"{seconds:.1f}s"
    else:
        return f"{seconds*1000:.0f}ms"


def parse_date(date_string: Optional[str], format: str = '%Y-%m-%d') -> Optional[datetime]:
    """Parse date string to datetime object.

    Args:
        date_string: Date string to parse (optional)
        format: Date format string (default: '%Y-%m-%d')

    Returns:
        datetime object or None if date_string is None
    """
    return datetime.strptime(date_string, format) if date_string else None