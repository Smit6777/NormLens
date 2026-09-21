"""Security and authentication dependencies."""
from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from app.core.config import get_settings, Settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(
    api_key: str | None = Security(api_key_header),
    settings: Settings = Depends(get_settings)
) -> str:
    """Validate standard API key. For testing/demo, it accepts the configured key."""
    if api_key in [settings.api_key, settings.admin_api_key]:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key"
    )

def get_admin_api_key(
    api_key: str | None = Security(api_key_header),
    settings: Settings = Depends(get_settings)
) -> str:
    """Validate admin API key."""
    if api_key == settings.admin_api_key:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin privileges required"
    )

def get_optional_api_key(api_key: str | None = Security(api_key_header)) -> str | None:
    """Return API key if provided, else None."""
    return api_key
