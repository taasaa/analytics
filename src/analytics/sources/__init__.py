"""Data source registry - simple dict for now"""

from typing import Callable, Dict

# Source functions: (get_requests, get_sessions)
SOURCES: Dict[str, tuple] = {
    'litellm': None,  # Will be imported on-demand
    # Future sources:
    # 'server_monitor': None,
    # 'network': None,
}

def get_source(name: str):
    """Get source functions by name"""
    if name not in SOURCES:
        raise ValueError(f"Unknown source: {name}")

    # Lazy import to avoid circular dependencies
    if name == 'litellm':
        from . import litellm
        return litellm.get_requests, litellm.get_sessions

    raise ValueError(f"Source not implemented: {name}")