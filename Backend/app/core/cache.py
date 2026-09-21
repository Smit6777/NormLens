"""Simple in-memory caching layer for advanced features."""
from typing import Any
import json
import hashlib
from app.core.config import get_settings

_cache: dict[str, Any] = {}

def _generate_key(prefix: str, **kwargs) -> str:
    key_str = json.dumps(kwargs, sort_keys=True)
    key_hash = hashlib.md5(key_str.encode("utf-8")).hexdigest()
    return f"{prefix}:{key_hash}"

def cache_get(prefix: str, **kwargs) -> Any | None:
    settings = get_settings()
    if not settings.enable_cache:
        return None
    key = _generate_key(prefix, **kwargs)
    return _cache.get(key)

def cache_set(prefix: str, value: Any, **kwargs) -> None:
    settings = get_settings()
    if settings.enable_cache:
        key = _generate_key(prefix, **kwargs)
        _cache[key] = value

def clear_cache() -> None:
    _cache.clear()
