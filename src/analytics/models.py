"""Data models for analytics"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Request:
    """Single request data"""
    timestamp: datetime
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    duration_seconds: Optional[float] = None
    status: str = 'success'
    session_id: Optional[str] = None
    user: Optional[str] = None
    cache_hit: bool = False


@dataclass
class Session:
    """Session data (aggregated)"""
    session_id: str
    request_count: int
    models: list
    session_start: datetime
    session_end: datetime
    total_tokens: int = 0