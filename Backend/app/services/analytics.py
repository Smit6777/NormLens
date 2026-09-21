"""Historical trend analysis and usage tracking."""
import json
import os
from typing import Dict
from app.core.config import get_settings

def get_analytics_file() -> str:
    return os.path.join(get_settings().data_dir, "analytics.json")

_usage_data: Dict[str, int] = {}
_loaded = False

def _load():
    global _loaded, _usage_data
    if _loaded:
        return
    fpath = get_analytics_file()
    if os.path.exists(fpath):
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                _usage_data = json.load(f)
        except json.JSONDecodeError:
            _usage_data = {}
    _loaded = True

def _save():
    fpath = get_analytics_file()
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(_usage_data, f, indent=2)

def track_recommendation(is_number: str):
    """Track that a standard was recommended."""
    _load()
    _usage_data[is_number] = _usage_data.get(is_number, 0) + 1
    _save()

def get_usage(is_number: str) -> int:
    """Get recommendation count for a standard."""
    _load()
    return _usage_data.get(is_number, 0)
